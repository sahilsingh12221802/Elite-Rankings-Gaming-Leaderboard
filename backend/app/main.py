"""
Main FastAPI application factory.
Configures routes, middleware, error handling, and monitoring.
"""
import json
import logging
import os
from contextlib import asynccontextmanager

# Initialize New Relic agent
import newrelic.agent

# Get absolute path to newrelic.ini
if 'NEW_RELIC_CONFIG_FILE' in os.environ:
    newrelic_config_file = os.environ['NEW_RELIC_CONFIG_FILE']
else:
    # default to newrelic.ini in the backend directory
    newrelic_config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'newrelic.ini')

if os.path.exists(newrelic_config_file):
    print(f"[NEW_RELIC] Initializing agent with config: {newrelic_config_file}")
    newrelic.agent.initialize(newrelic_config_file)
    print("[NEW_RELIC] Agent initialized successfully")
else:
    print(f"[NEW_RELIC] Config file not found: {newrelic_config_file}")
    print(f"[NEW_RELIC] Current directory: {os.getcwd()}")
    # Try with environment variables as fallback
    if os.environ.get('NEW_RELIC_LICENSE_KEY'):
        print("[NEW_RELIC] Using environment variables for initialization")
        newrelic.agent.initialize()

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
        # Initialize database (non-blocking, continue if it fails)
        try:
            db_manager.init_sync_engine()
            create_all_tables(db_manager.engine)
            logger.info("✓ Database initialized")
        except Exception as db_e:
            logger.warning(f"Database initialization failed (app will continue): {db_e}")

        # Initialize cache (non-blocking, continue if it fails)
        try:
            cache_manager.connect()
            logger.info("✓ Cache (Redis) connected")
        except Exception as cache_e:
            logger.warning(f"Cache initialization failed (app will continue): {cache_e}")

        logger.info(f"✓ Environment: {settings.ENVIRONMENT}")
        logger.info(f"✓ Debug: {settings.DEBUG}")
        logger.info("✓ New Relic monitoring enabled")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")

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
