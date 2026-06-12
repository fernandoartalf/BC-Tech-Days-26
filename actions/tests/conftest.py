"""Test configuration for pytest."""

import sys
from pathlib import Path

# Add the action source to the Python path so tests can import modules
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "actions" / "sharepoint-sync")
)
