"""JWT security utilities for FastAPI.

[Task]: T011
[From]: specs/001-user-auth/quickstart.md
"""
import os
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Get BetterAuth secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"


class JWTManager:
    """JWT token manager for BetterAuth integration."""

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload.

        Args:
            token: JWT token string

        Returns:
            Decoded JWT payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """Extract user_id from JWT token claims.

        Args:
            token: JWT token string

        Returns:
            User ID string from token's 'sub' claim

        Raises:
            HTTPException: If token is invalid or user_id missing
        """
        payload = JWTManager.verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id

    @staticmethod
    def get_token_from_header(authorization: str) -> str:
        """Extract token from Authorization header.

        Args:
            authorization: Authorization header value (e.g., "Bearer <token>")

        Returns:
            Extracted JWT token

        Raises:
            HTTPException: If header format is invalid
        """
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
