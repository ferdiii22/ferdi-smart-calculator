from decimal import Decimal
import unittest

from app.engine.formatter import format_editable, format_result


class FormatterTests(unittest.TestCase):
    def test_indonesian_grouping_and_decimal_separator(self):
        self.assertEqual(format_result(Decimal("1250000.25")), "1.250.000,25")

    def test_trailing_zeroes_are_removed(self):
        self.assertEqual(format_result(Decimal("15.000")), "15")

    def test_large_values_use_scientific_notation(self):
        self.assertIn("e+", format_result(Decimal("99999999999999999")))

    def test_editable_output_has_no_grouping(self):
        self.assertEqual(format_editable(Decimal("1250000.25")), "1250000.25")


if __name__ == "__main__":
    unittest.main()
