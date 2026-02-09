"""
Configuration management for the Gaming Leaderboard application.
Uses environment variables with Pydantic v2 settings.
"""
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    DEBUG: bool = Field(default=False)

    # Database
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost:5432/leaderboard_db")
    DB_POOL_SIZE: int = Field(default=20)
    DB_POOL_RECYCLE: int = Field(default=3600)
    DB_ECHO: bool = Field(default=False)

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_KEY_PREFIX: str = Field(default="leaderboard:")
    LEADERBOARD_CACHE_TTL: int = Field(default=300)  # 5 minutes
    SESSION_CACHE_TTL: int = Field(default=600)  # 10 minutes

    # API Configuration
    API_TITLE: str = Field(default="Gaming Leaderboard API")
    API_VERSION: str = Field(default="1.0.0")
    API_DESCRIPTION: str = Field(default="Real-time multiplayer gaming leaderboard system")
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # Server
    API_WORKERS: int = Field(default=4)
    LOG_LEVEL: str = Field(default="INFO")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # WebSocket
    WEBSOCKET_MANAGER_CLEANUP_INTERVAL: int = Field(default=30)  # seconds

    # Performance
    LEADERBOARD_TOP_N: int = Field(default=100)
    BATCH_UPDATE_INTERVAL: int = Field(default=5)  # seconds

    # New Relic Monitoring
    NEW_RELIC_LICENSE_KEY: str = Field(default="")
    NEW_RELIC_APP_NAME: str = Field(default="gaming-leaderboard")
    NEW_RELIC_ENABLED: bool = Field(default=False)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
