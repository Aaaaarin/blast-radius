from shop.notifications import SENT


def revenue() -> float:
    return float(sum(r["charged"] for _, r in SENT))
