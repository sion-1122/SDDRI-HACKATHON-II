"""Tools for task management AI agent.

[Task]: T010
[From]: specs/004-ai-chatbot/plan.md

This module provides tools that enable the AI agent to perform task
management operations through a standardized interface.

All tools enforce:
- User isolation via user_id parameter
- Stateless execution (no shared memory between invocations)
- Structured success/error responses
- Parameter validation

Tool Registration Pattern:
    Tools are registered in the tool_registry for discovery.
    The OpenAI Agents SDK will call these functions directly.
"""
from mcp_server.server import register_tool
from mcp_server.tools import (
    add_task, list_tasks, update_task, complete_task, delete_task,
    complete_all_tasks, delete_all_tasks
)

# Register all available tools
# [Task]: T013 - add_task tool
register_tool("add_task", add_task.add_task)

# [Task]: T024, T027 - list_tasks tool
register_tool("list_tasks", list_tasks.list_tasks)

# [Task]: T037 - update_task tool
register_tool("update_task", update_task.update_task)

# [Task]: T042 - complete_task tool
register_tool("complete_task", complete_task.complete_task)

# [Task]: T047 - delete_task tool
register_tool("delete_task", delete_task.delete_task)

# [Task]: T044, T045 - complete_all_tasks tool
register_tool("complete_all_tasks", complete_all_tasks.complete_all_tasks)

# [Task]: T048, T050 - delete_all_tasks tool
register_tool("delete_all_tasks", delete_all_tasks.delete_all_tasks)

# Export tool functions for direct access by the agent
__all__ = [
    "add_task", "list_tasks", "update_task", "complete_task", "delete_task",
    "complete_all_tasks", "delete_all_tasks"
]
