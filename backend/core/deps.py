"""Dependency injection for database sessions and JWT authentication.

[Task]: T013, T014
[From]: specs/001-user-auth/quickstart.md
"""
from typing import Annotated, Optional
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from starlette.requests import Request as StarletteRequest
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.database import get_session as db_get_session
from core.security import decode_access_token

# HTTP Bearer scheme for Authorization header
security = HTTPBearer(auto_error=False)


def get_session():
    """Yield a database session with automatic cleanup.

    Uses the get_session function from core.database for consistency.
    """
    yield from db_get_session()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: StarletteRequest = None
) -> str:
    """Get current user ID from JWT token.

    Extracts JWT token from Authorization header or httpOnly cookie,
    verifies it, and returns user_id.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        request: Starlette request object to access cookies

    Returns:
        Current authenticated user's ID

    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    # Extract token from Authorization header or cookie
    token = None

    # Try Authorization header first
    if credentials:
        token = credentials.credentials

    # If no token in header, try httpOnly cookie
    if not token and request:
        auth_token = request.cookies.get("auth_token")
        if auth_token:
            token = auth_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and verify token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id missing"
            )

        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# Type alias for JWT authentication dependency
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]
