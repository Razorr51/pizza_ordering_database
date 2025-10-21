"""Persistence helpers for creating and managing orders."""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional

from app.integration.models import db
from app.integration.models.order import Order, OrderItem
from app.integration.models.pizza import Pizza, PizzaMenuPrice
from app.integration.models.menu_item import MenuItem


class OrderRepository:
    """Repository abstraction for order entities."""

    def create_blank_order(
        self,
        *,
        customer_id: int,
        delivery_postcode_id: Optional[int],
        notes: Optional[str] = None,
    ) -> Order:
        """Instantiate a new order shell and add it to the session."""
        order = Order(
            customer_id=customer_id,
            delivery_postcode_id=delivery_postcode_id,
            notes=notes,
        )
        db.session.add(order)
        return order

    def add_pizza_item(
        self,
        order: Order,
        *,
        pizza: Pizza,
        unit_price: Decimal,
        quantity: int = 1,
    ) -> OrderItem:
        """Append a pizza line item to the order."""
        item = OrderItem(
            order=order,
            item_type="pizza",
            pizza_id=pizza.pizza_id,
            description=pizza.pizza_name,
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=Decimal("0.00"),
        )
        order.items.append(item)
        return item

    def add_menu_item(
        self,
        order: Order,
        *,
        menu_item: MenuItem,
        unit_price: Decimal,
        quantity: int = 1,
    ) -> OrderItem:
        """Append a non-pizza menu item line to the order."""
        item = OrderItem(
            order=order,
            item_type=menu_item.type,
            menu_item_id=menu_item.item_id,
            description=menu_item.name,
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=Decimal("0.00"),
        )
        order.items.append(item)
        return item

    def get_pizza_with_price(self, pizza_id: int) -> Optional[tuple[Pizza, PizzaMenuPrice]]:
        """Fetch a pizza together with its menu price row."""
        pizza = Pizza.query.filter_by(pizza_id=pizza_id).first()
        if not pizza or not pizza.menu_price:
            return None
        return pizza, pizza.menu_price

    def get_menu_items(self, item_ids: Iterable[int]) -> list[MenuItem]:
        """Retrieve menu items matching the supplied identifiers."""
        if not item_ids:
            return []
        return MenuItem.query.filter(MenuItem.item_id.in_(list(item_ids))).all()

    def persist(self) -> None:
        """Flush pending changes so generated identifiers become available."""
        db.session.flush()


__all__ = ["OrderRepository"]
