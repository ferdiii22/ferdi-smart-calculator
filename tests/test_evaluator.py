from decimal import Decimal
import unittest

from app.engine.evaluator import CalculationError, evaluate


class EvaluatorTests(unittest.TestCase):
    def test_decimal_precision(self):
        self.assertEqual(evaluate("0,1 + 0,2"), Decimal("0.3"))

    def test_operator_precedence_and_parentheses(self):
        self.assertEqual(evaluate("2 + 3 × 4"), Decimal("14"))
        self.assertEqual(evaluate("(2 + 3) × 4"), Decimal("20"))

    def test_contextual_percentage(self):
        self.assertEqual(evaluate("200 + 10%"), Decimal("220"))
        self.assertEqual(evaluate("200 - 10%"), Decimal("180"))

    def test_unclosed_parenthesis_is_closed_for_preview(self):
        self.assertEqual(evaluate("(12 + 8) × 3 ÷ 4"), Decimal("15"))
        self.assertEqual(evaluate("(2 + 3"), Decimal("5"))

    def test_grouped_integer(self):
        self.assertEqual(evaluate("1.250.000 + 2"), Decimal("1250002"))
        self.assertEqual(evaluate("1234.567"), Decimal("1234.567"))

    def test_scientific_functions(self):
        self.assertEqual(evaluate("sin(30)"), Decimal("0.5"))
        self.assertEqual(evaluate("sqrt(16) + log(100)"), Decimal("6"))
        self.assertEqual(evaluate("5!"), Decimal("120"))

    def test_division_by_zero_is_friendly(self):
        with self.assertRaisesRegex(CalculationError, "dibagi nol"):
            evaluate("5 ÷ 0")

    def test_unsafe_syntax_is_rejected(self):
        for expression in ("__import__('os')", "open('file')", "2 // 2"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    evaluate(expression)

    def test_bad_expression_is_rejected(self):
        with self.assertRaises(CalculationError):
            evaluate("5 ++ × 2")


if __name__ == "__main__":
    unittest.main()
