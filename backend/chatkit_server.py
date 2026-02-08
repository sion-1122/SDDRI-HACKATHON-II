"""ChatKit Server implementation for task management with Gemini LLM.

[Task]: T010
[From]: specs/010-chatkit-migration/contracts/backend.md - ChatKitServer Implementation
[From]: specs/010-chatkit-migration/research.md - Section 3

This module implements the ChatKitServer class which handles ChatKit protocol
requests and streams responses using Server-Sent Events (SSE).

The server integrates:
- ChatKit Python SDK for protocol handling
- OpenAI Agents SDK for agent orchestration
- Gemini LLM via OpenAI-compatible endpoint
- MCP tools wrapped as Agents SDK functions

Architecture:
    Frontend (ChatKit.js)
        ↓ SSE with custom fetch
    ChatKitServer (this module)
        ↓ Agents SDK
    Gemini API (via AsyncOpenAI with base_url)
"""
import asyncio
import logging
from typing import Any, AsyncIterator, Optional
from uuid import UUID
from openai import AsyncOpenAI
from agents import Agent, set_default_openai_client, RunContextWrapper, Runner

from core.config import get_gemini_client, get_settings
from services.chatkit_store import PostgresChatKitStore

logger = logging.getLogger(__name__)


class AgentContext:
    """Context object passed to agent during execution.

    Contains:
    - thread_id: Current thread/conversation ID
    - user_id: Authenticated user ID
    - store: Database store for persistence
    - request_context: Additional request metadata
    """

    def __init__(
        self,
        thread_id: str,
        user_id: str,
        store: PostgresChatKitStore,
        request_context: Optional[dict] = None,
    ):
        self.thread_id = thread_id
        self.user_id = user_id
        self.store = store
        self.request_context = request_context or {}


class TaskManagerChatKitServer:
    """ChatKit Server for task management with Gemini LLM.

    [From]: specs/010-chatkit-migration/contracts/backend.md - ChatKitServer Implementation

    This server extends the ChatKit protocol to work with:
    - Custom authentication (JWT cookies)
    - Gemini LLM via OpenAI-compatible endpoint
    - Server-side tool execution (MCP tools)
    - PostgreSQL thread/message persistence

    Usage:
        from fastapi import FastAPI, Request
        from chatkit_server import TaskManagerChatKitServer

        app = FastAPI()
        server = TaskManagerChatKitServer(store=postgres_store)

        @app.post("/api/chatkit")
        async def chatkit_endpoint(request: Request):
            body = await request.body()
            user_id = get_current_user_id(request)
            result = await server.process(body, {"user_id": user_id})
            if hasattr(result, '__aiter__'):
                return StreamingResponse(result, media_type="text/event-stream")
            return Response(content=result.json, media_type="application/json")
    """

    def __init__(self, store: PostgresChatKitStore):
        """Initialize the ChatKit server.

        Args:
            store: PostgresChatKitStore instance for persistence
        """
        self.store = store

        # Configure Gemini client as default for Agents SDK
        # [From]: specs/010-chatkit-migration/research.md - Section 2
        try:
            gemini_client = get_gemini_client()
            set_default_openai_client(gemini_client)
            logger.info("Gemini client configured for Agents SDK")
        except Exception as e:
            logger.warning(f"Gemini client not configured: {e}")

        # Assistant agent will be configured after tools are wrapped
        # This placeholder will be replaced in T019 with actual tools
        self.assistant_agent: Optional[Agent] = None

    def set_agent(self, agent: Agent) -> None:
        """Set the assistant agent with tools.

        [From]: specs/010-chatkit-migration/tasks.md - T019

        Args:
            agent: Configured Agent with tools and instructions
        """
        self.assistant_agent = agent
        logger.info(f"Agent configured: {agent.name} with model {agent.model}")

    async def process(
        self,
        body: bytes,
        context: dict[str, Any]
    ) -> Any:
        """Process ChatKit request and return streaming or non-streaming result.

        [From]: specs/010-chatkit-migration/contracts/backend.md - ChatKit SSE Endpoint

        Args:
            body: Raw request body bytes from ChatKit.js
            context: Request context containing user_id and auth info

        Returns:
            StreamingResult for SSE responses or dict for JSON responses

        Note: This is a placeholder implementation. The actual implementation
        would use the ChatKit Python SDK's process() method which handles
        protocol parsing, event routing, and response formatting.
        """
        import json
        from fastapi.responses import StreamingResponse

        # Parse ChatKit protocol request
        try:
            request_data = json.loads(body.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to parse ChatKit request: {e}")
            return {"error": "Invalid request format"}

        # Extract thread ID and message content
        conversation_id = request_data.get("conversation_id")
        item = request_data.get("item", {})
        event_type = request_data.get("event", "conversation_item_created")

        logger.info(f"ChatKit request: event={event_type}, conversation_id={conversation_id}")

        # Get or create thread
        thread_id = conversation_id
        if not thread_id:
            # Create new thread for first message
            user_id = context.get("user_id")
            if not user_id:
                return {"error": "Unauthorized: no user_id in context"}

            thread_meta = await self.store.create_thread(
                user_id=user_id,
                title=None,
                metadata={}
            )
            thread_id = thread_meta["id"]
            logger.info(f"Created new thread: {thread_id}")

        # Extract user message
        user_message = self._extract_message_content(item)
        if not user_message:
            return {"error": "No message content provided"}

        # Build agent context
        user_id = context.get("user_id")
        agent_context = AgentContext(
            thread_id=thread_id,
            user_id=user_id,
            store=self.store,
            request_context=context,
        )

        # Create user message in database
        await self.store.create_message(
            thread_id=thread_id,
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "text", "text": user_message}],
            }
        )

        # Stream agent response
        # [From]: specs/010-chatkit-migration/research.md - Section 3
        # [Task]: T034 - Add timeout handling for long-running tool executions
        async def stream_response():
            """Stream ChatKit events as SSE with timeout protection.

            [Task]: T034 - Timeout handling for long-running tool executions

            Implements a 120-second timeout for agent execution to prevent
            indefinite hangs from slow tools or network issues.
            """
            if not self.assistant_agent:
                yield self._sse_event("error", {"message": "Agent not configured"})
                return

            try:
                # Run agent with streaming and timeout
                # [Task]: T034 - 120 second timeout for entire agent execution
                # This covers LLM calls, tool executions, and any delays
                async with asyncio.timeout(120):
                    result = Runner.run_streamed(
                        self.assistant_agent,
                        [{"role": "user", "content": user_message}],
                        context=agent_context,
                    )

                    # Collect assistant response
                    full_response = ""
                    async for chunk in result:
                        if hasattr(chunk, 'content'):
                            content = chunk.content
                            if content:
                                full_response += content
                                # Stream text delta
                                yield self._sse_event("message_delta", {
                                    "type": "text",
                                    "text": content
                                })

                    # Create assistant message in database
                    await self.store.create_message(
                        thread_id=thread_id,
                        item={
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "text", "text": full_response}],
                        }
                    )

                    # Send message done event
                    yield self._sse_event("message_done", {
                        "message_id": thread_id,
                        "role": "assistant"
                    })

            except TimeoutError:
                # [Task]: T034 - Handle timeout gracefully
                logger.error(f"Agent execution timeout for thread {thread_id}")
                yield self._sse_event("error", {
                    "message": "Request timed out",
                    "detail": "The AI assistant took too long to respond. Please try again."
                })
            except Exception as e:
                logger.error(f"Agent execution error: {e}", exc_info=True)
                yield self._sse_event("error", {"message": str(e)})

        # Return streaming result
        class StreamingResult:
            def __init__(self, generator):
                self.generator = generator
                self.json = json.dumps({"thread_id": thread_id})

            def __aiter__(self):
                return self.generator()

        return StreamingResult(stream_response())

    def _extract_message_content(self, item: dict) -> str:
        """Extract text content from ChatKit item.

        Args:
            item: ChatKit message item

        Returns:
            Extracted text content
        """
        content_array = item.get("content", [])
        for content_block in content_array:
            if content_block.get("type") == "text":
                return content_block.get("text", "")
        return ""

    def _sse_event(self, event_type: str, data: dict) -> str:
        """Format data as Server-Sent Event.

        [From]: specs/010-chatkit-migration/contracts/backend.md - SSE Event Types

        Args:
            event_type: Event type name
            data: Event data payload

        Returns:
            Formatted SSE string
        """
        import json
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# Create singleton instance (will be configured with tools in T019)
_server_instance: Optional[TaskManagerChatKitServer] = None


