"""Application-data path selection for desktop and test environments."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def application_data_directory() -> Path:
    """Return a writable, stable data directory without requiring Flet."""
    override = os.environ.get("AJCM_DATA_DIR") or os.environ.get("FLET_APP_STORAGE_DATA")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AJCharacterManager" / "data"
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "AJCharacterManager" / "data"
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "aj-character-manager"


def database_path() -> Path:
    return application_data_directory() / "character-manager.sqlite3"
