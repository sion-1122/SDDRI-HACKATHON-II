"""MCP tool for updating tasks in the todo list.

[Task]: T037
[From]: specs/004-ai-chatbot/tasks.md

This tool allows the AI agent to update existing tasks on behalf of users
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
    "name": "update_task",
    "description": """Update an existing task in the user's todo list.

Use this tool when the user wants to modify, change, or edit an existing task.
You must identify the task first (by ID or by matching title/description).

Parameters:
- user_id (required): User ID (UUID) who owns the task
- task_id (required): Task ID (UUID) of the task to update
- title (optional): New task title
- description (optional): New task description
- due_date (optional): New due date (ISO 8601 date string or relative like 'tomorrow', 'next week')
- priority (optional): New priority level - 'low', 'medium', or 'high'
- completed (optional): Mark task as completed or not completed

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
                "description": "Task ID (UUID) of the task to update"
            },
            "title": {
                "type": "string",
                "description": "New task title (brief description)",
                "maxLength": 255
            },
            "description": {
                "type": "string",
                "description": "New task description",
                "maxLength": 2000
            },
            "due_date": {
                "type": "string",
                "description": "New due date in ISO 8601 format (e.g., '2025-01-15') or relative terms"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "New task priority level"
            },
            "completed": {
                "type": "boolean",
                "description": "Mark task as completed or not completed"
            }
        },
        "required": ["user_id", "task_id"]
    }
}


async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None
) -> dict[str, Any]:
    """Update an existing task for the user.

    [From]: specs/004-ai-chatbot/spec.md - US3

    Args:
        user_id: User ID (UUID string) who owns the task
        task_id: Task ID (UUID string) of the task to update
        title: Optional new task title
        description: Optional new task description
        due_date: Optional new due date (ISO 8601 or relative)
        priority: Optional new priority level (low/medium/high)
        completed: Optional new completion status

    Returns:
        Dictionary with updated task details

    Raises:
        ValueError: If validation fails or task not found
    """
    from core.validators import validate_task_title, validate_task_description

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

            # Track changes for confirmation message
            changes = []

            # Update title if provided
            if title is not None:
                validated_title = validate_task_title(title)
                old_title = task.title
                task.title = validated_title
                changes.append(f"title from '{old_title}' to '{validated_title}'")

            # Update description if provided
            if description is not None:
                validated_description = validate_task_description(description) if description else None
                task.description = validated_description
                changes.append("description")

            # Update due date if provided
            if due_date is not None:
                parsed_due_date = _parse_due_date(due_date)
                task.due_date = parsed_due_date
                changes.append(f"due date to '{parsed_due_date.isoformat() if parsed_due_date else 'None'}'")

            # Update priority if provided
            if priority is not None:
                normalized_priority = _normalize_priority(priority)
                old_priority = task.priority
                task.priority = normalized_priority
                changes.append(f"priority from '{old_priority}' to '{normalized_priority}'")

            # Update completion status if provided
            if completed is not None:
                old_status = "completed" if task.completed else "pending"
                task.completed = completed
                new_status = "completed" if completed else "pending"
                changes.append(f"status from '{old_status}' to '{new_status}'")

            # Always update updated_at timestamp
            task.updated_at = datetime.utcnow()

            # Save to database
            db.add(task)
            db.commit()
            db.refresh(task)

            # Build success message
            if changes:
                changes_str = " and ".join(changes)
                message = f"✅ Task updated: {changes_str}"
            else:
                message = f"✅ Task '{task.title}' retrieved (no changes made)"

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
                "message": message
            }

        except ValueError as e:
            db.rollback()
            raise ValueError(f"Failed to update task: {str(e)}")


def _parse_due_date(due_date_str: str) -> Optional[datetime]:
    """Parse due date from ISO 8601 or natural language.

    [From]: specs/004-ai-chatbot/plan.md - Natural Language Processing

    Supports:
    - ISO 8601: "2025-01-15", "2025-01-15T10:00:00Z"
    - Relative: "today", "tomorrow", "next week", "in 3 days"

    Args:
        due_date_str: Date string to parse

    Returns:
        Parsed datetime or None if parsing fails

    Raises:
        ValueError: If date format is invalid
    """
    from datetime import datetime
    import re

    # Try ISO 8601 format first
    try:
        # Handle YYYY-MM-DD format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", due_date_str):
            return datetime.fromisoformat(due_date_str)

        # Handle full ISO 8601 with time
        if "T" in due_date_str:
            return datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
    except ValueError:
        pass  # Fall through to natural language parsing

    # Natural language parsing (simplified)
    due_date_str = due_date_str.lower().strip()
    today = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

    if due_date_str == "today":
        return today
    elif due_date_str == "tomorrow":
        return today + __import__('datetime').timedelta(days=1)
    elif due_date_str == "next week":
        return today + __import__('datetime').timedelta(weeks=1)
    elif due_date_str.startswith("in "):
        # Parse "in X days/weeks"
        match = re.match(r"in (\d+) (day|days|week|weeks)", due_date_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit.startswith("day"):
                return today + __import__('datetime').timedelta(days=amount)
            elif unit.startswith("week"):
                return today + __import__('datetime').timedelta(weeks=amount)

    # If parsing fails, return None and let AI agent ask for clarification
    return None


def _normalize_priority(priority: Optional[str]) -> str:
    """Normalize priority string to valid values.

    [From]: models/task.py - Task model

    Args:
        priority: Priority string to normalize

    Returns:
        Normalized priority: "low", "medium", or "high"

    Raises:
        ValueError: If priority is invalid
    """
    if not priority:
        return "medium"  # Default priority

    priority_normalized = priority.lower().strip()

    if priority_normalized in ["low", "medium", "high"]:
        return priority_normalized

    # Map common alternatives
    priority_map = {
        "1": "low",
        "2": "medium",
        "3": "high",
        "urgent": "high",
        "important": "high",
        "normal": "medium",
        "routine": "low"
    }

    normalized = priority_map.get(priority_normalized, "medium")
    return normalized


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
    )(update_task)
