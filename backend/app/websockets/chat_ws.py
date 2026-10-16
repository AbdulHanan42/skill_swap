from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.chat import Message
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.user import User
from app.services.chat_manager import chat_manager

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
async def chat_websocket(websocket: WebSocket, match_id: int, db: Session = Depends(get_db)) -> None:
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

    await chat_manager.connect(match_id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            content = str(payload.get("content", "")).strip()
            if not content:
                continue
            message = Message(match_id=match_id, sender_id=user.id, content=content)
            db.add(message)
            db.commit()
            db.refresh(message)
            await chat_manager.broadcast(
                match_id,
                {
                    "id": message.id,
                    "match_id": message.match_id,
                    "sender_id": message.sender_id,
                    "content": message.content,
                    "sent_at": message.sent_at.isoformat(),
                },
            )
    except WebSocketDisconnect:
        chat_manager.disconnect(match_id, websocket)
