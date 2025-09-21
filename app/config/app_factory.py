from flask import Flask
from app.config.app_config import AppConfig

def _register_blueprints(app):
    from app.presentation.controllers.customers import customers_bp
    from app.presentation.controllers.menu import menu_bp
    app.register_blueprint(customers_bp)
    app.register_blueprint(menu_bp)

def create_app():
    app = Flask(__name__)
    config = AppConfig()

    app.config["SQLALCHEMY_DATABASE_URI"] = config.database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.track_modifications
    app.config["SQLALCHEMY_ECHO"] = config.echo
    app.config["SECRET_KEY"] = config.secret_key

    app.logger.info(f"Using database URL: {config.get_masked_uri()}")

    # Init db first
    from app.integration.models import db
    db.init_app(app)

    with app.app_context():
        # Create all tables BEFORE seeding data
        db.create_all()

        # Now setup schema and seed data
        from app.integration.database_manager import DatabaseManager
        db_manager = DatabaseManager(app)
        db_manager.setup_schema()

        from app.integration.models import seed_data
        seed_data()

    _register_blueprints(app)

    @app.route("/")
    def index():
        return ('<p>Pizza ordering system. Try '
                '<a href="/menu/">/menu/</a> and '
                '<a href="/customers/">/customers/</a>.</p>')

    return app
