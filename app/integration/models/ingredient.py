"""SQLAlchemy model for ingredient records."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class Ingredient(db.Model):
    """Represents a single ingredient that can be used on pizzas."""

    __tablename__ = "ingredients"

    ingredient_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    cost: Mapped[Decimal] = mapped_column(db.Numeric(8, 2), nullable=False)
    is_meat: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    is_dairy: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    is_vegan: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)

    pizza_links: Mapped[list["PizzaIngredient"]] = relationship(
        "PizzaIngredient",
        back_populates="ingredient",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Ingredient(name={self.name!r})"


__all__ = ["Ingredient"]
