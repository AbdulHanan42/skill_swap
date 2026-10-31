import shutil
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.enums import InterviewType, SkillType
from app.models.gamification import AIInterview, InterviewSession
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.schemas.interview_schema import (
    InterviewAnswerSubmit,
    InterviewQuestion,
    InterviewResult,
    InterviewReview,
    InterviewSkipSubmit,
    InterviewSkillScore,
    InterviewStatus,
    InterviewSubmission,
    InterviewTask,
)
from app.services import ai_service, interview_bank
from app.services.grading import grade_for_score
from app.services.pdf_brief import build_pdf
from app.services.uploads import display_name, read_capped, resolve_stored, save_upload

router = APIRouter(prefix="/interview", tags=["interview"])

TASK_FOLDER = "interview"


def _engine() -> str:
    return ai_service.provider_name() if ai_service.provider_configured() else "local-bank"


def _offered_skills(db: Session, user: User) -> list[str]:
    def names(*types: SkillType) -> list[str]:
        return list(
            db.scalars(
                select(Skill.name)
                .join(UserSkill, UserSkill.skill_id == Skill.id)
                .where(UserSkill.user_id == user.id, UserSkill.skill_type.in_(types))
                .order_by(Skill.name)
            ).all()
        )

    return names(SkillType.OFFERS) or names(SkillType.OFFERS, SkillType.WANTS)


def _active_session(db: Session, user: User) -> InterviewSession | None:
    return db.scalar(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == user.id,
            InterviewSession.status == "in_progress",
        )
        .order_by(InterviewSession.id.desc())
    )


def _latest_session(db: Session, user: User) -> InterviewSession | None:
    return db.scalar(
        select(InterviewSession)
        .where(InterviewSession.user_id == user.id)
        .order_by(InterviewSession.id.desc())
    )


def _brief_filename(task_key: str) -> str:
    return "SQL_Challenge_Brief.pdf" if "sql" in task_key else "Task_Brief.pdf"


def _pending_question(session: InterviewSession) -> dict | None:
    for question in session.questions:
        if str(question["id"]) not in session.answers:
            return question
    return None


def _template(session: InterviewSession) -> dict:
    return interview_bank.TASK_TEMPLATES.get(
        session.task_key, interview_bank.TASK_TEMPLATES["general"]
    )


def _submission(session: InterviewSession) -> InterviewSubmission | None:
    if not session.submission_path:
        return None
    return InterviewSubmission(
        filename=session.submission_name or "submission",
        size=session.submission_size or 0,
        mime_type=session.submission_mime,
    )


def _question_view(session: InterviewSession) -> InterviewQuestion | None:
    current = _pending_question(session)
    if current is None:
        return None
    return InterviewQuestion(
        id=current["id"],
        index=session.questions.index(current) + 1,
        total=len(session.questions),
        prompt=current["prompt"],
        options=list(current["options"]),
        answered=len(session.answers),
    )


def _task_view(session: InterviewSession) -> InterviewTask | None:
    if session.step < 1:
        return None
    template = _template(session)
    return InterviewTask(
        title=session.task_title,
        brief=session.task_brief,
        requirements=list(template["requirements"]),
        deliverables=list(template["deliverables"]),
        brief_filename=_brief_filename(session.task_key),
        accepted=list(interview_bank.ACCEPTED_SUFFIXES),
        max_upload_mb=settings.INTERVIEW_MAX_UPLOAD_MB,
        submission=_submission(session),
    )


def _result_view(session: InterviewSession) -> InterviewResult | None:
    if session.status != "submitted" or session.score is None:
        return None
    review: list[InterviewReview] = []
    per_skill: dict[str, InterviewSkillScore] = {}
    for question in session.questions:
        record = session.answers.get(str(question["id"]), {})
        family = question.get("family", "general")
        correct = bool(record.get("correct"))
        bucket = per_skill.setdefault(
            family, InterviewSkillScore(skill=family, correct=0, total=0)
        )
        bucket.total += 1
        if correct:
            bucket.correct += 1
        review.append(
            InterviewReview(
                prompt=question["prompt"],
                family=family,
                options=list(question["options"]),
                selected=record.get("selected"),
                answer_index=question.get("answer_index"),
                correct=correct,
                explanation=question.get("explanation", ""),
                skipped=bool(record.get("skipped")),
            )
        )
    return InterviewResult(
        score=session.score,
        grade=grade_for_score(session.score),
        correct=sum(1 for item in review if item.correct),
        total=len(review),
        skipped=sum(1 for item in review if item.skipped),
        feedback=session.feedback or "",
        review=review,
        per_skill=list(per_skill.values()),
        submission=_submission(session),
        graded_by=session.graded_by or "local-key",
        completed_at=session.completed_at,
    )


