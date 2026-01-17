"""Rate limiting service for chat API.

[Task]: T021
[From]: specs/004-ai-chatbot/tasks.md

This service enforces the 100 messages/day limit per user (NFR-011).
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy import func

from models.message import Message


# Rate limit constants
DAILY_MESSAGE_LIMIT = 100  # NFR-011: Maximum messages per user per day


def check_rate_limit(
    db: Session,
    user_id: uuid.UUID
) -> tuple[bool, int, Optional[datetime]]:
    """Check if user has exceeded their daily message limit.

    [From]: specs/004-ai-chatbot/spec.md - NFR-011

    Args:
        db: Database session (synchronous)
        user_id: User ID to check

    Returns:
        Tuple of (allowed, remaining_count, reset_time)
        - allowed: True if user can send message, False if limit exceeded
        - remaining_count: Number of messages remaining today
        - reset_time: When the limit resets (midnight UTC), or None if allowed

    Example:
        >>> allowed, remaining, reset = await check_rate_limit(db, user_id)
        >>> if not allowed:
        ...     print(f"Rate limited. Resets at {reset}")
    """
    # Calculate today's date range (UTC)
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Count messages sent by user today
    # [From]: specs/004-ai-chatbot/spec.md - NFR-011
    # Count both user and assistant messages (all messages in conversation)
    statement = select(func.count(Message.id)).where(
        Message.user_id == user_id,
        Message.created_at >= today_start,
        Message.created_at < today_end
    )

    message_count = db.exec(statement).one() or 0

    # Calculate remaining messages
    remaining = DAILY_MESSAGE_LIMIT - message_count

    if remaining <= 0:
        # Rate limit exceeded
        return False, 0, today_end
    else:
        # User can send message
        return True, remaining - 1, None


def record_message(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    role: str,
    content: str
) -> Message:
    """Record a message in the database (for rate limit tracking).

    [From]: specs/004-ai-chatbot/plan.md - Message Persistence

    Note: This function is primarily for rate limit tracking.
    The actual message persistence should happen in the chat API endpoint
    before AI processing (T017) and after AI response (T018).

    Args:
        db: Database session
        user_id: User ID who sent the message
        conversation_id: Conversation ID
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Created message object
    """
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_message_count_today(
    db: Session,
    user_id: uuid.UUID
) -> int:
    """Get the number of messages sent by user today.

    [From]: specs/004-ai-chatbot/spec.md - NFR-011

    Args:
        db: Database session
        user_id: User ID to check

    Returns:
        Number of messages sent today (both user and assistant)
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    statement = select(func.count(Message.id)).where(
        Message.user_id == user_id,
        Message.created_at >= today_start,
        Message.created_at < today_end
    )

    return db.exec(statement).one() or 0


def get_rate_limit_status(
    db: Session,
    user_id: uuid.UUID
) -> dict:
    """Get comprehensive rate limit status for a user.

    [From]: specs/004-ai-chatbot/spec.md - NFR-011

    Args:
        db: Database session
        user_id: User ID to check

    Returns:
        Dictionary with rate limit information:
        {
            "limit": 100,
            "used": 45,
            "remaining": 55,
            "resets_at": "2025-01-16T00:00:00Z"
        }
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Count messages sent today
    statement = select(func.count(Message.id)).where(
        Message.user_id == user_id,
        Message.created_at >= today_start,
        Message.created_at < today_end
    )

    message_count = db.exec(statement).one() or 0

    remaining = max(0, DAILY_MESSAGE_LIMIT - message_count)

    return {
        "limit": DAILY_MESSAGE_LIMIT,
        "used": message_count,
        "remaining": remaining,
        "resets_at": today_end.isoformat() + "Z"
    }
