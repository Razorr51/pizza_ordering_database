"""Staff reporting endpoints and dashboard views."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from flask import Blueprint, jsonify, render_template, request

from app.ownership.services.reporting_service import ReportingService

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

_service = ReportingService()


@reports_bp.get("/")
def dashboard():
    """Render the staff dashboard with reporting data."""
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    earnings = _service.monthly_earnings(year=year, month=month)
    top_pizzas = _service.top_pizzas_last_month()
    undelivered = _service.undelivered_orders()

    return render_template(
        "reports/dashboard.html",
        earnings=_convert_nested(earnings),
        top_pizzas=_convert_list(top_pizzas),
        undelivered=_convert_list(undelivered),
    )


@reports_bp.get("/undelivered")
def undelivered_orders():
    """Return outstanding orders in JSON form."""
    orders = _service.undelivered_orders()
    return jsonify({"orders": _convert_list(orders)})


@reports_bp.get("/top-pizzas")
def top_pizzas():
    """Return the most popular pizzas from last month."""
    limit = request.args.get("limit", default=3, type=int)
    pizzas = _service.top_pizzas_last_month(limit=limit)
    return jsonify({"pizzas": _convert_list(pizzas)})


@reports_bp.get("/earnings")
def earnings():
    """Return earnings breakdowns by demographic and postal code."""
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    data = _service.monthly_earnings(year=year, month=month)
    return jsonify(_convert_nested(data))


def _convert_list(rows: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [{key: _convert_value(value) for key, value in row.items()} for row in rows]


def _convert_nested(payload: Dict[str, Any]) -> Dict[str, Any]:
    converted: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            converted[key] = _convert_list(value)
        elif isinstance(value, dict):
            converted[key] = _convert_nested(value)
        else:
            converted[key] = _convert_value(value)
    return converted


def _convert_value(value: Any) -> Any:
    """Convert Decimal instances to floats while leaving other values untouched."""
    if isinstance(value, Decimal):
        return float(value)
    return value


__all__ = ["reports_bp"]
