"""Dependency injection for database sessions."""
from typing import Annotated
from sqlmodel import Session
from fastapi import Depends

from core import config


def get_session():
    """Yield a database session with automatic cleanup.

    Looks up the engine dynamically to support testing with different databases.
    """
    with Session(config.engine) as session:
        yield session


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
