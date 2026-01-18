"""Database connection and session management.

[Task]: T010
[From]: specs/001-user-auth/plan.md

[Task]: T004
[From]: specs/004-ai-chatbot/plan.md
"""
from sqlmodel import create_engine, Session
from typing import Generator

from core.config import get_settings

settings = get_settings()

# Create database engine with connection pooling
# Optimized for conversation/message table queries in Phase III
# SQLite doesn't support connection pooling, so we conditionally apply parameters
is_sqlite = settings.database_url.startswith("sqlite:")
is_postgresql = settings.database_url.startswith("postgresql:") or settings.database_url.startswith("postgres://")

if is_sqlite:
    # SQLite configuration (no pooling)
    engine = create_engine(
        settings.database_url,
        echo=settings.environment == "development",  # Log SQL in development
        connect_args={"check_same_thread": False}  # Allow multithreaded access
    )
elif is_postgresql:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        settings.database_url,
        echo=settings.environment == "development",  # Log SQL in development
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Additional connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
        pool_timeout=30,  # Timeout for getting connection from pool
        connect_args={
            "connect_timeout": 10,  # Connection timeout
        }
    )
else:
    # Default configuration for other databases
    engine = create_engine(
        settings.database_url,
        echo=settings.environment == "development",
        pool_pre_ping=True
    )


def get_session() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        Session: SQLModel database session

    Example:
        ```python
        @app.get("/users")
        def read_users(session: Session = Depends(get_session)):
            users = session.exec(select(User)).all()
            return users
        ```
    """
    with Session(engine) as session:
        yield session


# Alias for compatibility with chat.py
get_db = get_session


def init_db():
    """Initialize database tables.

    Creates all tables defined in SQLModel models.
    Should be called on application startup.
    """
    from sqlmodel import SQLModel
    import models.user  # Import models to register them with SQLModel
    import models.task  # Import task model

    # Phase III: Import conversation and message models
    try:
        import models.conversation
        import models.message
    except ImportError:
        # Models not yet created (Phase 2 pending)
        pass

    SQLModel.metadata.create_all(engine)
