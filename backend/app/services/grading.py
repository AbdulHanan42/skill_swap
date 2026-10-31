"""Single grade scale shared by Progress Tracking and the AI interview."""


def grade_for_score(score: float | None) -> str:
    value = score or 0.0
    if value >= 90:
        return "A+"
    if value >= 80:
        return "A"
    if value >= 70:
        return "B"
    if value >= 60:
        return "C"
    if value >= 50:
        return "D"
    return "E"
