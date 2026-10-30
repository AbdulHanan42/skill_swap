from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, get_db
from app.db.database import SessionLocal
from app.models.enums import MatchStatus, SessionStatus, SkillType
from app.models.gamification import ProgressTracking
from app.models.match import LearningSession, Match
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.schemas.chat_schema import ChatHistoryResponse, MessageResponse
from app.schemas.match_schema import (
    MatchResponse,
    MatchSuggestion,
    SessionCreate,
    SessionResponse,
    SwapRequestItem,
)
from app.services.match_engine import calculate_match_score, find_suggestions

router = APIRouter(tags=["matches"])


def _ordered_pair(user_id: int, target_id: int) -> tuple[int, int]:
    return (user_id, target_id) if user_id < target_id else (target_id, user_id)


def _peer_of(match: Match, user_id: int) -> User:
    return match.user_b if match.user_a_id == user_id else match.user_a


def _get_match_or_404(db: Session, match_id: int, user: User) -> Match:
    match = db.scalar(
        select(Match)
        .options(
            selectinload(Match.messages),
            selectinload(Match.user_a),
            selectinload(Match.user_b),
        )
        .where(Match.id == match_id)
    )
    if match is None or user.id not in {match.user_a_id, match.user_b_id}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return match


def _skill_names(db: Session, user_ids: set[int]) -> dict[int, tuple[list[str], list[str]]]:
    """Offered and wanted skill names per user, in one query."""
    index = {user_id: (set(), set()) for user_id in user_ids}
    if not user_ids:
        return {}
    rows = db.execute(
        select(UserSkill.user_id, UserSkill.skill_type, Skill.name)
        .join(Skill, Skill.id == UserSkill.skill_id)
        .where(UserSkill.user_id.in_(user_ids))
    ).all()
    for user_id, skill_type, name in rows:
        bucket = 0 if skill_type == SkillType.OFFERS else 1
        index[user_id][bucket].add(name)
    return {
        user_id: (sorted(offers), sorted(wants))
        for user_id, (offers, wants) in index.items()
    }


def _request_items(
    db: Session, matches: list[Match], current_user: User
) -> list[SwapRequestItem]:
    names = _skill_names(
        db, {match.user_a_id for match in matches} | {match.user_b_id for match in matches}
    )
    items = []
    for match in matches:
        peer = _peer_of(match, current_user.id)
        offers, wants = names.get(peer.id, ([], []))
        items.append(
            SwapRequestItem(
                match_id=match.id,
                status=match.status,
                match_score=match.match_score,
                requested_at=match.matched_at,
                is_mine=match.requested_by_id == current_user.id,
                peer_id=peer.id,
                peer_name=peer.full_name,
                peer_designation=peer.designation,
                peer_bio=peer.bio,
                peer_avatar=peer.avatar,
                offers=offers,
                wants=wants,
            )
        )
    return items


def _request_states(db: Session, user: User) -> dict[int, str]:
    """Who owes whom, per peer — lets Skill Matching lock its request button."""
    matches = db.scalars(
        select(Match).where(or_(Match.user_a_id == user.id, Match.user_b_id == user.id))
    ).all()
    states: dict[int, str] = {}
    for match in matches:
        peer_id = match.user_b_id if match.user_a_id == user.id else match.user_a_id
        if match.status == MatchStatus.ACCEPTED:
            states[peer_id] = "connected"
        elif match.status == MatchStatus.PENDING and match.requested_by_id is not None:
            states[peer_id] = (
                "requested_by_me"
                if match.requested_by_id == user.id
                else "requested_by_them"
            )
    return states


@router.get("/matches/suggestions", response_model=list[MatchSuggestion])
def match_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchSuggestion]:
    raw = find_suggestions(db, current_user)
    states = _request_states(db, current_user)
    return [
        MatchSuggestion(
            user=item["user"],
            match_score=item["match_score"],
            overlapping_offers=item["overlapping_offers"],
            overlapping_wants=item["overlapping_wants"],
            request_state=states.get(item["user"].id, "available"),
        )
        for item in raw
    ]


