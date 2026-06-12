"""Unit tests for delta.py."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from delta import (
    ChangeType,
    FileChange,
    detect_changes_full_scan,
    detect_changes_git_diff,
    resolve_sync_mode,
    _matches_patterns,
)


class TestMatchesPatterns:
    """Tests for the glob pattern matcher."""

    def test_no_patterns_matches_everything(self):
        assert _matches_patterns("any/file.txt", None) is True
        assert _matches_patterns("any/file.txt", []) is True

    def test_matching_pattern(self):
        assert _matches_patterns("readme.md", ["*.md"]) is True

    def test_non_matching_pattern(self):
        assert _matches_patterns("readme.txt", ["*.md"]) is False

    def test_multiple_patterns_any_match(self):
        assert _matches_patterns("doc.pdf", ["*.md", "*.pdf"]) is True

    def test_wildcard_subdir(self):
        assert _matches_patterns("sub/readme.md", ["**/*.md"]) is False
        # fnmatch does not support ** like glob; use * for flat match
        assert _matches_patterns("sub/readme.md", ["*/*.md"]) is True


class TestResolveSyncMode:
    """Tests for resolve_sync_mode()."""

    def test_auto_with_shas_returns_git_diff(self):
        assert resolve_sync_mode("auto", "abc123", "def456") == "git-diff"

    def test_auto_without_shas_returns_full(self):
        assert resolve_sync_mode("auto", None, None) == "full"
        assert resolve_sync_mode("auto", "", "") == "full"

    def test_explicit_mode_returned_as_is(self):
        assert resolve_sync_mode("full", "abc", "def") == "full"
        assert resolve_sync_mode("git-diff", None, None) == "git-diff"


class TestDetectChangesFullScan:
    """Tests for detect_changes_full_scan()."""

    def test_finds_all_files(self, tmp_path: Path):
        (tmp_path / "file1.md").write_text("hello")
        (tmp_path / "file2.txt").write_text("world")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.md").write_text("nested")

        changes = detect_changes_full_scan(tmp_path)

        paths = {c.path for c in changes}
        assert "file1.md" in paths
        assert "file2.txt" in paths
        assert "sub/nested.md" in paths
        assert all(c.change_type == ChangeType.MODIFIED for c in changes)

    def test_filters_by_pattern(self, tmp_path: Path):
        (tmp_path / "file.md").write_text("md")
        (tmp_path / "file.txt").write_text("txt")

        changes = detect_changes_full_scan(tmp_path, file_patterns=["*.md"])

        assert len(changes) == 1
        assert changes[0].path == "file.md"

    def test_empty_directory(self, tmp_path: Path):
        changes = detect_changes_full_scan(tmp_path)
        assert changes == []

    def test_preserves_subfolder_structure(self, tmp_path: Path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "deep.md").write_text("deep")

        changes = detect_changes_full_scan(tmp_path)

        assert any(c.path == "a/b/c/deep.md" for c in changes)


class TestDetectChangesGitDiff:
    """Tests for detect_changes_git_diff() with mocked subprocess."""

    @patch("delta.subprocess.run")
    def test_parses_added_modified_deleted(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            stdout="A\tdocs/new.md\nM\tdocs/changed.md\nD\tdocs/removed.md\n",
            returncode=0,
        )

        changes = detect_changes_git_diff(
            repo_root=Path("/repo"),
            source_folder="docs",
            base_sha="aaa",
            head_sha="bbb",
        )

        assert len(changes) == 3
        types = {c.path: c.change_type for c in changes}
        assert types["new.md"] == ChangeType.ADDED
        assert types["changed.md"] == ChangeType.MODIFIED
        assert types["removed.md"] == ChangeType.DELETED

    @patch("delta.subprocess.run")
    def test_empty_diff(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        changes = detect_changes_git_diff(
            repo_root=Path("/repo"),
            source_folder="docs",
            base_sha="aaa",
            head_sha="bbb",
        )

        assert changes == []

    @patch("delta.subprocess.run")
    def test_filters_by_pattern(self, mock_run: MagicMock):
        mock_run.return_value = MagicMock(
            stdout="A\tdocs/file.md\nA\tdocs/file.txt\n",
            returncode=0,
        )

        changes = detect_changes_git_diff(
            repo_root=Path("/repo"),
            source_folder="docs",
            base_sha="aaa",
            head_sha="bbb",
            file_patterns=["*.md"],
        )

        assert len(changes) == 1
        assert changes[0].path == "file.md"
