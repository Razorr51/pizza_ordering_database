import os, re
import secrets


class AppConfig:
    def __init__(self):
        self.database_uri = self._get_database_uri()
        self.track_modifications = False
        self.echo = os.environ.get("SQL_ECHO") == "1"
        self.secret_key = self._get_secret_key()

    def _get_secret_key(self):
        return os.environ.get("SECRET_KEY", secrets.token_hex(32))

    def _get_database_uri(self):
        default_mysql = "mysql+pymysql://pizza_app:Database2025!@localhost:3306/pizza_ordering"
        if os.environ.get("SQLITE_FALLBACK") == "1":
            # Fix: Use proper SQLite URI format
            return "sqlite:///pizza_ordering.db"
        return os.environ.get("DB_URL", default_mysql)

    def get_masked_uri(self):
        return re.sub(r"//([^:]+):[^@]*@", r"//\\1:***@", self.database_uri)
