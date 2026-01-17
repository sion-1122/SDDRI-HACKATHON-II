"""MCP tool for listing tasks from the todo list.

[Task]: T024, T027
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to list and filter tasks on behalf of users
through natural language conversations.
"""
from typing import Optional, Any
from uuid import UUID
from datetime import datetime, timedelta, date
from sqlalchemy import select

from models.task import Task
from core.database import engine
from sqlmodel import Session


# Tool metadata for MCP registration
tool_metadata = {
    "name": "list_tasks",
    "description": """List and filter tasks from the user's todo list.

Use this tool when the user wants to see their tasks, ask what they have to do,
or request a filtered view of their tasks.

Parameters:
- user_id (required): User ID (UUID) who owns the tasks
- status (optional): Filter by completion status - 'all', 'pending', or 'completed' (default: 'all')
- due_within_days (optional): Only show tasks due within X days (default: null, shows all)
- limit (optional): Maximum number of tasks to return (default: 50, max: 100)

Returns: List of tasks with titles, descriptions, due dates, priorities, and completion status.
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (UUID) who owns these tasks"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter by completion status",
                "default": "all"
            },
            "due_within_days": {
                "type": "number",
                "description": "Only show tasks due within X days (optional)",
                "minimum": 0
            },
            "limit": {
                "type": "number",
                "description": "Maximum tasks to return",
                "default": 50,
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["user_id"]
    }
}


async def list_tasks(
    user_id: str,
    status: str = "all",
    due_within_days: Optional[int] = None,
    limit: int = 50
) -> dict[str, Any]:
    """List tasks for the user with optional filtering.

    [From]: specs/004-ai-chatbot/spec.md - US2

    Args:
        user_id: User ID (UUID string) who owns the tasks
        status: Filter by completion status ("all", "pending", "completed")
        due_within_days: Optional filter for tasks due within X days
        limit: Maximum number of tasks to return

    Returns:
        Dictionary with task list and metadata

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    # Validate inputs
    if status not in ["all", "pending", "completed"]:
        raise ValueError(f"Invalid status: {status}. Must be 'all', 'pending', or 'completed'")

    if limit < 1 or limit > 100:
        raise ValueError(f"Invalid limit: {limit}. Must be between 1 and 100")

    # Get database session (synchronous)
    with Session(engine) as db:
        try:
            # Build query
            stmt = select(Task).where(Task.user_id == UUID(user_id))

            # Apply status filter
            # [From]: T027 - Add task status filtering
            if status == "pending":
                stmt = stmt.where(Task.completed == False)
            elif status == "completed":
                stmt = stmt.where(Task.completed == True)

            # Apply due date filter if specified
            if due_within_days is not None:
                today = datetime.utcnow().date()
                max_due_date = today + timedelta(days=due_within_days)

                # Only show tasks that have a due_date AND are within the range
                stmt = stmt.where(
                    Task.due_date.isnot(None),
                    Task.due_date <= max_due_date
                )

            # Order by due date (if available) then created date
            # Tasks with due dates come first, ordered by due date ascending
            # Tasks without due dates come after, ordered by created date descending
            stmt = stmt.order_by(
                Task.due_date.asc().nulls_last(),
                Task.created_at.desc()
            )

            # Apply limit
            stmt = stmt.limit(limit)

            # Execute query
            tasks = db.scalars(stmt).all()

            # Convert to dict format for AI
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                task_list.append(task_dict)

            # Get summary statistics
            total_count = len(task_list)
            completed_count = sum(1 for t in task_list if t["completed"])
            pending_count = total_count - completed_count

            # Generate summary message for AI
            # [From]: T026 - Handle empty task list responses
            if total_count == 0:
                summary = "No tasks found"
            elif status == "all":
                summary = f"Found {total_count} tasks ({pending_count} pending, {completed_count} completed)"
            elif status == "pending":
                summary = f"Found {total_count} pending tasks"
            elif status == "completed":
                summary = f"Found {total_count} completed tasks"
            else:
                summary = f"Found {total_count} tasks"

            return {
                "success": True,
                "tasks": task_list,
                "summary": summary,
                "total": total_count,
                "pending": pending_count,
                "completed": completed_count
            }

        except Exception as e:
            raise Exception(f"Failed to list tasks: {str(e)}")


def format_task_list_for_ai(tasks: list[dict[str, Any]]) -> str:
    """Format task list for AI response.

    [From]: specs/004-ai-chatbot/spec.md - US2-AC1

    This helper function formats the task list in a readable way
    that the AI can use to generate natural language responses.

    Args:
        tasks: List of task dictionaries

    Returns:
        Formatted string representation of tasks

    Example:
        >>> tasks = [
        ...     {"title": "Buy groceries", "completed": False, "due_date": "2025-01-15"},
        ...     {"title": "Finish report", "completed": True}
        ... ]
        >>> format_task_list_for_ai(tasks)
        '1. Buy groceries (Due: 2025-01-15) [Pending]\\n2. Finish report [Completed]'
    """
    if not tasks:
        return "No tasks found."

    lines = []
    for i, task in enumerate(tasks, 1):
        # Task title
        line = f"{i}. {task['title']}"

        # Due date if available
        if task.get('due_date'):
            line += f" (Due: {task['due_date']})"

        # Priority if not default (medium)
        if task.get('priority') and task['priority'] != 'medium':
            line += f" [{task['priority'].capitalize()} Priority]"

        # Completion status
        status = "✓ Completed" if task['completed'] else "○ Pending"
        line += f" - {status}"

        # Description if available
        if task.get('description'):
            line += f"\n   {task['description']}"

        lines.append(line)

    return "\n".join(lines)


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
    )(list_tasks)
