"""Configuration helpers for the pizza ordering application."""

import os, re
import secrets


class AppConfig:
    """Load application settings"""

    def __init__(self):
        """Initialize config values when the app starts."""
        self.database_uri = self._get_database_uri()
        self.track_modifications = False
        self.echo = os.environ.get("SQL_ECHO") == "1"
        self.secret_key = self._get_secret_key()
        self.reset_db_on_startup = os.environ.get("RESET_DB_ON_STARTUP", "0") == "1"

    def _get_secret_key(self):
        """Return a configured secret key"""
        return os.environ.get("SECRET_KEY", secrets.token_hex(32))

    def _get_database_uri(self):
        """Determine which database connection string the app should use."""
        default_mysql = "mysql+pymysql://pizza_app:Database2025!@localhost:3306/pizza_ordering"
        if os.environ.get("SQLITE_FALLBACK") == "1":
            return "sqlite:///pizza_ordering.db"
        return os.environ.get("DB_URL", default_mysql)

    def get_masked_uri(self):
        """Return the database URI with the right credentials"""
        return re.sub(r"//([^:]+):[^@]*@", r"//\\1:***@", self.database_uri)
