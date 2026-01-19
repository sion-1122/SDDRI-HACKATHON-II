"""WebSocket event types and broadcasting utilities.

[Task]: T069, T070
[From]: specs/004-ai-chatbot/tasks.md

This module defines the event types for real-time progress streaming
and provides helper functions for broadcasting events to WebSocket clients.
"""
import json
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ws_manager.manager import manager

logger = logging.getLogger("websockets.events")


class EventType(str, Enum):
    """WebSocket event types for real-time progress updates.

    [From]: specs/004-ai-chatbot/plan.md - WebSocket Event Types table

    Events flow in this order during AI agent processing:
    1. connection_established - WebSocket connection confirmed
    2. agent_thinking - AI agent is processing the request
    3. tool_starting - A tool is about to be executed
    4. tool_progress - Tool execution progress (e.g., "found 3 tasks")
    5. tool_complete - Tool finished successfully
    6. tool_error - Tool execution failed
    7. agent_done - AI agent finished, final response ready
    """

    CONNECTION_ESTABLISHED = "connection_established"
    """WebSocket connection successfully established."""

    AGENT_THINKING = "agent_thinking"
    """AI agent is processing the user's request."""

    TOOL_STARTING = "tool_starting"
    """A tool is about to be executed (e.g., "Searching your tasks...")."""

    TOOL_PROGRESS = "tool_progress"
    """Tool execution intermediate progress (e.g., "Found 3 tasks")."""

    TOOL_COMPLETE = "tool_complete"
    """Tool finished successfully with result."""

    TOOL_ERROR = "tool_error"
    """Tool execution failed with error."""

    AGENT_DONE = "agent_done"
    """AI agent finished processing, final response is ready."""


class ToolProgressEvent(BaseModel):
    """Structured event for tool execution progress.

    [From]: specs/004-ai-chatbot/research.md - Section 4

    This model is used to serialize progress events to JSON for WebSocket transmission.
    All fields are optional except event_type and message to support different event types.

    Attributes:
        event_type: The type of event (from EventType enum)
        tool: Name of the tool being executed (if applicable)
        task_id: ID of a task being operated on (if applicable)
        count: Numeric count for progress (e.g., tasks found)
        message: Human-readable progress message
        result: Tool execution result (for tool_complete events)
        error: Error message (for tool_error events)
    """

    event_type: EventType = Field(
        ...,
        description="Type of progress event"
    )
    tool: str | None = Field(
        None,
        description="Name of the tool being executed (e.g., 'list_tasks')"
    )
    task_id: str | None = Field(
        None,
        description="ID of a task being operated on"
    )
    count: int | None = Field(
        None,
        description="Numeric count for progress (e.g., number of tasks found)"
    )
    message: str = Field(
        ...,
        description="Human-readable progress message"
    )
    result: dict[str, Any] | None = Field(
        None,
        description="Tool execution result (for tool_complete events)"
    )
    error: str | None = Field(
        None,
        description="Error message (for tool_error events)"
    )


# User-friendly message templates for tool events
# [From]: specs/004-ai-chatbot/research.md - Section 6
TOOL_STARTING_MESSAGES = {
    "list_tasks": "Searching your tasks...",
    "add_task": "Creating a new task...",
    "update_task": "Updating your task...",
    "complete_task": "Updating task status...",
    "delete_task": "Deleting your task...",
    "complete_all_tasks": "Marking tasks as complete...",
    "delete_all_tasks": "Deleting tasks...",
}

TOOL_COMPLETE_MESSAGES = {
    "list_tasks": lambda count: f"Found {count} task{'s' if count != 1 else ''}",
    "add_task": lambda task: f"Created: {task.get('title', 'Task')}",
    "update_task": lambda task: "Task updated",
    "complete_task": lambda _: "Task status updated",
    "delete_task": lambda _: "Task deleted",
    "complete_all_tasks": lambda count: f"Marked {count} task{'s' if count != 1 else ''} as complete",
    "delete_all_tasks": lambda count: f"Deleted {count} task{'s' if count != 1 else ''}",
}


