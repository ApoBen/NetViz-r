import json
import asyncio
from typing import List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        async with self._lock:
            if not self.active_connections:
                return
                
            json_message = json.dumps(message)
            dead_connections = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(json_message)
                except Exception:
                    dead_connections.append(connection)
                    
            for connection in dead_connections:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = WebSocketManager()
