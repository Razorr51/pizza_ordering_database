"""SQLAlchemy models related to delivery personnel assignments."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db


class DeliveryPerson(db.Model):
    """Represents a delivery driver that can fulfill orders."""

    __tablename__ = "delivery_person"

    delivery_driver_id: Mapped[int] = mapped_column(
        "DeliveryDriver_ID",
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column("DeliveryDriver_Name", db.String(100), nullable=False)
    is_available: Mapped[bool] = mapped_column("isAvailable", db.Boolean, nullable=False, default=True)
    unavailable_until: Mapped[datetime | None] = mapped_column(db.DateTime, nullable=True)

    zones: Mapped[list["DeliveryPersonPostcode"]] = relationship(
        "DeliveryPersonPostcode",
        back_populates="driver",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="delivery_person",
        lazy="selectin",
    )

    def mark_unavailable_until(self, moment: datetime | None) -> None:
        """Update availability window based on the provided timestamp."""
        self.unavailable_until = moment
        self.is_available = moment is None or moment <= datetime.utcnow()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"DeliveryPerson(id={self.delivery_driver_id}, name={self.name!r})"


class DeliveryPersonPostcode(db.Model):
    """Join table linking drivers to the postcodes they serve."""

    __tablename__ = "delivery_person_postcode"

    delivery_driver_id: Mapped[int] = mapped_column(
        "DeliveryDriver_ID",
        ForeignKey("delivery_person.DeliveryDriver_ID", ondelete="CASCADE"),
        primary_key=True,
    )
    postcode_id: Mapped[int] = mapped_column(
        "Postcode_ID",
        ForeignKey("postcode.postcode_id", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
    )

    driver: Mapped[DeliveryPerson] = relationship(
        "DeliveryPerson",
        back_populates="zones",
        lazy="joined",
    )
    postcode: Mapped["Postcode"] = relationship("Postcode", lazy="joined")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"DeliveryPersonPostcode(driver_id={self.delivery_driver_id}, postcode_id={self.postcode_id})"


__all__ = ["DeliveryPerson", "DeliveryPersonPostcode"]
