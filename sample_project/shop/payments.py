from decimal import Decimal
from shop.pricing import with_tax
from shop.auth import verify


def charge(user: str, password: str, subtotal) -> dict:
    if not verify(user, password):
        raise PermissionError("bad credentials")
    total = with_tax(subtotal)
    return {"user": user, "charged": total, "status": "ok" if total > Decimal(0) else "void"}
