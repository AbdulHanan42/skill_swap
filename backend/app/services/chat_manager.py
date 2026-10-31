from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, dict[WebSocket, int]] = {}

    async def connect(self, match_id: int, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        self.active_connections.setdefault(match_id, {})[websocket] = user_id

    def disconnect(self, match_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(match_id)
        if not connections:
            return
        connections.pop(websocket, None)
        if not connections:
            self.active_connections.pop(match_id, None)

    def online_user_ids(self, match_id: int) -> set[int]:
        return set(self.active_connections.get(match_id, {}).values())

    async def broadcast(self, match_id: int, message: dict) -> None:
        for connection in list(self.active_connections.get(match_id, {})):
            await connection.send_json(message)


chat_manager = ChatConnectionManager()
