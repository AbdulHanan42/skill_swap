from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InterviewSubmission(BaseModel):
    filename: str
    size: int
    mime_type: str | None = None


class InterviewQuestion(BaseModel):
    id: int
    index: int
    total: int
    prompt: str
    options: list[str]
    answered: int


class InterviewTask(BaseModel):
    title: str
    brief: str
    requirements: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    brief_filename: str
    accepted: list[str] = Field(default_factory=list)
    max_upload_mb: int
    submission: InterviewSubmission | None = None


class InterviewReview(BaseModel):
    prompt: str
    family: str
    options: list[str]
    selected: int | None = None
    answer_index: int | None = None
    correct: bool | None = None
    explanation: str = ""
    skipped: bool = False


class InterviewSkillScore(BaseModel):
    skill: str
    correct: int
    total: int


class InterviewResult(BaseModel):
    score: float
    grade: str
    correct: int
    total: int
    skipped: int
    feedback: str
    review: list[InterviewReview] = Field(default_factory=list)
    per_skill: list[InterviewSkillScore] = Field(default_factory=list)
    submission: InterviewSubmission | None = None
    graded_by: str
    completed_at: datetime | None = None


class InterviewStatus(BaseModel):
    """Everything the wizard needs to render one screen, resumable at any step."""

    state: str
    step: int
    skills: list[str] = Field(default_factory=list)
    total_questions: int = 0
    answered: int = 0
    question: InterviewQuestion | None = None
    task: InterviewTask | None = None
    result: InterviewResult | None = None
    source: str = "local-bank"


class InterviewAnswerSubmit(BaseModel):
    question_id: int
    selected_option: int | str


class InterviewSkipSubmit(BaseModel):
    question_id: int
