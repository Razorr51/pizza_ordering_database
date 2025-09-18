# controllers/menu.py
from flask import Blueprint, jsonify
from models import db

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

@menu_bp.get("/")
def get_menu():
    rows = db.session.execute(db.text("""
        SELECT pizza_id, pizza_name, base_cost, final_price, veg_label
        FROM pizza_menu_view
        ORDER BY pizza_name
    """)).mappings().all()
    return jsonify([dict(r) for r in rows])
