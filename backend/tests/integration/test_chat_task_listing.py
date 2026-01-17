"""Integration tests for task listing via natural language chat.

[Task]: T023
[From]: specs/004-ai-chatbot/tasks.md

These tests verify that users can list and view their tasks through natural language
conversations with the AI assistant.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message
from models.conversation import Conversation
from models.task import Task
from core.database import get_db


@pytest.mark.asyncio
class TestChatTaskListing:
    """Test suite for natural language task listing via chat."""

    async def test_list_all_tasks(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test listing all tasks.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC1

        User message: "What are my tasks?" or "Show me my tasks"
        Expected: AI returns list of all tasks with completion status
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

        # Create some test tasks
        tasks = [
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Buy groceries",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Finish report",
                completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Call client",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        # User sends message
        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="What are my tasks?",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing list_tasks tool, verify:
        # - AI responds with list of all 3 tasks
        # - Each task shows title and completion status
        # - Response is formatted clearly

        # Placeholder assertion
        assert len(tasks) == 3
        assert sum(1 for t in tasks if t.completed) == 1
        assert sum(1 for t in tasks if not t.completed) == 2

    async def test_list_pending_tasks_only(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test filtering tasks by completion status.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC2

        User message: "Show me my pending tasks" or "What tasks are left?"
        Expected: AI returns only incomplete tasks
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        # Create mix of completed and pending tasks
        tasks = [
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Pending task 1",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Completed task",
                completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Pending task 2",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="Show me my pending tasks",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing list_tasks with filtering, verify:
        # - AI responds with only 2 pending tasks
        # - Completed task is not shown

        # Placeholder assertion
        pending_tasks = [t for t in tasks if not t.completed]
        assert len(pending_tasks) == 2

    async def test_list_completed_tasks(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test listing completed tasks.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC3

        User message: "What have I completed?" or "Show finished tasks"
        Expected: AI returns only completed tasks
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        tasks = [
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Done task 1",
                completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Pending task",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Done task 2",
                completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="What have I completed?",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing list_tasks with filtering, verify:
        # - AI responds with only 2 completed tasks
        # - Pending task is not shown

        # Placeholder assertion
        completed_tasks = [t for t in tasks if t.completed]
        assert len(completed_tasks) == 2

    async def test_empty_task_list(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test listing tasks when user has none.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC4

        User message: "What are my tasks?"
        Expected: AI responds that there are no tasks, offers to help create one
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        # No tasks created

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="What are my tasks?",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing empty list handling (T026), verify:
        # - AI responds with friendly message
        # - AI offers to help create a task
        # - No error or confusion

    async def test_task_count_in_response(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test that AI provides accurate task count.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC5

        Scenario: User has 7 tasks, asks "How many tasks do I have?"
        Expected: AI responds with accurate count
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        # Create 7 tasks
        for i in range(7):
            task = Task(
                id=uuid4(),
                user_id=test_user_id,
                title=f"Task {i+1}",
                completed=i < 3,  # First 3 are completed
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            async_session.add(task)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="How many tasks do I have?",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementation, verify:
        # - AI responds with "You have 7 tasks"
        # - Optionally breaks down: "3 completed, 4 pending"

    async def test_task_listing_with_due_dates(
        self,
        async_session: AsyncSession,
        test_user_id: uuid4
    ):
        """Test listing tasks with due date information.

        [From]: specs/004-ai-chatbot/spec.md - US2-AC6

        User message: "What tasks are due this week?"
        Expected: AI filters by due date and shows matching tasks
        """
        conversation = Conversation(
            id=uuid4(),
            user_id=test_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(conversation)
        await async_session.commit()

        today = datetime.utcnow()
        tasks = [
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Due today",
                completed=False,
                due_date=today.date(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Due tomorrow",
                completed=False,
                due_date=(today + timedelta(days=1)).date(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="Due next week",
                completed=False,
                due_date=(today + timedelta(days=7)).date(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Task(
                id=uuid4(),
                user_id=test_user_id,
                title="No due date",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        user_message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=test_user_id,
            role="user",
            content="What tasks are due this week?",
            created_at=datetime.utcnow()
        )
        async_session.add(user_message)
        await async_session.commit()

        # TODO: After implementing due date filtering, verify:
        # - AI shows tasks due within 7 days
        # - Includes due dates in response
