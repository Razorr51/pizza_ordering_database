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

    def setup_schema(self, *, reset: bool = True):
        try:
            config_root = Path(self.app.root_path).resolve()
            sql_dir = config_root.parent / "integration" / "sql"
            view_path = sql_dir / "views.sql"
            seed_path = sql_dir / "seed_min.sql"
            pizza_seed_path = sql_dir / "seed_pizzas.sql"
            orders_seed_path = sql_dir / "seed_orders.sql"
            self._drop_reporting_views()
            if reset:
                self._rebuild_order_tables()
            self._sync_discount_table()
            if view_path.exists():
                self.execute_sql_file(view_path)
            should_seed = reset or self._needs_initial_seed()
            if should_seed and seed_path.exists():
                self.execute_sql_file(seed_path)
            if should_seed and pizza_seed_path.exists():
                self.execute_sql_file(pizza_seed_path)
            if should_seed and orders_seed_path.exists():
                self.execute_sql_file(orders_seed_path)
            self._reset_driver_availability()
        except OperationalError as e:
            self.app.logger.error("Database setup failed: %s", e)
            raise
        finally:
            self._ensure_order_discount_nullable()
            self._ensure_discount_code_schema()
            self._ensure_customer_pk_autoincrement()

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

    def _ensure_order_discount_nullable(self) -> None:
        if self._using_sqlite:
            return
        inspector = inspect(db.engine)
        if not inspector.has_table("orders"):
            return
        columns = inspector.get_columns("orders")
        discount_column = next((col for col in columns if col["name"] == "DiscountCode_ID"), None)
        if discount_column and not discount_column.get("nullable", True):
            try:
                db.session.execute(text("ALTER TABLE orders MODIFY DiscountCode_ID INT NULL"))
                db.session.commit()
            except OperationalError:
                db.session.rollback()

    def _ensure_customer_pk_autoincrement(self) -> None:
        if self._using_sqlite:
            return
        inspector = inspect(db.engine)
        if not inspector.has_table("customers"):
            return
        try:
            extra_flag = db.session.execute(
                text(
                    "SELECT EXTRA FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = 'customers' "
                    "AND COLUMN_NAME = 'Customer_ID'"
                )
            ).scalar()
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            return
        if extra_flag and "auto_increment" in extra_flag.lower():
            return
        try:
            with db.engine.begin() as connection:
                connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                try:
                    connection.execute(
                        text("ALTER TABLE customers MODIFY COLUMN Customer_ID INT NOT NULL AUTO_INCREMENT")
                    )
                    next_id = connection.execute(
                        text("SELECT COALESCE(MAX(Customer_ID), 0) + 1 AS nxt FROM customers")
                    ).scalar() or 1
                    connection.execute(
                        text("ALTER TABLE customers AUTO_INCREMENT = :next_id"),
                        {"next_id": int(next_id)},
                    )
                finally:
                    connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        except OperationalError:
            db.session.rollback()

    def _ensure_discount_code_schema(self) -> None:
        if self._using_sqlite:
            return
        inspector = inspect(db.engine)
        if not inspector.has_table("discount_code"):
            return
        orders_fk_present = False
        if inspector.has_table("orders"):
            for fk in inspector.get_foreign_keys("orders"):
                if (
                    fk.get("constrained_columns") == ["DiscountCode_ID"]
                    and fk.get("referred_table") == "discount_code"
                ):
                    orders_fk_present = True
                    break
        needs_auto_increment = True
        try:
            extra_flag = db.session.execute(
                text(
                    "SELECT EXTRA FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = 'discount_code' "
                    "AND COLUMN_NAME = 'DiscountCode_ID'"
                )
            ).scalar()
            db.session.commit()
            needs_auto_increment = not (extra_flag and "auto_increment" in extra_flag.lower())
        except OperationalError:
            db.session.rollback()

        try:
            with db.engine.begin() as connection:
                if orders_fk_present:
                    try:
                        connection.execute(text("ALTER TABLE orders DROP FOREIGN KEY orders_ibfk_4"))
                    except OperationalError:
                        orders_fk_present = False
                foreign_checks_disabled = False
                try:
                    connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                    foreign_checks_disabled = True
                    exists_zero = connection.execute(
                        text(
                            "SELECT 1 FROM discount_code "
                            "WHERE DiscountCode_ID = 0 LIMIT 1"
                        )
                    ).scalar()
                    if exists_zero:
                        new_id = connection.execute(
                            text("SELECT COALESCE(MAX(DiscountCode_ID), 0) + 1 FROM discount_code")
                        ).scalar() or 1
                        connection.execute(
                            text(
                                "UPDATE discount_code "
                                "SET DiscountCode_ID = :new_id WHERE DiscountCode_ID = 0"
                            ),
                            {"new_id": int(new_id)},
                        )
                    if needs_auto_increment:
                        connection.execute(
                            text(
                                "ALTER TABLE discount_code "
                                "MODIFY COLUMN DiscountCode_ID INT NOT NULL AUTO_INCREMENT"
                            )
                        )
                    connection.execute(
                        text(
                            "ALTER TABLE discount_code "
                            "MODIFY COLUMN Discount_Value DECIMAL(5,2) NOT NULL"
                        )
                    )
                    connection.execute(
                        text(
                            "ALTER TABLE discount_code "
                            "MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"
                        )
                    )
                    connection.execute(
                        text(
                            "ALTER TABLE discount_code "
                            "MODIFY COLUMN code VARCHAR(32) NOT NULL"
                        )
                    )
                    next_id = connection.execute(
                        text("SELECT COALESCE(MAX(DiscountCode_ID), 0) + 1 AS nxt FROM discount_code")
                    ).scalar() or 1
                    connection.execute(
                        text("ALTER TABLE discount_code AUTO_INCREMENT = :next_id"),
                        {"next_id": int(next_id)},
                    )
                finally:
                    if foreign_checks_disabled:
                        connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                if orders_fk_present:
                    connection.execute(
                        text(
                            "ALTER TABLE orders "
                            "ADD CONSTRAINT orders_ibfk_4 FOREIGN KEY (DiscountCode_ID) "
                            "REFERENCES discount_code (DiscountCode_ID) ON DELETE SET NULL"
                        )
                    )
        except OperationalError:
            db.session.rollback()

    def _needs_initial_seed(self) -> bool:
        inspector = inspect(db.engine)
        required_tables = ["pizzas", "menu_items", "orders"]
        for table in required_tables:
            if not inspector.has_table(table):
                return True
        try:
            existing_pizzas = db.session.execute(
                text("SELECT COUNT(*) FROM pizzas")
            ).scalar()
            db.session.commit()
            return not existing_pizzas or int(existing_pizzas) == 0
        except OperationalError:
            db.session.rollback()
            return True

    def _reset_driver_availability(self) -> None:
        try:
            db.session.execute(
                text("UPDATE delivery_person SET isAvailable = 1, unavailable_until = NULL")
            )
            db.session.commit()
        except OperationalError:
            db.session.rollback()

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
