from decimal import Decimal
import pytest
from shop.payments import charge


def test_charge_ok():
    r = charge("ada", "lovelace", 100)
    assert r["charged"] == Decimal("110.25") and r["status"] == "ok"


def test_charge_bad_password():
    with pytest.raises(PermissionError):
        charge("ada", "wrong", 100)
