"""FastAPI application entry point.

[Task]: T015, T016
[From]: specs/001-user-auth/quickstart.md
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.config import init_db, engine
from core.middleware import JWTMiddleware
from api.tasks import router as tasks_router

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
    description="REST API for managing tasks",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT middleware (protects all routes except public ones)
# Excludes /api/auth/* for BetterAuth endpoints
app.add_middleware(JWTMiddleware, excluded_paths=["/api/auth/"])

# Include task router
app.include_router(tasks_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo List API", "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Verifies database connectivity and application status.
    Returns 503 if database is unavailable.
    """
    from sqlmodel import select
    from models.task import Task
    from sqlmodel import Session

    # Try to get database session
    try:
        # Create a simple query to test database connection
        with Session(engine) as session:
            # Execute a simple query (doesn't matter if it returns data)
            session.exec(select(Task).limit(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )
