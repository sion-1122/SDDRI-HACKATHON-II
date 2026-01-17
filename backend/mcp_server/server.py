"""Tool registry for AI agent.

[Task]: T009
[From]: specs/004-ai-chatbot/plan.md

This module provides a simple registry for tools that the AI agent can use.
Note: We're using OpenAI Agents SDK's built-in tool calling mechanism,
not the full Model Context Protocol server.
"""
from typing import Any, Callable, Dict
import logging

logger = logging.getLogger(__name__)

# Tool registry - maps tool names to their functions
tool_registry: Dict[str, Callable] = {}


def register_tool(name: str, func: Callable) -> None:
    """Register a tool function.

    Args:
        name: Tool name
        func: Tool function (async)
    """
    tool_registry[name] = func
    logger.info(f"Registered tool: {name}")


def get_tool(name: str) -> Callable:
    """Get a registered tool by name.

    Args:
        name: Tool name

    Returns:
        The tool function

    Raises:
        ValueError: If tool not found
    """
    if name not in tool_registry:
        raise ValueError(f"Tool '{name}' not found. Available tools: {list(tool_registry.keys())}")
    return tool_registry[name]


def list_tools() -> list[str]:
    """List all registered tools.

    Returns:
        List of tool names
    """
    return list(tool_registry.keys())


# Note: Tools are registered in the tools/__init__.py module
# The OpenAI Agents SDK will call these functions directly
# based on the agent's instructions and user input
