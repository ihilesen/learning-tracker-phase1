"""Database setup: engine, sessions, self-creating tables and seed data.

Run `python -m learning_tracker.db` to create the database and print a
short summary. It is safe to run as often as you like.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine, create_engine, event, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from . import config
from .models import Base, Platform
from .seed import PLATFORMS


def get_engine(url: str | None = None) -> Engine:
    """Build an engine. SQLite gets foreign keys switched on."""
    url = url or config.database_url()
    parsed = make_url(url)

    if parsed.get_backend_name() == "sqlite" and parsed.database not in (None, "", ":memory:"):
        # Create the data folder on first run.
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(url)

    if parsed.get_backend_name() == "sqlite":
        # SQLite ignores foreign keys unless asked on every connection.
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def seed_platforms(session: Session) -> int:
    """Add any missing platforms. Returns how many were added."""
    existing = set(session.scalars(select(Platform.name)))
    added = 0
    for name, colour, icon in PLATFORMS:
        if name not in existing:
            session.add(Platform(name=name, colour=colour, icon=icon))
            added += 1
    session.commit()
    return added


def init_db(engine: Engine | None = None) -> Engine:
    """Create all tables and seed the platforms. Safe to run repeatedly."""
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_platforms(session)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    """Open a session, commit on success, roll back on error."""
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    engine = init_db()
    with Session(engine) as session:
        names = list(session.scalars(select(Platform.name).order_by(Platform.id)))
    print(f"Database ready at {engine.url.render_as_string(hide_password=True)}")
    print(f"Platforms ({len(names)}): {', '.join(names)}")


if __name__ == "__main__":
    main()
