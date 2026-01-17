"""AI Agent module for task management.

[Task]: T014
[From]: specs/004-ai-chatbot/tasks.md

This module provides the AI agent that powers the chatbot functionality.
It uses OpenAI SDK with function calling and Gemini via AsyncOpenAI adapter.
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
