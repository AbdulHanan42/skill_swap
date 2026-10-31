from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import Proficiency, SkillType


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    bio: str | None = None
    designation: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    designation: str | None = None
    avatar: str | None = None

    @field_validator("avatar")
    @classmethod
    def _avatar_size(cls, value: str | None) -> str | None:
        if value and len(value) > 2_000_000:
            raise ValueError("Avatar image is too large (max ~1.5 MB)")
        return value


class UserSkillCreate(BaseModel):
    skill_id: int
    skill_type: SkillType
    proficiency: Proficiency


class UserSkillBulkCreate(BaseModel):
    skills: list[UserSkillCreate]


class UserSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_id: int
    skill_type: SkillType
    proficiency: Proficiency


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    bio: str | None = None
    designation: str | None = None
    avatar: str | None = None
    created_at: datetime
    skills: list[UserSkillResponse] = Field(default_factory=list)


class DashboardOverview(BaseModel):
    profile_completeness: float
    active_matches: int
    unread_notifications: int
