from shop.inventory import in_stock


def test_in_stock():
    assert in_stock("Rain Jacket", 1) and not in_stock("Trail Shoes", 99)
