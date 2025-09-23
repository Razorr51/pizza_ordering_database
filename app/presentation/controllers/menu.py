# app/presentation/controllers/menu.py
from flask import Blueprint, jsonify, render_template, current_app, render_template_string
from app.integration.models import db
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

menu_bp = Blueprint(
    "menu",
    __name__,
    url_prefix="/menu",
    template_folder=str(TEMPLATES_DIR)
)

@menu_bp.get("/")
def get_menu_json():
    rows = db.session.execute(db.text("""
        SELECT pizza_id, pizza_name, calculated_price AS final_price,
               pizza_isvegan AS is_vegan, pizza_isvegetarian AS is_vegetarian
        FROM pizza_menu_prices
        ORDER BY pizza_name
    """)).mappings().all()
    return jsonify([dict(r) for r in rows])

@menu_bp.get("/html")
def get_menu_html():
    # debug show where Flask is looking
    current_app.logger.info(f"Jinja search paths: {current_app.jinja_loader.searchpath}")
    current_app.logger.info(f"Menu blueprint template_folder: {TEMPLATES_DIR}")

    pizzas = db.session.execute(db.text("""
        SELECT 
            p.pizza_id,
            p.pizza_name,
            v.calculated_price AS final_price,
            v.pizza_isvegan    AS is_vegan,
            v.pizza_isvegetarian AS is_vegetarian,
            GROUP_CONCAT(DISTINCT i.name ORDER BY i.name SEPARATOR ', ') AS ingredients
        FROM pizzas p
        JOIN pizza_menu_prices v ON v.pizza_id = p.pizza_id
        JOIN pizza_ingredients  pi ON pi.pizza_id = p.pizza_id
        JOIN ingredients        i  ON i.ingredient_id = pi.ingredient_id
        GROUP BY p.pizza_id, p.pizza_name, v.calculated_price, v.pizza_isvegan, v.pizza_isvegetarian
        ORDER BY p.pizza_name
    """)).mappings().all()

    extras = db.session.execute(db.text("""
        SELECT item_id, name, type, base_price AS final_price, is_vegan, is_vegetarian
        FROM menu_items
        WHERE active = 1
        ORDER BY type, name
    """)).mappings().all()

    drinks   = [e for e in extras if e["type"] == "drink"]
    desserts = [e for e in extras if e["type"] == "dessert"]

    return render_template("menu.html", pizzas=pizzas, drinks=drinks, desserts=desserts)

@menu_bp.get("/test")
def menu_test():
    return render_template_string("<h1>Menu test works</h1>")
