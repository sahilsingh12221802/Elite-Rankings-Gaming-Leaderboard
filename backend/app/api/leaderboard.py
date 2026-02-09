"""
Leaderboard API endpoints.
POST /api/leaderboard/submit - Submit game score
GET /api/leaderboard/top - Get top leaderboard entries
GET /api/leaderboard/rank/{user_id} - Get user rank
"""
import logging
from datetime import datetime

from app.core import cache_manager, get_session
from app.models import Leaderboard, User
from app.schemas import (LeaderboardEntryResponse, LeaderboardTopResponse,
                         ScoreSubmitRequest, ScoreSubmitResponse,
                         UserRankResponse)
from app.services import LeaderboardService
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.post("/submit", response_model=ScoreSubmitResponse)
async def submit_score(
    request: ScoreSubmitRequest,
    db: Session = Depends(get_session),
):
    """
    Submit a new game score.

    - **user_id**: User's unique identifier
    - **score**: Score achieved in this game
    - **game_mode**: Game mode (classic, ranked, tournament, survival)
    - **duration_ms**: Duration of the game in milliseconds
    - **metadata**: Optional additional game data

    Returns the new rank and total score.
    """
    try:
        service = LeaderboardService(db)
        session_id, new_total_score, new_rank, rank_change = service.submit_score(request)

        # Get user info for response
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return ScoreSubmitResponse(
            session_id=session_id,
            user_id=request.user_id,
            score=request.score,
            new_total_score=new_total_score,
            new_rank=new_rank,
            rank_change=rank_change,
            message=f"Score submitted! New rank: {new_rank}" +
                    (f" (↑{rank_change})" if rank_change > 0 else f" (↓{abs(rank_change)})" if rank_change < 0 else ""),
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Service error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process score submission")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()


@router.get("/top", response_model=LeaderboardTopResponse)
async def get_top_leaderboard(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_session),
):
    """
    Get top leaderboard entries.

    - **limit**: Number of entries to return (1-1000, default: 100)
    - **offset**: Number of entries to skip for pagination

    Returns a list of top performers with their scores and rankings.
    """
    try:
        service = LeaderboardService(db)
        entries = service.get_top_leaderboard(limit=limit, offset=offset)

        return LeaderboardTopResponse(
            entries=entries,
            total_entries=len(entries),
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        import traceback
        logger.error(f"Error fetching leaderboard: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to fetch leaderboard")
    finally:
        db.close()


@router.get("/rank/{user_id}", response_model=UserRankResponse)
async def get_user_rank(
    user_id: int,
    db: Session = Depends(get_session),
):
    """
    Get rank information for a specific user.

    - **user_id**: User's unique identifier

    Returns detailed ranking information including percentile rank.
    """
    try:
        service = LeaderboardService(db)
        user_rank = service.get_user_rank(user_id)

        if not user_rank:
            raise HTTPException(status_code=404, detail="User not found in leaderboard")

        return user_rank

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user rank: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user rank")
    finally:
        db.close()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test cache connection
        cache_connected = cache_manager.exists("health_check")
        return {
            "status": "healthy",
            "cache": "connected" if cache_connected is not None else "connected",
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 503
