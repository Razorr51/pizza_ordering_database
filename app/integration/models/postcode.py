"""SQLAlchemy model describing the postcode table."""
from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import db


class Postcode(db.Model):
    """Stores the mapping between postcode codes and optional drivers."""

    __tablename__ = "postcode"

    postcode_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    postcode: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True)
    delivery_driver_id: Mapped[int | None] = mapped_column(
        "DeliveryDriver_ID",
        ForeignKey("delivery_person.DeliveryDriver_ID", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        """Return the postcode."""
        return f"Postcode(code={self.postcode!r})"


__all__ = ["Postcode"]
