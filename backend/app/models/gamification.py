from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InterviewType

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.user import User


class AIInterview(Base):
    __tablename__ = "ai_interviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[InterviewType] = mapped_column(
        Enum(InterviewType, name="interview_type"), nullable=False
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship()
    skill: Mapped["Skill"] = relationship()


class ProgressTracking(Base):
    __tablename__ = "progress_tracking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    badge_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    completed_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship()


class InterviewSession(Base):
    """One sitting of the three-step interview, so a reload can resume it."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # in_progress -> submitted; a submitted row is kept for the audit trail.
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skill_names: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # Questions keep their answer key here only — the API strips it before it ships.
    questions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    task_key: Mapped[str] = mapped_column(String(40), default="general", nullable=False)
    task_title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    task_brief: Mapped[str] = mapped_column(Text, default="", nullable=False)
    submission_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    submission_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submission_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submission_mime: Mapped[str | None] = mapped_column(String(255), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Which engine produced the score, so the UI can say where the analysis came from.
    graded_by: Mapped[str | None] = mapped_column(String(60), nullable=True)
    interview_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_interviews.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship()
    interview: Mapped["AIInterview | None"] = relationship()
