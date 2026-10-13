import json
from pathlib import Path
import tempfile
import unittest

from app.storage.store import Store, StoreError


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = Store.__new__(Store)
        self.store.data_dir = Path(self.temp_dir.name)
        self.store.settings_file = self.store.data_dir / "settings.json"
        self.store.history_file = self.store.data_dir / "history.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_settings_round_trip_and_window_clamp(self):
        self.store.save_settings({
            "theme": "light", "mode": "scientific", "always_on_top": True,
            "window": {"width": 100, "height": 9000},
        })
        settings = self.store.load_settings()
        self.assertEqual(settings["theme"], "light")
        self.assertEqual(settings["mode"], "scientific")
        self.assertEqual(settings["window"], {"width": 320, "height": 1600})

    def test_history_round_trip_and_limit(self):
        for number in range(505):
            self.store.add_history(str(number), str(number))
        history = self.store.load_history()
        self.assertEqual(len(history), 500)
        self.assertEqual(history[0]["expr"], "5")
        self.assertEqual(history[-1]["expr"], "504")

    def test_malformed_settings_are_reported(self):
        self.store.settings_file.write_text('{"theme":"ultraviolet"}', encoding="utf-8")
        with self.assertRaises(StoreError):
            self.store.load_settings()


if __name__ == "__main__":
    unittest.main()
