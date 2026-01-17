"""MCP tool for deleting all tasks with confirmation.

[Task]: T048, T050
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to delete all tasks with safety checks.
"""
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select

from models.task import Task
from core.database import engine
from sqlmodel import Session


# Tool metadata for MCP registration
tool_metadata = {
    "name": "delete_all_tasks",
    "description": """Delete all tasks from the user's todo list permanently.

⚠️ DESTRUCTIVE OPERATION: This will permanently delete all tasks.

Use this tool when the user wants to:
- Delete all tasks, clear entire task list
- Remove every task from their list
- Start fresh with no tasks

IMPORTANT: Always inform the user about how many tasks will be deleted before proceeding.

Parameters:
- user_id (required): User ID (UUID) who owns the tasks
- status_filter (optional): Only delete tasks with this status ('pending' or 'completed')
- confirmed (required): Must be true to proceed with deletion

Returns: Summary with count of tasks deleted.
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (UUID) who owns these tasks"
            },
            "status_filter": {
                "type": "string",
                "enum": ["pending", "completed"],
                "description": "Optional: Only delete tasks with this status. If not provided, deletes all tasks."
            },
            "confirmed": {
                "type": "boolean",
                "description": "Must be true to proceed with deletion. This ensures user confirmation."
            }
        },
        "required": ["user_id", "confirmed"]
    }
}


async def delete_all_tasks(
    user_id: str,
    confirmed: bool,
    status_filter: Optional[str] = None
) -> dict[str, Any]:
    """Delete all tasks from the user's todo list.

    [From]: specs/004-ai-chatbot/spec.md - US5

    Args:
        user_id: User ID (UUID string) who owns the tasks
        confirmed: Must be True to actually delete (safety check)
        status_filter: Optional filter to only delete tasks with current status

    Returns:
        Dictionary with count of tasks deleted and confirmation message

    Raises:
        ValueError: If validation fails
    """
    # Get database session (synchronous)
    with Session(engine) as db:
        try:
            # If not confirmed, return task count for confirmation prompt
            if not confirmed:
                # Build query to count tasks
                stmt = select(Task).where(Task.user_id == UUID(user_id))

                if status_filter:
                    if status_filter == "pending":
                        stmt = stmt.where(Task.completed == False)
                    elif status_filter == "completed":
                        stmt = stmt.where(Task.completed == True)

                tasks = list(db.scalars(stmt).all())
                task_count = len(tasks)

                if task_count == 0:
                    return {
                        "success": False,
                        "error": "No tasks found",
                        "message": f"Could not find any tasks{' matching the filter' if status_filter else ''}"
                    }

                filter_msg = f" {status_filter}" if status_filter else ""
                return {
                    "success": True,
                    "requires_confirmation": True,
                    "task_count": task_count,
                    "message": f"⚠️ This will delete {task_count} {filter_msg} task(s). Please confirm by saying 'yes' or 'confirm'."
                }

            # Confirmed - proceed with deletion
            # Build query based on filter
            stmt = select(Task).where(Task.user_id == UUID(user_id))

            if status_filter:
                if status_filter == "pending":
                    stmt = stmt.where(Task.completed == False)
                elif status_filter == "completed":
                    stmt = stmt.where(Task.completed == True)

            # Fetch matching tasks
            tasks = list(db.scalars(stmt).all())

            if not tasks:
                return {
                    "success": False,
                    "error": "No tasks found",
                    "message": f"Could not find any tasks{' matching the filter' if status_filter else ''}"
                }

            # Count and delete tasks
            deleted_count = len(tasks)
            for task in tasks:
                db.delete(task)

            # Commit deletion
            db.commit()

            # Build success message
            filter_msg = f" {status_filter}" if status_filter else ""
            message = f"✅ Deleted {deleted_count} {filter_msg} task{'' if deleted_count == 1 else 's'}"

            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": message
            }

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to delete tasks: {str(e)}")


# Register tool with MCP server
def register_tool(mcp_server: Any) -> None:
    """Register this tool with the MCP server.

    [From]: backend/mcp_server/server.py

    Args:
        mcp_server: MCP server instance
    """
    mcp_server.tool(
        name=tool_metadata["name"],
        description=tool_metadata["description"]
    )(delete_all_tasks)
