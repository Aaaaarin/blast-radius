from shop.auth import verify, session_token


def test_verify():
    assert verify("ada", "lovelace") and not verify("ada", "x")


def test_token_stable():
    assert session_token("ada") == session_token("ada")
