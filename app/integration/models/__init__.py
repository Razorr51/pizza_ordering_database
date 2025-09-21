# app/integration/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def seed_data():
    from .customer import Customer  # Changed from user to customer
    if not Customer.query.first():
        db.session.add(Customer(
            name="Alice Johnson",
            username="alice",
            password="hashed_password_123",
            email_address="alice@example.com"
        ))
        db.session.add(Customer(
            name="Bob Smith",
            username="bob",
            password="hashed_password_456",
            email_address="bob@example.com"
        ))
        db.session.commit()
