"""Helpers for querying delivery personnel availability."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy import case, func

from app.integration.models.delivery import DeliveryPerson, DeliveryPersonPostcode
from app.integration.models.postcode import Postcode


class DeliveryRepository:
    """Query helpers around delivery drivers and their zones."""

    def drivers_for_postcode(self, postcode_id: int) -> List[DeliveryPerson]:
        return (
            DeliveryPerson.query.join(DeliveryPersonPostcode)
            .filter(DeliveryPersonPostcode.postcode_id == postcode_id)
            .order_by(
                case((DeliveryPerson.unavailable_until.is_(None), 0), else_=1),
                DeliveryPerson.unavailable_until.asc(),
            )
            .all()
        )

    def fallback_drivers(self) -> List[DeliveryPerson]:
        return (
            DeliveryPerson.query
            .order_by(
                case((DeliveryPerson.unavailable_until.is_(None), 0), else_=1),
                DeliveryPerson.unavailable_until.asc(),
            )
            .all()
        )

    def find_available_driver(
        self,
        postcode_id: int,
        reference_time: Optional[datetime] = None,
    ) -> Optional[DeliveryPerson]:
        reference_time = reference_time or datetime.utcnow()
        candidates: Sequence[DeliveryPerson] = self.drivers_for_postcode(postcode_id)
        if not candidates:
            candidates = self.fallback_drivers()
        for driver in candidates:
            if driver.unavailable_until is None or driver.unavailable_until <= reference_time:
                return driver
        return None

    def assign_driver_to_postcode(self, driver_id: int, postcode_id: int) -> None:
        existing = (
            DeliveryPersonPostcode.query.filter_by(
                delivery_driver_id=driver_id,
                postcode_id=postcode_id,
            ).first()
        )
        if existing:
            return
        link = DeliveryPersonPostcode(
            delivery_driver_id=driver_id,
            postcode_id=postcode_id,
        )
        from app.integration.models import db

        db.session.add(link)

    def all_postcodes(self) -> List[Postcode]:
        return Postcode.query.order_by(Postcode.postcode_id).all()


__all__ = ["DeliveryRepository"]
