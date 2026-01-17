"""Validation utilities for the application.

[Task]: T008
[From]: specs/004-ai-chatbot/plan.md
"""
from pydantic import ValidationError, model_validator
from pydantic_core import PydanticUndefined
from typing import Any
from sqlmodel import Field


# Constants from spec
MAX_MESSAGE_LENGTH = 10000  # FR-042: Maximum message content length


class ValidationError(Exception):
    """Custom validation error."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_message_length(content: str) -> str:
    """Validate message content length.

    [From]: specs/004-ai-chatbot/spec.md - FR-042

    Args:
        content: Message content to validate

    Returns:
        str: The validated content

    Raises:
        ValidationError: If content exceeds maximum length
    """
    if not content:
        raise ValidationError("Message content cannot be empty", "content")

    if len(content) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message content exceeds maximum length of {MAX_MESSAGE_LENGTH} characters "
            f"(got {len(content)} characters)",
            "content"
        )

    return content


def validate_conversation_id(conversation_id: Any) -> int | None:
    """Validate conversation ID.

    Args:
        conversation_id: Conversation ID to validate

    Returns:
        int | None: Validated conversation ID or None

    Raises:
        ValidationError: If conversation_id is invalid
    """
    if conversation_id is None:
        return None

    if isinstance(conversation_id, int):
        if conversation_id <= 0:
            raise ValidationError("Conversation ID must be positive", "conversation_id")
        return conversation_id

    if isinstance(conversation_id, str):
        try:
            conv_id = int(conversation_id)
            if conv_id <= 0:
                raise ValidationError("Conversation ID must be positive", "conversation_id")
            return conv_id
        except ValueError:
            raise ValidationError("Conversation ID must be a valid integer", "conversation_id")

    raise ValidationError("Conversation ID must be an integer or null", "conversation_id")


# Task validation constants
MAX_TASK_TITLE_LENGTH = 255  # From Task model
MAX_TASK_DESCRIPTION_LENGTH = 2000  # From Task model


def validate_task_title(title: str) -> str:
    """Validate task title.

    [From]: models/task.py - Task.title

    Args:
        title: Task title to validate

    Returns:
        str: The validated title

    Raises:
        ValidationError: If title is empty or exceeds max length
    """
    if not title or not title.strip():
        raise ValidationError("Task title cannot be empty", "title")

    title = title.strip()

    if len(title) > MAX_TASK_TITLE_LENGTH:
        raise ValidationError(
            f"Task title exceeds maximum length of {MAX_TASK_TITLE_LENGTH} characters "
            f"(got {len(title)} characters)",
            "title"
        )

    return title


def validate_task_description(description: str | None) -> str:
    """Validate task description.

    [From]: models/task.py - Task.description

    Args:
        description: Task description to validate

    Returns:
        str: The validated description

    Raises:
        ValidationError: If description exceeds max length
    """
    if description is None:
        return ""

    description = description.strip()

    if len(description) > MAX_TASK_DESCRIPTION_LENGTH:
        raise ValidationError(
            f"Task description exceeds maximum length of {MAX_TASK_DESCRIPTION_LENGTH} characters "
            f"(got {len(description)} characters)",
            "description"
        )

    return description
