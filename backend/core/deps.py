"""Dependency injection for database sessions and JWT authentication.

[Task]: T013, T014
[From]: specs/001-user-auth/quickstart.md
"""
from typing import Annotated
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from starlette.requests import Request as StarletteRequest

from core.database import get_session as db_get_session


def get_session():
    """Yield a database session with automatic cleanup.

    Uses the get_session function from core.database for consistency.
    """
    yield from db_get_session()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


async def get_current_user_id(request: StarletteRequest) -> str:
    """Get current user ID from JWT token.

    Extracts user_id from request.state that was populated by JWTMiddleware.
    This function is used as a FastAPI dependency for protected routes.

    Args:
        request: Starlette request object with state populated by middleware

    Returns:
        Current authenticated user's ID

    Raises:
        HTTPException: If user_id not found in request state (not authenticated)
    """
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user_id


# Type alias for JWT authentication dependency
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]
