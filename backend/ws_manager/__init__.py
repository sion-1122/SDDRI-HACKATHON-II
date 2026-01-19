"""WebSocket connection management for real-time progress updates.

[Task]: T067
[From]: specs/004-ai-chatbot/tasks.md

This package provides WebSocket infrastructure for streaming AI agent
progress events to the frontend in real-time.
"""

from ws_manager.manager import manager
from ws_manager.events import (
    EventType,
    ToolProgressEvent,
    broadcast_progress,
)

__all__ = [
    "manager",
    "EventType",
    "ToolProgressEvent",
    "broadcast_progress",
]
