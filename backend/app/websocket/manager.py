"""
WebSocket manager for real-time leaderboard updates.
Handles multiple concurrent connections and broadcasts ranking changes.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Set

from app.core import get_session
from app.schemas import (LeaderboardEntryResponse, LeaderboardSnapshotEvent,
                         LeaderboardUpdateEvent)
from app.services import LeaderboardService
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}  # user_id -> set of websockets

    async def connect(self, websocket: WebSocket, user_id: int):
        """Register a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Unregister a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def broadcast_update(self, event: LeaderboardUpdateEvent):
        """
        Broadcast a ranking update to relevant users.
        Sends to all connected clients.
        """
        message = json.dumps(event.model_dump(), default=str)

        # Broadcast to all connected users
        for user_id, websockets in list(self.active_connections.items()):
            for websocket in list(websockets):
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    try:
                        await self.disconnect(websocket, user_id)
                    except Exception:
                        pass

    async def send_snapshot(self, websocket: WebSocket, entries: list[LeaderboardEntryResponse]):
        """Send a full leaderboard snapshot to a specific connection."""
        event = LeaderboardSnapshotEvent(
            entries=entries,
            timestamp=datetime.utcnow(),
        )
        message = json.dumps(event.model_dump(), default=str)
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send snapshot: {e}")

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()
