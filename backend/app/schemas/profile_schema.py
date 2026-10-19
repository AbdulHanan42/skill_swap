from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Proficiency, SkillType


class UserSkillAdd(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, max_length=100)
    skill_type: SkillType
    proficiency: Proficiency


class ProfileUpdate(BaseModel):
    bio: Optional[str] = Field(default=None, max_length=2000)
    designation: Optional[str] = Field(default=None, max_length=255)


class AddedSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_id: int
    skill_type: SkillType
    proficiency: Proficiency


class AddedSkillResult(BaseModel):
    message: str
    skill: AddedSkillResponse
