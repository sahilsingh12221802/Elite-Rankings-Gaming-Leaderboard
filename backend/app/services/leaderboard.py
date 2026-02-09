"""
Leaderboard service - Core business logic for leaderboard operations.
Handles scoring, ranking, caching, and transaction management.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from app.core import cache_manager, settings
from app.models import GameMode, GameSession, Leaderboard, User
from app.schemas import (LeaderboardEntryResponse, LeaderboardUpdateEvent,
                         ScoreSubmitRequest, UserRankResponse)
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LeaderboardService:
    """Service for managing leaderboard operations with caching and optimization."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def submit_score(self, request: ScoreSubmitRequest) -> Tuple[int, float, int, int]:
        """
        Submit a new game score and atomically update leaderboard ranking.

        Returns:
            Tuple of (session_id, new_total_score, new_rank, rank_change)
        """
        try:
            # Get or create user
            user = self.db.query(User).filter(User.id == request.user_id).first()
            if not user:
                # Auto-create user on first score submission
                user = User(
                    id=request.user_id,
                    username=f"Player_{request.user_id}",
                    email=f"player{request.user_id}@leaderboard.local",
                    join_date=datetime.utcnow(),
                    is_active=1,
                )
                self.db.add(user)
                self.db.flush()
                logger.info(f"Created new user: {request.user_id}")

            # Create game session record
            session = GameSession(
                user_id=request.user_id,
                score=request.score,
                game_mode=GameMode[request.game_mode.value.upper()],
                duration_ms=request.duration_ms,
                session_metadata=str(request.metadata) if request.metadata else None,
            )
            self.db.add(session)
            self.db.flush()  # Get session ID before proceeding

            # Update or create leaderboard entry
            leaderboard_entry = (
                self.db.query(Leaderboard)
                .filter(Leaderboard.user_id == request.user_id)
                .first()
            )

            old_rank = None
            if leaderboard_entry:
                old_rank = leaderboard_entry.rank
                leaderboard_entry.total_score += request.score
                leaderboard_entry.games_played += 1
                leaderboard_entry.last_updated = datetime.utcnow()
            else:
                leaderboard_entry = Leaderboard(
                    user_id=request.user_id,
                    total_score=request.score,
                    games_played=1,
                    rank=1,  # Will be recalculated
                    win_rate=0.0,
                )
                self.db.add(leaderboard_entry)

            self.db.flush()

            # Recalculate rank for this user
            new_rank = self._calculate_rank(request.user_id)
            leaderboard_entry.rank = new_rank

            # Flush changes (will be committed by FastAPI's session management)
            self.db.flush()

            # Calculate rank change
            rank_change = (old_rank - new_rank) if old_rank else 0

            # Invalidate cache
            self._invalidate_leaderboard_cache()

            # Commit the transaction to persist all changes
            self.db.commit()

            logger.info(
                f"Score submitted: user={request.user_id}, score={request.score}, "
                f"new_rank={new_rank}, old_rank={old_rank}"
            )

            # Broadcast update to WebSocket clients (fire and forget)
            try:
                from app.websocket.manager import manager
                update_event = LeaderboardUpdateEvent(
                    event_type="leaderboard_update",
                    user_id=request.user_id,
                    username=user.username,
                    new_rank=new_rank,
                    old_rank=old_rank or new_rank,
                    total_score=leaderboard_entry.total_score,
                    rank_change=rank_change,
                    timestamp=datetime.utcnow(),
                )
                # Schedule broadcast in the event loop (fire and forget)
                try:
                    loop = asyncio.get_running_loop()
                    # Schedule the coroutine to run in the background
                    asyncio.ensure_future(manager.broadcast_update(update_event))
                except RuntimeError:
                    # No event loop running (shouldn't happen in FastAPI, but handle it gracefully)
                    logger.debug("No running event loop for WebSocket broadcast")
            except Exception as e:
                logger.error(f"Failed to schedule WebSocket broadcast: {e}", exc_info=True)

            return session.id, leaderboard_entry.total_score, new_rank, rank_change

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error submitting score: {e}")
            raise RuntimeError("Failed to submit score")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error submitting score: {e}")
            raise

    def _calculate_rank(self, user_id: int) -> int:
        """
        Calculate the current rank for a user based on total score.
        Optimized with efficient SQL query.
        """
        # Get user's score
        user_score = (
            self.db.query(Leaderboard.total_score)
            .filter(Leaderboard.user_id == user_id, Leaderboard.is_active == 1)
            .scalar()
        )

        if user_score is None:
            return 1

        # Count how many users have a higher score
        rank = (
            self.db.query(func.count(Leaderboard.id))
            .filter(
                Leaderboard.total_score > user_score,
                Leaderboard.is_active == 1,
            )
            .scalar()
        ) + 1

        return rank

    def get_top_leaderboard(self, limit: int = None, offset: int = 0) -> List[LeaderboardEntryResponse]:
        """
        Get top leaderboard entries with caching.
        Optimized for reading millions of records.
        """
        limit = limit or settings.LEADERBOARD_TOP_N

        # Try cache first
        cache_key = f"top_leaderboard:{limit}:{offset}"
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            return [LeaderboardEntryResponse(**entry) for entry in cached_data]

        # Query database ordered by score (descending) for accurate ranking
        entries = (
            self.db.query(
                Leaderboard.user_id,
                User.username,
                Leaderboard.total_score,
                Leaderboard.games_played,
                Leaderboard.win_rate,
                Leaderboard.last_updated,
            )
            .join(User, Leaderboard.user_id == User.id)
            .filter(Leaderboard.is_active == 1)
            .order_by(desc(Leaderboard.total_score))  # Order by score descending
            .all()
        )

        result = []
        for rank, entry in enumerate(entries, start=1):
            result.append(
                LeaderboardEntryResponse(
                    rank=rank,
                    user_id=entry[0],
                    username=entry[1],
                    total_score=entry[2],
                    games_played=entry[3],
                    win_rate=entry[4],
                    last_updated=entry[5],
                )
            )

        # Apply pagination after calculating ranks
        paginated_result = result[offset : offset + limit]

        # Cache the result
        cache_manager.set(cache_key, [entry.model_dump() for entry in paginated_result])

        return paginated_result

    def get_user_rank(self, user_id: int) -> Optional[UserRankResponse]:
        """
        Get rank information for a specific user.
        Returns detailed ranking with percentile.
        """
        # Try cache
        cache_key = f"user_rank:{user_id}"
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            return UserRankResponse(**cached_data)

        # Query leaderboard and user info
        result = (
            self.db.query(
                Leaderboard.rank,
                Leaderboard.user_id,
                User.username,
                Leaderboard.total_score,
                Leaderboard.games_played,
                Leaderboard.win_rate,
                Leaderboard.last_updated,
            )
            .join(User, Leaderboard.user_id == User.id)
            .filter(Leaderboard.user_id == user_id, Leaderboard.is_active == 1)
            .first()
        )

        if not result:
            return None

        # Calculate percentile
        total_active_users = self.db.query(func.count(Leaderboard.id)).filter(Leaderboard.is_active == 1).scalar()
        percentile = ((total_active_users - result[0]) / total_active_users * 100) if total_active_users > 0 else 0

        response = UserRankResponse(
            user_id=result[1],
            username=result[2],
            rank=result[0],
            total_score=result[3],
            games_played=result[4],
            win_rate=result[5],
            percentile=percentile,
            last_updated=result[6],
        )

        # Cache the result
        cache_manager.set(cache_key, response.model_dump(), ttl=settings.SESSION_CACHE_TTL)

        return response

    def get_user_percentile_rank(self, user_id: int) -> Optional[int]:
        """Get the percentile rank of a user (for quick lookups)."""
        result = (
            self.db.query(Leaderboard.rank)
            .filter(Leaderboard.user_id == user_id, Leaderboard.is_active == 1)
            .scalar()
        )
        return result

    def _invalidate_leaderboard_cache(self):
        """Invalidate leaderboard cache entries after score update."""
        cache_manager.delete_pattern("top_leaderboard:*")
        cache_manager.delete_pattern("user_rank:*")

    def batch_recalculate_rankings(self, batch_size: int = 1000):
        """
        Recalculate all rankings efficiently in batches.
        Used for periodic consistency checks or migrations.
        """
        total_recalculated = 0
        offset = 0

        while True:
            # Get batch of users
            users = (
                self.db.query(Leaderboard.user_id)
                .filter(Leaderboard.is_active == 1)
                .order_by(Leaderboard.rank)
                .limit(batch_size)
                .offset(offset)
                .all()
            )

            if not users:
                break

            for (user_id,) in users:
                try:
                    new_rank = self._calculate_rank(user_id)
                    self.db.query(Leaderboard).filter(Leaderboard.user_id == user_id).update(
                        {Leaderboard.rank: new_rank}
                    )
                    total_recalculated += 1
                except Exception as e:
                    logger.error(f"Error recalculating rank for user {user_id}: {e}")

            self.db.commit()
            offset += batch_size
            logger.info(f"Batch processed: {offset} users recalculated so far")

        logger.info(f"Total rankings recalculated: {total_recalculated}")
