from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from learning_tracker.db import get_engine, init_db, seed_platforms
from learning_tracker.models import Platform
from learning_tracker.seed import PLATFORMS


def test_database_creates_itself(tmp_path):
    db_file = tmp_path / "nested" / "new.db"
    assert not db_file.exists()

    init_db(get_engine(f"sqlite:///{db_file}"))

    assert db_file.exists()


def test_all_tables_are_created(engine):
    tables = set(inspect(engine).get_table_names())
    assert {"platforms", "courses", "sessions", "ielts_scores", "targets"} <= tables


def test_seven_platforms_are_seeded(session):
    names = list(session.scalars(select(Platform.name).order_by(Platform.id)))
    assert names == [
        "Udemy",
        "Coursera",
        "Treehouse",
        "YouTube",
        "Mimo",
        "IELTS",
        "French",
    ]


def test_seeding_twice_adds_nothing(engine):
    init_db(engine)
    init_db(engine)
    with Session(engine) as s:
        assert len(list(s.scalars(select(Platform)))) == len(PLATFORMS)


def test_seeding_fills_a_missing_platform_only(engine):
    with Session(engine) as s:
        s.delete(s.scalars(select(Platform).where(Platform.name == "Mimo")).one())
        s.commit()
        assert seed_platforms(s) == 1
        assert len(list(s.scalars(select(Platform)))) == len(PLATFORMS)


def test_foreign_keys_are_switched_on(engine):
    with engine.connect() as conn:
        assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
