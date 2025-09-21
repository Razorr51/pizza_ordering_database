from flask import Blueprint, jsonify
from app.integration.models import db

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

@menu_bp.get("/")
def get_menu():
    rows = db.session.execute(db.text("""
        SELECT 
            pizza_id,
            pizza_name,
            calculated_price AS final_price,
            pizza_isvegan AS is_vegan,
            pizza_isvegetarian AS is_vegetarian
        FROM pizza_menu_prices
        ORDER BY pizza_name
    """)).mappings().all()
    return jsonify([dict(r) for r in rows])
