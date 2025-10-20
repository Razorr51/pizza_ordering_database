"""Discount-code data access helpers."""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func

from app.integration.models import db
from app.integration.models.discount import DiscountCode


class DiscountRepository:
    """Contains common lookup operations for discount codes."""

    def find_active_by_code(self, code: str, *, on_date: date | None = None) -> Optional[DiscountCode]:
        if not code:
            return None
        on_date = on_date or date.today()
        normalized = code.strip().lower()
        record = (
            DiscountCode.query
            .filter(func.lower(DiscountCode.code) == normalized)
            .first()
        )
        if record and record.is_valid_today(on_date):
            return record
        return None

    def mark_redeemed(self, discount: DiscountCode) -> None:
        discount.mark_redeemed()
        db.session.add(discount)

    def ensure_code(self, *, code: str, value: float, active: bool = True) -> DiscountCode:
        normalized = code.strip().lower()
        record = (
            DiscountCode.query
            .filter(func.lower(DiscountCode.code) == normalized)
            .first()
        )
        if record:
            return record
        discount = DiscountCode(
            code=code,
            discount_value=value,
            is_active=active,
        )
        db.session.add(discount)
        return discount


__all__ = ["DiscountRepository"]
