"""AI Agent streaming wrapper with WebSocket progress broadcasting.

[Task]: T072
[From]: specs/004-ai-chatbot/tasks.md

This module wraps the AI agent execution to broadcast real-time progress
events via WebSocket to connected clients. It provides hooks for tool-level
progress tracking.
"""
import logging
from typing import Optional

from ws_manager.events import (
    broadcast_agent_thinking,
    broadcast_agent_done,
    broadcast_tool_starting,
    broadcast_tool_complete,
    broadcast_tool_error,
)
from ai_agent import run_agent as base_run_agent

logger = logging.getLogger("ai_agent.streaming")


async def run_agent_with_streaming(
    messages: list[dict[str, str]],
    user_id: str,
    context: Optional[dict] = None
) -> str:
    """Run AI agent and broadcast progress events via WebSocket.

    [From]: specs/004-ai-chatbot/research.md - Section 6

    This wrapper broadcasts progress events during AI agent execution:
    1. agent_thinking - when processing starts
    2. agent_done - when processing completes

    Note: The OpenAI Agents SDK doesn't natively support streaming intermediate
    tool calls. For full tool-level progress, consider using the SDK's hooks
    or custom tool wrappers in future enhancements.

    Args:
        messages: Conversation history in OpenAI format
        user_id: User ID for WebSocket broadcasting and context
        context: Optional additional context for the agent

    Returns:
        str: Agent's final response message

    Example:
        response = await run_agent_with_streaming(
            messages=[{"role": "user", "content": "List my tasks"}],
            user_id="user-123"
        )
        # During execution, WebSocket clients receive:
        # - {"event_type": "agent_thinking", "message": "Processing..."}
        # - {"event_type": "agent_done", "message": "Done!", ...}
    """
    # Broadcast agent thinking start
    # [From]: specs/004-ai-chatbot/research.md - Section 6
    try:
        await broadcast_agent_thinking(user_id)
    except Exception as e:
        # Non-blocking - WebSocket failures shouldn't stop AI processing
        logger.warning(f"Failed to broadcast agent_thinking for user {user_id}: {e}")

    # Run the base agent
    # Note: For full tool-level progress, we'd need to wrap the tools themselves
    # or use SDK hooks. This is a foundation for future enhancement.
    try:
        response = await base_run_agent(
            messages=messages,
            user_id=user_id,
            context=context
        )

        # Broadcast agent done
        # [From]: specs/004-ai-chatbot/research.md - Section 6
        try:
            await broadcast_agent_done(user_id, response)
        except Exception as e:
            logger.warning(f"Failed to broadcast agent_done for user {user_id}: {e}")

        return response

    except Exception as e:
        # Broadcast error if agent fails
        logger.error(f"Agent execution failed for user {user_id}: {e}")
        # Re-raise for HTTP endpoint to handle
        raise


# Tool execution hooks for future enhancement
# These can be integrated when MCP tools are wrapped with progress tracking

async def execute_tool_with_progress(
    tool_name: str,
    tool_params: dict,
    user_id: str,
    tool_func
) -> dict:
    """Execute an MCP tool and broadcast progress events.

    [From]: specs/004-ai-chatbot/research.md - Section 6

    This is a template for future tool-level progress tracking.
    When MCP tools are wrapped, this function will:

    1. Broadcast tool_starting event
    2. Execute the tool
    3. Broadcast tool_complete or tool_error event

    Args:
        tool_name: Name of the tool being executed
        tool_params: Parameters to pass to the tool
        user_id: User ID for WebSocket broadcasting
        tool_func: The actual tool function to execute

    Returns:
        dict: Tool execution result

    Raises:
        Exception: If tool execution fails (after broadcasting error event)
    """
    # Broadcast tool starting
    try:
        await broadcast_tool_starting(user_id, tool_name, tool_params)
    except Exception as e:
        logger.warning(f"Failed to broadcast tool_starting for {tool_name}: {e}")

    # Execute the tool
    try:
        result = await tool_func(**tool_params)

        # Broadcast completion
        try:
            await broadcast_tool_complete(user_id, tool_name, result)
        except Exception as e:
            logger.warning(f"Failed to broadcast tool_complete for {tool_name}: {e}")

        return result

    except Exception as e:
        # Broadcast error
        try:
            await broadcast_tool_error(user_id, tool_name, str(e))
        except Exception as ws_error:
            logger.warning(f"Failed to broadcast tool_error for {tool_name}: {ws_error}")

        # Re-raise for calling code to handle
        raise


# Export the streaming version of run_agent
__all__ = [
    "run_agent_with_streaming",
    "execute_tool_with_progress",
]
