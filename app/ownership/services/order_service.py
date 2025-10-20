"""Order orchestration service covering Week 4 requirements."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError

from app.integration.models import db
from app.integration.models.customer import Customer
from app.integration.models.order import Order, OrderItem
from app.integration.repositories.customer_repository import CustomerRepository
from app.integration.repositories.delivery_repository import DeliveryRepository
from app.integration.repositories.discount_repository import DiscountRepository
from app.integration.repositories.order_repository import OrderRepository


@dataclass
class OrderRequestItem:
    item_id: int
    quantity: int


class OrderService:
    """Handles placing orders, applying discounts, and assigning drivers."""

    LOYALTY_THRESHOLD = 10
    LOYALTY_DISCOUNT = Decimal("0.10")
    DRIVER_COOLDOWN_MINUTES = 30

    def __init__(
        self,
        *,
        order_repository: Optional[OrderRepository] = None,
        customer_repository: Optional[CustomerRepository] = None,
        discount_repository: Optional[DiscountRepository] = None,
        delivery_repository: Optional[DeliveryRepository] = None,
    ) -> None:
        self._orders = order_repository or OrderRepository()
        self._customers = customer_repository or CustomerRepository()
        self._discounts = discount_repository or DiscountRepository()
        self._delivery = delivery_repository or DeliveryRepository()

    def place_order(
        self,
        *,
        customer_id: int,
        pizzas: Iterable[Dict[str, object]],
        drinks: Iterable[Dict[str, object]] | None = None,
        desserts: Iterable[Dict[str, object]] | None = None,
        discount_code: Optional[str] = None,
        notes: Optional[str] = None,
        requested_at: Optional[datetime] = None,
    ) -> Tuple[Optional[Order], Dict[str, str]]:
        errors: Dict[str, str] = {}

        customer = self._customers.get_by_id(customer_id)
        if not customer:
            errors["customer"] = "Customer not found."

        pizza_requests = self._normalize_request_items(pizzas)
        if not pizza_requests:
            errors["pizzas"] = "At least one pizza must be included in an order."

        drink_requests = self._normalize_request_items(drinks or [])
        dessert_requests = self._normalize_request_items(desserts or [])

        if errors:
            return None, errors

        requested_at = requested_at or datetime.utcnow()

        pizza_lines, pizza_errors = self._load_pizza_lines(pizza_requests)
        if pizza_errors:
            errors.update(pizza_errors)

        drink_lines, drink_errors = self._load_menu_lines(drink_requests, expected_type="drink")
        dessert_lines, dessert_errors = self._load_menu_lines(dessert_requests, expected_type="dessert")
        errors.update(drink_errors)
        errors.update(dessert_errors)

        discount = self._discounts.find_active_by_code(discount_code) if discount_code else None
        if discount_code and not discount:
            errors["discount_code"] = "Discount code is not valid or has already been used."

        if errors:
            return None, errors

        total_pizza_count = sum(qty for _, qty in pizza_lines)

        order = self._orders.create_blank_order(
            customer_id=customer.customer_id,
            delivery_postcode_id=customer.postcode_id,
            notes=notes,
        )

        for pizza, quantity in pizza_lines:
            menu_price = pizza.menu_price
            assert menu_price is not None  # ensured in _load_pizza_lines
            self._orders.add_pizza_item(
                order,
                pizza=pizza,
                quantity=quantity,
                unit_price=menu_price.calculated_price,
            )

        for menu_item, quantity in drink_lines + dessert_lines:
            self._orders.add_menu_item(
                order,
                menu_item=menu_item,
                quantity=quantity,
                unit_price=menu_item.base_price or Decimal("0"),
            )

        # Birthday freebies (cheapest pizza + drink)
        self._apply_birthday_rewards(order, customer, requested_at.date())

        # Loyalty discount (10% off once customer hit threshold)
        if customer.pizzas_ordered >= self.LOYALTY_THRESHOLD:
            self._apply_order_level_discount(order, self.LOYALTY_DISCOUNT)
            order.loyalty_discount_applied = True

        # Additional discount code
        if discount:
            order.discount_code = discount
            discount_amount = self._calculate_percentage_discount(order, discount.discount_multiplier())
            if discount_amount > Decimal("0"):
                self._apply_explicit_discount_amount(order, discount_amount)

        order.recalculate_totals()

        # Assign delivery driver
        assigned_driver = self._delivery.find_available_driver(
            customer.postcode_id,
            reference_time=requested_at,
        )
        if not assigned_driver:
            errors["delivery"] = "No delivery driver is available for the requested postcode at this time."
            db.session.rollback()
            return None, errors

        cooldown_until = requested_at + timedelta(minutes=self.DRIVER_COOLDOWN_MINUTES)
        assigned_driver.unavailable_until = cooldown_until
        assigned_driver.is_available = False
        order.delivery_person = assigned_driver

        # Loyalty tracking: add purchased pizza count
        customer.pizzas_ordered = (customer.pizzas_ordered or 0) + total_pizza_count

        try:
            if discount:
                self._discounts.mark_redeemed(discount)
            order.recalculate_totals()
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            errors["database"] = "Could not persist the order due to a database constraint."
            return None, errors
        except Exception:
            db.session.rollback()
            raise

        return order, {}

    # ------------------------------------------------------------------
    # Internal helpers

    def _normalize_request_items(
        self,
        raw_items: Iterable[Dict[str, object]],
    ) -> List[OrderRequestItem]:
        normalized: List[OrderRequestItem] = []
        for entry in raw_items:
            if not isinstance(entry, dict):
                continue
            item_id = entry.get("item_id") or entry.get("pizza_id")
            quantity = entry.get("quantity", 1)
            try:
                item_id = int(item_id)
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue
            if item_id <= 0 or quantity <= 0:
                continue
            normalized.append(OrderRequestItem(item_id=item_id, quantity=quantity))
        return normalized

    def _load_pizza_lines(
        self,
        requests: Iterable[OrderRequestItem],
    ) -> Tuple[List[Tuple["Pizza", int]], Dict[str, str]]:
        from app.integration.models.pizza import Pizza

        lines: List[Tuple[Pizza, int]] = []
        errors: Dict[str, str] = {}
        for req in requests:
            found = self._orders.get_pizza_with_price(req.item_id)
            if not found:
                errors.setdefault("pizzas", "One or more pizzas are unavailable.")
                continue
            pizza, _ = found
            lines.append((pizza, req.quantity))
        return lines, errors

    def _load_menu_lines(
        self,
        requests: Iterable[OrderRequestItem],
        *,
        expected_type: str,
    ) -> Tuple[List[Tuple["MenuItem", int]], Dict[str, str]]:
        from app.integration.models.menu_item import MenuItem

        errors: Dict[str, str] = {}
        if not requests:
            return [], errors

        id_map = defaultdict(int)
        for req in requests:
            id_map[req.item_id] += req.quantity

        menu_items = self._orders.get_menu_items(id_map.keys())
        items_by_id = {item.item_id: item for item in menu_items}

        lines: List[Tuple[MenuItem, int]] = []
        for item_id, quantity in id_map.items():
            item = items_by_id.get(item_id)
            if not item or (item.type or "").lower() != expected_type:
                key = "drinks" if expected_type == "drink" else "desserts"
                errors[key] = f"Item {item_id} is not an available {expected_type}."
                continue
            lines.append((item, quantity))
        return lines, errors

    def _apply_birthday_rewards(self, order: Order, customer: Customer, today: date) -> None:
        birthdate = customer.birthdate
        if not birthdate or (birthdate.month, birthdate.day) != (today.month, today.day):
            return

        pizza_items = [item for item in order.items if item.item_type == "pizza"]
        drink_items = [item for item in order.items if item.item_type == "drink"]

        if pizza_items:
            target = min(pizza_items, key=lambda item: item.unit_price)
            target.apply_discount(target.unit_price)
            order.birthday_pizza_applied = True

        if drink_items:
            target = min(drink_items, key=lambda item: item.unit_price)
            target.apply_discount(target.unit_price)
            order.birthday_drink_applied = True

    def _apply_order_level_discount(self, order: Order, percentage: Decimal) -> None:
        gross = sum((item.unit_price * item.quantity for item in order.items), Decimal("0"))
        existing_discounts = sum((item.discount_amount for item in order.items), Decimal("0"))
        base = gross - existing_discounts
        if base <= Decimal("0"):
            return
        amount = (base * percentage).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if amount <= Decimal("0"):
            return
        self._apply_explicit_discount_amount(order, amount)

    def _calculate_percentage_discount(self, order: Order, percentage: Decimal) -> Decimal:
        gross = sum((item.unit_price * item.quantity for item in order.items), Decimal("0"))
        existing_discounts = sum((item.discount_amount for item in order.items), Decimal("0"))
        base = gross - existing_discounts
        if base <= Decimal("0"):
            return Decimal("0")
        return (base * percentage).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _apply_explicit_discount_amount(self, order: Order, amount: Decimal) -> None:
        remaining = amount
        for item in sorted(
            order.items,
            key=lambda itm: itm.unit_price * itm.quantity - itm.discount_amount,
            reverse=True,
        ):
            available = (item.unit_price * item.quantity) - item.discount_amount
            if available <= Decimal("0"):
                continue
            apply = min(available, remaining)
            item.apply_discount(apply)
            remaining -= apply
            if remaining <= Decimal("0"):
                break


__all__ = ["OrderService"]
