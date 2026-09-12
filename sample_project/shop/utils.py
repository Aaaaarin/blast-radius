from decimal import Decimal, ROUND_HALF_UP


def money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def slug(s: str) -> str:
    return "-".join(s.lower().split())
