from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.gamification import AIInterview
    from app.models.user import UserSkill


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    user_skills: Mapped[List["UserSkill"]] = relationship(back_populates="skill")
    interviews: Mapped[List["AIInterview"]] = relationship(back_populates="skill")
