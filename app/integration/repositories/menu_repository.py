"""Menu queries.

Encapsulates SQL needed to build the pizza menu views so controllers
only see Python data structures.
"""
from __future__ import annotations

from typing import List, Mapping

from sqlalchemy import text

from app.integration.models import db


class MenuRepository:
    """Provides read-only access to menu-related database queries."""

    _MENU_OVERVIEW_SQL = text(
        """
        SELECT pizza_id, pizza_name, calculated_price AS final_price,
               pizza_isvegan AS is_vegan, pizza_isvegetarian AS is_vegetarian
        FROM pizza_menu_prices
        ORDER BY pizza_name
        """
    )

    _PIZZA_DETAILS_SQL = text(
        """
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
        """
    )

    _ACTIVE_MENU_ITEMS_SQL = text(
        """
        SELECT item_id, name, type, base_price AS final_price, is_vegan, is_vegetarian
        FROM menu_items
        WHERE active = 1
        ORDER BY type, name
        """
    )

    def fetch_menu_overview(self) -> List[Mapping[str, object]]:
        result = db.session.execute(self._MENU_OVERVIEW_SQL).mappings().all()
        return [dict(row) for row in result]

    def fetch_pizza_details(self) -> List[Mapping[str, object]]:
        result = db.session.execute(self._PIZZA_DETAILS_SQL).mappings().all()
        return [dict(row) for row in result]

    def fetch_active_menu_items(self) -> List[Mapping[str, object]]:
        result = db.session.execute(self._ACTIVE_MENU_ITEMS_SQL).mappings().all()
        return [dict(row) for row in result]


__all__ = ["MenuRepository"]
