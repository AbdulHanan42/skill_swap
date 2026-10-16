from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, get_db
from app.db.database import SessionLocal
from app.models.enums import MatchStatus, SessionStatus
from app.models.gamification import ProgressTracking
from app.models.match import LearningSession, Match
from app.models.user import User
from app.schemas.chat_schema import ChatHistoryResponse, MessageResponse
from app.schemas.match_schema import (
    MatchResponse,
    MatchSuggestion,
    SessionCreate,
    SessionResponse,
)
from app.services.match_engine import calculate_match_score, find_suggestions

router = APIRouter(tags=["matches"])


def _ordered_pair(user_id: int, target_id: int) -> tuple[int, int]:
    return (user_id, target_id) if user_id < target_id else (target_id, user_id)


def _get_match_or_404(db: Session, match_id: int, user: User) -> Match:
    match = db.scalar(
        select(Match).options(selectinload(Match.messages)).where(Match.id == match_id)
    )
    if match is None or user.id not in {match.user_a_id, match.user_b_id}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.get("/matches/suggestions", response_model=list[MatchSuggestion])
def match_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchSuggestion]:
    raw = find_suggestions(db, current_user)
    return [
        MatchSuggestion(
            user=item["user"],
            match_score=item["match_score"],
            overlapping_offers=item["overlapping_offers"],
            overlapping_wants=item["overlapping_wants"],
        )
        for item in raw
    ]


@router.post("/matches/request/{target_user_id}", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def request_match(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Match:
    if target_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot match with yourself")

    target = db.get(User, target_user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_a_id, user_b_id = _ordered_pair(current_user.id, target_user_id)
    existing = db.scalar(
        select(Match).where(Match.user_a_id == user_a_id, Match.user_b_id == user_b_id)
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Match already exists")

    score, _, _ = calculate_match_score(current_user, target)
    match = Match(
        user_a_id=user_a_id,
        user_b_id=user_b_id,
        status=MatchStatus.PENDING,
        match_score=score,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.patch("/matches/{match_id}/accept", response_model=MatchResponse)
def accept_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Match:
    match = _get_match_or_404(db, match_id, current_user)
    match.status = MatchStatus.ACCEPTED
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("/chat/{match_id}/history", response_model=ChatHistoryResponse)
def chat_history(
    match_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatHistoryResponse:
    match = _get_match_or_404(db, match_id, current_user)
    messages = sorted(match.messages, key=lambda item: item.sent_at)
    start = (page - 1) * page_size
    end = start + page_size
    items = messages[start:end]
    return ChatHistoryResponse(
        items=[MessageResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=len(messages),
    )


@router.post("/sessions/schedule", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def schedule_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LearningSession:
    match = _get_match_or_404(db, payload.match_id, current_user)
    if match.status != MatchStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match must be accepted")

    session = LearningSession(
        match_id=match.id,
        scheduled_for=payload.scheduled_for,
        meeting_link=payload.meeting_link,
        status=SessionStatus.SCHEDULED,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _complete_progress(user_id: int) -> None:
    db = SessionLocal()
    try:
        progress = db.scalar(select(ProgressTracking).where(ProgressTracking.user_id == user_id))
        if progress is None:
            progress = ProgressTracking(user_id=user_id, completed_swaps=0, total_points=0)
            db.add(progress)
        progress.completed_swaps += 1
        progress.total_points += 10
        if progress.completed_swaps >= 5:
            progress.badge_name = "Skill Swapper"
        db.commit()
    finally:
        db.close()


@router.post("/sessions/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LearningSession:
    session = db.get(LearningSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    _get_match_or_404(db, session.match_id, current_user)
    session.status = SessionStatus.COMPLETED
    db.add(session)
    db.commit()
    db.refresh(session)
    background_tasks.add_task(_complete_progress, current_user.id)
    return session
