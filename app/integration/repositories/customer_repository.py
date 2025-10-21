"""Data access helpers for customer-related queries."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func

from app.integration.models import db
from app.integration.models.customer import Customer


class CustomerRepository:
    """Encapsulate customer entity lookup and creation logic."""

    def get_all(self) -> Sequence[Customer]:
        """Return all customers ordered by primary key for better output."""
        return Customer.query.order_by(Customer.customer_id).all()

    def get_by_username(self, username: str) -> Optional[Customer]:
        """Fetch a customer record by username if provided."""
        if not username:
            return None
        return Customer.query.filter_by(username=username).first()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Return the customer who matches ``customer_id``."""
        if not customer_id:
            return None
        return Customer.query.filter_by(customer_id=customer_id).first()

    def username_exists(self, username: str) -> bool:
        """True when another customer already uses the givrn username."""
        if not username:
            return False
        return bool(
            db.session.query(func.count(Customer.customer_id))
            .filter(func.lower(Customer.username) == username.lower())
            .scalar()
        )

    def email_exists(self, email: str) -> bool:
        """True when the email address is already being used."""
        if not email:
            return False
        return bool(
            db.session.query(func.count(Customer.customer_id))
            .filter(func.lower(Customer.email_address) == email.lower())
            .scalar()
        )

    def create(self, **customer_data) -> Customer:
        """Create a new customer record and return the instance."""
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.flush()
        return customer


__all__ = ["CustomerRepository"]
