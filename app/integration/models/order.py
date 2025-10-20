"""Order-related SQLAlchemy models."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class Order(db.Model):
    """Represents a customer's purchase order."""

    __tablename__ = "orders"
    __table_args__ = (
        db.CheckConstraint(
            "Order_Status IN ('new','preparing','dispatched','delivered','failed')",
            name="ck_order_status_valid",
        ),
    )

    order_id: Mapped[int] = mapped_column(
        "Order_ID", primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        "Customer_ID",
        ForeignKey("customers.Customer_ID", ondelete="CASCADE"),
        nullable=False,
    )
    delivery_postcode_id: Mapped[Optional[int]] = mapped_column(
        "Delivery_Postcode_ID",
        ForeignKey("postcode.postcode_id", ondelete="SET NULL"),
        nullable=True,
    )
    delivery_driver_id: Mapped[Optional[int]] = mapped_column(
        "DeliveryDriver_ID",
        ForeignKey("delivery_person.DeliveryDriver_ID", ondelete="SET NULL"),
        nullable=True,
    )
    discount_code_id: Mapped[Optional[int]] = mapped_column(
        "DiscountCode_ID",
        ForeignKey("discount_code.DiscountCode_ID", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        "Order_Status", db.String(20), nullable=False, default="new"
    )
    placed_at: Mapped[datetime] = mapped_column(
        "Placed_At", db.DateTime, nullable=False, default=datetime.utcnow
    )
    total_before_discounts: Mapped[Decimal] = mapped_column(
        "Total_Before_Discounts",
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    discount_total: Mapped[Decimal] = mapped_column(
        "Discount_Total",
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total_due: Mapped[Decimal] = mapped_column(
        "Total_Due",
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    loyalty_discount_applied: Mapped[bool] = mapped_column(
        "Loyalty_Discount_Applied", db.Boolean, nullable=False, default=False
    )
    birthday_pizza_applied: Mapped[bool] = mapped_column(
        "Birthday_Pizza_Applied", db.Boolean, nullable=False, default=False
    )
    birthday_drink_applied: Mapped[bool] = mapped_column(
        "Birthday_Drink_Applied", db.Boolean, nullable=False, default=False
    )
    notes: Mapped[Optional[str]] = mapped_column("Notes", db.String(255))

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="orders",
        lazy="joined",
    )
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    delivery_person: Mapped[Optional["DeliveryPerson"]] = relationship(
        "DeliveryPerson",
        back_populates="orders",
        lazy="joined",
    )
    discount_code: Mapped[Optional["DiscountCode"]] = relationship(
        "DiscountCode",
        lazy="joined",
    )

    def recalculate_totals(self) -> None:
        """Recompute totals based on associated line items."""
        items = list(dict.fromkeys(self.items))
        gross = sum(
            (item.unit_price * item.quantity for item in items),
            Decimal("0.00"),
        )
        discounts = sum(
            (item.discount_amount for item in items),
            Decimal("0.00"),
        )
        self.total_before_discounts = gross.quantize(Decimal("0.01"))
        self.discount_total = discounts.quantize(Decimal("0.01"))
        self.total_due = (gross - discounts).quantize(Decimal("0.01"))

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Order(id={self.order_id}, customer_id={self.customer_id}, total={self.total_due})"


class OrderItem(db.Model):
    """Line items for orders, covering pizzas and optional extras."""

    __tablename__ = "order_items"
    __table_args__ = (
        db.CheckConstraint("Quantity > 0", name="ck_order_item_quantity_positive"),
        db.CheckConstraint("Unit_Price >= 0", name="ck_order_item_price_non_negative"),
        db.CheckConstraint("Discount_Amount >= 0", name="ck_order_item_discount_non_negative"),
    )

    order_item_id: Mapped[int] = mapped_column(
        "OrderItem_ID", primary_key=True, autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        "Order_ID",
        ForeignKey("orders.Order_ID", ondelete="CASCADE"),
        nullable=False,
    )
    item_type: Mapped[str] = mapped_column("Item_Type", db.String(20), nullable=False)
    pizza_id: Mapped[Optional[int]] = mapped_column(
        "Pizza_ID",
        ForeignKey("pizzas.pizza_id", ondelete="SET NULL"),
        nullable=True,
    )
    menu_item_id: Mapped[Optional[int]] = mapped_column(
        "MenuItem_ID",
        ForeignKey("menu_items.item_id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column("Description", db.String(120))
    quantity: Mapped[int] = mapped_column("Quantity", db.Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(
        "Unit_Price", db.Numeric(10, 2), nullable=False
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        "Discount_Amount",
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    order: Mapped[Order] = relationship("Order", back_populates="items")
    pizza: Mapped[Optional["Pizza"]] = relationship("Pizza", lazy="joined")
    menu_item: Mapped[Optional["MenuItem"]] = relationship("MenuItem", lazy="joined")

    @property
    def extended_price(self) -> Decimal:
        return (self.unit_price * self.quantity) - self.discount_amount

    def apply_discount(self, amount: Decimal) -> None:
        if amount <= 0:
            return
        max_discount = self.unit_price * self.quantity
        self.discount_amount = min(max_discount, self.discount_amount + amount)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"OrderItem(type={self.item_type!r}, qty={self.quantity}, unit={self.unit_price})"


__all__ = ["Order", "OrderItem"]
