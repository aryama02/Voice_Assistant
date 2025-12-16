from fastapi import WebSocket
from typing import List
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.loop = None

    def set_loop(self, loop):
        self.loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

    def broadcast_sync(self, message: dict):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)

manager = ConnectionManager()
