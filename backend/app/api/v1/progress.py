from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.gamification import ProgressTracking
from app.models.user import User
from app.schemas.match_schema import ProgressResponse

router = APIRouter(tags=["progress"])


@router.get("/progress/me", response_model=ProgressResponse)
def read_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    progress = db.scalar(select(ProgressTracking).where(ProgressTracking.user_id == current_user.id))
    if progress is None:
        return ProgressResponse(badge_name=None, completed_swaps=0, total_points=0)
    return progress


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
    return [{"name": f"{category} Hub", "category": category} for category in categories]
