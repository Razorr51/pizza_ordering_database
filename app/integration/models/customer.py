from sqlalchemy.orm import relationship

from . import db

class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column("Customer_ID", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(100), nullable=False)
    gender = db.Column("Gender", db.String(10))
    birthdate = db.Column("Birthdate", db.Date)
    postcode_id = db.Column("Postcode_ID", db.Integer)
    street_number = db.Column("Street_Number", db.Integer)
    email_address = db.Column("Email_Address", db.String(100), unique=True)
    phone_number = db.Column("Phone_Number", db.String(15))
    username = db.Column("Username", db.String(50), unique=True)
    password = db.Column("Password", db.String(255))
    can_birthday = db.Column("canBirthDay", db.Boolean, default=False, nullable=False)
    can_discount = db.Column("canDiscount", db.Boolean, default=False, nullable=False)
    pizzas_ordered = db.Column("PizzasOrdered", db.Integer, default=0, nullable=False)
    street_name = db.Column("Street_Name", db.String(255))

    orders = relationship("Order", back_populates="customer", lazy="selectin")
    def __repr__(self):
        return f"<Customer {self.username}>"
