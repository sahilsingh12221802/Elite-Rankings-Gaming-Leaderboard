"""
Pydantic schemas for request/response validation and serialization.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GameModeEnum(str, Enum):
    """Game mode enumeration."""
    CLASSIC = "classic"
    RANKED = "ranked"
    TOURNAMENT = "tournament"
    SURVIVAL = "survival"


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class UserCreate(UserBase):
    """Schema for user creation."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    join_date: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ScoreSubmitRequest(BaseModel):
    """Schema for score submission request."""
    user_id: int = Field(..., gt=0)
    score: float = Field(..., gt=0)
    game_mode: GameModeEnum = Field(default=GameModeEnum.CLASSIC)
    duration_ms: Optional[int] = Field(None, ge=0)
    metadata: Optional[dict] = None


class ScoreSubmitResponse(BaseModel):
    """Schema for score submission response."""
    session_id: int
    user_id: int
    score: float
    new_total_score: float
    new_rank: int
    rank_change: int
    message: str


class LeaderboardEntryResponse(BaseModel):
    """Schema for a single leaderboard entry."""
    rank: int
    user_id: int
    username: str
    total_score: float
    games_played: int
    win_rate: float
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardTopResponse(BaseModel):
    """Schema for top leaderboard response."""
    entries: list[LeaderboardEntryResponse]
    total_entries: int
    timestamp: datetime


class UserRankResponse(BaseModel):
    """Schema for user rank lookup response."""
    user_id: int
    username: str
    rank: int
    total_score: float
    games_played: int
    win_rate: float
    percentile: float  # User's percentile (0-100)
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardUpdateEvent(BaseModel):
    """Schema for WebSocket leaderboard update event."""
    event_type: str = "leaderboard_update"
    user_id: int
    username: str
    new_rank: int
    old_rank: Optional[int]
    total_score: float
    rank_change: int
    timestamp: datetime


class LeaderboardSnapshotEvent(BaseModel):
    """Schema for full leaderboard snapshot event."""
    event_type: str = "leaderboard_snapshot"
    entries: list[LeaderboardEntryResponse]
    timestamp: datetime
