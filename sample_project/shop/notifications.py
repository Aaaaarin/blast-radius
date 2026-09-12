SENT: list[tuple[str, dict]] = []


def send_receipt(user: str, receipt: dict) -> None:
    SENT.append((user, receipt))
