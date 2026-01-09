"""FastAPI application entry point.

[Task]: T047
[From]: specs/001-user-auth/plan.md
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.database import init_db, engine
from core.config import get_settings
from api.auth import router as auth_router
from api.tasks import router as tasks_router

settings = get_settings()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down application...")


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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Todo List API",
        "status": "running",
        "version": "1.0.0",
        "authentication": "JWT"
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
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )


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
