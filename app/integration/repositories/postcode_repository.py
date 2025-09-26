
from __future__ import annotations

from typing import Optional

from sqlalchemy import text

from app.integration.models import db


class PostcodeRepository:

    def find_id_by_code(self, postcode_code: str) -> Optional[int]:
        if not postcode_code:
            return None
        row = db.session.execute(
            text("SELECT postcode_id FROM postcode WHERE postcode = :code"),
            {"code": postcode_code},
        ).first()
        return row.postcode_id if row else None

    def _next_id(self) -> int:
        result = db.session.execute(
            text("SELECT COALESCE(MAX(postcode_id), 0) + 1 AS next_id FROM postcode")
        ).scalar_one()
        return int(result)

    def create(self, postcode_code: str) -> int:
        new_id = self._next_id()
        db.session.execute(
            text(
                "INSERT INTO postcode (postcode_id, postcode) VALUES (:id, :code)"
            ),
            {"id": new_id, "code": postcode_code},
        )
        db.session.flush()
        return new_id

    def get_or_create_id(self, postcode_code: str) -> int:
        existing = self.find_id_by_code(postcode_code)
        if existing is not None:
            return existing
        return self.create(postcode_code)


__all__ = ["PostcodeRepository"]
