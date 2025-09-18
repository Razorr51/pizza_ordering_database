# `Connector.py`
from flask import Flask
from controllers import users_bp
from models import db, seed_data
import os
from sqlalchemy.exc import OperationalError
import re


def create_app():
    app = Flask(__name__)

    # Prefer environment variable DB_URL; fallback to local MySQL; allow SQLITE_FALLBACK=1 to use sqlite for quick dev.
    default_mysql = "mysql+pymysql://omaralibrandi:ombrellone2@localhost:3306/pizza_ordering"
    if os.environ.get("SQLITE_FALLBACK") == "1":
        default_mysql = "sqlite:///dev.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL", default_mysql)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Log which DB URL is in effect (password masked)
    _raw = app.config["SQLALCHEMY_DATABASE_URI"]
    masked = re.sub(r"//([^:]+):[^@]*@", r"//\\1:***@", _raw)
    app.logger.info(f"Using database URL: {masked}")

    db.init_app(app)
    app.register_blueprint(users_bp)

    with app.app_context():
        try:
            db.create_all()
            seed_data()
        except OperationalError as e:
            app.logger.error("Database connection failed. Details: %s", e)
            app.logger.error("Check that MySQL is running, credentials/database exist, and network/host is correct.")

    @app.route("/")
    def index():
        return ('<p>Flask MVC example. Go to '
                '<a href="/users">/users</a>. If you get DB errors, verify MySQL running and DB_URL env var.</p>')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