def _status(session: InterviewSession | None, skills: list[str]) -> InterviewStatus:
    if session is None:
        return InterviewStatus(
            state="not_started",
            step=0,
            skills=skills,
            total_questions=interview_bank.QUESTION_COUNT,
            source=_engine(),
        )
    if session.status == "submitted":
        state = "verified"
    elif session.step >= 1:
        state = "task"
    else:
        state = "mcq"
    return InterviewStatus(
        state=state,
        step=session.step,
        skills=list(session.skill_names),
        total_questions=len(session.questions),
        answered=len(session.answers),
        question=_question_view(session) if state == "mcq" else None,
        task=_task_view(session),
        result=_result_view(session),
        source=_engine(),
    )


def _resolve_option(raw: int | str, option_count: int) -> int:
    if isinstance(raw, bool):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Use an option index or its letter"
        )
    if isinstance(raw, int):
        index = raw
    elif str(raw).strip().isdigit():
        index = int(str(raw).strip())
    elif len(str(raw).strip()) == 1 and str(raw).strip().isalpha():
        index = ord(str(raw).strip().upper()) - ord("A")
    else:
        index = -1
    if not 0 <= index < option_count:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "That option is not on this question"
        )
    return index


def _grade_locally(session: InterviewSession) -> tuple[float, str]:
    total = len(session.questions)
    correct = 0
    notes: list[str] = []
    for question in session.questions:
        record = session.answers.get(str(question["id"]), {})
        if record.get("correct"):
            correct += 1
            continue
        label = "Skipped" if record.get("skipped") else "Review"
        notes.append(f"{label} — {question.get('explanation') or question['prompt']}")
    score = round((correct / total) * 100, 1) if total else 0.0
    lines = [f"You answered {correct} of {total} technical questions correctly."]
    lines.extend(notes[:4])
    if session.submission_name:
        lines.append(
            f"{session.submission_name} is attached so your swap partner can review the code."
        )
    return score, " ".join(lines)


def _qa_pairs(session: InterviewSession) -> list[dict]:
    pairs = []
    for question in session.questions:
        record = session.answers.get(str(question["id"]), {})
        selected = record.get("selected")
        answer = (
            question["options"][selected]
            if isinstance(selected, int) and 0 <= selected < len(question["options"])
            else "Skipped"
        )
        pairs.append({"question": question["prompt"], "answer": answer})
    return pairs


def _finalize(db: Session, session: InterviewSession, current_user: User) -> None:
    """Score the sitting and record it so Progress Tracking can pick it up."""
    score, feedback = _grade_locally(session)
    graded_by = "local-key"
    if ai_service.provider_configured():
        try:
            score, feedback = ai_service.evaluate_answers(_qa_pairs(session))
            graded_by = ai_service.provider_name()
        except ai_service.AIProviderError:
            # A provider outage must not cost the user their interview result.
            pass

    session.score = score
    session.feedback = feedback
    session.graded_by = graded_by
    session.status = "submitted"
    session.step = 2
    session.completed_at = datetime.now(timezone.utc)

    skill_name = (session.skill_names or ["General"])[0]
    skill = db.scalar(select(Skill).where(Skill.name == skill_name))
    if skill is None:
        skill = Skill(name=skill_name[:100], category="Interview")
        db.add(skill)
        db.flush()
    interview = AIInterview(
        user_id=current_user.id,
        skill_id=skill.id,
        type=InterviewType.PRACTICAL,
        score=score,
        ai_feedback=feedback,
    )
    db.add(interview)
    db.flush()
    session.interview_id = interview.id


@router.get("/status", response_model=InterviewStatus)
def interview_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    session = _active_session(db, current_user) or _latest_session(db, current_user)
    return _status(session, _offered_skills(db, current_user))


