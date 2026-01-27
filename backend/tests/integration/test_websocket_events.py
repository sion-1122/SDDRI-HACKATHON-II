"""Integration tests for WebSocket progress event broadcasting.

[Task]: T080
[From]: specs/004-ai-chatbot/tasks.md

These tests verify that progress events are correctly broadcast
during AI agent tool execution.
"""
import asyncio
import uuid
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from core.database import get_db
from core.security import create_access_token
from main import app
from websockets.events import (
    EventType,
    ToolProgressEvent,
    broadcast_progress,
    broadcast_agent_thinking,
    broadcast_tool_starting,
    broadcast_tool_complete,
    broadcast_tool_error,
    broadcast_agent_done,
)
from websockets.manager import manager


# Test database session dependency override
@pytest.fixture
def db_session():
    """Mock database session for testing."""
    yield MagicMock()


@pytest.fixture
def test_user():
    """Create a test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def test_jwt(test_user):
    """Create a test JWT token."""
    return create_access_token({"sub": test_user})


@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestProgressEventBroadcasting:
    """Tests for progress event broadcasting functionality."""

    @pytest.mark.asyncio
    async def test_broadcast_progress_event(self, test_user):
        """Test that progress events can be broadcast to a user.

        [From]: specs/004-ai-chatbot/research.md - Section 4
        """
        # Clear any existing connections
        manager.active_connections.clear()

        # Create mock WebSocket connection
        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()

        # Connect the mock WebSocket
        await manager.connect(test_user, mock_ws)

        # Broadcast a test event
        test_event = ToolProgressEvent(
            event_type=EventType.TOOL_COMPLETE,
            tool="list_tasks",
            message="Found 3 tasks",
            count=3
        )

        await broadcast_progress(test_user, test_event)

        # Verify the event was sent
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "tool_complete"
        assert call_args["tool"] == "list_tasks"
        assert call_args["message"] == "Found 3 tasks"
        assert call_args["count"] == 3

    @pytest.mark.asyncio
    async def test_broadcast_agent_thinking(self, test_user):
        """Test broadcasting agent_thinking event.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        manager.active_connections.clear()

        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()
        await manager.connect(test_user, mock_ws)

        await broadcast_agent_thinking(test_user)

        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "agent_thinking"
        assert "Processing" in call_args["message"]

    @pytest.mark.asyncio
    async def test_broadcast_tool_starting(self, test_user):
        """Test broadcasting tool_starting event.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        manager.active_connections.clear()

        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()
        await manager.connect(test_user, mock_ws)

        await broadcast_tool_starting(test_user, "list_tasks", {})

        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "tool_starting"
        assert call_args["tool"] == "list_tasks"
        assert "Searching" in call_args["message"]

    @pytest.mark.asyncio
    async def test_broadcast_tool_complete(self, test_user):
        """Test broadcasting tool_complete event.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        manager.active_connections.clear()

        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()
        await manager.connect(test_user, mock_ws)

        result = {"tasks": [{"id": 1, "title": "Task 1"}]}
        await broadcast_tool_complete(test_user, "list_tasks", result)

        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "tool_complete"
        assert call_args["tool"] == "list_tasks"
        assert "Found" in call_args["message"]
        assert call_args["result"] == result

    @pytest.mark.asyncio
    async def test_broadcast_tool_error(self, test_user):
        """Test broadcasting tool_error event.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        manager.active_connections.clear()

        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()
        await manager.connect(test_user, mock_ws)

        await broadcast_tool_error(test_user, "list_tasks", "Database error")

        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "tool_error"
        assert call_args["tool"] == "list_tasks"
        assert "Database error" in call_args["message"]
        assert call_args["error"] == "Database error"

    @pytest.mark.asyncio
    async def test_broadcast_agent_done(self, test_user):
        """Test broadcasting agent_done event.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        manager.active_connections.clear()

        mock_ws = MagicMock()
        mock_ws.send_json = AsyncMock()
        await manager.connect(test_user, mock_ws)

        response = "I found 3 tasks for you."
        await broadcast_agent_done(test_user, response)

        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]

        assert call_args["event_type"] == "agent_done"
        assert call_args["message"] == "Done!"
        assert call_args["result"]["response"] == response

    @pytest.mark.asyncio
    async def test_broadcast_to_no_connections(self, test_user):
        """Test that broadcasting to a user with no connections doesn't error.

        [From]: specs/004-ai-chatbot/research.md - Section 4
        """
        manager.active_connections.clear()

        # Should not raise an error
        await broadcast_agent_thinking(test_user)

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_connections(self, test_user):
        """Test that broadcasting reaches all connections for a user.

        [From]: specs/004-ai-chatbot/research.md - Section 4
        """
        manager.active_connections.clear()

        # Create multiple mock connections
        mock_ws1 = MagicMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = MagicMock()
        mock_ws2.send_json = AsyncMock()

        await manager.connect(test_user, mock_ws1)
        await manager.connect(test_user, mock_ws2)

        await broadcast_agent_thinking(test_user)

        # Both connections should receive the event
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()

        # Verify same event was sent to both
        call1 = mock_ws1.send_json.call_args[0][0]
        call2 = mock_ws2.send_json.call_args[0][0]

        assert call1["event_type"] == call2["event_type"]
        assert call1["message"] == call2["message"]


