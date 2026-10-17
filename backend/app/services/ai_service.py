import json

import httpx

from app.core.config import settings
from app.models.enums import InterviewType
from app.models.user import User


class AIProviderError(RuntimeError):
    pass


def _generate_json(instructions: str, prompt: str) -> dict:
    api_key = settings.OPENAI_API_KEY.get_secret_value()
    if not api_key:
        raise AIProviderError("AI provider is not configured")
    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": settings.OPENAI_MODEL,
                "instructions": instructions,
                "input": prompt,
                "text": {"format": {"type": "json_object"}},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise AIProviderError("AI provider request failed") from exc

    output_text = body.get("output_text")
    if not output_text:
        output_text = "".join(
            part.get("text", "")
            for item in body.get("output", [])
            for part in item.get("content", [])
            if part.get("type") == "output_text"
        )
    try:
        result = json.loads(output_text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AIProviderError("AI provider returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise AIProviderError("AI provider returned an invalid response")
    return result


def generate_interview(user: User, interview_type: InterviewType, question_count: int = 5) -> dict:
    offered = [
        item.skill.name
        for item in user.skills
        if item.skill_type.value == "OFFERS" and item.skill
    ]
    focus = offered[:3] or ["general software skills"]

    question_data = _generate_json(
        "Create clear, original skill interview questions. Return JSON with a 'questions' array. "
        "Each question must have 'prompt' and 'options'; options is an array of four short choices "
        "for MCQ and null for other types. Do not include answers or explanations.",
        json.dumps({"skills": focus, "type": interview_type.value, "question_count": question_count}),
    )
    raw_questions = question_data.get("questions")
    if not isinstance(raw_questions, list) or len(raw_questions) < question_count:
        raise AIProviderError("AI provider returned too few questions")
    questions = []
    for index, item in enumerate(raw_questions[:question_count], 1):
        if not isinstance(item, dict) or not isinstance(item.get("prompt"), str):
            raise AIProviderError("AI provider returned an invalid question")
        options = item.get("options")
        if interview_type == InterviewType.MCQ and (not isinstance(options, list) or len(options) != 4):
            raise AIProviderError("AI provider returned invalid multiple-choice options")
        questions.append({"id": index, "prompt": item["prompt"], "options": options})

    return {
        "provider_configured": bool(settings.OPENAI_API_KEY.get_secret_value()),
        "skills": focus,
        "type": interview_type.value,
        "questions": questions,
    }


def evaluate_answers(answers: list[dict]) -> tuple[float, str]:
    if not answers:
        return 0.0, "No answers were submitted."

    correct = sum(1 for item in answers if item.get("correct") is True)
    score = round((correct / len(answers)) * 100, 2)
    feedback = (
        f"You scored {score}%. Focus on the skills you offer and practice weaker topics "
        "before your next swap session."
    )
    return score, feedback


def learning_suggestions(user: User, recent_scores: list[float]) -> dict:
    offered = [item.skill.name for item in user.skills if item.skill and item.skill_type.value == "OFFERS"]
    wanted = [item.skill.name for item in user.skills if item.skill and item.skill_type.value == "WANTS"]
    average = round(sum(recent_scores) / len(recent_scores), 2) if recent_scores else 0.0

    local_paths = [
        {"title": f"Strengthen {skill}", "reason": "Based on your current offers and interview history."}
        for skill in (offered[:3] or ["core fundamentals"])
    ]
    paths = local_paths
    if settings.OPENAI_API_KEY.get_secret_value():
        generated = _generate_json(
            "Suggest practical learning paths using only the supplied skills and scores. "
            "Return JSON with a 'learning_paths' array of objects with 'title' and 'reason'.",
            json.dumps({"offered_skills": offered, "wanted_skills": wanted, "recent_scores": recent_scores}),
        ).get("learning_paths")
        if not isinstance(generated, list) or not all(
            isinstance(item, dict) and isinstance(item.get("title"), str) and isinstance(item.get("reason"), str)
            for item in generated
        ):
            raise AIProviderError("AI provider returned invalid learning suggestions")
        paths = generated[:5]

    return {
        "average_score": average,
        "suggested_next_skills": wanted[:5],
        "learning_paths": paths,
    }
