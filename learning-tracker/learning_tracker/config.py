"""Settings read from the environment, with safe local defaults."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Set LEARNING_TRACKER_DB to a full SQLAlchemy URL to use another database.
# In the cloud this will point at Postgres. Secrets never go in the code.
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "learning_tracker.db"


def database_url() -> str:
    """Return the database URL, defaulting to a local SQLite file."""
    return os.environ.get("LEARNING_TRACKER_DB", f"sqlite:///{DEFAULT_DB_PATH}")
