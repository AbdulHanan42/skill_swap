from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.enums import MatchStatus
from app.models.gamification import AIInterview, ProgressTracking
from app.models.match import Match
from app.models.user import User, UserSkill
from app.schemas.match_schema import ProgressResponse

router = APIRouter(tags=["progress"])


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
