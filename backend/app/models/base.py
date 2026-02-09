"""
Database models for the Gaming Leaderboard system.
Uses SQLAlchemy ORM with optimized indexing for millions of records.
"""
import enum
from datetime import datetime

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Index,
                        Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GameMode(str, enum.Enum):
    """Supported game modes."""
    CLASSIC = "classic"
    RANKED = "ranked"
    TOURNAMENT = "tournament"
    SURVIVAL = "survival"


class User(Base):
    """User model - stores gamer information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    join_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1, index=True)

    # Relationships
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    leaderboard_entry = relationship("Leaderboard", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_username_active", "username", "is_active"),
        Index("idx_user_join_date", "join_date"),
        Index("idx_user_last_activity", "last_activity"),
    )


class GameSession(Base):
    """Game session model - stores individual game records for history."""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    game_mode = Column(Enum(GameMode), default=GameMode.CLASSIC, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Game duration in milliseconds
    multiplier = Column(Float, default=1.0, nullable=False)  # Score multiplier
    session_metadata = Column(String(512), nullable=True)  # JSON metadata as string

    # Relationships
    user = relationship("User", back_populates="game_sessions")

    __table_args__ = (
        Index("idx_session_user_timestamp", "user_id", "timestamp", unique=False),
        Index("idx_session_timestamp", "timestamp"),
        Index("idx_session_user_game_mode", "user_id", "game_mode"),
        Index("idx_session_score", "score"),  # For quick score range queries
    )


class Leaderboard(Base):
    """Leaderboard model - denormalized view for fast ranking queries."""
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    total_score = Column(Float, default=0.0, nullable=False, index=True)
    rank = Column(Integer, nullable=False, index=True)  # Current rank
    games_played = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, default=0.0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    is_active = Column(Integer, default=1, index=True)

    # Relationships
    user = relationship("User", back_populates="leaderboard_entry")

    __table_args__ = (
        Index("idx_leaderboard_score_rank", "total_score", "rank"),  # Critical for top-N queries
        Index("idx_leaderboard_rank", "rank"),
        Index("idx_leaderboard_active_score", "is_active", "total_score"),  # For active players only
        Index("idx_leaderboard_last_updated", "last_updated"),
    )


def create_all_tables(engine):
    """Create all tables in the database."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Ignore errors for objects that already exist
        if "already exists" not in str(e) and "duplicate key" not in str(e):
            raise
