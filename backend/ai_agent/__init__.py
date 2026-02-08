"""AI Agent module for task management.

[Task]: T014, T072
[From]: specs/004-ai-chatbot/tasks.md
[From]: T045 - Delete agent_streaming.py (ChatKit migration replaces WebSocket streaming)

This module provides the AI agent that powers the chatbot functionality.
It uses OpenAI SDK with function calling and Gemini via AsyncOpenAI adapter.

NOTE: The streaming agent functionality has been migrated to ChatKit SSE endpoint.
See backend/chatkit_server.py for the new ChatKit-based implementation.
"""
from ai_agent.agent_simple import (
    get_gemini_client,
    run_agent,
    is_gemini_configured
)

__all__ = [
    "get_gemini_client",
    "run_agent",
    "is_gemini_configured"
]
