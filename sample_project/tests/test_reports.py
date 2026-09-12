from shop.reports import revenue


def test_revenue_is_number():
    assert isinstance(revenue(), float)
