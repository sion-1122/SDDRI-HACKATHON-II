"""Agents SDK function wrappers for MCP task management tools.

[Task]: T012-T018
[From]: specs/010-chatkit-migration/tasks.md - Phase 3 Backend Implementation
[From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts

This module wraps existing MCP tools as Agents SDK functions using the
@function_tool decorator. Each wrapper calls the underlying MCP tool function
and returns the result in a format compatible with the Agents SDK.

Tools wrapped:
1. create_task (T012) - from mcp_server/tools/add_task.py
2. list_tasks (T013) - from mcp_server/tools/list_tasks.py
3. update_task (T014) - from mcp_server/tools/update_task.py
4. delete_task (T015) - from mcp_server/tools/delete_task.py
5. complete_task (T016) - from mcp_server/tools/complete_task.py
6. complete_all_tasks (T017) - from mcp_server/tools/complete_all_tasks.py
7. delete_all_tasks (T018) - from mcp_server/tools/delete_all_tasks.py

[From]: specs/010-chatkit-migration/research.md - Section 7 (Tool Visualization Support)
"""
import json
import logging
from typing import Optional

from agents import function_tool, RunContextWrapper

# Import MCP tools
# Note: We import the actual async functions from MCP tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcp_server.tools.add_task import add_task as mcp_add_task
from mcp_server.tools.list_tasks import list_tasks as mcp_list_tasks
from mcp_server.tools.update_task import update_task as mcp_update_task
from mcp_server.tools.delete_task import delete_task as mcp_delete_task
from mcp_server.tools.complete_task import complete_task as mcp_complete_task
from mcp_server.tools.complete_all_tasks import complete_all_tasks as mcp_complete_all_tasks
from mcp_server.tools.delete_all_tasks import delete_all_tasks as mcp_delete_all_tasks

logger = logging.getLogger(__name__)


# =============================================================================
# Agents SDK Function Wrappers
# =============================================================================

