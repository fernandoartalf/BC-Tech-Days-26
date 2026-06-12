"""SharePoint Document Sync — Microsoft Graph client."""

from __future__ import annotations

import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from azure.identity import DefaultAzureCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item_uploadable_properties import (
    DriveItemUploadableProperties,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

logger = logging.getLogger(__name__)

# 4 MB threshold for resumable uploads (Graph API recommendation)
LARGE_FILE_THRESHOLD = 4 * 1024 * 1024
# Maximum size per upload range for resumable upload (10 MB)
UPLOAD_RANGE_SIZE = 10 * 1024 * 1024
# Retry settings
MAX_RETRIES = 5
RETRY_BASE_DELAY = 1.0


class GraphSyncClient:
    """Wraps Microsoft Graph SDK operations for SharePoint file sync."""

    def __init__(
        self,
        sharepoint_site: str,
        sharepoint_folder: str,
        credential: Optional[DefaultAzureCredential] = None,
    ) -> None:
        # SENSITIVE INFORMATION: DefaultAzureCredential acquires tokens from the
        # environment (OIDC in CI, CLI/managed identity locally). The resulting
        # access token grants write access to SharePoint — never log or expose it.
        self._credential = credential or DefaultAzureCredential()
        self._client = GraphServiceClient(
            credentials=self._credential,
            scopes=["https://graph.microsoft.com/.default"],
        )
        # SENSITIVE INFORMATION: sharepoint_site and sharepoint_folder reveal
        # internal infrastructure naming. Sourced from config — not hardcoded.
        self._sharepoint_site = sharepoint_site
        self._sharepoint_folder = sharepoint_folder.rstrip("/")
        # SENSITIVE INFORMATION: site_id and drive_id are internal SharePoint
        # resource identifiers resolved at runtime — do not log at INFO level.
        self._site_id: Optional[str] = None
        self._drive_id: Optional[str] = None

        self.files_uploaded = 0
        self.files_skipped = 0
        self.files_failed = 0
        self.bytes_transferred = 0

    async def initialize(self) -> None:
        """Resolve SharePoint site ID and default drive ID."""
        logger.info("Resolving SharePoint site: %s", self._sharepoint_site)

        # Parse site URL — expects format like "contoso.sharepoint.com:/sites/MySite"
        hostname, _, server_relative = self._sharepoint_site.partition(":/")
        if not server_relative:
            raise ValueError(
                f"Invalid sharepoint_site format: '{self._sharepoint_site}'. "
                "Expected 'hostname:/sites/SiteName'."
            )

        # The Graph SDK's by_site_id() URL-encodes colons and slashes,
        # which breaks the hostname:/path notation. Resolve the site ID
        # via a direct Graph API call instead.
        token = self._credential.get_token("https://graph.microsoft.com/.default")
        site_url = (
            f"https://graph.microsoft.com/v1.0/sites/"
            f"{hostname}:/{server_relative.lstrip('/')}"
        )
        async with httpx.AsyncClient() as http:
            resp = await http.get(
                site_url,
                headers={"Authorization": f"Bearer {token.token}"},
                timeout=30,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Could not resolve SharePoint site: {self._sharepoint_site}. "
                    f"HTTP {resp.status_code}: {resp.text}"
                )
            site_data = resp.json()

        self._site_id = site_data.get("id")
        if not self._site_id:
            raise RuntimeError(
                f"Could not resolve SharePoint site: {self._sharepoint_site}"
            )
        logger.info("Resolved site ID: %s", self._site_id)

        # Get the default document library drive (site ID is now a GUID — safe for SDK)
        drive = await self._client.sites.by_site_id(
            self._site_id
        ).drive.get()

        if not drive or not drive.id:
            raise RuntimeError("Could not resolve default drive for site")
        self._drive_id = drive.id
        logger.info("Resolved drive ID: %s", self._drive_id)

    async def upload_file(
        self,
        local_path: Path,
        remote_relative_path: str,
    ) -> bool:
        """Upload a single file to SharePoint.

        Uses simple upload for files < 4 MB, resumable upload for larger files.

        Args:
            local_path: Absolute path to the local file.
            remote_relative_path: Path relative to the SharePoint target folder.

        Returns:
            True if upload succeeded, False otherwise.
        """
        file_size = local_path.stat().st_size
        remote_path = f"{self._sharepoint_folder}/{remote_relative_path}"
        # Normalize path separators
        remote_path = remote_path.replace("\\", "/")
        # Remove double slashes
        while "//" in remote_path:
            remote_path = remote_path.replace("//", "/")

        logger.info(
            "Uploading %s (%d bytes) → %s",
            local_path.name,
            file_size,
            remote_path,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if file_size < LARGE_FILE_THRESHOLD:
                    await self._simple_upload(local_path, remote_path)
                else:
                    await self._resumable_upload(
                        local_path, remote_path, file_size
                    )

                self.files_uploaded += 1
                self.bytes_transferred += file_size
                return True

            except Exception as exc:
                delay = _backoff_delay(attempt)
                logger.warning(
                    "Upload attempt %d/%d failed for %s: %s. "
                    "Retrying in %.1fs...",
                    attempt,
                    MAX_RETRIES,
                    remote_relative_path,
                    exc,
                    delay,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(delay)

        logger.error(
            "All %d upload attempts failed for %s",
            MAX_RETRIES,
            remote_relative_path,
        )
        self.files_failed += 1
        return False

    async def _simple_upload(
        self, local_path: Path, remote_path: str
    ) -> None:
        """Upload a small file (< 4 MB) using PUT content."""
        content_type = (
            mimetypes.guess_type(str(local_path))[0]
            or "application/octet-stream"
        )
        with open(local_path, "rb") as fh:
            content = fh.read()

        await (
            self._client.drives.by_drive_id(self._drive_id)
            .items.by_drive_item_id(f"root:{remote_path}:")
            .content.put(content)
        )

    async def _resumable_upload(
        self, local_path: Path, remote_path: str, file_size: int
    ) -> None:
        """Upload a large file (>= 4 MB) using upload session."""
        props = DriveItemUploadableProperties(
            additional_data={
                "@microsoft.graph.conflictBehavior": "replace",
            }
        )

        upload_session = await (
            self._client.drives.by_drive_id(self._drive_id)
            .items.by_drive_item_id(f"root:{remote_path}:")
            .create_upload_session.post(
                body=props  # type: ignore[arg-type]
            )
        )

        if not upload_session or not upload_session.upload_url:
            raise RuntimeError("Failed to create upload session")

        # Upload in ranges
        with open(local_path, "rb") as fh:
            start = 0
            while start < file_size:
                end = min(start + UPLOAD_RANGE_SIZE, file_size) - 1
                chunk = fh.read(UPLOAD_RANGE_SIZE)
                content_range = f"bytes {start}-{end}/{file_size}"
                content_length = len(chunk)

                logger.debug(
                    "Uploading range %s (%d bytes)",
                    content_range,
                    content_length,
                )

                # Use httpx directly for range upload
                async with httpx.AsyncClient() as http:
                    resp = await http.put(
                        upload_session.upload_url,
                        content=chunk,
                        headers={
                            "Content-Range": content_range,
                            "Content-Length": str(content_length),
                        },
                        timeout=300,
                    )
                    resp.raise_for_status()

                start = end + 1

    def summary(self) -> str:
        """Return a human-readable summary of sync operations."""
        return (
            f"Uploaded: {self.files_uploaded} | "
            f"Failed: {self.files_failed} | "
            f"Skipped: {self.files_skipped} | "
            f"Bytes transferred: {self.bytes_transferred:,}"
        )


def _backoff_delay(attempt: int) -> float:
    """Exponential backoff with jitter."""
    import random

    delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
    jitter = random.uniform(0, delay * 0.5)  # noqa: S311
    return delay + jitter
