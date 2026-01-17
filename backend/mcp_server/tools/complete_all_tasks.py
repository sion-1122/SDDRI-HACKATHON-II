"""MCP tool for marking all tasks as complete or incomplete.

[Task]: T044, T045
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to mark all tasks with a completion status
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
    "name": "complete_all_tasks",
    "description": """Mark all tasks as completed or not completed.

Use this tool when the user wants to:
- Mark all tasks as complete, done, or finished
- Mark all tasks as incomplete or pending
- Complete every task in their list

Parameters:
- user_id (required): User ID (UUID) who owns the tasks
- completed (required): True to mark all complete, False to mark all incomplete
- status_filter (optional): Only affect tasks with this status ('pending' or 'completed')

Returns: Summary with count of tasks updated.
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (UUID) who owns these tasks"
            },
            "completed": {
                "type": "boolean",
                "description": "True to mark all tasks complete, False to mark all incomplete"
            },
            "status_filter": {
                "type": "string",
                "enum": ["pending", "completed"],
                "description": "Optional: Only affect tasks with this status. If not provided, affects all tasks."
            }
        },
        "required": ["user_id", "completed"]
    }
}


async def complete_all_tasks(
    user_id: str,
    completed: bool,
    status_filter: Optional[str] = None
) -> dict[str, Any]:
    """Mark all tasks as completed or incomplete.

    [From]: specs/004-ai-chatbot/spec.md - US4

    Args:
        user_id: User ID (UUID string) who owns the tasks
        completed: True to mark all complete, False to mark all incomplete
        status_filter: Optional filter to only affect tasks with current status

    Returns:
        Dictionary with count of tasks updated and confirmation message

    Raises:
        ValueError: If validation fails
    """
    # Get database session (synchronous)
    with Session(engine) as db:
        try:
            # Build query based on filter
            stmt = select(Task).where(Task.user_id == UUID(user_id))

            # Apply status filter if provided
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

            # Count tasks before update
            task_count = len(tasks)
            already_correct = sum(1 for t in tasks if t.completed == completed)

            # If all tasks already have the desired status
            if already_correct == task_count:
                status_word = "completed" if completed else "pending"
                return {
                    "success": True,
                    "updated_count": 0,
                    "skipped_count": task_count,
                    "message": f"All {task_count} task(s) are already {status_word}."
                }

            # Update completion status for all tasks
            updated_count = 0
            for task in tasks:
                if task.completed != completed:
                    task.completed = completed
                    task.updated_at = datetime.utcnow()
                    db.add(task)
                    updated_count += 1

            # Save to database
            db.commit()

            # Build success message
            action = "completed" if completed else "marked as pending"
            if status_filter:
                filter_msg = f" {status_filter} tasks"
            else:
                filter_msg = ""

            message = f"✅ {updated_count} task{'' if updated_count == 1 else 's'}{filter_msg} marked as {action}"

            return {
                "success": True,
                "updated_count": updated_count,
                "skipped_count": already_correct,
                "total_count": task_count,
                "message": message
            }

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to update tasks: {str(e)}")


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
    )(complete_all_tasks)
