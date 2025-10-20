"""Application-facing reporting service exposing staff dashboards."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from app.integration.repositories.reporting_repository import ReportingRepository


class ReportingService:
    """Aggregates staff-facing metrics from reporting repository."""

    def __init__(self, repository: Optional[ReportingRepository] = None) -> None:
        self._repository = repository or ReportingRepository()

    def undelivered_orders(self) -> List[Dict[str, object]]:
        return self._repository.fetch_undelivered_orders()

    def top_pizzas_last_month(self, limit: int = 3) -> List[Dict[str, object]]:
        safe_limit = max(1, min(limit, 10))
        return self._repository.fetch_top_pizzas_last_month(limit=safe_limit)

    def monthly_earnings(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, object]]]:
        year, month = self._normalize_period(year, month)
        return {
            "period": {"year": year, "month": month},
            "by_gender": self._repository.earnings_by_gender(year, month),
            "by_age_group": self._repository.earnings_by_age_group(year, month),
            "by_postcode": self._repository.earnings_by_postcode(year, month),
        }

    @staticmethod
    def _normalize_period(year: Optional[int], month: Optional[int]) -> tuple[int, int]:
        if year and month:
            return year, month
        today = date.today()
        return today.year, today.month


__all__ = ["ReportingService"]
