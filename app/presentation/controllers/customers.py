"""Customer API endpoints."""
from flask import Blueprint, jsonify, request

from app.ownership.services.customer_service import CustomerService

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

_service = CustomerService()

@customers_bp.get("/")
def list_customers():
    """Return a list of registered customers."""
    return jsonify(_service.list_customers())


@customers_bp.post("/login")
def customer_login():
    """Authenticate a customer and return their ID."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    customer = _service.authenticate(username, password)
    if customer:
        return jsonify({"success": True, "customer_id": customer.customer_id})
    return jsonify({"success": False}), 401
