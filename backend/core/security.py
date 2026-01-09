"""Password hashing and JWT token management.

[Task]: T011
[From]: specs/001-user-auth/plan.md, specs/001-user-auth/research.md
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from core.config import get_settings

settings = get_settings()

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _pre_hash_password(password: str) -> bytes:
    """Pre-hash password with SHA-256 to handle bcrypt's 72-byte limit.

    Bcrypt cannot hash passwords longer than 72 bytes. This function
    pre-hashes the password with SHA-256 first, then bcrypt hashes that.

    Args:
        password: Plaintext password (any length)

    Returns:
        SHA-256 hash of the password (always 32 bytes)
    """
    return hashlib.sha256(password.encode()).digest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches hash, False otherwise
    """
    # Pre-hash the plain password to match how it was stored
    pre_hashed = _pre_hash_password(plain_password)
    return pwd_context.verify(pre_hashed, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with SHA-256 pre-hashing.

    This two-step approach:
    1. Hash password with SHA-256 (handles any length)
    2. Hash the SHA-256 hash with bcrypt (adds salt and security)

    Args:
        password: Plaintext password to hash (any length)

    Returns:
        Hashed password (bcrypt hash with salt)

    Example:
        ```python
        hashed = get_password_hash("my_password")
        # Returns: $2b$12$... (bcrypt hash)
        ```
    """
    # Pre-hash with SHA-256 to handle long passwords
    pre_hashed = _pre_hash_password(password)

    # Hash the pre-hash with bcrypt
    return pwd_context.hash(pre_hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Payload data to encode in token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        ```python
        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )
        ```
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Encode JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
