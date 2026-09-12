from shop.utils import slug


def test_slug():
    assert slug("Rain  Jacket") == "rain-jacket"