@function_tool(
    name="create_task",
    description_override="Create a new task in the user's todo list. Use this when the user wants to create, add, or remind themselves about a task. Parameters: title (required), description (optional), due_date (optional, ISO 8601 or relative), priority (optional: low/medium/high), tags (optional list)."
)
async def create_task_tool(
    ctx: RunContextWrapper,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> str:
    """Create a task via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T012

    Args:
        ctx: Agents SDK run context containing user_id
        title: Task title
        description: Optional task description
        due_date: Optional due date
        priority: Optional priority level
        tags: Optional list of tags

    Returns:
        JSON string with created task details
    """
    user_id = ctx.context.user_id

    try:
        result = await mcp_add_task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            tags=tags or []
        )
        logger.info(f"Task created: {result['task']['id']} for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to create task for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


@function_tool(
    name="list_tasks",
    description_override="List all tasks for the user, optionally filtered by completion status, priority, tag, or due date range. Returns a list of tasks with their details."
)
async def list_tasks_tool(
    ctx: RunContextWrapper,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
) -> str:
    """List tasks via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T013

    Args:
        ctx: Agents SDK run context containing user_id
        completed: Optional filter by completion status
        priority: Optional filter by priority
        tag: Optional filter by tag
        due_before: Optional due date upper bound
        due_after: Optional due date lower bound

    Returns:
        JSON string with list of tasks
    """
    user_id = ctx.context.user_id

    try:
        result = await mcp_list_tasks(
            user_id=user_id,
            completed=completed,
            priority=priority,
            tag=tag,
            due_before=due_before,
            due_after=due_after
        )
        task_count = len(result.get("tasks", []))
        logger.info(f"Listed {task_count} tasks for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to list tasks for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e), "tasks": []})


@function_tool(
    name="update_task",
    description_override="Update an existing task. Parameters: task_id (required), title (optional), description (optional), due_date (optional), priority (optional), tags (optional)."
)
async def update_task_tool(
    ctx: RunContextWrapper,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> str:
    """Update a task via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T014

    Args:
        ctx: Agents SDK run context containing user_id
        task_id: Task ID to update
        title: Optional new title
        description: Optional new description
        due_date: Optional new due date
        priority: Optional new priority
        tags: Optional new tag list

    Returns:
        JSON string with updated task details
    """
    user_id = ctx.context.user_id

    try:
        result = await mcp_update_task(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            tags=tags
        )
        logger.info(f"Task updated: {task_id} for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to update task {task_id} for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


@function_tool(
    name="delete_task",
    description_override="Delete a task permanently. Parameters: task_id (required)."
)
async def delete_task_tool(
    ctx: RunContextWrapper,
    task_id: str,
) -> str:
    """Delete a task via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T015

    Args:
        ctx: Agents SDK run context containing user_id
        task_id: Task ID to delete

    Returns:
        JSON string with deletion confirmation
    """
    user_id = ctx.context.user_id

    try:
        result = await mcp_delete_task(
            user_id=user_id,
            task_id=task_id
        )
        logger.info(f"Task deleted: {task_id} for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to delete task {task_id} for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


@function_tool(
    name="complete_task",
    description_override="Mark a task as completed or incomplete. Parameters: task_id (required), completed (boolean, required)."
)
async def complete_task_tool(
    ctx: RunContextWrapper,
    task_id: str,
    completed: bool,
) -> str:
    """Complete/uncomplete a task via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T016

    Args:
        ctx: Agents SDK run context containing user_id
        task_id: Task ID to toggle
        completed: Whether task is completed (true) or not (false)

    Returns:
        JSON string with updated task details
    """
    user_id = ctx.context.user_id

    try:
        result = await mcp_complete_task(
            user_id=user_id,
            task_id=task_id,
            completed=completed
        )
        logger.info(f"Task completion updated: {task_id} -> {completed} for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to update completion for task {task_id} for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


@function_tool(
    name="complete_all_tasks",
    description_override="Mark all tasks as completed. Parameters: confirm (boolean, required - must be true to execute)."
)
async def complete_all_tasks_tool(
    ctx: RunContextWrapper,
    confirm: bool,
) -> str:
    """Complete all tasks via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T017

    Args:
        ctx: Agents SDK run context containing user_id
        confirm: Must be true to execute this destructive operation

    Returns:
        JSON string with bulk completion results
    """
    user_id = ctx.context.user_id

    if not confirm:
        return json.dumps({
            "success": False,
            "error": "Confirmation required. Set confirm=true to complete all tasks."
        })

    try:
        result = await mcp_complete_all_tasks(
            user_id=user_id
        )
        completed_count = result.get("completed_count", 0)
        logger.info(f"Completed {completed_count} tasks for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to complete all tasks for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


@function_tool(
    name="delete_all_tasks",
    description_override="Delete all tasks permanently. Parameters: confirm (boolean, required - must be true to execute)."
)
async def delete_all_tasks_tool(
    ctx: RunContextWrapper,
    confirm: bool,
) -> str:
    """Delete all tasks via MCP tool.

    [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
    [Task]: T018

    Args:
        ctx: Agents SDK run context containing user_id
        confirm: Must be true to execute this destructive operation

    Returns:
        JSON string with bulk deletion results
    """
    user_id = ctx.context.user_id

    if not confirm:
        return json.dumps({
            "success": False,
            "error": "Confirmation required. Set confirm=true to delete all tasks."
        })

    try:
        result = await mcp_delete_all_tasks(
            user_id=user_id
        )
        deleted_count = result.get("deleted_count", 0)
        logger.info(f"Deleted {deleted_count} tasks for user {user_id}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to delete all tasks for user {user_id}: {e}")
        return json.dumps({"success": False, "error": str(e)})


# =============================================================================
# Tool List for Agent Configuration
# =============================================================================

# Export all tool functions for easy import
TOOL_FUNCTIONS = [
    create_task_tool,
    list_tasks_tool,
    update_task_tool,
    delete_task_tool,
    complete_task_tool,
    complete_all_tasks_tool,
    delete_all_tasks_tool,
]


def get_tool_names() -> list[str]:
    """Get list of all tool names.

    [From]: specs/010-chatkit-migration/tasks.md - T019

    Returns:
        List of tool function names
    """
    return [tool.name for tool in TOOL_FUNCTIONS]
