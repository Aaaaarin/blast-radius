from decimal import Decimal
from shop.utils import money

TAX_RATE = Decimal("0.1025")  # Seattle combined sales tax


def apply_discount(price, pct) -> Decimal:
    """Return price reduced by pct percent."""
    return money(Decimal(str(price)) * (Decimal(1) - Decimal(str(pct)) / Decimal(100)))


def with_tax(subtotal) -> Decimal:
    return money(Decimal(str(subtotal)) * (Decimal(1) + TAX_RATE))
