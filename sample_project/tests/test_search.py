from shop.search import search


def test_search():
    assert search("coffee") == ["Coffee Beans"]
