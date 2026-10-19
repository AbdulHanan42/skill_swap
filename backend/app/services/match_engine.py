from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import SkillType
from app.models.user import User, UserSkill


def _skill_ids(user: User, skill_type: SkillType) -> set[int]:
    return {item.skill_id for item in user.skills if item.skill_type == skill_type}


def _skill_names(user: User, skill_ids: set[int]) -> list[str]:
    names = []
    for item in user.skills:
        if item.skill_id in skill_ids and item.skill:
            names.append(item.skill.name)
    return sorted(set(names))


def calculate_match_score(user_a: User, user_b: User) -> tuple[float, set[int], set[int]]:
    a_wants = _skill_ids(user_a, SkillType.WANTS)
    a_offers = _skill_ids(user_a, SkillType.OFFERS)
    b_wants = _skill_ids(user_b, SkillType.WANTS)
    b_offers = _skill_ids(user_b, SkillType.OFFERS)

    a_gets = a_wants & b_offers
    b_gets = b_wants & a_offers

    if not a_gets or not b_gets:
        return 0.0, a_gets, b_gets

    reciprocal = (len(a_gets) + len(b_gets)) / max(len(a_wants | b_wants | a_offers | b_offers), 1)
    return round(reciprocal * 100, 2), a_gets, b_gets


def find_suggestions(db: Session, current_user: User, limit: int = 20) -> list[dict]:
    users = db.scalars(
        select(User)
        .options(selectinload(User.skills).selectinload(UserSkill.skill))
        .where(User.id != current_user.id)
    ).all()

    current = db.scalar(
        select(User)
        .options(selectinload(User.skills).selectinload(UserSkill.skill))
        .where(User.id == current_user.id)
    )
    if current is None:
        return []

    suggestions: list[dict] = []
    for candidate in users:
        score, a_gets, b_gets = calculate_match_score(current, candidate)
        if score <= 0:
            # A candidate can still be useful when they offer a skill the
            # current user wants, even if the exchange is not reciprocal yet.
            wanted = _skill_ids(current, SkillType.WANTS)
            offered = _skill_ids(candidate, SkillType.OFFERS)
            a_gets = wanted & offered
            if not a_gets:
                continue
            score = round(len(a_gets) / max(len(wanted), 1) * 100, 2)
        suggestions.append(
            {
                "user": candidate,
                "match_score": score,
                "overlapping_offers": _skill_names(candidate, a_gets),
                "overlapping_wants": _skill_names(current, b_gets),
            }
        )

    suggestions.sort(key=lambda item: item["match_score"], reverse=True)
    return suggestions[:limit]
