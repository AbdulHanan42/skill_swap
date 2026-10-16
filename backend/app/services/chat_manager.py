from typing import Dict, Set

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, match_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(match_id, set()).add(websocket)

    def disconnect(self, match_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(match_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(match_id, None)

    async def broadcast(self, match_id: int, message: dict) -> None:
        for connection in list(self.active_connections.get(match_id, set())):
            await connection.send_json(message)


chat_manager = ChatConnectionManager()
