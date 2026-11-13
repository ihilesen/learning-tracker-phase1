import pytest
from sqlalchemy.orm import Session

from learning_tracker.db import init_db, get_engine


@pytest.fixture
def engine(tmp_path):
    """A fresh database file for each test."""
    url = f"sqlite:///{tmp_path / 'test.db'}"
    return init_db(get_engine(url))


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s
