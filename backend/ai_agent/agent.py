"""AI Agent initialization using OpenAI Agents SDK with Gemini.

[Task]: T014
[From]: specs/004-ai-chatbot/tasks.md

This module initializes the OpenAI Agents SDK with Gemini models via AsyncOpenAI adapter.
It provides the task management agent that can interact with MCP tools to perform
task operations on behalf of users.
"""
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from typing import Optional
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# Initialize AsyncOpenAI client configured for Gemini API
# [From]: specs/004-ai-chatbot/plan.md - Technical Context
# [From]: specs/004-ai-chatbot/tasks.md - Implementation Notes
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


# Initialize the task management agent
# [From]: specs/004-ai-chatbot/spec.md - US1
_task_agent: Optional[Agent] = None


def get_task_agent() -> Agent:
    """Get or create the task management AI agent.

    [From]: specs/004-ai-chatbot/plan.md - AI Agent Layer

    The agent is configured to:
    - Help users create, list, update, complete, and delete tasks
    - Understand natural language requests
    - Ask for clarification when requests are ambiguous
    - Confirm actions clearly

    Returns:
        Agent: Configured task management agent

    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    global _task_agent

    if _task_agent is None:
        gemini_client = get_gemini_client()

        # Initialize task management agent
        _task_agent = Agent(
            name="task_manager",
            instructions="""You are a helpful task management assistant.

Users can create, list, update, complete, and delete tasks through natural language.

Your capabilities:
- Create tasks with title, description, due date, and priority
- List and filter tasks (e.g., "show me high priority tasks due this week")
- Update existing tasks (title, description, due date, priority)
- Mark tasks as complete or incomplete
- Delete tasks

Guidelines:
- Always confirm actions clearly before executing them
- Ask for clarification when requests are ambiguous
- Be concise and friendly in your responses
- Use the MCP tools provided to interact with the user's task list
- Maintain context across the conversation
- If you need more information (e.g., which task to update), ask specifically

Empty task list handling:
- [From]: T026 - When users have no tasks, respond warmly and offer to help create one
- Examples: "You don't have any tasks yet. Would you like me to help you create one?"
- For filtered queries with no results: "No tasks match that criteria. Would you like to see all your tasks instead?"

Task presentation:
- When listing tasks, organize them logically (e.g., pending first, then completed)
- Include key details: title, due date, priority, completion status
- Use clear formatting (bullet points or numbered lists)
- For long lists, offer to filter or show specific categories

Example interactions:
User: "Create a task to buy groceries"
You: "I'll create a task titled 'Buy groceries' for you." → Use add_task tool

User: "Show me my tasks"
You: "Let me get your task list." → Use list_tasks tool

User: "What are my pending tasks?"
You: "Let me check your pending tasks." → Use list_tasks tool with status="pending"

User: "I have no tasks"
You: "That's right! You don't have any tasks yet. Would you like me to help you create one?"

User: "Mark the grocery task as complete"
You: "Which task would you like me to mark as complete?" → Ask for clarification if unclear

User: "I need to finish the report by Friday"
You: "I'll create a task 'Finish the report' due this Friday." → Use add_task with due_date
""",
            model=OpenAIChatCompletionsModel(
                model=settings.gemini_model,
                openai_client=gemini_client,
            ),
        )
        logger.info(f"✅ Task agent initialized with model: {settings.gemini_model}")

    return _task_agent


async def run_agent(
    messages: list[dict[str, str]],
    user_id: str,
    context: Optional[dict] = None
) -> str:
    """Run the task agent with conversation history.

    [From]: specs/004-ai-chatbot/plan.md - Agent Execution Pattern

    Args:
        messages: Conversation history in OpenAI format
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        user_id: User ID for context (passed to tools)
        context: Optional additional context for the agent

    Returns:
        str: Agent's response message

    Raises:
        ValueError: If agent initialization fails
        ConnectionError: If Gemini API is unreachable
        Exception: If agent execution fails for other reasons
    """
    try:
        agent = get_task_agent()

        # Prepare context with user_id for MCP tools
        agent_context = {"user_id": user_id}
        if context:
            agent_context.update(context)

        # Run agent with conversation history
        # [From]: OpenAI Agents SDK documentation
        result = await Runner.run(
            agent,
            input=messages,
            context=agent_context
        )

        logger.info(f"✅ Agent executed successfully for user {user_id}")
        return result.final_output

    except ValueError as e:
        # Re-raise configuration errors (missing API key, invalid model, etc.)
        logger.error(f"❌ Agent configuration error: {e}")
        raise
    except ConnectionError as e:
        # [From]: T022 - Add error handling for Gemini API unavailability
        # Specific handling for network/connection issues
        logger.error(f"❌ Gemini API connection error: {e}")
        raise ConnectionError(
            "Unable to reach AI service. Please check your internet connection "
            "and try again later."
        )
    except TimeoutError as e:
        # [From]: T022 - Handle timeout scenarios
        logger.error(f"❌ Gemini API timeout error: {e}")
        raise TimeoutError(
            "AI service request timed out. Please try again."
        )
    except Exception as e:
        # Generic error handler for other issues
        error_msg = str(e).lower()

        # Detect specific API errors
        if "rate limit" in error_msg or "quota" in error_msg:
            logger.error(f"❌ Gemini API rate limit error: {e}")
            raise Exception(
                "AI service rate limit exceeded. Please wait a moment and try again."
            )
        elif "authentication" in error_msg or "unauthorized" in error_msg:
            logger.error(f"❌ Gemini API authentication error: {e}")
            raise Exception(
                "AI service authentication failed. Please check your API key configuration."
            )
        elif "context" in error_msg or "prompt" in error_msg:
            logger.error(f"❌ Gemini API context error: {e}")
            raise Exception(
                "AI service unable to process request. Please rephrase your message."
            )
        else:
            # Unknown error
            logger.error(f"❌ Agent execution error: {e}")
            raise Exception(
                f"AI service temporarily unavailable: {str(e)}"
            )


def is_gemini_configured() -> bool:
    """Check if Gemini API is properly configured.

    [From]: specs/004-ai-chatbot/tasks.md - T022

    Returns:
        bool: True if GEMINI_API_KEY is set, False otherwise
    """
    return bool(settings.gemini_api_key)


__all__ = [
    "get_gemini_client",
    "get_task_agent",
    "run_agent",
    "is_gemini_configured"
]