@router.post(
    "/matches/request/{target_user_id}",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_match(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Match:
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot match with yourself"
        )

    target = db.get(User, target_user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_a_id, user_b_id = _ordered_pair(current_user.id, target_user_id)
    existing = db.scalar(
        select(Match).where(Match.user_a_id == user_a_id, Match.user_b_id == user_b_id)
    )
    if existing:
        if existing.status == MatchStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already connected with this user",
            )
        if existing.status == MatchStatus.REJECTED or existing.requested_by_id is None:
            # Re-sending a declined request reopens it, and a pending row that was
            # never attributed to a sender is claimed here — while it belongs to
            # nobody the receiver's inbox stays empty.
            score, _, _ = calculate_match_score(current_user, target)
            existing.status = MatchStatus.PENDING
            existing.match_score = score
            existing.requested_by_id = current_user.id
            existing.matched_at = datetime.now(timezone.utc)
            db.add(existing)
            db.commit()
            db.refresh(existing)
        return existing

    score, _, _ = calculate_match_score(current_user, target)
    match = Match(
        user_a_id=user_a_id,
        user_b_id=user_b_id,
        status=MatchStatus.PENDING,
        match_score=score,
        requested_by_id=current_user.id,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def _pending_requests(db: Session, user: User, *, mine: bool) -> list[Match]:
    stmt = (
        select(Match)
        .options(selectinload(Match.user_a), selectinload(Match.user_b))
        .where(
            Match.status == MatchStatus.PENDING,
            or_(Match.user_a_id == user.id, Match.user_b_id == user.id),
        )
    )
    if mine:
        stmt = stmt.where(Match.requested_by_id == user.id)
    else:
        stmt = stmt.where(
            Match.requested_by_id.is_not(None), Match.requested_by_id != user.id
        )
    return list(db.scalars(stmt.order_by(Match.matched_at.desc())))


@router.get("/matches/requests/pending", response_model=list[SwapRequestItem])
def incoming_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SwapRequestItem]:
    return _request_items(db, _pending_requests(db, current_user, mine=False), current_user)


@router.get("/matches/requests/sent", response_model=list[SwapRequestItem])
def sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SwapRequestItem]:
    return _request_items(db, _pending_requests(db, current_user, mine=True), current_user)


def _answerable_request(db: Session, match_id: int, user: User) -> Match:
    match = _get_match_or_404(db, match_id, user)
    if match.status != MatchStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been answered",
        )
    if match.requested_by_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only answer requests sent to you",
        )
    return match


@router.put("/matches/requests/{match_id}/accept", response_model=SwapRequestItem)
def accept_request(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SwapRequestItem:
    match = _answerable_request(db, match_id, current_user)
    match.status = MatchStatus.ACCEPTED
    db.add(match)
    db.commit()
    return _request_items(db, [match], current_user)[0]


@router.put("/matches/requests/{match_id}/decline", response_model=SwapRequestItem)
def decline_request(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SwapRequestItem:
    match = _answerable_request(db, match_id, current_user)
    match.status = MatchStatus.REJECTED
    db.add(match)
    db.commit()
    return _request_items(db, [match], current_user)[0]


@router.get("/matches/{match_id}", response_model=SwapRequestItem)
def match_detail(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SwapRequestItem:
    match = _get_match_or_404(db, match_id, current_user)
    return _request_items(db, [match], current_user)[0]


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


@router.post(
    "/sessions/schedule",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def schedule_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LearningSession:
    match = _get_match_or_404(db, payload.match_id, current_user)
    if match.status != MatchStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Match must be accepted"
        )

    session = LearningSession(
        match_id=match.id,
        scheduled_for=payload.scheduled_for,
        meeting_link=payload.meeting_link,
        duration_minutes=payload.duration_minutes,
        status=SessionStatus.SCHEDULED,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _complete_progress(user_id: int) -> None:
    db = SessionLocal()
    try:
        progress = db.scalar(
            select(ProgressTracking).where(ProgressTracking.user_id == user_id)
        )
        if progress is None:
            progress = ProgressTracking(
                user_id=user_id, completed_swaps=0, total_points=0
            )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    _get_match_or_404(db, session.match_id, current_user)
    already_completed = session.status == SessionStatus.COMPLETED
    if not already_completed:
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
    db.add(session)
    db.commit()
    db.refresh(session)
    if not already_completed:
        background_tasks.add_task(_complete_progress, current_user.id)
    return session
