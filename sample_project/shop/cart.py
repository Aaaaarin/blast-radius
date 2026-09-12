from decimal import Decimal
from shop.pricing import apply_discount
from shop.inventory import in_stock


class Cart:
    def __init__(self):
        self.items: list[tuple[str, Decimal, int, int]] = []

    def add(self, name: str, price, qty: int = 1, discount_pct: int = 0):
        if not in_stock(name, qty):
            raise ValueError("out of stock")
        self.items.append((name, Decimal(str(price)), qty, discount_pct))

    def subtotal(self) -> Decimal:
        return sum((apply_discount(p, d) * q for _, p, q, d in self.items), Decimal("0.00"))
