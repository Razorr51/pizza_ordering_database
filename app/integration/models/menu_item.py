"""SQLAlchemy model for generic menu items."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from . import db


class MenuItem(db.Model):
    """Represents drinks, desserts, and other non-pizza menu entries."""

    __tablename__ = "menu_items"
    __table_args__ = (
        db.CheckConstraint(
            "(base_price IS NULL) OR (base_price > 0)",
            name="ck_menu_item_price_positive",
        ),
    )

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    type: Mapped[str] = mapped_column(db.Enum("pizza", "drink", "dessert"), nullable=False)
    base_price: Mapped[Decimal | None] = mapped_column(db.Numeric(8, 2))
    is_vegan: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    is_vegetarian: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"MenuItem(name={self.name!r}, type={self.type!r})"


__all__ = ["MenuItem"]
