"""Integration tests for task creation via natural language chat.

[Task]: T011
[From]: specs/004-ai-chatbot/tasks.md

These tests verify that users can create tasks through natural language
conversations with the AI assistant.
"""
import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message
from models.conversation import Conversation
from models.task import Task
from core.database import get_db


@pytest.mark.asyncio
class TestChatTaskCreation:
    """Test suite for natural language task creation via chat."""

    async def test_create_task_via_simple_message(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test creating a task with a simple natural language message.

        [From]: specs/004-ai-chatbot/spec.md - US1-AC1

        User message: "Create a task to buy groceries"
        Expected: New task created with title "Buy groceries"
        """
        # Create conversation
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        # User sends message
        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Create a task to buy groceries",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing chat API, this will:
        # 1. POST to /api/{user_id}/chat with message
        # 2. AI agent processes via MCP add_task tool
        # 3. Verify task created in database
        # 4. Verify AI response message added

        # Placeholder assertion - will be updated when chat API implemented
        # Verify message was persisted
        assert user_message.content == "Create a task to buy groceries"
        assert user_message.role == "user"

    async def test_create_task_with_due_date(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test creating a task with due date in natural language.

        [From]: specs/004-ai-chatbot/spec.md - US1-AC2

        User message: "Remind me to finish the report by Friday"
        Expected: Task created with title "Finish the report" and due date
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Remind me to finish the report by Friday",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After chat API implementation, verify:
        # - Task created with proper due date parsing
        # - AI confirms the due date

    async def test_create_task_with_priority(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test creating a task with priority level.

        [From]: specs/004-ai-chatbot/spec.md - US1-AC3

        User message: "Add a high priority task to call the client"
        Expected: Task created with high priority
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Add a high priority task to call the client",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After chat API implementation, verify:
        # - Task created with priority="high"
        # - AI acknowledges priority level

    async def test_conversation_context_maintained(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test that AI maintains context across multiple messages.

        [From]: specs/004-ai-chatbot/spec.md - FR-040

        Scenario:
        1. User: "Create a task to learn Python"
        2. AI: Confirms task created
        3. User: "Make it due next week"
        4. AI: Updates the same task with due date
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        # First message
        msg1 = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Create a task to learn Python",
            created_at=datetime.utcnow()
        )
        async_session.add(msg1)
        await async_session.commit()

        # TODO: After AI response, send second message
        # msg2 = Message(..., content="Make it due next week")

        # TODO: Verify:
        # - Only one task created
        # - Task updated with due date
        # - Conversation history includes all messages

    async def test_ambiguous_request_clarification(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test AI asks for clarification on ambiguous requests.

        [From]: specs/004-ai-chatbot/spec.md - US1-AC4

        User message: "Create a task"
        Expected: AI asks "What task would you like to create?"
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Create a task",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After chat API implementation, verify:
        # - AI responds asking for clarification
        # - No task created yet
        # - User can provide details in next message

    async def test_message_persistence_before_ai_processing(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test that user messages are persisted before AI processing.

        [From]: specs/004-ai-chatbot/plan.md - Message Persistence

        This ensures message durability even if AI processing fails.
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Test message persistence",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # Verify message persisted
        result = await async_session.get(Message, user_message.id)
        assert result is not None
        assert result.content == "Test message persistence"

        # TODO: After chat API implementation, verify:
        # - Message saved before AI call made
        # - If AI fails, message still in database
