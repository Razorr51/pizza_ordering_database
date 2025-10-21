"""Authentication-related Flask route handlers."""
from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.ownership.services.customer_service import CustomerService


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_service = CustomerService()


@auth_bp.get("/login")
def login_form():
    """Render the login form, optionally pre-filling the username."""
    username = request.args.get("username", "")
    return render_template("auth/login.html", form_data={"username": username})


@auth_bp.post("/login")
def login_submit():
    """Authenticate a customer and redirect to the menu on success."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    customer = _service.authenticate(username, password)
    if customer:
        session["customer_id"] = customer.customer_id
        session["customer_name"] = customer.name
        flash(f"Welcome back, {customer.name}!", "success")
        return redirect(url_for("menu.get_menu_html"))

    flash("Invalid username or password.", "error")
    return render_template(
        "auth/login.html",
        form_data={"username": username},
    )


@auth_bp.get("/signup")
def signup_form():
    """Render the customer registration form."""
    return render_template("auth/signup.html", form_data={})


@auth_bp.post("/signup")
def signup_submit():
    """Validate signup data, create a customer, and handle validation errors."""
    form_data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "username": request.form.get("username", "").strip(),
        "password": request.form.get("password", ""),
        "phone_number": request.form.get("phone_number", "").strip(),
        "street_name": request.form.get("street_name", "").strip(),
        "street_number": request.form.get("street_number", "").strip(),
        "postcode": request.form.get("postcode", "").strip(),
        "birthdate": request.form.get("birthdate", "").strip(),
    }

    customer, errors = _service.register_customer(**form_data)
    if customer:
        session["customer_id"] = customer.customer_id
        session["customer_name"] = customer.name
        flash("Account created successfully!", "success")
        return redirect(url_for("menu.get_menu_html"))

    if errors.get("form"):
        flash(errors["form"], "error")
        errors = {k: v for k, v in errors.items() if k != "form"}

    return render_template("auth/signup.html", form_data=form_data, form_errors=errors)


@auth_bp.post("/logout")
def logout():
    """Clear session state and redirect to the login page."""
    session.pop("customer_id", None)
    session.pop("customer_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login_form"))


__all__ = ["auth_bp"]
