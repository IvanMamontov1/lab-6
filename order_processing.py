from __future__ import annotations

from typing import Any


DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

COUPON_SAVE10 = "SAVE10"
COUPON_SAVE20 = "SAVE20"
COUPON_VIP = "VIP"

SAVE10_RATE = 0.10
SAVE20_RATE_BIG = 0.20
SAVE20_RATE_SMALL = 0.05
SAVE20_THRESHOLD = 200

VIP_DISCOUNT_DEFAULT = 50
VIP_DISCOUNT_SMALL_SUBTOTAL = 10


def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    _validate_user_id(user_id)
    items = _validate_items(items)
    currency = _normalize_currency(currency)

    subtotal = _calculate_subtotal(items)
    discount = _calculate_discount(subtotal, coupon)

    total_after_discount = _apply_discount(subtotal, discount)
    tax = _calculate_tax(total_after_discount)
    total = total_after_discount + tax

    order_id = _make_order_id(user_id, len(items))

    return _build_response(
        order_id=order_id,
        user_id=user_id,
        currency=currency,
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        items_count=len(items),
    )


def _validate_user_id(user_id: Any) -> None:
    if user_id is None:
        raise ValueError("user_id is required")


def _normalize_currency(currency: Any) -> str:
    if currency is None:
        return DEFAULT_CURRENCY
    return currency


def _validate_items(items: Any) -> list[dict]:
    if items is None:
        raise ValueError("items is required")
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for it in items:
        _validate_item(it)

    return items


def _validate_item(item: dict) -> None:
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    if item["price"] <= 0:
        raise ValueError("price must be positive")
    if item["qty"] <= 0:
        raise ValueError("qty must be positive")


def _calculate_subtotal(items: list[dict]) -> int:
    subtotal = 0
    for it in items:
        subtotal = subtotal + it["price"] * it["qty"]
    return subtotal


def _calculate_discount(subtotal: int, coupon: Any) -> int:
    if coupon is None or coupon == "":
        return 0

    if coupon == COUPON_SAVE10:
        return int(subtotal * SAVE10_RATE)

    if coupon == COUPON_SAVE20:
        if subtotal >= SAVE20_THRESHOLD:
            return int(subtotal * SAVE20_RATE_BIG)
        return int(subtotal * SAVE20_RATE_SMALL)

    if coupon == COUPON_VIP:
        if subtotal < 100:
            return VIP_DISCOUNT_SMALL_SUBTOTAL
        return VIP_DISCOUNT_DEFAULT

    raise ValueError("unknown coupon")


def _apply_discount(subtotal: int, discount: int) -> int:
    total_after_discount = subtotal - discount
    if total_after_discount < 0:
        return 0
    return total_after_discount


def _calculate_tax(amount: int) -> int:
    return int(amount * TAX_RATE)


def _make_order_id(user_id: Any, items_count: int) -> str:
    return str(user_id) + "-" + str(items_count) + "-" + "X"


def _build_response(
    *,
    order_id: str,
    user_id: Any,
    currency: str,
    subtotal: int,
    discount: int,
    tax: int,
    total: int,
    items_count: int,
) -> dict:
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": items_count,
    }
