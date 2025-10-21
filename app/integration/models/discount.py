"""SQLAlchemy model describing redeemable discount codes."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from . import db


class DiscountCode(db.Model):
    """Represents a single-use discount code."""

    __tablename__ = "discount_code"

    discount_code_id: Mapped[int] = mapped_column(
        "DiscountCode_ID",
        primary_key=True,
        autoincrement=True,
    )
    code: Mapped[str] = mapped_column(db.String(32), unique=True, nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(
        "Discount_Value",
        db.Numeric(5, 2),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    valid_from: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    redeemed_at: Mapped[datetime | None] = mapped_column(db.DateTime, nullable=True)

    def mark_redeemed(self) -> None:
        """Flag discount code as used and store the redemption timestamp."""
        self.redeemed_at = datetime.utcnow()
        self.is_active = False

    def is_valid_today(self, today: date | None = None) -> bool:
        """Return True if the code can be redeemed given the date."""
        today = today or date.today()
        if not self.is_active:
            return False
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_to and today > self.valid_to:
            return False
        return True

    def discount_multiplier(self) -> Decimal:
        """Return the fraction (e.g. 0.10) represented by this code."""
        return Decimal(self.discount_value) / Decimal(100)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"DiscountCode(code={self.code!r}, value={self.discount_value})"


__all__ = ["DiscountCode"]
