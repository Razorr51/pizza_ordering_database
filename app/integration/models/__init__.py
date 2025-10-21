"""Shared SQLAlchemy models and seeding utilities."""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


def _ensure_postcode(code: str, preferred_id: int) -> int:
    """Create the postcode if it does not exist and return its identifier."""
    from .postcode import Postcode

    existing = Postcode.query.filter_by(postcode=code).first()
    if existing:
        return existing.postcode_id

    desired_id_taken = Postcode.query.filter_by(postcode_id=preferred_id).first() is not None
    next_id = preferred_id
    if desired_id_taken:
        current_max = db.session.query(func.coalesce(func.max(Postcode.postcode_id), 0)).scalar()
        next_id = int(current_max) + 1

    postcode = Postcode(postcode_id=next_id, postcode=code)
    db.session.add(postcode)
    db.session.flush()
    return postcode.postcode_id


def seed_data():
    """Example Customers"""
    from .customer import Customer

    if Customer.query.first():
        return

    amsterdam_central = _ensure_postcode("1011AB", 1011)
    amsterdam_damrak = _ensure_postcode("1012CD", 1012)

    db.session.add(Customer(
        name="Alice Johnson",
        username="alice",
        password="alice123",
        email_address="alice@example.com",
        phone_number="+31101234567",
        street_name="Canal Street",
        street_number=12,
        postcode_id=amsterdam_central,
        birthdate=date(1992, 5, 14)
    ))
    db.session.add(Customer(
        name="Bob Smith",
        username="bob",
        password="bob12345",
        email_address="bob@example.com",
        phone_number="+31107654321",
        street_name="Damrak",
        street_number=45,
        postcode_id=amsterdam_damrak,
        birthdate=date(1988, 11, 2)
    ))
    db.session.commit()


from .customer import Customer
from .delivery import DeliveryPerson, DeliveryPersonPostcode
from .discount import DiscountCode
from .ingredient import Ingredient
from .menu_item import MenuItem
from .order import Order, OrderItem
from .pizza import Pizza, PizzaIngredient, PizzaMenuPrice
from .postcode import Postcode

__all__ = [
    "db",
    "Customer",
    "DeliveryPerson",
    "DeliveryPersonPostcode",
    "DiscountCode",
    "Ingredient",
    "MenuItem",
    "Order",
    "OrderItem",
    "Pizza",
    "PizzaIngredient",
    "PizzaMenuPrice",
    "Postcode",
    "seed_data",
]
