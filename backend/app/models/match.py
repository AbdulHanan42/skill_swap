from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MatchStatus, SessionStatus

if TYPE_CHECKING:
    from app.models.chat import Message
    from app.models.user import User


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id", name="uq_match_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_a_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_b_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"),
        default=MatchStatus.PENDING,
        nullable=False,
    )
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_a: Mapped["User"] = relationship(foreign_keys=[user_a_id])
    user_b: Mapped["User"] = relationship(foreign_keys=[user_b_id])
    messages: Mapped[list["Message"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )
    learning_sessions: Mapped[list["LearningSession"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"),
        default=SessionStatus.SCHEDULED,
        nullable=False,
    )

    match: Mapped["Match"] = relationship(back_populates="learning_sessions")
