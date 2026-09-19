import unittest
from fractions import Fraction

from src.expression import parse_expression
from src.fraction_utils import format_fraction, parse_fraction


class FractionUtilTest(unittest.TestCase):
    def test_format_natural_number(self):
        self.assertEqual(format_fraction(Fraction(7)), "7")

    def test_format_proper_fraction(self):
        self.assertEqual(format_fraction(Fraction(3, 5)), "3/5")

    def test_format_mixed_fraction(self):
        self.assertEqual(format_fraction(Fraction(19, 8)), "2'3/8")

    def test_parse_round_trip(self):
        for text in ("0", "9", "3/5", "2'3/8"):
            self.assertEqual(format_fraction(parse_fraction(text)), text)


class ParserTest(unittest.TestCase):
    def test_fraction_addition(self):
        self.assertEqual(parse_expression("1/6 + 1/8 =").evaluate(), Fraction(7, 24))

    def test_precedence(self):
        self.assertEqual(parse_expression("2 + 3 × 4").evaluate(), Fraction(14))

    def test_parentheses(self):
        self.assertEqual(parse_expression("(2 + 3) × 4").evaluate(), Fraction(20))

    def test_mixed_number_expression(self):
        self.assertEqual(parse_expression("2'3/8 + 1/8").evaluate(), Fraction(5, 2))

    def test_ascii_operators(self):
        self.assertEqual(parse_expression("6 / 2 - 1").evaluate(), Fraction(2))


class CanonicalTest(unittest.TestCase):
    def test_commutative_addition_is_duplicate(self):
        self.assertEqual(
            parse_expression("23 + 45").canonical(),
            parse_expression("45 + 23").canonical(),
        )

    def test_commutative_multiplication_is_duplicate(self):
        self.assertEqual(
            parse_expression("6 × 8").canonical(),
            parse_expression("8 × 6").canonical(),
        )

    def test_left_associative_is_duplicate(self):
        self.assertEqual(
            parse_expression("1 + 2 + 3").canonical(),
            parse_expression("3 + (2 + 1)").canonical(),
        )

    def test_different_order_is_not_duplicate(self):
        self.assertNotEqual(
            parse_expression("1 + 2 + 3").canonical(),
            parse_expression("3 + 2 + 1").canonical(),
        )

    def test_subtraction_order_matters(self):
        self.assertNotEqual(
            parse_expression("5 - 3").canonical(),
            parse_expression("3 - 5").canonical(),
        )


if __name__ == "__main__":
    unittest.main()
