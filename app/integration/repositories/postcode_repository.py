
from __future__ import annotations

from typing import Optional

from sqlalchemy import func

from app.integration.models import db
from app.integration.models.postcode import Postcode


class PostcodeRepository:
    """Persistence helpers for postcode records."""

    def find_id_by_code(self, postcode_code: str) -> Optional[int]:
        if not postcode_code:
            return None
        record = Postcode.query.filter_by(postcode=postcode_code).first()
        return record.postcode_id if record else None

    def _next_id(self) -> int:
        max_id = db.session.query(func.max(Postcode.postcode_id)).scalar() or 0
        return int(max_id) + 1

    def create(self, postcode_code: str) -> int:
        new_postcode = Postcode(
            postcode_id=self._next_id(),
            postcode=postcode_code,
        )
        db.session.add(new_postcode)
        db.session.flush()
        return new_postcode.postcode_id

    def get_or_create_id(self, postcode_code: str) -> int:
        existing = self.find_id_by_code(postcode_code)
        if existing is not None:
            return existing
        return self.create(postcode_code)


__all__ = ["PostcodeRepository"]
