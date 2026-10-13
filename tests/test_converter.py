from decimal import Decimal
import unittest

from app.engine.converter import convert


class ConverterTests(unittest.TestCase):
    def test_length_conversion(self):
        self.assertEqual(
            convert(Decimal("1000"), "Panjang", "Meter", "Kilometer"),
            Decimal("1"),
        )

    def test_mass_conversion(self):
        self.assertEqual(
            convert(Decimal("1"), "Berat", "Kilogram", "Gram"),
            Decimal("1E+3"),
        )

    def test_temperature_conversion(self):
        self.assertEqual(
            convert(Decimal("0"), "Suhu", "Celsius", "Fahrenheit"),
            Decimal("32"),
        )

    def test_data_conversion(self):
        self.assertEqual(
            convert(Decimal("1"), "Data", "Gibibyte", "Byte"),
            Decimal("1073741824"),
        )

    def test_unknown_units_are_rejected(self):
        with self.assertRaises(ValueError):
            convert(1, "Panjang", "Meter", "Celsius")


if __name__ == "__main__":
    unittest.main()
