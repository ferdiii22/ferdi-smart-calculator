"""Atomic JSON persistence for settings and calculation history."""

import json
import os
import tempfile
from datetime import datetime

from app.config import DATA_DIR, HISTORY_FILE, SETTINGS_FILE


DEFAULT_SETTINGS = {
    "theme": "dark", "mode": "standard", "always_on_top": False,
    "window": {"width": 430, "height": 700},
}


class StoreError(RuntimeError):
    """Raised when application data cannot be read or written."""


class Store:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.settings_file = SETTINGS_FILE
        self.history_file = HISTORY_FILE
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise StoreError("Folder data tidak dapat dibuat: {}".format(error))

    def load_settings(self):
        settings = self._read_json(self.settings_file, dict(DEFAULT_SETTINGS))
        if not isinstance(settings, dict):
            raise StoreError("Format pengaturan tidak valid")
        result = dict(DEFAULT_SETTINGS)
        result.update(settings)
        if result["theme"] not in ("dark", "light"):
            raise StoreError("Tema pada pengaturan tidak dikenal")
        if result["mode"] not in (
                "standard", "scientific", "converter", "date", "programmer"):
            raise StoreError("Mode pada pengaturan tidak dikenal")
        if not isinstance(result["always_on_top"], bool):
            raise StoreError("Preferensi always-on-top tidak valid")
        window = result.get("window")
        if not isinstance(window, dict):
            raise StoreError("Ukuran jendela pada pengaturan tidak valid")
        try:
            width = int(window.get("width", 430))
            height = int(window.get("height", 700))
        except (TypeError, ValueError) as error:
            raise StoreError("Ukuran jendela pada pengaturan tidak valid: {}".format(error))
        result["window"] = {
            "width": min(2000, max(320, width)),
            "height": min(1600, max(480, height)),
        }
        return result

    def save_settings(self, settings):
        self._write_json(self.settings_file, settings)

    def load_history(self):
        history = self._read_json(self.history_file, [])
        if not isinstance(history, list):
            raise StoreError("Format riwayat tidak valid")
        return [item for item in history if isinstance(item, dict)][-500:]

    def add_history(self, expression, result):
        history = self.load_history()
        history.append({
            "expr": expression, "result": result,
            "time": datetime.now().isoformat(timespec="seconds"),
        })
        self._write_json(self.history_file, history[-500:])

    def clear_history(self):
        self._write_json(self.history_file, [])

    @staticmethod
    def _read_json(path, default):
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8") as data_file:
                return json.load(data_file)
        except (OSError, ValueError) as error:
            raise StoreError("Data {} tidak dapat dibaca: {}".format(path.name, error))

    @staticmethod
    def _write_json(path, value):
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=str(path.parent),
                    prefix=path.name, suffix=".tmp", delete=False) as data_file:
                temporary_path = data_file.name
                json.dump(value, data_file, ensure_ascii=False, indent=2)
                data_file.flush()
                os.fsync(data_file.fileno())
            os.replace(temporary_path, str(path))
        except (OSError, TypeError, ValueError) as error:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)
            raise StoreError("Data {} tidak dapat disimpan: {}".format(path.name, error))
