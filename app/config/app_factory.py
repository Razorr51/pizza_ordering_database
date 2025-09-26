from flask import Flask, render_template
from pathlib import Path
from app.config.app_config import AppConfig

def _register_blueprints(app):
    from app.presentation.controllers.auth import auth_bp
    from app.presentation.controllers.customers import customers_bp
    from app.presentation.controllers.menu import menu_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(menu_bp)

def create_app():
    base_app_dir  = Path(__file__).resolve().parents[1]
    templates_dir = base_app_dir / "templates"
    static_dir    = base_app_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir)
    )

    config = AppConfig()
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.track_modifications
    app.config["SQLALCHEMY_ECHO"] = config.echo
    app.config["SECRET_KEY"] = config.secret_key


    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    app.logger.info(f"Using database URL: {config.get_masked_uri()}")

    from app.integration.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
        from app.integration.database_manager import DatabaseManager
        DatabaseManager(app).setup_schema()
        from app.integration.models import seed_data
        seed_data()

    _register_blueprints(app)

    @app.route("/")
    def index():
        return render_template("menu.html")

    return app
