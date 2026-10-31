import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.chat import Message
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.user import User
from app.schemas.chat_schema import MessageCreate
from app.services.chat_manager import chat_manager
from app.services.chat_payload import message_payload

router = APIRouter()


def _authenticate_socket(websocket: WebSocket, db: Session) -> User | None:
    token = websocket.query_params.get("token")
    if not token:
        return None
    subject = decode_access_token(token)
    if subject is None:
        return None
    try:
        user_id = int(subject)
    except ValueError:
        return None
    return db.scalar(select(User).where(User.id == user_id))


@router.websocket("/ws/chat/{match_id}")
async def chat_websocket(
    websocket: WebSocket, match_id: int, db: Session = Depends(get_db)
) -> None:
    user = _authenticate_socket(websocket, db)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    match = db.get(Match, match_id)
    if (
        match is None
        or match.status != MatchStatus.ACCEPTED
        or user.id not in {match.user_a_id, match.user_b_id}
    ):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_manager.connect(match_id, websocket, user.id)
    peer_id = match.user_b_id if match.user_a_id == user.id else match.user_a_id
    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                decoded = json.loads(raw_message)
                payload = (
                    decoded if isinstance(decoded, dict) else {"content": raw_message}
                )
            except json.JSONDecodeError:
                payload = {"content": raw_message}

            try:
                content = MessageCreate.model_validate(payload).content.strip()
            except (ValueError, TypeError):
                await websocket.send_json(
                    {"error": "Message content must be between 1 and 4000 characters."}
                )
                continue
            if not content:
                await websocket.send_json({"error": "Message content cannot be blank."})
                continue
            message = Message(match_id=match_id, sender_id=user.id, content=content)
            db.add(message)
            db.commit()
            db.refresh(message)
            if peer_id in chat_manager.online_user_ids(match_id):
                # The recipient is sitting in this room, so the message is read
                # the moment it lands — no badge should flash for it.
                message.read_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(message)
            await chat_manager.broadcast(match_id, message_payload(message))
    except WebSocketDisconnect:
        chat_manager.disconnect(match_id, websocket)
