import hashlib

_USERS = {"ada": hashlib.sha256(b"lovelace").hexdigest()}


def verify(user: str, password: str) -> bool:
    return _USERS.get(user) == hashlib.sha256(password.encode()).hexdigest()


def session_token(user: str) -> str:
    return hashlib.sha256(f"session:{user}".encode()).hexdigest()[:16]
