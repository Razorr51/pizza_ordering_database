from pathlib import Path
from sqlalchemy.exc import OperationalError
from app.integration.models import db

class DatabaseManager:
    def __init__(self, app):
        self.app = app

    def execute_sql_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        for stmt in [s.strip() for s in sql_script.split(";") if s.strip()]:
            db.session.execute(db.text(stmt))
        db.session.commit()

    def setup_schema(self):
        try:
            base = Path(self.app.root_path)
            view_path = base / "integration" / "sql" / "views.sql"
            seed_path = base / "integration" / "sql" / "seed_min.sql"
            if view_path.exists():
                self.execute_sql_file(view_path)
            if seed_path.exists():
                self.execute_sql_file(seed_path)
        except OperationalError as e:
            self.app.logger.error("Database setup failed: %s", e)
            raise
