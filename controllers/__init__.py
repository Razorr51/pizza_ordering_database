from flask import Blueprint, jsonify
from models import db
from models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.get("/")
def list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username} for u in users])

