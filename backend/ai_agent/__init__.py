"""AI Agent module for task management.

[Task]: T014, T072
[From]: specs/004-ai-chatbot/tasks.md

This module provides the AI agent that powers the chatbot functionality.
It uses OpenAI SDK with function calling and Gemini via AsyncOpenAI adapter.

Includes streaming support for real-time WebSocket progress events.
"""
from ai_agent.agent_simple import (
    get_gemini_client,
    run_agent,
    is_gemini_configured
)
from ai_agent.agent_streaming import (
    run_agent_with_streaming,
    execute_tool_with_progress,
)

__all__ = [
    "get_gemini_client",
    "run_agent",
    "run_agent_with_streaming",
    "execute_tool_with_progress",
    "is_gemini_configured"
]
