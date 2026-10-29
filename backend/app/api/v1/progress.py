from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.enums import MatchStatus, SessionStatus, SkillType
from app.models.gamification import AIInterview, ProgressTracking
from app.models.match import LearningSession, Match
from app.models.user import User, UserSkill
from app.schemas.match_schema import (
    ActivityPoint,
    BadgeItem,
    CompletedSessionItem,
    ProgressDashboard,
    ProgressResponse,
    SkillMasteryItem,
)

router = APIRouter(tags=["progress"])

PROFICIENCY_BASELINE = {"Beginner": 35, "Intermediate": 65, "Expert": 90}


def _grade(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "E"


def _completed_sessions(db: Session, user_id: int) -> list[tuple[LearningSession, Match]]:
    rows = db.execute(
        select(LearningSession, Match)
        .join(Match, LearningSession.match_id == Match.id)
        .options(selectinload(Match.user_a), selectinload(Match.user_b))
        .where(
            Match.status == MatchStatus.ACCEPTED,
            or_(Match.user_a_id == user_id, Match.user_b_id == user_id),
            LearningSession.status == SessionStatus.COMPLETED,
        )
        .order_by(LearningSession.scheduled_for.asc())
    ).all()
    return list(rows)


def _when(session: LearningSession) -> datetime:
    value = session.completed_at or session.scheduled_for
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _streak(days: set[date], today: date) -> int:
    if not days:
        return 0
    cursor = today if today in days else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


def _subject(user: User, peer: User) -> str:
    peer_offers = {
        item.skill.name
        for item in peer.skills
        if item.skill_type == SkillType.OFFERS and item.skill
    }
    wanted = {
        item.skill.name
        for item in user.skills
        if item.skill_type == SkillType.WANTS and item.skill
    }
    shared = sorted(peer_offers & wanted)
    if shared:
        return shared[0]
    remaining = sorted(peer_offers) or sorted(
        {item.skill.name for item in peer.skills if item.skill}
    )
    return remaining[0] if remaining else "Skill swap session"


def _badges(
    *, swaps: int, sessions: int, streak: int, average: float
) -> list[BadgeItem]:
    ladder = [
        ("active_swapper", "Active Swapper", "1 successful swap", swaps, 1),
        ("knowledge_giver", "Knowledge Giver", "3 completed sessions", sessions, 3),
        ("skill_master", "Skill Master", "5 successful swaps", swaps, 5),
        ("deep_learner", "Deep Learner", "80+ interview average", average, 80),
        ("continuous_learner", "Continuous Learner", "7 day streak", streak, 7),
    ]
    return [
        BadgeItem(
            key=key,
            name=name,
            description=goal,
            unlocked=value >= target,
            progress=round(min(value / target, 1) * 100, 1),
        )
        for key, name, goal, value, target in ladder
    ]


@router.get("/progress/dashboard", response_model=ProgressDashboard)
def read_progress_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressDashboard:
    completed = _completed_sessions(db, current_user.id)
    today = datetime.now(timezone.utc).date()

    hours_by_day: dict[date, float] = defaultdict(float)
    for session, _match in completed:
        hours_by_day[_when(session).date()] += session.duration_minutes / 60

    swap_hours = round(sum(hours_by_day.values()), 2)
    week_start = today - timedelta(days=6)
    current_week = round(
        sum(h for d, h in hours_by_day.items() if d >= week_start), 2
    )
    previous_week = round(
        sum(
            h
            for d, h in hours_by_day.items()
            if week_start - timedelta(days=7) <= d < week_start
        ),
        2,
    )
    delta = (
        round(((current_week - previous_week) / previous_week) * 100, 1)
        if previous_week > 0
        else None
    )

    weekly_activity = [
        ActivityPoint(
            date=day.isoformat(),
            label=day.strftime("%a"),
            hours=round(hours_by_day.get(day, 0.0), 2),
        )
        for day in (week_start + timedelta(days=offset) for offset in range(7))
    ]

    interviews = db.scalars(
        select(AIInterview)
        .where(AIInterview.user_id == current_user.id, AIInterview.score.isnot(None))
        .order_by(AIInterview.taken_at.desc())
    ).all()
    scores = [interview.score or 0.0 for interview in interviews]
    interview_count = len(scores)
    average = round(sum(scores) / interview_count, 1) if interview_count else 0.0

    latest_score_by_skill: dict[int, float] = {}
    for interview in interviews:
        latest_score_by_skill.setdefault(interview.skill_id, interview.score or 0.0)

    mastery: dict[str, SkillMasteryItem] = {}
    for item in current_user.skills:
        if item.skill is None:
            continue
        verified_score = latest_score_by_skill.get(item.skill_id)
        percent = (
            round(verified_score)
            if verified_score is not None
            else PROFICIENCY_BASELINE[item.proficiency.value]
        )
        candidate = SkillMasteryItem(
            skill_name=item.skill.name,
            proficiency=item.proficiency.value,
            percent=percent,
            verified=verified_score is not None,
        )
        existing = mastery.get(item.skill.name)
        if existing is None or candidate.percent > existing.percent:
            mastery[item.skill.name] = candidate
    mastery_rows = sorted(
        mastery.values(), key=lambda row: row.percent, reverse=True
    )[:6]

    accepted_matches = db.scalars(
        select(Match)
        .options(selectinload(Match.user_a), selectinload(Match.user_b))
        .where(
            Match.status == MatchStatus.ACCEPTED,
            or_(
                Match.user_a_id == current_user.id,
                Match.user_b_id == current_user.id,
            ),
        )
    ).all()

    completed_rows = [
        CompletedSessionItem(
            id=session.id,
            subject=_subject(
                current_user,
                match.user_b if match.user_a_id == current_user.id else match.user_a,
            ),
            peer_name=(
                match.user_b.full_name
                if match.user_a_id == current_user.id
                else match.user_a.full_name
            ),
            completed_at=_when(session),
            hours=round(session.duration_minutes / 60, 2),
        )
        for session, match in sorted(completed, key=lambda pair: _when(pair[0]))[::-1]
    ][:5]

    total_skills = db.scalar(
        select(func.count(UserSkill.id)).where(UserSkill.user_id == current_user.id)
    )
    streak_days = _streak(set(hours_by_day), today)

    return ProgressDashboard(
        user_name=current_user.full_name,
        badge=(
            "Skill Master"
            if len(accepted_matches) >= 5
            else "Active Swapper"
            if accepted_matches
            else "Novice Learner"
        ),
        swap_hours=swap_hours,
        swap_hours_delta=delta,
        skill_twins=len(accepted_matches),
        active_streak_days=streak_days,
        ai_interview_average=average,
        ai_interview_count=interview_count,
        ai_grade=_grade(average) if interview_count else "",
        total_skills_listed=total_skills or 0,
        successful_swaps=len(accepted_matches),
        completed_sessions_total=len(completed),
        weekly_activity=weekly_activity,
        skill_mastery=mastery_rows,
        badges=_badges(
            swaps=len(accepted_matches),
            sessions=len(completed),
            streak=streak_days,
            average=average,
        ),
        completed_sessions=completed_rows,
    )


@router.get("/progress/me", response_model=ProgressResponse)
def read_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    progress = db.scalar(
        select(ProgressTracking).where(ProgressTracking.user_id == current_user.id)
    )
    total_skills = (
        db.scalar(
            select(func.count(UserSkill.id)).where(UserSkill.user_id == current_user.id)
        )
        or 0
    )
    successful_swaps = (
        db.scalar(
            select(func.count(Match.id)).where(
                Match.status == MatchStatus.ACCEPTED,
                or_(
                    Match.user_a_id == current_user.id,
                    Match.user_b_id == current_user.id,
                ),
            )
        )
        or 0
    )
    average_score = (
        db.scalar(
            select(func.avg(AIInterview.score)).where(
                AIInterview.user_id == current_user.id
            )
        )
        or 0.0
    )

    if successful_swaps >= 5:
        badge = "Skill Master"
    elif successful_swaps >= 1:
        badge = "Active Swapper"
    else:
        badge = "Novice Learner"

    return ProgressResponse(
        user_name=current_user.full_name,
        badge=badge,
        total_skills_listed=total_skills,
        successful_swaps=successful_swaps,
        ai_interview_average=round(float(average_score), 2),
        badge_name=badge,
        completed_swaps=progress.completed_swaps if progress else 0,
        total_points=progress.total_points if progress else 0,
    )


@router.get("/community/groups")
def community_groups(current_user: User = Depends(get_current_user)) -> list[dict]:
    categories = sorted(
        {
            item.skill.category
            for item in current_user.skills
            if item.skill and item.skill.category
        }
    )
    if not categories:
        return [{"name": "General", "category": "General"}]
    return [
        {"name": f"{category} Hub", "category": category} for category in categories
    ]
