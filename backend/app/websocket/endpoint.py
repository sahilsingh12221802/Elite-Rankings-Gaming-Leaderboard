"""
WebSocket endpoint for real-time leaderboard updates.
"""
import logging

from app.core import get_session
from app.schemas import LeaderboardUpdateEvent
from app.services import LeaderboardService
from app.websocket.manager import manager
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/leaderboard/{user_id}")
async def websocket_leaderboard_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time leaderboard updates.

    Clients connect with their user_id and receive:
    1. Immediate full leaderboard snapshot
    2. Live updates when rankings change
    3. User-specific ranking changes
    """
    await manager.connect(websocket, user_id)

    try:
        # Send initial leaderboard snapshot
        db: Session = get_session()
        try:
            service = LeaderboardService(db)
            snapshot = service.get_top_leaderboard(limit=100)
            await manager.send_snapshot(websocket, snapshot)
            logger.info(f"WebSocket connected for user {user_id}, snapshot sent")
        except Exception as e:
            logger.error(f"Error sending snapshot to user {user_id}: {e}", exc_info=True)
            raise
        finally:
            db.close()

        # Listen for client messages (heartbeat, etc.)
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received message from user {user_id}: {data}")

            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}", exc_info=True)
        await manager.disconnect(websocket, user_id)


@router.get("/ws/health")
async def websocket_health():
    """Health check endpoint for WebSocket service."""
    return {
        "status": "healthy",
        "active_connections": manager.get_connection_count(),
    }
