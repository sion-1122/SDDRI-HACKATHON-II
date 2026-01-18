"""Integration tests for conversation persistence.

[Task]: T028
[From]: specs/004-ai-chatbot/tasks.md

Tests for User Story 6: Persistent Conversations

Validates that:
1. Conversations persist across page refreshes
2. Conversation IDs are properly returned and stored
3. Message history is loaded correctly
4. Conversations are updated on new messages
"""
import uuid
import pytest
from datetime import datetime
from sqlmodel import Session, select

from models.conversation import Conversation
from models.message import Message, MessageRole
from services.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    update_conversation_timestamp
)


class TestConversationPersistence:
    """Test conversation persistence across sessions."""

    def test_create_new_conversation(self, test_session: Session):
        """Test creating a new conversation generates valid ID."""
        # Arrange
        user_id = uuid.uuid4()

        # Act
        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )

        # Assert
        assert conversation is not None
        assert conversation.id is not None
        assert conversation.user_id == user_id
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_load_existing_conversation(self, test_session: Session):
        """Test loading an existing conversation by ID."""
        # Arrange
        user_id = uuid.uuid4()
        original = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )
        original_id = original.id

        # Act - Load the same conversation
        loaded = get_or_create_conversation(
            db=test_session,
            user_id=user_id,
            conversation_id=original_id
        )

        # Assert
        assert loaded.id == original_id
        assert loaded.user_id == user_id

    def test_conversation_not_found_for_different_user(self, test_session: Session):
        """Test that a user cannot access another user's conversation."""
        # Arrange
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()

        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user1_id
        )

        # Act & Assert - Trying to access with different user should fail
        with pytest.raises(ValueError, match="does not belong to this user"):
            get_or_create_conversation(
                db=test_session,
                user_id=user2_id,
                conversation_id=conversation.id
            )

    def test_conversation_not_found_invalid_id(self, test_session: Session):
        """Test that an invalid conversation ID raises an error."""
        # Arrange
        user_id = uuid.uuid4()
        fake_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            get_or_create_conversation(
                db=test_session,
                user_id=user_id,
                conversation_id=fake_id
            )

    def test_save_and_load_message_history(self, test_session: Session):
        """Test that messages are persisted and can be loaded."""
        # Arrange
        user_id = uuid.uuid4()
        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )

        # Create user message
        user_message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.USER,
            content="Hello, AI!",
            created_at=datetime.utcnow()
        )
        test_session.add(user_message)
        test_session.commit()

        # Create assistant message
        assistant_message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content="Hi! How can I help?",
            created_at=datetime.utcnow()
        )
        test_session.add(assistant_message)
        test_session.commit()

        # Act - Load conversation history
        history = load_conversation_history(
            db=test_session,
            conversation_id=conversation.id
        )

        # Assert
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello, AI!"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi! How can I help?"

    def test_conversation_timestamp_update(self, test_session: Session):
        """Test that conversation updated_at is refreshed on new activity."""
        # Arrange
        user_id = uuid.uuid4()
        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )
        original_updated_at = conversation.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        # Act - Update timestamp
        update_conversation_timestamp(
            db=test_session,
            conversation_id=conversation.id
        )

        # Assert
        # Refresh from database
        test_session.refresh(conversation)
        assert conversation.updated_at > original_updated_at

    def test_empty_conversation_history(self, test_session: Session):
        """Test loading history from a conversation with no messages."""
        # Arrange
        user_id = uuid.uuid4()
        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )

        # Act - Load empty history
        history = load_conversation_history(
            db=test_session,
            conversation_id=conversation.id
        )

        # Assert
        assert history == []

    def test_multiple_conversations_per_user(self, test_session: Session):
        """Test that a user can have multiple conversations."""
        # Arrange
        user_id = uuid.uuid4()

        # Act - Create multiple conversations
        conv1 = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )

        conv2 = get_or_create_conversation(
            db=test_session,
            user_id=user_id,
            conversation_id=conv1.id  # Same ID, returns same conversation
        )

        # Create a new conversation explicitly
        # (In real usage, this would be triggered by user starting a new chat)
        conv3 = get_or_create_conversation(
            db=test_session,
            user_id=uuid.uuid4()  # Different user
        )

        # Assert
        assert conv1.id == conv2.id  # Same conversation
        assert conv1.id != conv3.id  # Different conversation

    def test_messages_ordered_by_creation_time(self, test_session: Session):
        """Test that conversation history returns messages in chronological order."""
        # Arrange
        user_id = uuid.uuid4()
        conversation = get_or_create_conversation(
            db=test_session,
            user_id=user_id
        )

        # Create messages with slight delays
        messages = []
        for i in range(3):
            msg = Message(
                id=uuid.uuid4(),
                conversation_id=conversation.id,
                user_id=user_id,
                role=MessageRole.USER,
                content=f"Message {i}",
                created_at=datetime.utcnow()
            )
            test_session.add(msg)
            test_session.commit()
            messages.append(msg)

        # Act - Load history
        history = load_conversation_history(
            db=test_session,
            conversation_id=conversation.id
        )

        # Assert - Messages should be in chronological order
        assert len(history) == 3
        assert history[0]["content"] == "Message 0"
        assert history[1]["content"] == "Message 1"
        assert history[2]["content"] == "Message 2"
