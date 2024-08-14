from typing import List, Dict, Tuple
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Tuple[WebSocket, str]]] = {}

    async def connect(self, websocket: WebSocket, room: str, username: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append((websocket, username))

    def disconnect(self, websocket: WebSocket, room: str) -> None:
        if room in self.active_connections:
            self.active_connections[room] = [
                (conn, user) for conn, user in self.active_connections[room] if conn != websocket
            ]
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def disconnect_all(self, room: str):
        if room in self.active_connections:
            for websocket, _ in self.active_connections[room]:
                await websocket.send_text("The room was closed. You will be redirected to the main page.")
                await websocket.close()
            del self.active_connections[room]

    async def broadcast(self, message: str, room: str, username: str):
        if room in self.active_connections:
            for connection, _ in self.active_connections[room]:
                await connection.send_text(f"{username}: {message}")
