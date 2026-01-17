"""MCP tool for deleting tasks from the todo list.

[Task]: T047
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to permanently delete tasks
through natural language conversations.
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
    "name": "delete_task",
    "description": """Delete a task from the user's todo list permanently.

Use this tool when the user wants to:
- Delete, remove, or get rid of a task
- Clear a task from their list
- Permanently remove a task

Parameters:
- user_id (required): User ID (UUID) who owns the task
- task_id (required): Task ID (UUID) of the task to delete

Returns: Confirmation of deletion with task details.
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (UUID) who owns this task"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID (UUID) of the task to delete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}


async def delete_task(
    user_id: str,
    task_id: str
) -> dict[str, Any]:
    """Delete a task from the user's todo list.

    [From]: specs/004-ai-chatbot/spec.md - US5

    Args:
        user_id: User ID (UUID string) who owns the task
        task_id: Task ID (UUID string) of the task to delete

    Returns:
        Dictionary with deletion confirmation

    Raises:
        ValueError: If validation fails or task not found
    """
    # Get database session (synchronous)
    with Session(engine) as db:
        try:
            # Fetch the task
            stmt = select(Task).where(
                Task.id == UUID(task_id),
                Task.user_id == UUID(user_id)
            )
            task = db.scalars(stmt).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Could not find task with ID {task_id}"
                }

            # Store task details for confirmation
            task_details = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            # Delete the task
            db.delete(task)
            db.commit()

            # Build success message
            message = f"✅ Task '{task.title}' deleted successfully"

            return {
                "success": True,
                "task": task_details,
                "message": message
            }

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to delete task: {str(e)}")


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
    )(delete_task)
