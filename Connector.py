# connector.py (additions)
import os
from flask import Flask
from controllers import users_bp
from controllers.menu import menu_bp  # new
from models import db, seed_data
from sqlalchemy.exc import OperationalError
import re
from pathlib import Path

def _exec_sql_from_file(path):
    from sqlalchemy import text
    with open(path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    # Split on semicolons cautiously; most of our scripts are simple.
    for stmt in [s.strip() for s in sql_script.split(";") if s.strip()]:
        db.session.execute(db.text(stmt))
    db.session.commit()

def create_app():
    app = Flask(__name__)

    default_mysql = "mysql+pymysql://pizza_app:Database2025!@localhost:3306/pizza_ordering"
    if os.environ.get("SQLITE_FALLBACK") == "1":
        default_mysql = "sqlite:///dev.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL", default_mysql)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQL_ECHO") == "1"

    _raw = app.config["SQLALCHEMY_DATABASE_URI"]
    masked = re.sub(r"//([^:]+):[^@]*@", r"//\\1:***@", _raw)
    app.logger.info(f"Using database URL: {masked}")

    db.init_app(app)
    app.register_blueprint(users_bp)
    app.register_blueprint(menu_bp)  # new

    with app.app_context():
        try:
            # Create ORM tables that already exist in your codebase (User etc.)
            db.create_all()

            # Execute Week 2 SQL schema and view (idempotent)
            base = Path(__file__).resolve().parent

            view_path = base / "sql" / "views.sql"
            seed_min_path = base / "sql" / "seed_min.sql"

            if view_path.exists():
                _exec_sql_from_file(view_path)
            if seed_min_path.exists():
                _exec_sql_from_file(seed_min_path)

            # Keep existing seed_data() for users
            seed_data()

        except OperationalError as e:
            app.logger.error("Database connection failed. Details: %s", e)
            app.logger.error("Check that the DB is running and DB_URL is set correctly.")

    @app.route("/")
    def index():
        return ('<p>Flask MVC example. Try '
                '<a href="/menu/">/menu/</a> for Week 2 menu pricing view and '
                '<a href="/users/">/users/</a> for users.</p>')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port = 5002)