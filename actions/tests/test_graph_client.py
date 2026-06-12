"""Integration tests for graph_client.py.

These tests require a real Azure AD App Registration and SharePoint site.
They are skipped by default unless the SHAREPOINT_INTEGRATION_TEST env var
is set to "1".

Required environment variables:
  AZURE_TENANT_ID     — Entra ID tenant
  AZURE_CLIENT_ID     — App Registration client ID
  TEST_SP_SITE        — e.g. phoenixdevelopments.sharepoint.com:/sites/BCTechDays2026
  TEST_SP_FOLDER      — e.g. /Shared Documents/IntegrationTest
"""

from __future__ import annotations

import asyncio
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from graph_client import GraphSyncClient, LARGE_FILE_THRESHOLD


SKIP_REASON = "Set SHAREPOINT_INTEGRATION_TEST=1 and configure credentials to run"


@pytest.fixture
def mock_graph_client():
    """Create a GraphSyncClient with mocked internals for unit-level integration tests."""
    with patch("graph_client.GraphServiceClient") as MockGSC, \
         patch("graph_client.DefaultAzureCredential"):
        client = GraphSyncClient(
            sharepoint_site="test.sharepoint.com:/sites/Test",
            sharepoint_folder="/Shared Documents/Test",
        )
        # Mock the internal SDK client
        mock_gsc = MockGSC.return_value
        client._client = mock_gsc
        client._site_id = "mock-site-id"
        client._drive_id = "mock-drive-id"
        yield client


class TestGraphSyncClientUnit:
    """Unit-level tests for GraphSyncClient with mocked Graph SDK."""

    def test_summary_initial_state(self, mock_graph_client: GraphSyncClient):
        summary = mock_graph_client.summary()
        assert "Uploaded: 0" in summary
        assert "Failed: 0" in summary

    def test_summary_after_operations(self, mock_graph_client: GraphSyncClient):
        mock_graph_client.files_uploaded = 5
        mock_graph_client.files_failed = 1
        mock_graph_client.files_skipped = 2
        mock_graph_client.bytes_transferred = 1024000

        summary = mock_graph_client.summary()
        assert "Uploaded: 5" in summary
        assert "Failed: 1" in summary
        assert "Skipped: 2" in summary

    @pytest.mark.asyncio
    async def test_upload_small_file(
        self, mock_graph_client: GraphSyncClient, tmp_path: Path
    ):
        # Create a small test file
        test_file = tmp_path / "small.txt"
        test_file.write_text("Hello, SharePoint!")

        # Mock the upload chain
        mock_drive = MagicMock()
        mock_items = MagicMock()
        mock_content = MagicMock()
        mock_content.put = AsyncMock(return_value=None)
        mock_items.content = mock_content
        mock_drive.items.by_drive_item_id.return_value = mock_items
        mock_graph_client._client.drives.by_drive_id.return_value = mock_drive

        result = await mock_graph_client.upload_file(test_file, "small.txt")

        assert result is True
        assert mock_graph_client.files_uploaded == 1
        assert mock_graph_client.bytes_transferred == test_file.stat().st_size


@pytest.mark.skipif(
    os.environ.get("SHAREPOINT_INTEGRATION_TEST") != "1",
    reason=SKIP_REASON,
)
class TestGraphSyncClientLive:
    """Live integration tests against a real SharePoint site."""

    @pytest.fixture
    def live_client(self):
        return GraphSyncClient(
            sharepoint_site=os.environ["TEST_SP_SITE"],
            sharepoint_folder=os.environ["TEST_SP_FOLDER"],
        )

    @pytest.mark.asyncio
    async def test_initialize_resolves_site(self, live_client):
        await live_client.initialize()
        assert live_client._site_id is not None
        assert live_client._drive_id is not None

    @pytest.mark.asyncio
    async def test_upload_and_verify(self, live_client, tmp_path: Path):
        await live_client.initialize()

        test_file = tmp_path / "integration-test.txt"
        test_file.write_text(
            "SharePoint Sync Integration Test — safe to delete"
        )

        result = await live_client.upload_file(
            test_file, "integration-test.txt"
        )
        assert result is True
        assert live_client.files_uploaded == 1
