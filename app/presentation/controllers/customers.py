# app/presentation/controllers/customers.py
from flask import Blueprint, jsonify, request
from app.integration.models.customer import Customer

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.get("/")
def list_customers():
    customers = Customer.query.all()
    return jsonify([{"id": c.customer_id, "username": c.username, "name": c.name} for c in customers])


@customers_bp.post("/login")
def customer_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    customer = Customer.query.filter_by(username=username).first()
    if customer and customer.password == password:  # Add proper hashing later
        return jsonify({"success": True, "customer_id": customer.customer_id})
    return jsonify({"success": False}), 401
