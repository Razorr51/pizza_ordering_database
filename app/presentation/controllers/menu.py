"""Menu presentation endpoints."""
from pathlib import Path

from flask import Blueprint, jsonify, render_template, current_app, render_template_string

from app.ownership.services.menu_service import MenuService

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

menu_bp = Blueprint(
    "menu",
    __name__,
    url_prefix="/menu",
    template_folder=str(TEMPLATES_DIR)
)

_service = MenuService()

@menu_bp.get("/")
def get_menu_json():
    """Return the menu as JSON for API consumers."""
    return jsonify(_service.menu_overview())

@menu_bp.get("/html")
def get_menu_html():
    """Render the menu page with pizzas and categorized extras."""
    # for debugging
    current_app.logger.info(f"Jinja search paths: {current_app.jinja_loader.searchpath}")
    current_app.logger.info(f"Menu blueprint template_folder: {TEMPLATES_DIR}")

    sections = _service.build_sections()
    drinks = sections.category("drink")
    desserts = sections.category("dessert")

    return render_template(
        "menu.html",
        pizzas=sections.pizzas,
        drinks=drinks,
        desserts=desserts,
        other_extras={k: v for k, v in sections.extras_by_type.items() if k not in {"drink", "dessert"}},
    )

@menu_bp.get("/test")
def menu_test():
    return render_template_string("<h1>Menu test works</h1>")
