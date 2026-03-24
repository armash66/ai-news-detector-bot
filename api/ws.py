"""WebSocket Router — real-time live event feed."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from typing import List

logger = logging.getLogger("truthlens.ws")
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to websocket: {e}")

manager = ConnectionManager()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """Live stream of new events, alerts, and intelligence updates."""
    await manager.connect(websocket)
    try:
        # In a real setup, a background task would read from Redis Streams
        # and broadcast to connected WebSockets via manager.broadcast()
        while True:
            data = await websocket.receive_text()
            # Echo for testing
            await websocket.send_json({"msg": "Received", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
