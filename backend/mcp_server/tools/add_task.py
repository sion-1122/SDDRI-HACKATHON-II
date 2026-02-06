"""MCP tool for adding tasks to the todo list.

[Task]: T013, T031
[From]: specs/004-ai-chatbot/tasks.md, specs/007-intermediate-todo-features/tasks.md (US2)

This tool allows the AI agent to create tasks on behalf of users
through natural language conversations.

Now supports tag extraction from natural language patterns.
"""
from typing import Optional, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from models.task import Task
from core.database import engine
from sqlmodel import Session

# Import tag extraction service [T029, T031]
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.nlp_service import extract_tags_from_task_data, normalize_tag_name


# Tool metadata for MCP registration
tool_metadata = {
    "name": "add_task",
    "description": """Create a new task in the user's todo list.

Use this tool when the user wants to create, add, or remind themselves about a task.
The task will be associated with their user account and persist across conversations.

Parameters:
- title (required): Brief task title (max 255 characters)
- description (optional): Detailed task description (max 2000 characters)
- due_date (optional): When the task is due (ISO 8601 date string or relative like 'tomorrow', 'next week')
- priority (optional): Task priority - 'low', 'medium', or 'high' (default: 'medium')
- tags (optional): List of tag names for categorization (e.g., ["work", "urgent"])

Natural Language Tag Support [T031]:
- "tagged with X" or "tags X" → extracts tag X
- "add tag X" or "with tag X" → extracts tag X
- "#tagname" → extracts hashtag as tag
- "labeled X" → extracts tag X

Returns: Created task details including ID, title, and confirmation.
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User ID (UUID) who owns this task"
            },
            "title": {
                "type": "string",
                "description": "Task title (brief description)",
                "maxLength": 255
            },
            "description": {
                "type": "string",
                "description": "Detailed task description",
                "maxLength": 2000
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO 8601 format (e.g., '2025-01-15') or relative terms"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Task priority level"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tag names for categorization"
            }
        },
        "required": ["user_id", "title"]
    }
}


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> dict[str, Any]:
    """Create a new task for the user.

    [From]: specs/004-ai-chatbot/spec.md - US1
    [Task]: T031 - Integrate tag extraction for natural language

    Args:
        user_id: User ID (UUID string) who owns this task
        title: Brief task title
        description: Optional detailed description
        due_date: Optional due date (ISO 8601 or relative)
        priority: Optional priority level (low/medium/high)
        tags: Optional list of tag names

    Returns:
        Dictionary with created task details

    Raises:
        ValueError: If validation fails
        ValidationError: If task constraints violated
    """
    from core.validators import validate_task_title, validate_task_description

    # Validate inputs
    validated_title = validate_task_title(title)
    validated_description = validate_task_description(description) if description else None

    # Parse and validate due date if provided
    parsed_due_date = None
    if due_date:
        parsed_due_date = _parse_due_date(due_date)

    # Normalize priority
    normalized_priority = _normalize_priority(priority)

    # [T031] Extract tags from natural language in title and description
    extracted_tags = extract_tags_from_task_data(validated_title, validated_description)

    # Normalize extracted tags
    normalized_extracted_tags = [normalize_tag_name(tag) for tag in extracted_tags]

    # Combine provided tags with extracted tags, removing duplicates
    all_tags = set(normalized_extracted_tags)
    if tags:
        # Normalize provided tags
        normalized_provided_tags = [normalize_tag_name(tag) for tag in tags]
        all_tags.update(normalized_provided_tags)

    final_tags = sorted(list(all_tags)) if all_tags else []

    # Get database session (synchronous)
    with Session(engine) as db:
        try:
            # Create task instance
            task = Task(
                id=uuid4(),
                user_id=UUID(user_id),
                title=validated_title,
                description=validated_description,
                due_date=parsed_due_date,
                priority=normalized_priority,
                tags=final_tags,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Save to database
            db.add(task)
            db.commit()
            db.refresh(task)

            # Return success response
            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "tags": task.tags,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                },
                "message": f"✅ Task created: {task.title}" + (f" (tags: {', '.join(final_tags)})" if final_tags else "")
            }

        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create task: {str(e)}")


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
        return today + timedelta(days=1)
    elif due_date_str == "next week":
        return today + timedelta(weeks=1)
    elif due_date_str.startswith("in "):
        # Parse "in X days/weeks"
        match = re.match(r"in (\d+) (day|days|week|weeks)", due_date_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit.startswith("day"):
                return today + timedelta(days=amount)
            elif unit.startswith("week"):
                return today + timedelta(weeks=amount)

    # If parsing fails, return None and let AI agent ask for clarification
    return None


def _normalize_priority(priority: Optional[str]) -> str:
    """Normalize priority string to valid values.

    [From]: models/task.py - Task model
    [Task]: T009-T011 - Priority extraction from natural language

    Args:
        priority: Priority string to normalize

    Returns:
        Normalized priority: "LOW", "MEDIUM", or "HIGH" (uppercase enum values)

    Raises:
        ValueError: If priority is invalid
    """
    from models.task import PriorityLevel

    if not priority:
        return PriorityLevel.MEDIUM  # Default priority (uppercase)

    priority_normalized = priority.lower().strip()

    # Direct matches - return uppercase enum values
    if priority_normalized in ["low", "medium", "high"]:
        return priority_normalized.upper()

    # Enhanced priority mapping from natural language patterns
    # [Task]: T011 - Integrate priority extraction in MCP tools
    priority_map_high = {
        # Explicit high priority keywords
        "urgent", "asap", "important", "critical", "emergency", "immediate",
        "high", "priority", "top", "now", "today", "deadline", "crucial",
        # Numeric mappings
        "3", "high priority", "very important", "must do"
    }

    priority_map_low = {
        # Explicit low priority keywords
        "low", "later", "whenever", "optional", "nice to have", "someday",
        "eventually", "routine", "normal", "regular", "backlog",
        # Numeric mappings
        "1", "low priority", "no rush", "can wait"
    }

    priority_map_medium = {
        "2", "medium", "normal", "standard", "default", "moderate"
    }

    # Check high priority patterns
    if priority_normalized in priority_map_high or any(
        keyword in priority_normalized for keyword in ["urgent", "asap", "critical", "deadline", "today"]
    ):
        return PriorityLevel.HIGH

    # Check low priority patterns
    if priority_normalized in priority_map_low or any(
        keyword in priority_normalized for keyword in ["whenever", "later", "optional", "someday"]
    ):
        return PriorityLevel.LOW

    # Default to medium
    return PriorityLevel.MEDIUM


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
    )(add_task)
