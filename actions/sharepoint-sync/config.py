"""SharePoint Document Sync — configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class SyncConfig:
    """Parsed representation of .github/sharepoint-sync.yml."""

    source_folder: str
    sharepoint_site: str
    sharepoint_folder: str
    delete_orphaned: bool = False
    file_patterns: List[str] = field(default_factory=list)
    sync_mode: str = "auto"  # "auto" | "git-diff" | "full"

    # Resolved at runtime
    source_path: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.sync_mode not in ("auto", "git-diff", "full"):
            raise ValueError(
                f"Invalid sync_mode '{self.sync_mode}'. "
                "Must be 'auto', 'git-diff', or 'full'."
            )

    def resolve_source(self, repo_root: Path) -> Path:
        """Return the absolute source path and validate it exists."""
        resolved = (repo_root / self.source_folder).resolve()
        if not resolved.is_dir():
            raise FileNotFoundError(
                f"Source folder '{self.source_folder}' does not exist "
                f"at {resolved}"
            )
        self.source_path = resolved
        return resolved


def load_config(config_path: str | Path) -> SyncConfig:
    """Load and validate the sync configuration from a YAML file.

    Args:
        config_path: Path to the .github/sharepoint-sync.yml file.

    Returns:
        A validated SyncConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If required fields are missing or invalid.
    """
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError(
            f"Configuration file must be a YAML mapping, got {type(raw).__name__}"
        )

    required = ("source_folder", "sharepoint_site", "sharepoint_folder")
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(
            f"Missing required configuration keys: {', '.join(missing)}"
        )

    return SyncConfig(
        source_folder=str(raw["source_folder"]),
        sharepoint_site=str(raw["sharepoint_site"]),
        sharepoint_folder=str(raw["sharepoint_folder"]),
        delete_orphaned=bool(raw.get("delete_orphaned", False)),
        file_patterns=list(raw.get("file_patterns", [])),
        sync_mode=str(raw.get("sync_mode", "auto")),
    )


def load_config_from_env() -> SyncConfig:
    """Load config using environment variables set by the composite action."""
    config_path = os.environ.get(
        "SYNC_CONFIG_PATH", ".github/sharepoint-sync.yml"
    )
    return load_config(config_path)
