from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Proficiency, SkillType

if TYPE_CHECKING:
    from app.models.chat import Message
    from app.models.gamification import AIInterview, ProgressTracking
    from app.models.match import Match
    from app.models.skill import Skill


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    skills: Mapped[List["UserSkill"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sent_messages: Mapped[List["Message"]] = relationship(back_populates="sender")
    interviews: Mapped[List["AIInterview"]] = relationship(back_populates="user")
    progress: Mapped[List["ProgressTracking"]] = relationship(back_populates="user")
    matches_as_a: Mapped[List["Match"]] = relationship(
        back_populates="user_a", foreign_keys="Match.user_a_id"
    )
    matches_as_b: Mapped[List["Match"]] = relationship(
        back_populates="user_b", foreign_keys="Match.user_b_id"
    )


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", "skill_type", name="uq_user_skill_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    skill_type: Mapped[SkillType] = mapped_column(Enum(SkillType, name="skill_type"), nullable=False)
    proficiency: Mapped[Proficiency] = mapped_column(
        Enum(Proficiency, name="proficiency"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="user_skills")
