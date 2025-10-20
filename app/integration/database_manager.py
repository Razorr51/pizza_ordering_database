from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.integration.models import db

class DatabaseManager:
    def __init__(self, app):
        self.app = app
        self._using_sqlite = str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith("sqlite")

    def execute_sql_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        for stmt in [s.strip() for s in sql_script.split(";") if s.strip()]:
            normalized = self._prepare_statement(stmt)
            db.session.execute(text(normalized))
        db.session.commit()

    def setup_schema(self):
        try:
            config_root = Path(self.app.root_path).resolve()
            sql_dir = config_root.parent / "integration" / "sql"
            view_path = sql_dir / "views.sql"
            seed_path = sql_dir / "seed_min.sql"
            pizza_seed_path = sql_dir / "seed_pizzas.sql"
            orders_seed_path = sql_dir / "seed_orders.sql"
            self._drop_reporting_views()
            self._rebuild_order_tables()
            self._sync_discount_table()
            if view_path.exists():
                self.execute_sql_file(view_path)
            if seed_path.exists():
                self.execute_sql_file(seed_path)
            if pizza_seed_path.exists():
                self.execute_sql_file(pizza_seed_path)
            if orders_seed_path.exists():
                self.execute_sql_file(orders_seed_path)
        except OperationalError as e:
            self.app.logger.error("Database setup failed: %s", e)
            raise

    def _prepare_statement(self, statement: str) -> str:
        if not self._using_sqlite:
            return statement
        return (
            statement.replace("INSERT IGNORE", "INSERT OR IGNORE")
            .replace("NOW()", "CURRENT_TIMESTAMP")
        )

    def _drop_menu_price_table(self) -> None:
        try:
            db.session.execute(text("DROP VIEW IF EXISTS pizza_menu_prices"))
            db.session.commit()
        except OperationalError:
            db.session.rollback()
        try:
            db.session.execute(text("DROP TABLE IF EXISTS pizza_menu_prices"))
            db.session.commit()
        except OperationalError:
            db.session.rollback()

    def _drop_reporting_views(self) -> None:
        inspector = inspect(db.engine)
        existing_views = set(inspector.get_view_names()) if hasattr(inspector, "get_view_names") else set()

        targets = [
            "staff_undelivered_orders",
            "staff_top_pizzas_last_month",
            "staff_monthly_earnings_by_gender",
            "staff_monthly_earnings_by_age_group",
            "staff_monthly_earnings_by_postcode",
            "pizza_menu_prices",
        ]
        for view in targets:
            if view in existing_views:
                try:
                    db.session.execute(text(f"DROP VIEW IF EXISTS {view}"))
                    db.session.commit()
                except OperationalError:
                    db.session.rollback()
        # Drop any lingering compatibility table created for pizza_menu_prices
        self._drop_menu_price_table()

    def _rebuild_order_tables(self) -> None:
        from app.integration.models.order import Order, OrderItem

        engine = db.session.bind or db.engine

        # Drop dependent tables first to avoid foreign key violations
        OrderItem.__table__.drop(bind=engine, checkfirst=True)
        Order.__table__.drop(bind=engine, checkfirst=True)

        Order.__table__.create(bind=engine, checkfirst=True)
        OrderItem.__table__.create(bind=engine, checkfirst=True)
        db.session.commit()

    def _sync_discount_table(self) -> None:
        inspector = inspect(db.engine)
        if not inspector.has_table("discount_code"):
            return
        columns = {col["name"].lower() for col in inspector.get_columns("discount_code")}
        if "redeemed_at" not in columns:
            db.session.execute(text("ALTER TABLE discount_code ADD COLUMN redeemed_at DATETIME NULL"))
            db.session.commit()
