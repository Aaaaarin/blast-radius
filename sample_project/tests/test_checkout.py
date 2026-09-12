from decimal import Decimal
from shop.cart import Cart
from shop.checkout import checkout


def test_checkout_end_to_end():
    c = Cart()
    c.add("Coffee Beans", 20, qty=1, discount_pct=50)
    r = checkout(c, "ada", "lovelace")
    assert r["charged"] == Decimal("11.03")
