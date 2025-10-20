"""Customer data access helpers.
isolates database interactions for customer-related queries.
"""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func

from app.integration.models import db
from app.integration.models.customer import Customer


class CustomerRepository:
    """query helpers for customer entities."""

    def get_all(self) -> Sequence[Customer]:
        """Return all customers ordered by primary key for better output."""
        return Customer.query.order_by(Customer.customer_id).all()

    def get_by_username(self, username: str) -> Optional[Customer]:
        if not username:
            return None
        return Customer.query.filter_by(username=username).first()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        if not customer_id:
            return None
        return Customer.query.filter_by(customer_id=customer_id).first()

    def username_exists(self, username: str) -> bool:
        if not username:
            return False
        return bool(
            db.session.query(func.count(Customer.customer_id))
            .filter(func.lower(Customer.username) == username.lower())
            .scalar()
        )

    def email_exists(self, email: str) -> bool:
        if not email:
            return False
        return bool(
            db.session.query(func.count(Customer.customer_id))
            .filter(func.lower(Customer.email_address) == email.lower())
            .scalar()
        )

    def create(self, **customer_data) -> Customer:
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.flush()
        return customer


__all__ = ["CustomerRepository"]
