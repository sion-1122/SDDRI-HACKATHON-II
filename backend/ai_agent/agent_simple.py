"""Simple AI agent implementation using OpenAI SDK with function calling.

[From]: specs/004-ai-chatbot/plan.md - AI Agent Layer

This is a simplified implementation that uses OpenAI's function calling
capabilities directly through the AsyncOpenAI client with Gemini.
"""
import uuid
import logging
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI

from core.config import get_settings
from mcp_server.tools import (
    add_task, list_tasks, update_task, complete_task, delete_task,
    complete_all_tasks, delete_all_tasks
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Global client instance
_gemini_client: Optional[AsyncOpenAI] = None


def get_gemini_client() -> AsyncOpenAI:
    """Get or create the AsyncOpenAI client for Gemini API.

    [From]: specs/004-ai-chatbot/plan.md - Gemini Integration Pattern

    The client uses Gemini's OpenAI-compatible endpoint:
    https://generativelanguage.googleapis.com/v1beta/openai/

    Returns:
        AsyncOpenAI: Configured client for Gemini API

    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    global _gemini_client

    if _gemini_client is None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please set GEMINI_API_KEY in your environment variables."
            )

        _gemini_client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=settings.gemini_api_key
        )
        logger.info("✅ Gemini AI client initialized via AsyncOpenAI adapter")

    return _gemini_client


# Define tools for function calling
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task in the user's todo list. Use this when the user wants to create, add, or remind themselves about a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (UUID) who owns this task"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (brief description)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO 8601 format or relative terms like 'tomorrow', 'next week'"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority level"
                    }
                },
                "required": ["user_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List and filter tasks from the user's todo list. Use this when the user wants to see their tasks, ask what they have to do, or request a filtered view of their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (UUID) who owns these tasks"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by completion status"
                    },
                    "due_within_days": {
                        "type": "number",
                        "description": "Only show tasks due within X days"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum tasks to return (1-100)"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task in the user's todo list. Use this when the user wants to modify, change, or edit an existing task. You need the task_id to update.",
            "parameters": {
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
                        "description": "New task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO 8601 format or relative terms"
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
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed or not completed (toggle completion status). Use this when the user wants to mark a task as done, finished, complete, or conversely as pending, not done, incomplete.",
            "parameters": {
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
                        "description": "True to mark complete, False to mark incomplete/pending"
                    }
                },
                "required": ["user_id", "task_id", "completed"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the user's todo list permanently. Use this when the user wants to remove, delete, or get rid of a task.",
            "parameters": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "complete_all_tasks",
            "description": "Mark all tasks as completed or not completed. Use this when the user wants to mark all tasks as done, complete, finished, or conversely mark all as pending or incomplete.",
            "parameters": {
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
                        "description": "Optional: Only affect tasks with this status (e.g., only mark pending tasks as complete)"
                    }
                },
                "required": ["user_id", "completed"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_all_tasks",
            "description": "Delete all tasks from the user's todo list permanently. This is a destructive operation - always inform the user how many tasks will be deleted and ask for confirmation before calling with confirmed=true.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (UUID) who owns these tasks"
                    },
                    "confirmed": {
                        "type": "boolean",
                        "description": "Must be true to actually delete. First call with confirmed=false to show count, then call again with confirmed=true after user confirms."
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "Optional: Only delete tasks with this status (e.g., only delete completed tasks)"
                    }
                },
                "required": ["user_id", "confirmed"]
            }
        }
    }
]


async def run_agent(
    messages: List[Dict[str, str]],
    user_id: str,
    context: Optional[Dict] = None
) -> str:
    """Run the task agent with conversation history.

    [From]: specs/004-ai-chatbot/plan.md - Agent Execution Pattern

    Args:
        messages: Conversation history in OpenAI format
        user_id: User ID for context
        context: Optional additional context

    Returns:
        str: Agent's response message

    Raises:
        ValueError: If agent initialization fails
        ConnectionError: If Gemini API is unreachable
        Exception: If agent execution fails
    """
    try:
        client = get_gemini_client()

        # System prompt with user_id context
        system_prompt = f"""You are a helpful task management assistant.

Users can create, list, update, complete, and delete tasks through natural language.

IMPORTANT: You are currently assisting user with ID: {user_id}
When calling tools, ALWAYS include this user_id parameter. Do not ask the user for their user ID.

Your capabilities:
- Create tasks with title, description, due date, and priority
- List and filter tasks (e.g., "show me high priority tasks due this week")
- Update existing tasks (title, description, due date, priority)
- Mark tasks as complete or incomplete (individual or all tasks)
- Delete tasks (individual or all tasks)
- Handle multi-action requests in a single response (e.g., "add a task and list my tasks")

Guidelines for task references:
- Users may refer to tasks by position (e.g., "task 1", "the first task", "my last task")
- When user references a task by position, ALWAYS first list tasks to identify the correct task_id
- Then confirm with the user before proceeding (e.g., "I found 'Buy groceries' as your first task. Is that the one you want to mark complete?")
- Example flow: User says "mark task 1 as done" → You list_tasks → Find first task → Confirm → complete_task with correct task_id

Guidelines for bulk operations:
- "Mark all tasks as complete" → Use complete_all_tasks with completed=True
- "Mark all pending tasks as complete" → Use complete_all_tasks with completed=True, status_filter="pending"
- "Delete all tasks" → First call delete_all_tasks with confirmed=false to show count → Wait for user confirmation → Call again with confirmed=True

Safety confirmations:
- For delete_all_tasks: ALWAYS call with confirmed=false first, inform user of count, and ask for explicit confirmation
- Example: "This will delete 5 tasks. Please confirm by saying 'yes' or 'confirm'."

Empty task list handling:
- When users have no tasks, respond warmly and offer to help create one
- Examples: "You don't have any tasks yet. Would you like me to help you create one?"
- For filtered queries with no results: "No tasks match that criteria. Would you like to see all your tasks instead?"

Task presentation:
- When listing tasks, organize them logically (e.g., pending first, then completed)
- Include key details: title, due date, priority, completion status
- Use clear formatting (bullet points or numbered lists)
- For long lists, offer to filter or show specific categories

Response formatting:
- When completing tasks: Include the task title and confirmation (e.g., "✅ 'Buy groceries' marked as complete")
- When completing multiple tasks: Include count (e.g., "✅ 3 tasks marked as complete")
- When updating tasks: Describe what changed (e.g., "✅ Task updated: title changed to 'Buy groceries and milk'")
- When deleting tasks: Include title and confirmation (e.g., "✅ 'Buy groceries' deleted")

When you need to create a task, use the add_task function with user_id="{user_id}".
When you need to list tasks, use the list_tasks function with user_id="{user_id}".
When you need to update a task, use the update_task function with user_id="{user_id}" and task_id.
When you need to mark a task complete/incomplete, use the complete_task function with user_id="{user_id}", task_id, and completed=True/False.
When you need to mark all tasks complete/incomplete, use the complete_all_tasks function with user_id="{user_id}" and completed=True/False.
When you need to delete a task, use the delete_task function with user_id="{user_id}" and task_id.
When you need to delete all tasks, use the delete_all_tasks function with user_id="{user_id}" and confirmed=false first, then confirmed=true after user confirms.
"""

        # Prepare messages with system prompt
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend(messages)

        # Call the API
        response = await client.chat.completions.create(
            model=settings.gemini_model,
            messages=api_messages,
            tools=TOOLS_DEFINITION,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            tool_results = []

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments

                # Add user_id to function args if not present
                import json
                args = json.loads(function_args)
                if "user_id" not in args:
                    args["user_id"] = user_id

                # Call the appropriate function
                if function_name == "add_task":
                    result = await add_task.add_task(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "list_tasks":
                    result = await list_tasks.list_tasks(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "update_task":
                    result = await update_task.update_task(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "complete_task":
                    result = await complete_task.complete_task(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "delete_task":
                    result = await delete_task.delete_task(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "complete_all_tasks":
                    result = await complete_all_tasks.complete_all_tasks(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                elif function_name == "delete_all_tasks":
                    result = await delete_all_tasks.delete_all_tasks(**args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })

            # Get final response from assistant
            api_messages.append(assistant_message)
            api_messages.extend(tool_results)

            final_response = await client.chat.completions.create(
                model=settings.gemini_model,
                messages=api_messages
            )

            # Ensure we always return a non-empty string
            content = final_response.choices[0].message.content
            return content or "I've processed your request. Is there anything else you'd like help with?"
        else:
            # No tool calls, return the content directly
            # Ensure we always return a non-empty string
            content = assistant_message.content
            return content or "I understand. How can I help you with your tasks?"

    except ValueError as e:
        # Re-raise configuration errors
        logger.error(f"❌ Agent configuration error: {e}")
        raise
    except Exception as e:
        # Detect specific error types
        error_msg = str(e).lower()

        if "connection" in error_msg or "network" in error_msg:
            logger.error(f"❌ Gemini API connection error: {e}")
            raise ConnectionError(
                "Unable to reach AI service. Please check your internet connection "
                "and try again later."
            )
        elif "timeout" in error_msg:
            logger.error(f"❌ Gemini API timeout error: {e}")
            raise TimeoutError(
                "AI service request timed out. Please try again."
            )
        elif "rate limit" in error_msg or "quota" in error_msg:
            logger.error(f"❌ Gemini API rate limit error: {e}")
            raise Exception(
                "AI service rate limit exceeded. Please wait a moment and try again."
            )
        elif "authentication" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
            logger.error(f"❌ Gemini API authentication error: {e}")
            raise Exception(
                "AI service authentication failed. Please check your API key configuration."
            )
        else:
            # Unknown error
            logger.error(f"❌ Agent execution error: {e}")
            raise Exception(
                f"AI service temporarily unavailable: {str(e)}"
            )


def is_gemini_configured() -> bool:
    """Check if Gemini API is properly configured.

    Returns:
        bool: True if GEMINI_API_KEY is set, False otherwise
    """
    return bool(settings.gemini_api_key)


__all__ = [
    "get_gemini_client",
    "run_agent",
    "is_gemini_configured"
]
