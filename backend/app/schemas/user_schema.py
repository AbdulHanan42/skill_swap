from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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
    created_at: datetime
    skills: list[UserSkillResponse] = Field(default_factory=list)


class DashboardOverview(BaseModel):
    profile_completeness: float
    active_matches: int
    unread_notifications: int
