"""SharePoint Document Sync — delta detection."""

from __future__ import annotations

import fnmatch
import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"


@dataclass
class FileChange:
    """A single file change detected by delta analysis."""

    path: str  # Relative to source_folder
    change_type: ChangeType


def detect_changes_git_diff(
    repo_root: Path,
    source_folder: str,
    base_sha: str,
    head_sha: str,
    file_patterns: Optional[List[str]] = None,
) -> List[FileChange]:
    """Detect changes using git diff between two commits.

    Args:
        repo_root: Root of the git repository.
        source_folder: Relative path to the sync source folder.
        base_sha: Base commit SHA (merge base).
        head_sha: Head commit SHA (merged commit).
        file_patterns: Optional glob patterns to filter files.

    Returns:
        List of FileChange objects for files within source_folder.
    """
    cmd = [
        "git", "diff", "--name-status", "--no-renames",
        base_sha, head_sha, "--", source_folder,
    ]
    logger.info("Running: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )

    changes: List[FileChange] = []
    for line in result.stdout.strip().splitlines():
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            logger.warning("Unexpected git diff line: %s", line)
            continue

        status, file_path = parts
        # Make path relative to source_folder
        rel_path = file_path
        if rel_path.startswith(source_folder + "/"):
            rel_path = rel_path[len(source_folder) + 1:]
        elif rel_path.startswith(source_folder + "\\"):
            rel_path = rel_path[len(source_folder) + 1:]

        if not _matches_patterns(rel_path, file_patterns):
            continue

        change_type = _parse_status(status)
        if change_type:
            changes.append(FileChange(path=rel_path, change_type=change_type))

    logger.info("Git diff detected %d changes", len(changes))
    return changes


def detect_changes_full_scan(
    source_path: Path,
    file_patterns: Optional[List[str]] = None,
) -> List[FileChange]:
    """Full scan: treat every file in source_path as ADDED/MODIFIED.

    This mode does not detect deletions — it's additive-only.

    Args:
        source_path: Absolute path to the resolved source folder.
        file_patterns: Optional glob patterns to filter files.

    Returns:
        List of FileChange objects for all matching files.
    """
    changes: List[FileChange] = []
    for file in sorted(source_path.rglob("*")):
        if not file.is_file():
            continue
        rel = str(file.relative_to(source_path)).replace("\\", "/")
        if not _matches_patterns(rel, file_patterns):
            continue
        changes.append(FileChange(path=rel, change_type=ChangeType.MODIFIED))

    logger.info("Full scan found %d files", len(changes))
    return changes


def resolve_sync_mode(
    sync_mode: str,
    base_sha: Optional[str],
    head_sha: Optional[str],
) -> str:
    """Resolve 'auto' sync_mode to a concrete mode.

    Returns 'git-diff' if SHAs are available, otherwise 'full'.
    """
    if sync_mode == "auto":
        if base_sha and head_sha:
            return "git-diff"
        logger.info(
            "No base/head SHA available; falling back to full scan"
        )
        return "full"
    return sync_mode


def _parse_status(status: str) -> Optional[ChangeType]:
    """Map git status letter to ChangeType."""
    mapping = {"A": ChangeType.ADDED, "M": ChangeType.MODIFIED, "D": ChangeType.DELETED}
    return mapping.get(status[0].upper())


def _matches_patterns(
    rel_path: str, patterns: Optional[List[str]]
) -> bool:
    """Check if a relative path matches at least one glob pattern.

    If patterns is empty or None, all files match.
    """
    if not patterns:
        return True
    return any(fnmatch.fnmatch(rel_path, p) for p in patterns)
