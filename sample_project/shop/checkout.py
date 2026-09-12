from shop.cart import Cart
from shop.payments import charge
from shop.inventory import reserve
from shop.notifications import send_receipt


def checkout(cart: Cart, user: str, password: str) -> dict:
    receipt = charge(user, password, cart.subtotal())
    for name, _, qty, _ in cart.items:
        reserve(name, qty)
    send_receipt(user, receipt)
    return receipt
