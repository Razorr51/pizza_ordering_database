# app/integration/models/__init__.py
from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def seed_data():
    from .customer import Customer
    if not Customer.query.first():
        db.session.add(Customer(
            name="Alice Johnson",
            username="alice",
            password="alice123",
            email_address="alice@example.com",
            phone_number="+31101234567",
            street_name="Canal Street",
            street_number=12,
            postcode_id=1011,
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
            postcode_id=1012,
            birthdate=date(1988, 11, 2)
        ))
        db.session.commit()
