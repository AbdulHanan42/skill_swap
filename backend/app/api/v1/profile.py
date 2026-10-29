from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.schemas.profile_schema import AddedSkillResult, ProfileUpdate, UserSkillAdd
from app.schemas.user_schema import (
    DashboardOverview,
    UserResponse,
    UserSkillBulkCreate,
    UserSkillResponse,
    UserUpdate,
)

router = APIRouter(tags=["profile"])


def _profile_completeness(user: User) -> float:
    fields = [user.full_name, user.bio, user.designation, user.email, user.avatar]
    filled = sum(1 for field in fields if field)
    skill_bonus = 1 if user.skills else 0
    return round(((filled + skill_bonus) / 6) * 100, 2)


@router.get("/profile/me", response_model=UserResponse)
def read_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/profile/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdate | ProfileUpdate,
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


@router.post(
    "/profile/skills",
    response_model=list[UserSkillResponse] | AddedSkillResult,
)
def add_skills(
    payload: UserSkillBulkCreate | UserSkillAdd,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserSkill] | AddedSkillResult:
    if isinstance(payload, UserSkillAdd):
        skill_name = payload.skill_name.strip()
        if not skill_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Skill name cannot be empty",
            )

        skill = db.scalar(select(Skill).where(Skill.name == skill_name))
        if skill is None:
            skill = Skill(name=skill_name, category=payload.category)
            db.add(skill)
            db.flush()

        existing = db.scalar(
            select(UserSkill).where(
                UserSkill.user_id == current_user.id,
                UserSkill.skill_id == skill.id,
                UserSkill.skill_type == payload.skill_type,
            )
        )
        if existing:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Skill already added to your profile",
            )

        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=skill.id,
            skill_type=payload.skill_type,
            proficiency=payload.proficiency,
        )
        db.add(user_skill)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Skill already added to your profile",
            ) from exc
        db.refresh(user_skill)
        response.status_code = status.HTTP_201_CREATED
        return AddedSkillResult(message="Skill added successfully", skill=user_skill)

    skill_ids = [item.skill_id for item in payload.skills]
    selections = [(item.skill_id, item.skill_type) for item in payload.skills]
    if len(selections) != len(set(selections)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate skill selections",
        )
    found_ids = (
        set(db.scalars(select(Skill.id).where(Skill.id.in_(skill_ids))).all())
        if skill_ids
        else set()
    )
    missing_ids = set(skill_ids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skills not found: {sorted(missing_ids)}",
        )

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


@router.get("/skills", response_model=list[dict[str, object]])
def list_skills(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return [
        {"id": skill.id, "name": skill.name, "category": skill.category}
        for skill in db.scalars(select(Skill).order_by(Skill.name)).all()
    ]


@router.get("/dashboard/overview", response_model=DashboardOverview)
def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOverview:
    active_matches = (
        db.scalar(
            select(func.count())
            .select_from(Match)
            .where(
                Match.status == MatchStatus.ACCEPTED,
                or_(
                    Match.user_a_id == current_user.id,
                    Match.user_b_id == current_user.id,
                ),
            )
        )
        or 0
    )
    return DashboardOverview(
        profile_completeness=_profile_completeness(current_user),
        active_matches=active_matches,
        unread_notifications=0,
    )
