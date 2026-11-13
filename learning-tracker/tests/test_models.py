from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from learning_tracker.models import Course, IeltsScore, Platform, StudySession, Target


def make_course(session, **overrides):
    udemy = session.scalars(select(Platform).where(Platform.name == "Udemy")).one()
    values = dict(
        platform_id=udemy.id,
        title="Python for Data Science",
        category="Software and coding",
        total_units=40,
        unit_type="lessons",
        start_date=date(2026, 11, 1),
        target_end_date=date(2026, 12, 15),
    )
    values.update(overrides)
    course = Course(**values)
    session.add(course)
    session.commit()
    return course


def test_course_defaults(session):
    course = make_course(session)
    assert course.status == "active"
    assert course.priority == 2
    assert course.created_at is not None
    assert course.platform.name == "Udemy"


def test_course_and_sessions_relationship(session):
    course = make_course(session)
    session.add(
        StudySession(course_id=course.id, session_date=date(2026, 11, 12), minutes=45, units_done=3)
    )
    session.commit()
    assert [s.minutes for s in course.sessions] == [45]


def test_deleting_a_course_removes_its_sessions(session):
    course = make_course(session)
    session.add_all(
        [
            StudySession(course_id=course.id, session_date=date(2026, 11, d), minutes=30)
            for d in (10, 11, 12)
        ]
    )
    session.commit()

    session.delete(course)
    session.commit()

    assert session.scalars(select(StudySession)).all() == []


def test_session_for_missing_course_is_rejected(session):
    session.add(StudySession(course_id=999, session_date=date(2026, 11, 12), minutes=30))
    with pytest.raises(IntegrityError):
        session.commit()


@pytest.mark.parametrize(
    "overrides",
    [
        {"total_units": 0},
        {"unit_type": "weeks"},
        {"priority": 0},
        {"priority": 4},
        {"status": "finished"},
        {"target_end_date": date(2026, 11, 1)},  # same day as start
        {"target_end_date": date(2026, 10, 1)},  # before start
    ],
)
def test_invalid_courses_are_rejected(session, overrides):
    with pytest.raises(IntegrityError):
        make_course(session, **overrides)


@pytest.mark.parametrize("field", ["minutes", "units_done"])
def test_negative_session_values_are_rejected(session, field):
    course = make_course(session)
    values = dict(course_id=course.id, session_date=date(2026, 11, 12), minutes=30, units_done=1)
    values[field] = -1
    session.add(StudySession(**values))
    with pytest.raises(IntegrityError):
        session.commit()


def test_platform_names_are_unique(session):
    session.add(Platform(name="Udemy", colour="#000000", icon="course"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_ielts_overall_is_set_on_insert(session):
    score = IeltsScore(
        test_date=date(2026, 11, 9), listening=7, reading=6.5, writing=6, speaking=6.5
    )
    session.add(score)
    session.commit()
    assert score.overall == 6.5
    assert score.kind == "practice"


def test_ielts_overall_updates_when_a_skill_changes(session):
    score = IeltsScore(
        test_date=date(2026, 11, 9), listening=6, reading=6, writing=6, speaking=6
    )
    session.add(score)
    session.commit()
    assert score.overall == 6.0

    score.writing = 7
    session.commit()
    assert score.overall == 6.5  # average 6.25 rounds up to 6.5


@pytest.mark.parametrize("bad", [6.3, 9.5, -0.5])
def test_ielts_invalid_band_is_rejected(session, bad):
    session.add(
        IeltsScore(test_date=date(2026, 11, 9), listening=bad, reading=6, writing=6, speaking=6)
    )
    with pytest.raises(Exception):
        session.commit()


def test_ielts_kind_must_be_practice_or_real(session):
    session.add(
        IeltsScore(
            test_date=date(2026, 11, 9),
            kind="mock",
            listening=6,
            reading=6,
            writing=6,
            speaking=6,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_target_can_be_saved_without_a_due_date(session):
    session.add(Target(name="IELTS band", value="7.0"))
    session.add(Target(name="Weekly hours", value="10", due_date=date(2026, 12, 14)))
    session.commit()
    assert session.scalars(select(Target)).all()[0].due_date is None
