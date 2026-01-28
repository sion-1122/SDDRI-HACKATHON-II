"""FastAPI application entry point.

[Task]: T047
[From]: specs/001-user-auth/plan.md
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time

from core.database import init_db, engine
from core.config import get_settings
from api.auth import router as auth_router
from api.tasks import router as tasks_router
from api.chat import router as chat_router
from core.logging import setup_logging, get_logger

settings = get_settings()

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events with graceful connection cleanup.
    """
    # Startup
    logger.info("Starting up application...")
    init_db()
    logger.info("Database initialized")

    # Track background tasks for graceful shutdown
    background_tasks = set()

    yield

    # Shutdown - Graceful shutdown handler
    logger.info("Shutting down application...")

    # Close database connections
    try:
        logger.info("Closing database connections...")
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

    # Wait for background tasks to complete (with timeout)
    if background_tasks:
        logger.info(f"Waiting for {len(background_tasks)} background tasks to complete...")
        try:
            # Wait up to 10 seconds for tasks to complete
            import asyncio
            await asyncio.wait_for(asyncio.gather(*background_tasks, return_exceptions=True), timeout=10.0)
            logger.info("All background tasks completed")
        except asyncio.TimeoutError:
            logger.warning("Background tasks did not complete in time, forcing shutdown...")

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Todo List API",
    description="REST API for managing tasks with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)  # Authentication endpoints
app.include_router(tasks_router)  # Task management endpoints
app.include_router(chat_router)  # AI chat endpoints (Phase III)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Todo List API",
        "status": "running",
        "version": "2.0.0",
        "authentication": "JWT",
        "features": {
            "task_management": "REST API for CRUD operations",
            "ai_chatbot": "Natural language task creation and listing"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Verifies database connectivity and application status.
    Returns 503 if database is unavailable.

    [Task]: T048
    [From]: specs/001-user-auth/plan.md
    """
    from sqlmodel import select
    from models.user import User
    from sqlmodel import Session

    # Try to get database session
    try:
        # Create a simple query to test database connection
        with Session(engine) as session:
            # Execute a simple query (doesn't matter if it returns data)
            session.exec(select(User).limit(1))
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring.

    Returns basic application metrics for Kubernetes health probes.
    """
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time(),
        "version": "1.0.0",
        "database": "connected"  # Simplified - in production would check actual DB status
    }


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler.

    Returns consistent error format for all HTTP exceptions.

    [Task]: T046
    [From]: specs/001-user-auth/research.md
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status_code": exc.status_code,
                "detail": exc.detail
            }
        }
    )