def format_tool_starting_message(tool: str, params: dict[str, Any] | None = None) -> str:
    """Generate user-friendly message for tool starting event.

    [From]: specs/004-ai-chatbot/research.md - Section 6

    Args:
        tool: The tool name being executed
        params: Optional tool parameters for context

    Returns:
        User-friendly message describing what's happening
    """
    return TOOL_STARTING_MESSAGES.get(tool, f"Running {tool}...")


def format_tool_complete_message(tool: str, result: dict[str, Any]) -> str:
    """Generate user-friendly message for tool complete event.

    [From]: specs/004-ai-chatbot/research.md - Section 6

    Args:
        tool: The tool name that completed
        result: The tool execution result

    Returns:
        User-friendly message describing the result
    """
    message_func = TOOL_COMPLETE_MESSAGES.get(tool)
    if message_func:
        try:
            return message_func(result)
        except (KeyError, TypeError):
            return f"Completed {tool}"
    return f"Completed {tool}"


async def broadcast_progress(user_id: str, event: ToolProgressEvent) -> None:
    """Send progress event to all WebSocket connections for a user.

    [From]: specs/004-ai-chatbot/research.md - Section 4
    [Task]: T070

    This is the primary function called by the AI agent to broadcast
    progress events during tool execution. It's non-blocking - if
    WebSocket fails, the AI processing continues.

    Args:
        user_id: The user's unique identifier (UUID string)
        event: The ToolProgressEvent to broadcast

    Example:
        await broadcast_progress(user_id, ToolProgressEvent(
            event_type=EventType.TOOL_COMPLETE,
            tool="list_tasks",
            message="Found 3 tasks",
            count=3
        ))
    """
    try:
        await manager.broadcast(user_id, event.model_dump())
        logger.debug(f"Broadcasted {event.event_type} event for user {user_id}")
    except Exception as e:
        # Log but don't raise - WebSocket failures shouldn't block AI processing
        logger.warning(f"Failed to broadcast progress event for user {user_id}: {e}")


async def broadcast_agent_thinking(user_id: str) -> None:
    """Broadcast that AI agent is thinking.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.AGENT_THINKING,
        message="Processing your request..."
    ))


async def broadcast_tool_starting(user_id: str, tool: str, params: dict[str, Any] | None = None) -> None:
    """Broadcast that a tool is starting execution.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
        tool: The tool name
        params: Optional tool parameters
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.TOOL_STARTING,
        tool=tool,
        message=format_tool_starting_message(tool, params)
    ))


async def broadcast_tool_progress(user_id: str, tool: str, message: str, count: int | None = None) -> None:
    """Broadcast tool execution progress.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
        tool: The tool name
        message: Progress message
        count: Optional count for progress
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.TOOL_PROGRESS,
        tool=tool,
        message=message,
        count=count
    ))


async def broadcast_tool_complete(user_id: str, tool: str, result: dict[str, Any]) -> None:
    """Broadcast that a tool completed successfully.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
        tool: The tool name
        result: Tool execution result
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.TOOL_COMPLETE,
        tool=tool,
        message=format_tool_complete_message(tool, result),
        result=result
    ))


async def broadcast_tool_error(user_id: str, tool: str, error: str) -> None:
    """Broadcast that a tool execution failed.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
        tool: The tool name
        error: Error message
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.TOOL_ERROR,
        tool=tool,
        message=f"Error in {tool}: {error}",
        error=error
    ))


async def broadcast_agent_done(user_id: str, response: str) -> None:
    """Broadcast that AI agent finished processing.

    Helper function for common event type.

    Args:
        user_id: The user's unique identifier
        response: The final AI response
    """
    await broadcast_progress(user_id, ToolProgressEvent(
        event_type=EventType.AGENT_DONE,
        message="Done!",
        result={"response": response}
    ))
