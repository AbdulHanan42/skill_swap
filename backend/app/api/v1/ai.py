from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.enums import InterviewType
from app.models.gamification import AIInterview
from app.models.skill import Skill
from app.models.user import User
from app.schemas.match_schema import InterviewGenerateRequest, InterviewResponse, InterviewSubmitRequest
from app.services.ai_service import AIProviderError, evaluate_answers, generate_interview, learning_suggestions

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/interview/generate")
def generate_ai_interview(
    payload: InterviewGenerateRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        interview_type = InterviewType(payload.type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interview type") from exc
    try:
        return generate_interview(current_user, interview_type, payload.question_count)
    except AIProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/interview/submit", response_model=InterviewResponse)
def submit_ai_interview(
    payload: InterviewSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIInterview:
    skill = db.get(Skill, payload.skill_id)
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    try:
        interview_type = InterviewType(payload.type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interview type") from exc

    score, feedback = evaluate_answers(payload.answers)
    interview = AIInterview(
        user_id=current_user.id,
        skill_id=skill.id,
        type=interview_type,
        score=score,
        ai_feedback=feedback,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("/suggestions")
def ai_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    scores = list(
        db.scalars(select(AIInterview.score).where(AIInterview.user_id == current_user.id)).all()
    )
    numeric_scores = [score for score in scores if score is not None]
    try:
        return learning_suggestions(current_user, numeric_scores)
    except AIProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
