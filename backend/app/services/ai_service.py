import json

import httpx

from app.core.config import settings
from app.models.enums import InterviewType
from app.models.user import User


class AIProviderError(RuntimeError):
    pass


def _has_ai_provider() -> bool:
    return bool(
        settings.GEMINI_API_KEY.get_secret_value()
        or settings.OPENAI_API_KEY.get_secret_value()
    )


def provider_configured() -> bool:
    """True when a live model can generate or grade questions."""
    return _has_ai_provider()


def provider_name() -> str:
    if settings.GEMINI_API_KEY.get_secret_value():
        return settings.GEMINI_MODEL
    if settings.OPENAI_API_KEY.get_secret_value():
        return settings.OPENAI_MODEL
    return "local-bank"


def _generate_json(instructions: str, prompt: str) -> dict:
    gemini_key = settings.GEMINI_API_KEY.get_secret_value()
    if gemini_key:
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent",
                headers={"x-goog-api-key": gemini_key},
                json={
                    "contents": [{"parts": [{"text": f"{instructions}\n\n{prompt}"}]}],
                    "generationConfig": {"responseMimeType": "application/json"},
                },
                timeout=45.0,
            )
            response.raise_for_status()
            body = response.json()
            output_text = "".join(
                part.get("text", "")
                for candidate in body.get("candidates", [])
                for part in candidate.get("content", {}).get("parts", [])
            )
        except (httpx.HTTPError, ValueError) as exc:
            raise AIProviderError("Gemini request failed") from exc
        try:
            result = json.loads(output_text)
        except (TypeError, json.JSONDecodeError) as exc:
            raise AIProviderError("Gemini returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise AIProviderError("Gemini returned an invalid response")
        return result

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


def generate_interview(
    user: User,
    interview_type: InterviewType,
    question_count: int = 3,
    skill_name: str | None = None,
    proficiency: str = "Beginner",
) -> dict:
    offered = [
        item.skill.name
        for item in user.skills
        if item.skill_type.value == "OFFERS" and item.skill
    ]
    focus = (
        [skill_name.strip()]
        if skill_name and skill_name.strip()
        else offered[:3] or ["general software skills"]
    )

    question_data = _generate_json(
        "Create clear, original skill interview questions. Return JSON with a 'questions' array. "
        "Each question must have 'prompt' and 'options'; options is an array of four short choices "
        "for MCQ and null for other types. Do not include answers or explanations.",
        json.dumps(
            {
                "skills": focus,
                "type": interview_type.value,
                "proficiency": proficiency,
                "question_count": question_count,
            }
        ),
    )
    raw_questions = question_data.get("questions")
    if not isinstance(raw_questions, list) or len(raw_questions) < question_count:
        raise AIProviderError("AI provider returned too few questions")
    questions = []
    for index, item in enumerate(raw_questions[:question_count], 1):
        if not isinstance(item, dict) or not isinstance(item.get("prompt"), str):
            raise AIProviderError("AI provider returned an invalid question")
        options = item.get("options")
        if interview_type == InterviewType.MCQ and (
            not isinstance(options, list) or len(options) != 4
        ):
            raise AIProviderError(
                "AI provider returned invalid multiple-choice options"
            )
        questions.append({"id": index, "prompt": item["prompt"], "options": options})

    return {
        "provider_configured": _has_ai_provider(),
        "skills": focus,
        "type": interview_type.value,
        "questions": questions,
    }


def evaluate_answers(answers: list[dict]) -> tuple[float, str]:
    if not answers:
        raise AIProviderError("Submit at least one question and answer")

    if not all(
        isinstance(item.get("question"), str) and isinstance(item.get("answer"), str)
        for item in answers
    ):
        raise AIProviderError("Each answer must include its question and answer text")

    result = _generate_json(
        "Evaluate the candidate's answers fairly and constructively. Return JSON with an integer 'score' from 0 to 100 and a concise string 'feedback'.",
        json.dumps({"question_and_answers": answers}),
    )
    score = result.get("score")
    feedback = result.get("feedback")
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not 0 <= score <= 100
    ):
        raise AIProviderError("AI provider returned an invalid interview score")
    if not isinstance(feedback, str) or not feedback.strip():
        raise AIProviderError("AI provider returned invalid interview feedback")
    return round(float(score), 2), feedback.strip()


def learning_suggestions(user: User, recent_scores: list[float]) -> dict:
    offered = [
        item.skill.name
        for item in user.skills
        if item.skill and item.skill_type.value == "OFFERS"
    ]
    wanted = [
        item.skill.name
        for item in user.skills
        if item.skill and item.skill_type.value == "WANTS"
    ]
    average = (
        round(sum(recent_scores) / len(recent_scores), 2) if recent_scores else 0.0
    )

    local_paths = [
        {
            "title": f"Strengthen {skill}",
            "reason": "Based on your current offers and interview history.",
        }
        for skill in (offered[:3] or ["core fundamentals"])
    ]
    paths = local_paths
    if _has_ai_provider():
        generated = _generate_json(
            "Suggest practical learning paths using only the supplied skills and scores. "
            "Return JSON with a 'learning_paths' array of objects with 'title' and 'reason'.",
            json.dumps(
                {
                    "offered_skills": offered,
                    "wanted_skills": wanted,
                    "recent_scores": recent_scores,
                }
            ),
        ).get("learning_paths")
        if not isinstance(generated, list) or not all(
            isinstance(item, dict)
            and isinstance(item.get("title"), str)
            and isinstance(item.get("reason"), str)
            for item in generated
        ):
            raise AIProviderError("AI provider returned invalid learning suggestions")
        paths = generated[:5]

    return {
        "average_score": average,
        "suggested_next_skills": wanted[:5],
        "learning_paths": paths,
    }
