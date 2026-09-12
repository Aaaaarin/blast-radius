from decimal import Decimal
from shop.pricing import apply_discount, with_tax


def test_discount_ten_percent():
    assert apply_discount(100, 10) == Decimal("90.00")


def test_tax_seattle():
    assert with_tax(100) == Decimal("110.25")
