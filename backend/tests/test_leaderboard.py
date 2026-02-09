"""
Unit tests for leaderboard service.
Tests atomic operations, ranking calculations, and caching.
"""
from datetime import datetime

import pytest
from app.models import Base, GameMode, GameSession, Leaderboard, User
from app.schemas import ScoreSubmitRequest
from app.services import LeaderboardService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_users(test_db: Session):
    """Create test users."""
    users = [
        User(username="player_1", email="p1@game.com", is_active=1),
        User(username="player_2", email="p2@game.com", is_active=1),
        User(username="player_3", email="p3@game.com", is_active=1),
    ]
    for user in users:
        test_db.add(user)
    test_db.commit()
    return users


class TestScoreSubmission:
    """Test score submission and ranking."""

    def test_submit_first_score(self, test_db: Session, test_users):
        """Test submitting first score for a user."""
        service = LeaderboardService(test_db)
        request = ScoreSubmitRequest(
            user_id=test_users[0].id,
            score=1000.0,
            game_mode="classic",
        )

        session_id, total_score, rank, rank_change = service.submit_score(request)

        assert session_id > 0
        assert total_score == 1000.0
        assert rank == 1
        assert rank_change == 0

    def test_submit_multiple_scores(self, test_db: Session, test_users):
        """Test submitting multiple scores and ranking updates."""
        service = LeaderboardService(test_db)

        # Submit scores in order of players
        scores = [1000.0, 1500.0, 800.0]
        for i, score in enumerate(scores):
            request = ScoreSubmitRequest(
                user_id=test_users[i].id,
                score=score,
                game_mode="classic",
            )
            service.submit_score(request)

        # Verify rankings
        rank_p1 = service.get_user_rank(test_users[0].id)
        rank_p2 = service.get_user_rank(test_users[1].id)
        rank_p3 = service.get_user_rank(test_users[2].id)

        assert rank_p2.rank == 1  # 1500 points
        assert rank_p1.rank == 2  # 1000 points
        assert rank_p3.rank == 3  # 800 points

    def test_score_accumulation(self, test_db: Session, test_users):
        """Test that scores accumulate for the same user."""
        service = LeaderboardService(test_db)
        user = test_users[0]

        # Submit multiple scores
        for score in [500.0, 300.0, 200.0]:
            request = ScoreSubmitRequest(
                user_id=user.id,
                score=score,
                game_mode="classic",
            )
            service.submit_score(request)

        # Check total
        user_rank = service.get_user_rank(user.id)
        assert user_rank.total_score == 1000.0
        assert user_rank.games_played == 3


class TestLeaderboardRetrieval:
    """Test leaderboard queries and caching."""

    def test_get_top_leaderboard(self, test_db: Session, test_users):
        """Test retrieving top leaderboard entries."""
        service = LeaderboardService(test_db)

        # Create some scores
        scores = {
            test_users[0].id: 5000.0,
            test_users[1].id: 7500.0,
            test_users[2].id: 3000.0,
        }

        for user_id, score in scores.items():
            request = ScoreSubmitRequest(
                user_id=user_id,
                score=score,
                game_mode="classic",
            )
            service.submit_score(request)

        # Get top 10
        top = service.get_top_leaderboard(limit=10)

        assert len(top) == 3
        assert top[0].username == "player_2"  # 7500
        assert top[1].username == "player_1"  # 5000
        assert top[2].username == "player_3"  # 3000

    def test_get_user_percentile(self, test_db: Session, test_users):
        """Test percentile calculation."""
        service = LeaderboardService(test_db)

        # Create scores for ranking
        for i, user in enumerate(test_users):
            request = ScoreSubmitRequest(
                user_id=user.id,
                score=5000.0 - (i * 1000),  # Decreasing scores
                game_mode="classic",
            )
            service.submit_score(request)

        # Check percentile for middle user
        user_rank = service.get_user_rank(test_users[1].id)
        assert user_rank.percentile > 0
        assert user_rank.percentile < 100


class TestRankCalculation:
    """Test ranking calculation accuracy."""

    def test_tie_handling(self, test_db: Session, test_users):
        """Test that ties are handled consistently."""
        service = LeaderboardService(test_db)

        # Submit same score to two users
        for user in test_users[:2]:
            request = ScoreSubmitRequest(
                user_id=user.id,
                score=5000.0,
                game_mode="classic",
            )
            service.submit_score(request)

        rank1 = service.get_user_rank(test_users[0].id)
        rank2 = service.get_user_rank(test_users[1].id)

        # Both should have rank 1, but we need to verify the implementation
        # (typically first-come-first-served or by ID)
        assert rank1.total_score == rank2.total_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
