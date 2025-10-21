"""Read-only reporting queries backed by database views."""
from __future__ import annotations

from datetime import date
from typing import List, Mapping

from sqlalchemy import text

from app.integration.models import db


class ReportingRepository:
    """Executes reporting queries against pre-built SQL views."""

    def fetch_undelivered_orders(self) -> List[Mapping[str, object]]:
        """Return outstanding orders."""
        stmt = text(
            """
            SELECT *
            FROM staff_undelivered_orders
            ORDER BY placed_at ASC
            """
        )
        rows = db.session.execute(stmt).mappings().all()
        return [dict(row) for row in rows]

    def fetch_top_pizzas_last_month(self, limit: int = 3) -> List[Mapping[str, object]]:
        """Return a list of top-selling pizzas for the previous month."""
        stmt = text(
            """
            SELECT pizza_id,
                   pizza_name,
                   total_quantity,
                   ROUND(pizza_revenue, 2) AS pizza_revenue
            FROM staff_top_pizzas_last_month
            ORDER BY total_quantity DESC, pizza_id
            LIMIT :limit
            """
        )
        rows = db.session.execute(stmt, {"limit": limit}).mappings().all()
        results = []
        for idx, row in enumerate(rows, start=1):
            data = dict(row)
            data["popularity_rank"] = idx
            results.append(data)
        return results

    def earnings_by_gender(self, year: int | None, month: int | None) -> List[Mapping[str, object]]:
        """Summarize revenue grouped by customer gender."""
        year, month = self._resolve_period(year, month)
        stmt = text(
            """
            SELECT report_year,
                   report_month,
                   gender,
                   order_count,
                   revenue
            FROM staff_monthly_earnings_by_gender
            WHERE report_year = :year AND report_month = :month
            ORDER BY gender
            """
        )
        rows = db.session.execute(stmt, {"year": year, "month": month}).mappings().all()
        return [dict(row) for row in rows]

    def earnings_by_age_group(self, year: int | None, month: int | None) -> List[Mapping[str, object]]:
        """Summarize monthly revenue by age bracket."""
        year, month = self._resolve_period(year, month)
        stmt = text(
            """
            SELECT report_year,
                   report_month,
                   age_group,
                   order_count,
                   revenue
            FROM staff_monthly_earnings_by_age_group
            WHERE report_year = :year AND report_month = :month
            ORDER BY FIELD(age_group, '18-24', '25-34', '35-44', '45-54', '55+', 'Unknown')
            """
        )
        rows = db.session.execute(stmt, {"year": year, "month": month}).mappings().all()
        return [dict(row) for row in rows]

    def earnings_by_postcode(self, year: int | None, month: int | None) -> List[Mapping[str, object]]:
        """Summarize monthly revenue by postcode."""
        year, month = self._resolve_period(year, month)
        stmt = text(
            """
            SELECT report_year,
                   report_month,
                   postcode,
                   order_count,
                   revenue
            FROM staff_monthly_earnings_by_postcode
            WHERE report_year = :year AND report_month = :month
            ORDER BY postcode
            """
        )
        rows = db.session.execute(stmt, {"year": year, "month": month}).mappings().all()
        return [dict(row) for row in rows]

    @staticmethod
    def _resolve_period(year: int | None, month: int | None) -> tuple[int, int]:
        """Fallback to the current month when no explicit period is supplied."""
        if year and month:
            return year, month
        today = date.today()
        return today.year, today.month


__all__ = ["ReportingRepository"]