def get_chatkit_server(store: PostgresChatKitStore) -> TaskManagerChatKitServer:
    """Get or create ChatKit server singleton with agent configuration.

    [From]: specs/010-chatkit-migration/contracts/backend.md

    [Task]: T019 - Configure TaskAssistant agent with Gemini model and wrapped tools

    Args:
        store: PostgresChatKitStore instance

    Returns:
        ChatKit server instance with configured agent
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = TaskManagerChatKitServer(store)

        # Configure the assistant agent with tools
        # [From]: specs/010-chatkit-migration/tasks.md - T019
        # [From]: specs/010-chatkit-migration/contracts/backend.md - Tool Contracts
        from ai_agent.tool_wrappers import TOOL_FUNCTIONS
        from core.config import get_settings

        settings = get_settings()

        # Create the TaskAssistant agent with Gemini model
        # [From]: specs/010-chatkit-migration/research.md - Section 3
        assistant_agent = Agent[AgentContext](
            name="TaskAssistant",
            model=settings.gemini_model or "gemini-2.0-flash-exp",
            instructions="""You are a helpful task management assistant. You help users create, list, update, complete, and delete tasks through natural language.

Available tools:
- create_task: Create a new task with title, description, due date, priority, tags
- list_tasks: List all tasks with optional filters
- update_task: Update an existing task
- delete_task: Delete a task
- complete_task: Mark a task as completed or incomplete
- complete_all_tasks: Mark all tasks as completed (requires confirmation)
- delete_all_tasks: Delete all tasks (requires confirmation)

When users ask about tasks, use the appropriate tool. Always confirm destructive actions (complete_all_tasks, delete_all_tasks) by requiring the confirm parameter.

Be concise and helpful. If a user's request is unclear, ask for clarification.""",
            tools=TOOL_FUNCTIONS,
        )

        _server_instance.set_agent(assistant_agent)
        logger.info(f"ChatKit server initialized with {len(TOOL_FUNCTIONS)} tools and model {settings.gemini_model}")

    return _server_instance
