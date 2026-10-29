from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MatchStatus, SessionStatus
from app.schemas.user_schema import UserResponse


class MatchSuggestion(BaseModel):
    user: UserResponse
    match_score: float
    overlapping_offers: list[str] = []
    overlapping_wants: list[str] = []


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_a_id: int
    user_b_id: int
    status: MatchStatus
    match_score: float | None = None
    requested_by_id: int | None = None
    matched_at: datetime


class SessionCreate(BaseModel):
    match_id: int
    scheduled_for: datetime
    meeting_link: str | None = None
    duration_minutes: int = Field(default=60, ge=5, le=480)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    scheduled_for: datetime
    meeting_link: str | None = None
    duration_minutes: int
    completed_at: datetime | None = None
    status: SessionStatus


class InterviewGenerateRequest(BaseModel):
    skill_id: int | None = None
    skill_name: str | None = Field(default=None, min_length=1, max_length=100)
    type: str = "MCQ"
    proficiency: str = "Beginner"
    question_count: int = Field(default=3, ge=1, le=10)


class InterviewAnswer(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    answer: str = Field(min_length=1, max_length=4000)


class InterviewSubmitRequest(BaseModel):
    skill_id: int | None = None
    skill_name: str | None = Field(default=None, min_length=1, max_length=100)
    type: str = "MCQ"
    answers: list[InterviewAnswer] = Field(default_factory=list)
    qa_pairs: list[InterviewAnswer] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    skill_id: int
    type: str
    score: float | None = None
    ai_feedback: str | None = None
    taken_at: datetime


class ProgressResponse(BaseModel):
    user_name: str
    badge: str
    total_skills_listed: int
    successful_swaps: int
    ai_interview_average: float
    badge_name: str | None = None
    completed_swaps: int = 0
    total_points: int = 0


class ActivityPoint(BaseModel):
    date: str
    label: str
    hours: float


class SkillMasteryItem(BaseModel):
    skill_name: str
    proficiency: str
    percent: int
    verified: bool


class BadgeItem(BaseModel):
    key: str
    name: str
    description: str
    unlocked: bool
    progress: float


class CompletedSessionItem(BaseModel):
    id: int
    subject: str
    peer_name: str
    completed_at: datetime
    hours: float


class ProgressDashboard(BaseModel):
    user_name: str
    badge: str
    swap_hours: float
    swap_hours_delta: float | None = None
    skill_twins: int
    active_streak_days: int
    ai_interview_average: float
    ai_interview_count: int
    ai_grade: str
    total_skills_listed: int
    successful_swaps: int
    completed_sessions_total: int
    weekly_activity: list[ActivityPoint]
    skill_mastery: list[SkillMasteryItem]
    badges: list[BadgeItem]
    completed_sessions: list[CompletedSessionItem]
