"""
Database connection and session management.
Optimized for high-performance concurrent operations.
"""
import logging

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.sync_session_factory = None
        self.async_session_factory = None

    def init_sync_engine(self):
        """Initialize synchronous database engine with connection pooling."""
        if self.engine is None:
            self.engine = create_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=10,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
                echo=settings.DB_ECHO,
            )
            self._setup_connection_handlers(self.engine)
            self.sync_session_factory = Session

    def init_async_engine(self):
        """Initialize asynchronous database engine for high-concurrency scenarios."""
        if self.async_engine is None:
            # Use asyncpg driver for better performance
            async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            self.async_engine = create_async_engine(
                async_url,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=10,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
            )
            self.async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

    def _setup_connection_handlers(self, engine):
        """Setup event handlers for database connections."""

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Setup connection features for better compatibility."""
            pass

    def get_sync_session(self) -> Session:
        """Get a synchronous database session."""
        if self.engine is None:
            self.init_sync_engine()
        return Session(self.engine)

    async def get_async_session(self) -> AsyncSession:
        """Get an asynchronous database session."""
        if self.async_engine is None:
            self.init_async_engine()
        async with self.async_session_factory() as session:
            return session

    async def close(self):
        """Close all database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


def get_session() -> Session:
    """Dependency injection for synchronous database sessions."""
    db_manager.init_sync_engine()
    return db_manager.get_sync_session()


async def get_async_session() -> AsyncSession:
    """Dependency injection for asynchronous database sessions."""
    db_manager.init_async_engine()
    async with db_manager.async_session_factory() as session:
        return session
