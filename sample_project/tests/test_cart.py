from decimal import Decimal
from shop.cart import Cart


def test_cart_subtotal_with_discount():
    c = Cart()
    c.add("Rain Jacket", 80, qty=2, discount_pct=25)
    assert c.subtotal() == Decimal("120.00")
