"""Authentication dependencies for protected routes.

[Task]: T036, T037
[From]: specs/001-user-auth/plan.md
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from models.user import User
from core.database import get_session
from core.security import decode_access_token

# Optional: HTTP Bearer scheme for Authorization header
security = HTTPBearer(auto_error=False)


async def get_current_user(
    response: Optional[str] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_token: Optional[str] = Cookie(None),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token.

    Extracts JWT from Authorization header or httpOnly cookie,
    verifies signature, queries database for user.

    [Task]: T036, T037
    [From]: specs/001-user-auth/plan.md

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        auth_token: JWT token from httpOnly cookie
        session: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or missing
    """
    # Extract token from Authorization header or cookie
    token = None

    # Try Authorization header first
    if credentials:
        token = credentials.credentials

    # If no token in header, try cookie
    if not token and auth_token:
        token = auth_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
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

        # Query user from database
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
