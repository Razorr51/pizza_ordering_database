"""Customer-facing domain services."""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from unittest.mock import right

from sqlalchemy.exc import IntegrityError

from app.integration.models import db
from app.integration.repositories.customer_repository import CustomerRepository
from app.integration.repositories.postcode_repository import PostcodeRepository
from app.integration.models.customer import Customer


class CustomerService:

    def __init__(self, repository: Optional[CustomerRepository] = None) -> None:
        self._repository = repository or CustomerRepository()
        self._postcode_repository = PostcodeRepository()

    def list_customers(self) -> List[Dict[str, object]]:
        customers = self._repository.get_all()
        return [
            {"id": customer.customer_id, "username": customer.username, "name": customer.name}
            for customer in customers
        ]

    def authenticate(self, username: str, password: str) -> Optional[Customer]:
        """Return the matching customer when credentials are valid."""
        if not username or not password:
            return None
        customer = self._repository.get_by_username(username)
        if not customer:
            return None
        if customer.password == password:
            return customer
        return None

    def register_customer(
        self,
        *,
        name: str,
        email: str,
        username: str,
        password: str,
        phone_number: str,
        street_name: str,
        street_number: str,
        postcode: str,
        birthdate: str,
    ) -> Tuple[Optional[Customer], Dict[str, str]]:
        errors: Dict[str, str] = {}

        right_name = (name or "").strip()
        right_username = (username or "").strip()
        right_email = (email or "").strip()
        right_password = password or ""
        right_phone = (phone_number or "").strip()
        phone_digits = "".join(ch for ch in right_phone if ch.isdigit())
        right_street = (street_name or "").strip()
        right_street_number = (street_number or "").strip()
        right_postcode = "".join((postcode or "").split()).upper()
        right_birthdate = (birthdate or "").strip()

        parsed_birthdate: Optional[date] = None
        if right_birthdate:
            try:
                parsed_birthdate = datetime.strptime(right_birthdate, "%d-%m-%Y").date()
                if parsed_birthdate > date.today():
                    errors["birthdate"] = "Birthdate cannot be in the future."
            except ValueError:
                errors["birthdate"] = "Birthdate must be in DD-MM-YYYY format."
        else:
            errors["birthdate"] = "Birthdate is required."

        if not right_name:
            errors["name"] = "Name is required."
        if not right_username:
            errors["username"] = "Username is required."
        if not right_email:
            errors["email"] = "Email is required."
        if not right_password or len(right_password) < 6:
            errors["password"] = "Password must be at least 6 characters long."
        if not phone_digits or len(phone_digits) < 7:
            errors["phone_number"] = "Phone number must include at least 7 digits."
        if not right_street:
            errors["street_name"] = "Street name is required."

        parsed_street_number: Optional[int] = None
        if right_street_number:
            if right_street_number.isdigit():
                parsed_street_number = int(right_street_number)
                if parsed_street_number <= 0:
                    errors["street_number"] = "Street number must be positive."
            else:
                errors["street_number"] = "Street number must be numeric."
        else:
            errors["street_number"] = "Street number is required."

        if not right_postcode:
            errors["postcode"] = "Postcode is required."
        elif len(right_postcode) < 4:
            errors["postcode"] = "Postcode looks too short."

        if right_username and self._repository.username_exists(right_username):
            errors["username"] = "Username already taken."
        if right_email and self._repository.email_exists(right_email):
            errors["email"] = "An account with this email already exists."

        if errors:
            return None, errors

        try:
            postcode_id_value = self._postcode_repository.get_or_create_id(right_postcode)

            customer = self._repository.create(
                name=right_name,
                username=right_username,
                email_address=right_email,
                password=right_password,
                phone_number=right_phone,
                street_name=right_street,
                street_number=parsed_street_number,
                postcode_id=postcode_id_value,
                birthdate=parsed_birthdate,
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            errors["form"] = "We could not create your account due to a database constraint. Please verify your details and try again."
            return None, errors
        except Exception:
            db.session.rollback()
            raise

        return customer, {}


__all__ = ["CustomerService"]
