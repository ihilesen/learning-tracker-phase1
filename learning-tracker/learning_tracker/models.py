"""Database models for the Learning Tracker.

These follow the backend schema in the planning pack. Progress, streaks and
weekly hours are never stored: they are calculated from sessions so they
cannot drift out of date.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .ielts import ielts_overall


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Platform(Base):
    """Where a course lives, for example Udemy or IELTS."""

    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    colour: Mapped[str] = mapped_column(String(7))
    icon: Mapped[str] = mapped_column(String(30))

    courses: Mapped[list["Course"]] = relationship(back_populates="platform")

    def __repr__(self) -> str:
        return f"<Platform {self.name}>"


class Course(Base):
    """One thing you are learning."""

    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("total_units > 0", name="ck_courses_total_units_positive"),
        CheckConstraint(
            "unit_type IN ('lessons', 'hours')", name="ck_courses_unit_type"
        ),
        CheckConstraint(
            "target_end_date > start_date", name="ck_courses_end_after_start"
        ),
        CheckConstraint(
            "priority BETWEEN 1 AND 3", name="ck_courses_priority_range"
        ),
        CheckConstraint(
            "status IN ('active', 'paused', 'done')", name="ck_courses_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"))
    title: Mapped[str] = mapped_column(String(200))
    # A plain text heading for now. Phase 2 replaces it with categories.
    category: Mapped[str | None] = mapped_column(String(80), default=None)
    total_units: Mapped[float] = mapped_column(Float)
    unit_type: Mapped[str] = mapped_column(String(10), default="lessons")
    start_date: Mapped[date] = mapped_column(Date)
    target_end_date: Mapped[date] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(Integer, default=2)
    status: Mapped[str] = mapped_column(String(10), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    platform: Mapped[Platform] = relationship(back_populates="courses")
    # Deleting a course removes its sessions, as the pack specifies.
    sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Course {self.title}>"


class StudySession(Base):
    """One block of study on one day."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("minutes >= 0", name="ck_sessions_minutes_not_negative"),
        CheckConstraint(
            "units_done >= 0", name="ck_sessions_units_done_not_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE")
    )
    session_date: Mapped[date] = mapped_column(Date)
    minutes: Mapped[int] = mapped_column(Integer)
    units_done: Mapped[float] = mapped_column(Float, default=0)
    note: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    course: Mapped[Course] = relationship(back_populates="sessions")


_BAND_CHECK = "{col} BETWEEN 0 AND 9 AND {col} * 2 = CAST({col} * 2 AS INTEGER)"


class IeltsScore(Base):
    """A practice or real IELTS result. Overall is set automatically."""

    __tablename__ = "ielts_scores"
    __table_args__ = (
        CheckConstraint("kind IN ('practice', 'real')", name="ck_ielts_kind"),
        CheckConstraint(_BAND_CHECK.format(col="listening"), name="ck_ielts_listening"),
        CheckConstraint(_BAND_CHECK.format(col="reading"), name="ck_ielts_reading"),
        CheckConstraint(_BAND_CHECK.format(col="writing"), name="ck_ielts_writing"),
        CheckConstraint(_BAND_CHECK.format(col="speaking"), name="ck_ielts_speaking"),
        CheckConstraint(_BAND_CHECK.format(col="overall"), name="ck_ielts_overall"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    test_date: Mapped[date] = mapped_column(Date)
    kind: Mapped[str] = mapped_column(String(10), default="practice")
    listening: Mapped[float] = mapped_column(Float)
    reading: Mapped[float] = mapped_column(Float)
    writing: Mapped[float] = mapped_column(Float)
    speaking: Mapped[float] = mapped_column(Float)
    overall: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


@event.listens_for(IeltsScore, "before_insert")
@event.listens_for(IeltsScore, "before_update")
def _set_overall(mapper, connection, target: IeltsScore) -> None:
    """Keep overall equal to the rounded average of the four skills."""
    target.overall = ielts_overall(
        target.listening, target.reading, target.writing, target.speaking
    )


class Target(Base):
    """A goal, such as weekly hours or an IELTS band."""

    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(String(40))
    due_date: Mapped[date | None] = mapped_column(Date, default=None)