@router.post("/start", response_model=InterviewStatus)
def start_interview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    existing = _active_session(db, current_user)
    if existing is not None:
        return _status(existing, list(existing.skill_names))

    skills = _offered_skills(db, current_user)
    attempts = (
        db.scalar(select(AIInterview.id).where(AIInterview.user_id == current_user.id)) or 0
    )
    # Rotating the seed keeps a retake from being the identical paper.
    questions = interview_bank.build_questions(skills, seed=current_user.id * 7 + attempts)
    task = interview_bank.task_for(skills)

    session = InterviewSession(
        user_id=current_user.id,
        status="in_progress",
        step=0,
        skill_names=skills,
        questions=questions,
        answers={},
        task_key=task["key"],
        task_title=task["title"],
        task_brief=task["brief"],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _status(session, skills)


@router.post("/answer", response_model=InterviewStatus)
def answer_question(
    payload: InterviewAnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    session = _active_session(db, current_user)
    if session is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Start the interview before answering")

    current = _pending_question(session)
    if current is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Every question is already answered")
    if current["id"] != payload.question_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Answer the current question first")

    index = _resolve_option(payload.selected_option, len(current["options"]))
    answers = dict(session.answers)
    answers[str(current["id"])] = {
        "selected": index,
        "skipped": False,
        "correct": index == current.get("answer_index"),
    }
    session.answers = answers
    session.step = 1 if _pending_question(session) is None else 0
    db.commit()
    db.refresh(session)
    return _status(session, list(session.skill_names))


@router.post("/skip", response_model=InterviewStatus)
def skip_question(
    payload: InterviewSkipSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    session = _active_session(db, current_user)
    if session is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Start the interview before answering")

    current = _pending_question(session)
    if current is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Every question is already answered")
    if current["id"] != payload.question_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Answer the current question first")

    answers = dict(session.answers)
    answers[str(current["id"])] = {"selected": None, "skipped": True, "correct": False}
    session.answers = answers
    session.step = 1 if _pending_question(session) is None else 0
    db.commit()
    db.refresh(session)
    return _status(session, list(session.skill_names))


@router.get("/task-brief")
def task_brief(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    session = _active_session(db, current_user) or _latest_session(db, current_user)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Start the interview to get the brief")

    template = _template(session)
    blocks: list[tuple[str, str]] = [
        ("heading", "Objective"),
        ("body", session.task_brief),
        ("gap", ""),
        ("heading", "Requirements"),
        *[("bullet", item) for item in template["requirements"]],
        ("gap", ""),
        ("heading", "What to hand in"),
        *[("bullet", item) for item in template["deliverables"]],
        ("gap", ""),
        ("heading", "Skills under test"),
        ("body", ", ".join(session.skill_names) or "General engineering"),
        ("gap", ""),
        ("heading", "Submission rules"),
        (
            "body",
            f"Upload one file with one of these extensions: {', '.join(interview_bank.ACCEPTED_SUFFIXES)}. "
            f"The limit is {settings.INTERVIEW_MAX_UPLOAD_MB} MB.",
        ),
    ]
    filename = _brief_filename(session.task_key)
    quoted = filename.replace('"', "")
    return Response(
        content=build_pdf(session.task_title, blocks),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{quoted}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/submit-task", response_model=InterviewStatus)
async def submit_task(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    session = _active_session(db, current_user)
    if session is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Start the interview before submitting")
    if _pending_question(session) is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Finish the technical questions before submitting the task",
        )

    name = display_name(file.filename)
    lowered = name.lower()
    if not any(lowered.endswith(suffix) for suffix in interview_bank.ACCEPTED_SUFFIXES):
        allowed = ", ".join(interview_bank.ACCEPTED_SUFFIXES)
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported file type. Allowed: {allowed}",
        )

    too_big = f"Submissions are limited to {settings.INTERVIEW_MAX_UPLOAD_MB} MB."
    data = await read_capped(file, request, settings.interview_max_upload_bytes, too_big)

    if session.submission_path:
        previous = resolve_stored(settings.upload_root, session.submission_path)
        if previous is not None:
            previous.unlink(missing_ok=True)
    stored = save_upload(settings.upload_root, f"{TASK_FOLDER}/{session.id}", name, data)

    session.submission_name = name
    session.submission_path = stored
    session.submission_size = len(data)
    session.submission_mime = (file.content_type or "")[:255] or None
    _finalize(db, session, current_user)
    db.commit()
    db.refresh(session)
    return _status(session, list(session.skill_names))


@router.post("/reset", response_model=InterviewStatus)
def reset_interview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatus:
    session = _active_session(db, current_user)
    if session is not None:
        shutil.rmtree(settings.upload_root / TASK_FOLDER / str(session.id), ignore_errors=True)
        db.delete(session)
        db.commit()
    return InterviewStatus(
        state="not_started",
        step=0,
        skills=_offered_skills(db, current_user),
        total_questions=interview_bank.QUESTION_COUNT,
        source=_engine(),
    )
