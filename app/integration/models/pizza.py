"""SQLAlchemy models that describe pizzas and their priced view."""
from __future__ import annotations

from decimal import Decimal

from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class Pizza(db.Model):
    """A pizza definition that can be assembled from ingredients."""

    __tablename__ = "pizzas"

    pizza_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    pizza_name: Mapped[str | None] = mapped_column(db.String(100))

    pizza_ingredients: Mapped[list["PizzaIngredient"]] = relationship(
        "PizzaIngredient",
        back_populates="pizza",
        lazy="selectin",
    )
    menu_price: Mapped[Optional["PizzaMenuPrice"]] = relationship(
        "PizzaMenuPrice",
        back_populates="pizza",
        uselist=False,
        lazy="selectin",
        viewonly=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        """Return pizza name for debugging."""
        return f"Pizza(name={self.pizza_name!r})"


class PizzaIngredient(db.Model):
    """Association record linking pizzas to their ingredients."""

    __tablename__ = "pizza_ingredients"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="ck_pizza_ingredient_quantity_positive"),
    )

    pizza_id: Mapped[int] = mapped_column(
        ForeignKey("pizzas.pizza_id", ondelete="CASCADE"),
        primary_key=True,
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.ingredient_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    quantity_unit: Mapped[str] = mapped_column(db.String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(db.Numeric(8, 2), nullable=False)

    pizza: Mapped[Pizza] = relationship(
        "Pizza",
        back_populates="pizza_ingredients",
        lazy="joined",
    )
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        back_populates="pizza_links",
        lazy="joined",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        """Return identifiers that link pizzas and ingredients."""
        return f"PizzaIngredient(pizza_id={self.pizza_id}, ingredient_id={self.ingredient_id})"


class PizzaMenuPrice(db.Model):
    """Read-only view that contains pre-calculated pizza pricing information."""

    __tablename__ = "pizza_menu_prices"

    pizza_id: Mapped[int] = mapped_column(
        ForeignKey("pizzas.pizza_id"), primary_key=True
    )
    pizza_name: Mapped[str | None] = mapped_column(db.String(100))
    calculated_price: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    pizza_isvegan: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    pizza_isvegetarian: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)

    pizza: Mapped[Pizza] = relationship(
        "Pizza",
        back_populates="menu_price",
        lazy="joined",
        viewonly=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        """Return a summary of the menu price view entry."""
        return f"PizzaMenuPrice(pizza_id={self.pizza_id}, price={self.calculated_price})"


__all__ = ["Pizza", "PizzaIngredient", "PizzaMenuPrice"]
