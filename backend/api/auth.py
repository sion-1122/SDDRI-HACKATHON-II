"""Authentication API endpoints.

[Task]: T017
[From]: specs/001-user-auth/contracts/openapi.yaml, specs/001-user-auth/plan.md
"""
import re
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select

from models.user import User, UserCreate, UserRead, UserLogin
from core.database import get_session
from core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def validate_email_format(email: str) -> bool:
    """Validate email format.

    Check for @ symbol and domain part.

    [Task]: T019
    [From]: specs/001-user-auth/spec.md

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    if not email:
        return False

    # Basic email validation: must contain @ and at least one . after @
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password length.

    Minimum 8 characters.

    [Task]: T020
    [From]: specs/001-user-auth/spec.md

    Args:
        password: Password to validate

    Returns:
        True if password meets requirements, False otherwise
    """
    return len(password) >= 8


@router.post("/sign-up", response_model=dict, status_code=status.HTTP_200_OK)
async def sign_up(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user account.

    Validates email format and password length, checks email uniqueness,
    hashes password with bcrypt, creates user in database.

    [Task]: T018
    [From]: specs/001-user-auth/contracts/openapi.yaml

    Args:
        user_data: User registration data (email, password)
        session: Database session

    Returns:
        Success response with message and user data

    Raises:
        HTTPException 400: Invalid email format or password too short
        HTTPException 409: Email already registered
        HTTPException 500: Database error
    """
    # Validate email format
    if not validate_email_format(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password length
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password with bcrypt
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

    # Return user data (excluding password)
    user_dict = UserRead.model_validate(user).model_dump(mode='json')
    return {
        "success": True,
        "message": "Account created successfully",
        "user": user_dict
    }


def get_user_by_email(email: str, session: Session) -> Optional[User]:
    """Query database for user by email.

    [Task]: T030
    [From]: specs/001-user-auth/plan.md

    Args:
        email: User email address
        session: Database session

    Returns:
        User object if found, None otherwise
    """
    return session.exec(select(User).where(User.email == email)).first()


@router.post("/sign-in", response_model=dict, status_code=status.HTTP_200_OK)
async def sign_in(
    user_data: UserLogin,
    session: Session = Depends(get_session)
):
    """Authenticate user and generate JWT token.

    Verifies credentials, generates JWT token, sets httpOnly cookie,
    returns token and user data.

    [Task]: T027
    [From]: specs/001-user-auth/contracts/openapi.yaml

    Args:
        user_data: User login credentials (email, password)
        session: Database session

    Returns:
        Login response with JWT token, user data, and expiration time

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 500: Database or JWT generation error
    """
    # Get user by email
    user = get_user_by_email(user_data.email, session)
    if not user:
        # Generic error message (don't reveal if email exists)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.jwt_expiration_days)
    )

    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)

    # Create response
    response_data = {
        "success": True,
        "token": access_token,
        "user": UserRead.model_validate(user).model_dump(mode='json'),
        "expires_at": expires_at.isoformat() + "Z"
    }

    # Create response with httpOnly cookie
    response = JSONResponse(content=response_data)

    # Set httpOnly cookie with JWT token
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",  # Only send over HTTPS in production
        samesite="lax",  # CSRF protection
        max_age=settings.jwt_expiration_days * 24 * 60 * 60,  # Convert days to seconds
        path="/"
    )

    return response


@router.get("/session", response_model=dict, status_code=status.HTTP_200_OK)
async def get_session(
    response: Response,
    Authorization: Optional[str] = None,
    auth_token: Optional[str] = Cookie(None),
    session: Session = Depends(get_session)
):
    """Verify JWT token and return user session data.

    Checks JWT token from Authorization header or httpOnly cookie,
    verifies signature, returns user data if authenticated.

    [Task]: T026
    [From]: specs/001-user-auth/contracts/openapi.yaml

    Args:
        response: FastAPI response object
        Authorization: Bearer token from Authorization header
        auth_token: JWT token from httpOnly cookie
        session: Database session

    Returns:
        Session response with authentication status and user data

    Raises:
        HTTPException 401: Invalid, expired, or missing token
    """
    # Extract token from Authorization header or cookie
    token = None

    # Try Authorization header first
    if Authorization:
        try:
            scheme, header_token = Authorization.split()
            if scheme.lower() == "bearer":
                token = header_token
        except ValueError:
            pass  # Fall through to cookie

    # If no token in header, try cookie
    if not token and auth_token:
        token = auth_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
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

        # Calculate expiration time
        exp = payload.get("exp")
        expires_at = None
        if exp:
            expires_at = datetime.fromtimestamp(exp).isoformat() + "Z"

        return {
            "authenticated": True,
            "user": UserRead.model_validate(user).model_dump(mode='json'),
            "expires_at": expires_at
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
