"""Conversation service for managing chat sessions.

[Task]: T016
[From]: specs/004-ai-chatbot/tasks.md

This service handles conversation persistence and history loading.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select

from models.conversation import Conversation
from models.message import Message, MessageRole


def get_or_create_conversation(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: Optional[uuid.UUID] = None
) -> Conversation:
    """Get existing conversation or create new one.

    [From]: specs/004-ai-chatbot/plan.md - Conversation Management

    Args:
        db: Database session
        user_id: User ID who owns the conversation
        conversation_id: Optional conversation ID to load

    Returns:
        Conversation object (existing or new)

    Raises:
        ValueError: If conversation_id provided but not found or doesn't belong to user
    """
    if conversation_id:
        # Load existing conversation
        conversation = db.get(Conversation, conversation_id)

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        if conversation.user_id != user_id:
            raise ValueError("Conversation does not belong to this user")

        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation


def load_conversation_history(
    db: Session,
    conversation_id: uuid.UUID
) -> List[dict[str, str]]:
    """Load conversation history in OpenAI format.

    [From]: specs/004-ai-chatbot/plan.md - Conversation History Loading

    Args:
        db: Database session
        conversation_id: Conversation ID to load

    Returns:
        List of messages in OpenAI format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    messages = db.exec(statement).all()

    # Convert to OpenAI format (role is already a string from database)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    return conversation_history


def list_user_conversations(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0
) -> List[Conversation]:
    """List all conversations for a user.

    [From]: specs/004-ai-chatbot/spec.md - US2 (Future)

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip

    Returns:
        List of conversations ordered by updated_at (most recent first)
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(
        Conversation.updated_at.desc()
    ).offset(offset).limit(limit)

    conversations = db.exec(statement).all()
    return list(conversations)


def update_conversation_timestamp(
    db: Session,
    conversation_id: uuid.UUID
) -> None:
    """Update conversation's updated_at timestamp.

    [From]: specs/004-ai-chatbot/plan.md - Conversation Management

    This is called when a new message is added to update the conversation's
    position in the user's conversation list.

    Args:
        db: Database session
        conversation_id: Conversation ID to update
    """
    conversation = db.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db.add(conversation)
        db.commit()
