from app.core.config import settings
from app.models.enums import InterviewType
from app.models.user import User


def generate_interview(user: User, interview_type: InterviewType, question_count: int = 5) -> dict:
    offered = [
        item.skill.name
        for item in user.skills
        if item.skill_type.value == "OFFERS" and item.skill
    ]
    focus = offered[:3] or ["general software skills"]

    questions = []
    for index in range(1, question_count + 1):
        questions.append(
            {
                "id": index,
                "prompt": f"Question {index} about {focus[0]} ({interview_type.value}).",
                "options": ["A", "B", "C", "D"] if interview_type == InterviewType.MCQ else None,
            }
        )

    return {
        "provider_configured": bool(
            settings.OPENAI_API_KEY.get_secret_value() or settings.GEMINI_API_KEY.get_secret_value()
        ),
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

    return {
        "average_score": average,
        "suggested_next_skills": wanted[:5],
        "learning_paths": [
            {
                "title": f"Strengthen {skill}",
                "reason": "Based on your current offers and interview history.",
            }
            for skill in (offered[:3] or ["core fundamentals"])
        ],
    }
