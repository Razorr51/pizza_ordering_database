from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def seed_data():
    from .user import User  # local import to avoid circular import
    if not User.query.first():
        db.session.add(User(username="alice"))
        db.session.add(User(username="bob"))
        db.session.commit()

