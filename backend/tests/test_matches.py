from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import SkillType
from app.services.match_engine import calculate_match_score


def _user(user_id: int, offers: list[int], wants: list[int]):
    skills = [
        SimpleNamespace(skill_id=skill_id, skill_type=SkillType.OFFERS, skill=SimpleNamespace(name=f"s{skill_id}"))
        for skill_id in offers
    ] + [
        SimpleNamespace(skill_id=skill_id, skill_type=SkillType.WANTS, skill=SimpleNamespace(name=f"s{skill_id}"))
        for skill_id in wants
    ]
    return SimpleNamespace(id=user_id, skills=skills)


def test_reciprocal_match_score():
    user_a = _user(1, offers=[1], wants=[2])
    user_b = _user(2, offers=[2], wants=[1])
    score, a_gets, b_gets = calculate_match_score(user_a, user_b)
    assert score > 0
    assert a_gets == {2}
    assert b_gets == {1}


def test_one_way_interest_is_not_a_match():
    user_a = _user(1, offers=[1], wants=[2])
    user_b = _user(2, offers=[3], wants=[1])
    score, _, _ = calculate_match_score(user_a, user_b)
    assert score == 0


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
