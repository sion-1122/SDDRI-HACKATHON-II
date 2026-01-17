"""MCP tool for completing/uncompleting tasks in the todo list.

[Task]: T042, T043
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to mark tasks as complete or incomplete
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
    "name": "complete_task",
    "description": """Mark a task as completed or not completed (toggle completion status).

Use this tool when the user wants to:
- Mark a task as complete, done, finished
- Mark a task as incomplete, pending, not done
- Unmark a task as complete (revert to pending)
- Toggle the completion status of a task

Parameters:
- user_id (required): User ID (UUID) who owns the task
- task_id (required): Task ID (UUID) of the task to mark complete/incomplete
- completed (required): True to mark as complete, False to mark as incomplete/pending

Returns: Updated task details with confirmation.
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
                "description": "Task ID (UUID) of the task to mark complete/incomplete"
            },
            "completed": {
                "type": "boolean",
                "description": "True to mark complete, False to mark incomplete"
            }
        },
        "required": ["user_id", "task_id", "completed"]
    }
}


async def complete_task(
    user_id: str,
    task_id: str,
    completed: bool
) -> dict[str, Any]:
    """Mark a task as completed or incomplete.

    [From]: specs/004-ai-chatbot/spec.md - US4

    Args:
        user_id: User ID (UUID string) who owns the task
        task_id: Task ID (UUID string) of the task to update
        completed: True to mark complete, False to mark incomplete

    Returns:
        Dictionary with updated task details

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

            # Update completion status
            old_status = "completed" if task.completed else "pending"
            task.completed = completed
            task.updated_at = datetime.utcnow()

            # Save to database
            db.add(task)
            db.commit()
            db.refresh(task)

            # Build success message
            new_status = "completed" if completed else "pending"
            action = "marked as complete" if completed else "marked as pending"
            message = f"✅ Task '{task.title}' {action}"

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "message": message,
                "old_status": old_status,
                "new_status": new_status
            }

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to update task completion status: {str(e)}")


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
    )(complete_task)
