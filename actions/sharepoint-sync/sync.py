"""SharePoint Document Sync — main entry point."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from config import SyncConfig, load_config
from delta import (
    ChangeType,
    FileChange,
    detect_changes_full_scan,
    detect_changes_git_diff,
    resolve_sync_mode,
)
from graph_client import GraphSyncClient

logger = logging.getLogger("sharepoint-sync")


async def run_sync(
    config: SyncConfig,
    repo_root: Path,
    base_sha: str | None = None,
    head_sha: str | None = None,
) -> bool:
    """Execute the full sync workflow.

    Args:
        config: Parsed sync configuration.
        repo_root: Root of the git repository.
        base_sha: PR merge base SHA (for git-diff mode).
        head_sha: PR head SHA (for git-diff mode).

    Returns:
        True if sync completed without errors, False otherwise.
    """
    # 1. Resolve source folder
    source_path = config.resolve_source(repo_root)
    logger.info("Source folder resolved: %s", source_path)

    # 2. Determine sync mode
    mode = resolve_sync_mode(config.sync_mode, base_sha, head_sha)
    logger.info("Sync mode: %s", mode)

    # 3. Detect changes
    if mode == "git-diff":
        assert base_sha and head_sha
        changes = detect_changes_git_diff(
            repo_root=repo_root,
            source_folder=config.source_folder,
            base_sha=base_sha,
            head_sha=head_sha,
            file_patterns=config.file_patterns or None,
        )
    else:
        changes = detect_changes_full_scan(
            source_path=source_path,
            file_patterns=config.file_patterns or None,
        )

    if not changes:
        logger.info("No files to sync. Exiting.")
        _write_summary("No files to sync — source folder has no matching changes.")
        return True

    # 4. Filter out deletions (additive-only per user decision)
    upload_changes = [c for c in changes if c.change_type != ChangeType.DELETED]
    deleted_count = len(changes) - len(upload_changes)
    if deleted_count:
        logger.info(
            "Skipping %d deleted file(s) (delete_orphaned=False policy)",
            deleted_count,
        )

    if not upload_changes:
        logger.info("All changes are deletions; nothing to upload.")
        _write_summary(
            f"No uploads needed. {deleted_count} deletion(s) skipped "
            "(additive-only mode)."
        )
        return True

    logger.info("Files to upload: %d", len(upload_changes))

    # 5. Initialize Graph client
    client = GraphSyncClient(
        sharepoint_site=config.sharepoint_site,
        sharepoint_folder=config.sharepoint_folder,
    )
    await client.initialize()

    # 6. Upload files
    has_errors = False
    for change in upload_changes:
        local_file = source_path / change.path
        if not local_file.is_file():
            logger.warning("File not found locally, skipping: %s", change.path)
            client.files_skipped += 1
            continue

        success = await client.upload_file(
            local_path=local_file,
            remote_relative_path=change.path,
        )
        if not success:
            has_errors = True

    # 7. Write summary
    summary = client.summary()
    logger.info("Sync complete. %s", summary)
    _write_summary(summary)

    return not has_errors


def _write_summary(text: str) -> None:
    """Write a summary to GitHub Actions step summary."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as fh:
            fh.write(f"## SharePoint Sync Results\n\n{text}\n")
    # Also set output
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as fh:
            fh.write(f"sync-summary={text}\n")


def main() -> None:
    """CLI entry point invoked by the composite action."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    config_path = os.environ.get(
        "SYNC_CONFIG_PATH",
        str(repo_root / ".github" / "sharepoint-sync.yml"),
    )
    base_sha = os.environ.get("BASE_SHA")
    head_sha = os.environ.get("HEAD_SHA")

    logger.info("Repository root: %s", repo_root)
    logger.info("Config path: %s", config_path)

    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)

    success = asyncio.run(
        run_sync(config, repo_root, base_sha, head_sha)
    )
    if not success:
        logger.error("Sync completed with errors")
        sys.exit(1)

    logger.info("Sync completed successfully")


if __name__ == "__main__":
    main()
