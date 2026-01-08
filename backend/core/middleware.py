"""JWT middleware for FastAPI.

[Task]: T012
[From]: specs/001-user-auth/quickstart.md
"""
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import JWTManager


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware.

    Validates JWT tokens for all requests except public paths.
    Adds user_id to request.state for downstream dependency injection.
    """

    def __init__(self, app, excluded_paths: list[str] = None):
        """Initialize JWT middleware.

        Args:
            app: FastAPI application instance
            excluded_paths: List of paths to exclude from JWT validation
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or []
        self.public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        ] + self.excluded_paths

    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request with JWT validation.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with JWT validation applied

        Raises:
            HTTPException: If JWT validation fails
        """
        # Skip JWT validation for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Extract Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Verify token and extract user_id
            token = JWTManager.get_token_from_header(authorization)
            user_id = JWTManager.get_user_id_from_token(token)

            # Add user_id to request state for route handlers
            request.state.user_id = user_id

            return await call_next(request)

        except HTTPException as e:
            raise e
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authentication"},
            )