class TestToolProgressEventModel:
    """Tests for ToolProgressEvent model validation."""

    def test_tool_progress_event_serialization(self):
        """Test that ToolProgressEvent serializes to JSON correctly.

        [From]: specs/004-ai-chatbot/research.md - Section 4
        """
        event = ToolProgressEvent(
            event_type=EventType.TOOL_COMPLETE,
            tool="list_tasks",
            message="Found 3 tasks",
            count=3,
            result={"tasks": []}
        )

        serialized = event.model_dump()

        assert serialized["event_type"] == "tool_complete"
        assert serialized["tool"] == "list_tasks"
        assert serialized["message"] == "Found 3 tasks"
        assert serialized["count"] == 3
        assert serialized["result"] == {"tasks": []}

    def test_tool_progress_event_minimal(self):
        """Test ToolProgressEvent with minimal required fields.

        [From]: specs/004-ai-chatbot/research.md - Section 4
        """
        event = ToolProgressEvent(
            event_type=EventType.AGENT_THINKING,
            message="Processing..."
        )

        serialized = event.model_dump()

        assert serialized["event_type"] == "agent_thinking"
        assert serialized["message"] == "Processing..."
        assert serialized["tool"] is None
        assert serialized["count"] is None


class TestMessageFormatting:
    """Tests for user-friendly message formatting."""

    def test_format_tool_starting_messages(self):
        """Test that tool starting messages are user-friendly.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        from websockets.events import format_tool_starting_message

        assert "Searching" in format_tool_starting_message("list_tasks")
        assert "Creating" in format_tool_starting_message("add_task")
        assert "Updating" in format_tool_starting_message("update_task")
        assert "complete" in format_tool_starting_message("complete_task").lower()
        assert "Deleting" in format_tool_starting_message("delete_task")

    def test_format_tool_complete_messages(self):
        """Test that tool complete messages are user-friendly.

        [From]: specs/004-ai-chatbot/research.md - Section 6
        """
        from websockets.events import format_tool_complete_message

        # Test list_tasks with count
        msg = format_tool_complete_message("list_tasks", {"count": 3})
        assert "3" in msg
        assert "task" in msg

        # Test list_tasks singular
        msg = format_tool_complete_message("list_tasks", {"count": 1})
        assert "1" in msg
        assert "task" in msg

        # Test add_task
        msg = format_tool_complete_message("add_task", {"title": "Buy groceries"})
        assert "Created" in msg
        assert "Buy groceries" in msg
