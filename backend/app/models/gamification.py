from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InterviewType

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.user import User


class AIInterview(Base):
    __tablename__ = "ai_interviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[InterviewType] = mapped_column(Enum(InterviewType, name="interview_type"), nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="interviews")
    skill: Mapped["Skill"] = relationship(back_populates="interviews")


class ProgressTracking(Base):
    __tablename__ = "progress_tracking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    completed_swaps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="progress")
