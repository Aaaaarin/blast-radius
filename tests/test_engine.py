import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from blastradius.graph import build_graph, reverse_graph  # noqa: E402
from blastradius.engine import analyze  # noqa: E402
from blastradius.diff import functions_hit, rel_to_module  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_project")


def test_graph_finds_modules_and_imports():
    g = build_graph(SAMPLE)
    assert "shop.checkout" in g and "shop.pricing" in g
    assert "shop.cart" in g["shop.checkout"].imports
    assert "shop.utils" in g["shop.pricing"].imports
    assert g["tests.test_cart"].is_test


def test_reverse_graph_dependents():
    g = build_graph(SAMPLE)
    r = reverse_graph(g)
    assert {"shop.cart", "shop.payments", "tests.test_pricing"} <= r["shop.pricing"]


def test_pricing_change_reaches_checkout_not_search():
    rep = analyze(SAMPLE, changed_override=["shop.pricing"])
    impacted = {i.module for i in rep.impacted}
    assert {"shop.cart", "shop.payments", "shop.checkout"} <= impacted
    assert "shop.search" not in impacted
    assert "tests.test_checkout" in rep.tests_selected
    assert "tests.test_search" not in rep.tests_selected
    assert rep.risk_level == "HIGH"


def test_leaf_change_is_low_risk():
    rep = analyze(SAMPLE, changed_override=["shop.search"])
    assert rep.tests_selected == ["tests.test_search"]
    assert rep.risk_level == "LOW"


def test_functions_hit_maps_lines():
    assert functions_hit({"a": (1, 5), "b": (10, 20)}, {12}) == ["b"]


def test_rel_to_module():
    assert rel_to_module("shop/pricing.py") == "shop.pricing"
    assert rel_to_module("shop/__init__.py") == "shop"
