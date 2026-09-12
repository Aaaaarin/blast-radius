from shop.utils import slug

CATALOG = ["Rain Jacket", "Trail Shoes", "Coffee Beans"]


def search(q: str) -> list[str]:
    return [c for c in CATALOG if slug(q) in slug(c)]
