from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.user import User
from app.schemas.user_schema import (
    DashboardOverview,
    UserResponse,
    UserSkillBulkCreate,
    UserSkillResponse,
    UserUpdate,
)

router = APIRouter(tags=["profile"])


def _profile_completeness(user: User) -> float:
    fields = [user.full_name, user.bio, user.designation, user.email]
    filled = sum(1 for field in fields if field)
    skill_bonus = 1 if user.skills else 0
    return round(((filled + skill_bonus) / 5) * 100, 2)


@router.get("/profile/me", response_model=UserResponse)
def read_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/profile/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/profile/skills", response_model=list[UserSkillResponse])
def add_skills(
    payload: UserSkillBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserSkill]:
    created: list[UserSkill] = []
    for item in payload.skills:
        skill = UserSkill(
            user_id=current_user.id,
            skill_id=item.skill_id,
            skill_type=item.skill_type,
            proficiency=item.proficiency,
        )
        db.add(skill)
        created.append(skill)
    db.commit()
    for skill in created:
        db.refresh(skill)
    return created


@router.get("/dashboard/overview", response_model=DashboardOverview)
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOverview:
    active_matches = db.scalar(
        select(func.count())
        .select_from(Match)
        .where(
            Match.status == MatchStatus.ACCEPTED,
            or_(Match.user_a_id == current_user.id, Match.user_b_id == current_user.id),
        )
    ) or 0
    return DashboardOverview(
        profile_completeness=_profile_completeness(current_user),
        active_matches=active_matches,
        unread_notifications=0,
    )
