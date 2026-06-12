"""Unit tests for config.py."""

from __future__ import annotations

import pytest
from pathlib import Path
from config import SyncConfig, load_config


@pytest.fixture
def tmp_config(tmp_path: Path):
    """Helper to write a YAML config file and return its path."""
    def _write(content: str) -> Path:
        p = tmp_path / "sharepoint-sync.yml"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


class TestLoadConfig:
    """Tests for load_config()."""

    def test_load_valid_minimal_config(self, tmp_config):
        path = tmp_config(
            "source_folder: docs\n"
            "sharepoint_site: contoso.sharepoint.com:/sites/MySite\n"
            "sharepoint_folder: /Shared Documents/Sync\n"
        )
        cfg = load_config(path)
        assert cfg.source_folder == "docs"
        assert cfg.sharepoint_site == "contoso.sharepoint.com:/sites/MySite"
        assert cfg.sharepoint_folder == "/Shared Documents/Sync"
        assert cfg.delete_orphaned is False
        assert cfg.file_patterns == []
        assert cfg.sync_mode == "auto"

    def test_load_full_config(self, tmp_config):
        path = tmp_config(
            "source_folder: docs/publish\n"
            "sharepoint_site: contoso.sharepoint.com:/sites/Proj\n"
            "sharepoint_folder: /Shared Documents/AutoSync\n"
            "delete_orphaned: true\n"
            "sync_mode: full\n"
            "file_patterns:\n"
            "  - '**/*.md'\n"
            "  - '**/*.pdf'\n"
        )
        cfg = load_config(path)
        assert cfg.delete_orphaned is True
        assert cfg.sync_mode == "full"
        assert cfg.file_patterns == ["**/*.md", "**/*.pdf"]

    def test_missing_required_field_raises(self, tmp_config):
        path = tmp_config(
            "source_folder: docs\n"
            "sharepoint_site: contoso.sharepoint.com:/sites/X\n"
            # missing sharepoint_folder
        )
        with pytest.raises(ValueError, match="sharepoint_folder"):
            load_config(path)

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.yml")

    def test_invalid_yaml_raises(self, tmp_config):
        path = tmp_config("just a string, not a mapping")
        with pytest.raises(ValueError, match="YAML mapping"):
            load_config(path)

    def test_invalid_sync_mode_raises(self, tmp_config):
        path = tmp_config(
            "source_folder: docs\n"
            "sharepoint_site: contoso.sharepoint.com:/sites/X\n"
            "sharepoint_folder: /Docs\n"
            "sync_mode: invalid\n"
        )
        with pytest.raises(ValueError, match="sync_mode"):
            load_config(path)


class TestSyncConfigResolveSource:
    """Tests for SyncConfig.resolve_source()."""

    def test_resolve_existing_folder(self, tmp_path: Path):
        src = tmp_path / "docs"
        src.mkdir()
        cfg = SyncConfig(
            source_folder="docs",
            sharepoint_site="x.sharepoint.com:/sites/X",
            sharepoint_folder="/Docs",
        )
        resolved = cfg.resolve_source(tmp_path)
        assert resolved == src.resolve()
        assert cfg.source_path == resolved

    def test_resolve_missing_folder_raises(self, tmp_path: Path):
        cfg = SyncConfig(
            source_folder="nonexistent",
            sharepoint_site="x.sharepoint.com:/sites/X",
            sharepoint_folder="/Docs",
        )
        with pytest.raises(FileNotFoundError, match="nonexistent"):
            cfg.resolve_source(tmp_path)
