"""HTTP endpoints for placing and inspecting orders."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request, session

from app.integration.models.order import Order, OrderItem
from app.ownership.services.order_service import OrderService

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")
_service = OrderService()


@orders_bp.post("/")
def create_order():
    payload = request.get_json(silent=True) or {}
    customer_id = session.get("customer_id") or payload.get("customer_id")
    if not customer_id:
        return (
            jsonify({"errors": {"auth": "Please log in or create an account before checking out."}}),
            401,
        )

    try:
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        return jsonify({"errors": {"customer": "Invalid customer identifier."}}), 400

    pizzas = payload.get("pizzas", [])
    drinks = payload.get("drinks", [])
    desserts = payload.get("desserts", [])
    discount_code = payload.get("discount_code")
    notes = payload.get("notes")

    order, errors = _service.place_order(
        customer_id=customer_id,
        pizzas=pizzas,
        drinks=drinks,
        desserts=desserts,
        discount_code=discount_code,
        notes=notes,
        requested_at=datetime.utcnow(),
    )
    if errors:
        status_code = 400
        if "customer" in errors and "not found" in errors["customer"].lower():
            status_code = 401
        return jsonify({"errors": errors}), status_code

    return jsonify(_serialize_order(order)), 201


def _serialize_order(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "placed_at": order.placed_at.isoformat(),
        "totals": {
            "total_before_discounts": _decimal_to_float(order.total_before_discounts),
            "discount_total": _decimal_to_float(order.discount_total),
            "total_due": _decimal_to_float(order.total_due),
        },
        "discounts": {
            "loyalty": order.loyalty_discount_applied,
            "birthday_pizza": order.birthday_pizza_applied,
            "birthday_drink": order.birthday_drink_applied,
            "discount_code": order.discount_code.code if order.discount_code else None,
        },
        "delivery": {
            "driver_id": order.delivery_person.delivery_driver_id if order.delivery_person else None,
            "driver_name": order.delivery_person.name if order.delivery_person else None,
            "unavailable_until": order.delivery_person.unavailable_until.isoformat() if order.delivery_person and order.delivery_person.unavailable_until else None,
        },
        "items": [
            _serialize_item(item)
            for item in order.items
        ],
    }


def _serialize_item(item: OrderItem) -> dict:
    return {
        "item_type": item.item_type,
        "description": item.description,
        "quantity": item.quantity,
        "unit_price": _decimal_to_float(item.unit_price),
        "discount_amount": _decimal_to_float(item.discount_amount),
        "line_total": _decimal_to_float((item.unit_price * item.quantity) - item.discount_amount),
    }


def _decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


__all__ = ["orders_bp"]
