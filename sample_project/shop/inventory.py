from shop.utils import slug

_STOCK = {"rain-jacket": 12, "trail-shoes": 3, "coffee-beans": 40}


def in_stock(name: str, qty: int = 1) -> bool:
    return _STOCK.get(slug(name), 0) >= qty


def reserve(name: str, qty: int) -> None:
    key = slug(name)
    if not in_stock(key, qty):
        raise ValueError(f"insufficient stock for {key}")
    _STOCK[key] -= qty
