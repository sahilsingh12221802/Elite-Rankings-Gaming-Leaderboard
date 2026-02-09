"""
Main FastAPI application factory.
Configures routes, middleware, error handling, and monitoring.
"""
import json
import logging
from contextlib import asynccontextmanager

from app.api import leaderboard_router
from app.core import cache_manager, db_manager, settings
from app.models import create_all_tables
from app.websocket import websocket_router
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    """
    # Startup
    logger.info("=== Application Startup ===")
    try:
        # Initialize database
        db_manager.init_sync_engine()
        create_all_tables(db_manager.engine)
        logger.info("✓ Database initialized")

        # Initialize cache
        cache_manager.connect()
        logger.info("✓ Cache (Redis) connected")

        logger.info(f"✓ Environment: {settings.ENVIRONMENT}")
        logger.info(f"✓ Debug: {settings.DEBUG}")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("=== Application Shutdown ===")
    try:
        cache_manager.close()
        await db_manager.close()
        logger.info("✓ Resources cleaned up")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Include routers
    app.include_router(leaderboard_router)
    app.include_router(websocket_router)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "Gaming Leaderboard API",
            "version": settings.API_VERSION,
            "status": "running",
        }

    # Health check
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
        }

    logger.info("FastAPI application created and configured")
    return app


# Create application instance
app = create_app()
