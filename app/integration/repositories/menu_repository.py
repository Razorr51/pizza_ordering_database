"""Menu queries expressed with the SQLAlchemy ORM."""
from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Mapping

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.integration.models import db
from app.integration.models.menu_item import MenuItem
from app.integration.models.pizza import Pizza, PizzaIngredient, PizzaMenuPrice


class MenuRepository:
    """Provides read-only access to menu data via ORM queries."""

    def fetch_menu_overview(self) -> List[Mapping[str, object]]:
        """Return a compact list of pizzas with their menu pricing."""
        stmt = select(PizzaMenuPrice).order_by(PizzaMenuPrice.pizza_name)
        records = db.session.execute(stmt).scalars().all()
        return [self._serialize_menu_overview(record) for record in records]

    def fetch_pizza_details(self) -> List[Mapping[str, object]]:
        """Return pizzas enriched with ingredient lists and pricing details."""
        stmt = (
            select(Pizza)
            .options(
                joinedload(Pizza.menu_price),
                joinedload(Pizza.pizza_ingredients).joinedload(PizzaIngredient.ingredient),
            )
            .order_by(Pizza.pizza_name)
        )
        pizzas = db.session.execute(stmt).scalars().unique().all()
        return [
            self._serialize_pizza_detail(pizza)
            for pizza in pizzas
            if pizza.menu_price is not None
        ]

    def fetch_active_menu_items(self) -> List[Mapping[str, object]]:
        """Return all active non-pizza menu items."""
        stmt = (
            select(MenuItem)
            .where(MenuItem.active.is_(True))
            .order_by(MenuItem.type, MenuItem.name)
        )
        items = db.session.execute(stmt).scalars().all()
        return [self._serialize_menu_item(item) for item in items]

    @staticmethod
    def _serialize_menu_overview(price: PizzaMenuPrice) -> Dict[str, object]:
        return {
            "pizza_id": price.pizza_id,
            "pizza_name": price.pizza_name,
            "final_price": MenuRepository._decimal_to_float(price.calculated_price),
            "is_vegan": MenuRepository._to_bool(price.pizza_isvegan),
            "is_vegetarian": MenuRepository._to_bool(price.pizza_isvegetarian),
        }

    @staticmethod
    def _serialize_pizza_detail(pizza: Pizza) -> Dict[str, object]:
        price = pizza.menu_price
        ingredient_names = sorted(
            {
                link.ingredient.name
                for link in pizza.pizza_ingredients
                if link.ingredient is not None
            }
        )
        return {
            "pizza_id": pizza.pizza_id,
            "pizza_name": price.pizza_name or pizza.pizza_name,
            "final_price": MenuRepository._decimal_to_float(price.calculated_price),
            "is_vegan": MenuRepository._to_bool(price.pizza_isvegan),
            "is_vegetarian": MenuRepository._to_bool(price.pizza_isvegetarian),
            "ingredients": ", ".join(ingredient_names),
        }

    @staticmethod
    def _serialize_menu_item(item: MenuItem) -> Dict[str, object]:
        return {
            "item_id": item.item_id,
            "name": item.name,
            "type": item.type,
            "final_price": MenuRepository._decimal_to_float(item.base_price),
            "is_vegan": MenuRepository._to_bool(item.is_vegan),
            "is_vegetarian": MenuRepository._to_bool(item.is_vegetarian),
        }

    @staticmethod
    def _decimal_to_float(value: Decimal | None) -> float | None:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def _to_bool(value: object) -> bool:
        return bool(value)


__all__ = ["MenuRepository"]
