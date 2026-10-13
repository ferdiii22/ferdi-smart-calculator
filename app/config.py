"""Application paths shared by the UI, storage layer, and PyInstaller build."""

import sys
from pathlib import Path


def base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_path(relative_path):
    root = Path(getattr(sys, "_MEIPASS", base_dir()))
    return root / relative_path


DATA_DIR = base_dir() / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE = DATA_DIR / "history.json"
