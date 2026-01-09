"""Database connection and session management.

[Task]: T010
[From]: specs/001-user-auth/plan.md
"""
from sqlmodel import create_engine, Session
from typing import Generator

from core.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL in development
    pool_pre_ping=True,  # Verify connections before using
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


def init_db():
    """Initialize database tables.

    Creates all tables defined in SQLModel models.
    Should be called on application startup.
    """
    from sqlmodel import SQLModel
    import models.user  # Import models to register them with SQLModel

    SQLModel.metadata.create_all(engine)
