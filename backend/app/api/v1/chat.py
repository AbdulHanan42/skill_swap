import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.chat import Message
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.user import User
from app.schemas.chat_schema import (
    ChatContact,
    ChatReadResponse,
    ChatUnreadResponse,
    MessageResponse,
)
from app.services.chat_manager import chat_manager
from app.services.chat_payload import message_payload

router = APIRouter(tags=["chat"])

CHUNK = 64 * 1024
SAFE_SUFFIX = re.compile(r"[^a-z0-9]")
# Anything outside this set is served as a download, never rendered by the browser.
INLINE_TYPES = {
    "application/pdf",
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
    "text/plain",
}


def _accepted_matches(db: Session, user: User) -> list[Match]:
    return list(
        db.scalars(
            select(Match)
            .options(selectinload(Match.user_a), selectinload(Match.user_b))
            .where(
                Match.status == MatchStatus.ACCEPTED,
                or_(Match.user_a_id == user.id, Match.user_b_id == user.id),
            )
        )
    )


def _peer_of(match: Match, user_id: int) -> User:
    return match.user_b if match.user_a_id == user_id else match.user_a


def _get_room_or_404(db: Session, match_id: int, user: User) -> Match:
    match = db.scalar(
        select(Match)
        .options(selectinload(Match.user_a), selectinload(Match.user_b))
        .where(Match.id == match_id)
    )
    if match is None or user.id not in {match.user_a_id, match.user_b_id}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found"
        )
    return match


def _latest_message(db: Session, match_ids: list[int]) -> dict[int, Message]:
    latest_ids = (
        select(func.max(Message.id).label("message_id"))
        .where(Message.match_id.in_(match_ids))
        .group_by(Message.match_id)
        .subquery()
    )
    rows = db.execute(
        select(Message)
        .join(latest_ids, latest_ids.c.message_id == Message.id)
    ).scalars()
    return {row.match_id: row for row in rows}


def _unread_counts(db: Session, match_ids: list[int], user_id: int) -> dict[int, int]:
    rows = db.execute(
        select(Message.match_id, func.count(Message.id))
        .where(
            Message.match_id.in_(match_ids),
            Message.sender_id != user_id,
            Message.read_at.is_(None),
        )
        .group_by(Message.match_id)
    ).all()
    return {match_id: count for match_id, count in rows}


@router.get("/chat/contacts", response_model=list[ChatContact])
def chat_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatContact]:
    matches = _accepted_matches(db, current_user)
    if not matches:
        return []

    match_ids = [match.id for match in matches]
    latest = _latest_message(db, match_ids)
    unread = _unread_counts(db, match_ids, current_user.id)

    contacts = []
    for match in matches:
        peer = _peer_of(match, current_user.id)
        last = latest.get(match.id)
        contacts.append(
            ChatContact(
                id=match.id,
                peer_id=peer.id,
                name=peer.full_name,
                avatar=peer.avatar,
                designation=peer.designation,
                last_message=(last.content or last.attachment_filename) if last else None,
                last_message_at=last.sent_at if last else match.matched_at,
                last_message_mine=last is not None and last.sender_id == current_user.id,
                unread_count=unread.get(match.id, 0),
                online=peer.id in chat_manager.online_user_ids(match.id),
            )
        )
    contacts.sort(key=lambda item: item.last_message_at, reverse=True)
    return contacts


@router.get("/chat/unread", response_model=ChatUnreadResponse)
def chat_unread(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatUnreadResponse:
    match_ids = [match.id for match in _accepted_matches(db, current_user)]
    if not match_ids:
        return ChatUnreadResponse(total=0)
    return ChatUnreadResponse(total=sum(_unread_counts(db, match_ids, current_user.id).values()))


def _display_name(raw: str | None) -> str:
    name = (raw or "").replace("\\", "/").split("/")[-1].strip() or "file"
    return name[:200]


def _stored_name(raw: str | None) -> str:
    suffix = SAFE_SUFFIX.sub("", Path(_display_name(raw)).suffix.lower())[:12]
    return f"{uuid4().hex}{suffix}"


@router.post(
    "/chat/{match_id}/attachments",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    match_id: int,
    request: Request,
    file: UploadFile = File(...),
    caption: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Message:
    _get_room_or_404(db, match_id, current_user)
    limit = settings.max_upload_bytes
    too_big = f"Files are limited to {settings.MAX_UPLOAD_MB} MB."

    declared = request.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > limit + CHUNK:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, too_big)

    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(CHUNK):
        total += len(chunk)
        if total > limit:
            # The browser may lie about the size, so the cap is checked while reading.
            raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, too_big)
        chunks.append(chunk)
    if total == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That file is empty.")

    folder = settings.upload_root / "chat" / str(match_id)
    folder.mkdir(parents=True, exist_ok=True)
    stored = _stored_name(file.filename)
    (folder / stored).write_bytes(b"".join(chunks))

    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=caption.strip()[:4000],
        attachment_filename=_display_name(file.filename),
        attachment_path=f"chat/{match_id}/{stored}",
        attachment_size=total,
        attachment_mime=(file.content_type or "")[:255] or None,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    await chat_manager.broadcast(match_id, message_payload(message))
    return message


@router.get("/chat/attachments/{message_id}", response_class=FileResponse)
def download_attachment(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    message = db.get(Message, message_id)
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )
    _get_room_or_404(db, message.match_id, current_user)
    if not message.attachment_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )

    root = settings.upload_root
    path = (root / message.attachment_path).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )

    mime = message.attachment_mime or "application/octet-stream"
    inline = mime in INLINE_TYPES
    return FileResponse(
        path,
        media_type=mime if inline else "application/octet-stream",
        filename=message.attachment_filename,
        content_disposition_type="inline" if inline else "attachment",
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.post("/chat/{match_id}/read", response_model=ChatReadResponse)
def mark_room_read(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatReadResponse:
    _get_room_or_404(db, match_id, current_user)
    marked_at = datetime.now(timezone.utc)
    result = db.execute(
        update(Message)
        .where(
            Message.match_id == match_id,
            Message.sender_id != current_user.id,
            Message.read_at.is_(None),
        )
        .values(read_at=marked_at)
    )
    db.commit()
    return ChatReadResponse(marked=result.rowcount, marked_at=marked_at)
