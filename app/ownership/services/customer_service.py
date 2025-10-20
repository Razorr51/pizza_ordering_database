"""Customer-facing domain services."""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

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

        clean_name = (name or "").strip()
        clean_username = (username or "").strip()
        clean_email = (email or "").strip()
        clean_password = password or ""
        clean_phone = (phone_number or "").strip()
        phone_digits_only = "".join(ch for ch in clean_phone if ch.isdigit())
        clean_street = (street_name or "").strip()
        clean_street_number = (street_number or "").strip()
        normalized_postcode = "".join((postcode or "").split()).upper()
        clean_birthdate = (birthdate or "").strip()

        parsed_birthdate: Optional[date] = None
        if clean_birthdate:
            parsed_birthdate, birthdate_error = self._parse_birthdate(clean_birthdate)
            if birthdate_error:
                errors["birthdate"] = birthdate_error
            elif parsed_birthdate and parsed_birthdate > date.today():
                errors["birthdate"] = "Birthdate cannot be in the future."
        else:
            errors["birthdate"] = "Birthdate is required."

        if not clean_name:
            errors["name"] = "Name is required."
        if not clean_username:
            errors["username"] = "Username is required."
        if not clean_email:
            errors["email"] = "Email is required."
        if not clean_password or len(clean_password) < 6:
            errors["password"] = "Password must be at least 6 characters long."
        if not phone_digits_only or len(phone_digits_only) < 7:
            errors["phone_number"] = "Phone number must include at least 7 digits."
        if not clean_street:
            errors["street_name"] = "Street name is required."

        parsed_street_number: Optional[int] = None
        if clean_street_number:
            if clean_street_number.isdigit():
                parsed_street_number = int(clean_street_number)
                if parsed_street_number <= 0:
                    errors["street_number"] = "Street number must be positive."
            else:
                errors["street_number"] = "Street number must be numeric."
        else:
            errors["street_number"] = "Street number is required."

        if not normalized_postcode:
            errors["postcode"] = "Postcode is required."
        elif len(normalized_postcode) < 4:
            errors["postcode"] = "Postcode looks too short."

        if clean_username and self._repository.username_exists(clean_username):
            errors["username"] = "Username already taken."
        if clean_email and self._repository.email_exists(clean_email):
            errors["email"] = "An account with this email already exists."

        if errors:
            return None, errors

        try:
            postcode_id_value = self._postcode_repository.get_or_create_id(normalized_postcode)

            customer = self._repository.create(
                name=clean_name,
                username=clean_username,
                email_address=clean_email,
                password=clean_password,
                phone_number=clean_phone,
                street_name=clean_street,
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

    def _parse_birthdate(self, raw_value: str) -> Tuple[Optional[date], Optional[str]]:
        """Attempt to parse multiple acceptable birthdate formats."""
        formats = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(raw_value, fmt).date(), None
            except ValueError:
                continue
        return None, "Birthdate must be in DD-MM-YYYY format."


__all__ = ["CustomerService"]
