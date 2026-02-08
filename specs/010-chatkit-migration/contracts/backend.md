# Backend API Contracts: ChatKit Migration

**Feature**: 010-chatkit-migration
**Date**: 2026-02-06

## Overview

This document defines the backend API contracts for the ChatKit-based chat system. The primary endpoint is the ChatKit SSE streaming endpoint, replacing the existing REST-based chat API.

## Endpoints

### 1. ChatKit SSE Endpoint

**Purpose**: Main streaming endpoint for ChatKit communication. Handles all chat requests, tool executions, and returns Server-Sent Events stream.

**Endpoint**: `POST /api/chatkit`

**Authentication**: Required (JWT via httpOnly cookie)

**Request Headers**:
```
Content-Type: application/json
Cookie: auth_token=<jwt_token>
```

**Request Body** (ChatKit protocol):
```json
{
  "event": "conversation_item_created",
  "conversation_id": "<thread_uuid>",
  "item": {
    "type": "message",
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Create a task called buy groceries"
      }
    ]
  }
}
```

**Response**: Server-Sent Events (SSE) stream

**Response Headers**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**SSE Event Types**:

| Event Type | Description |
|------------|-------------|
| `message_delta` | Streaming text content |
| `tool_call_created` | Tool/function invocation started |
| `tool_call_delta` | Tool call progress update |
| `tool_call_done` | Tool execution completed |
| `message_done` | Message fully streamed |
| `error` | Error occurred |

**Example SSE Stream**:
```
event: message_delta
data: {"type":"text","text":"I'll"}

event: message_delta
data: {"type":"text","text":" create"}

event: tool_call_created
data: {"id":"call_123","type":"function","function":{"name":"create_task","arguments":"{\"title\":\"buy groceries\"}"}}

event: tool_call_done
data: {"id":"call_123","result":"Task created successfully"}

event: message_delta
data: {"type":"text","text":" that task for you."}

event: message_done
data: {"message_id":"msg_456","role":"assistant"}
```

**Error Responses**:

| Status | Description | Body |
|--------|-------------|------|
| 401 | Unauthorized | `{"detail": "Invalid authentication"}` |
| 429 | Rate limited | `{"detail": "Daily message limit reached", "resets_at": "2024-01-01T00:00:00Z"}` |
| 500 | Server error | `{"detail": "Internal server error"}` |

---

### 2. WebSocket Removal (Deprecated)

**Status**: These endpoints will be **REMOVED**

**Removed Endpoints**:
- `GET /api/{user_id}/ws` - WebSocket connection endpoint
- `POST /api/{user_id}/chat` - REST-based chat endpoint (replaced by SSE)

**Migration**: Frontend should use `/api/chatkit` SSE endpoint instead.

---

## Internal Service Contracts

### ChatKitServer Implementation

```python
from typing import Any, AsyncIterator
from openai_chatkit import (
    ChatKitServer,
    Event,
    StreamingResult,
    ThreadMetadata,
    UserMessageItem,
    ClientToolCallOutputItem,
)
from agents import Agent, RunContextWrapper, Runner, stream_agent_response

class TaskManagerChatKitServer(ChatKitServer):
    """ChatKit server for task management with Gemini LLM.

    [From]: specs/010-chatkit-migration/research.md - Section 3
    """

    assistant_agent: Agent[AgentContext] = Agent[AgentContext](
        model="gemini-2.5-flash",
        name="TaskAssistant",
        instructions="You are a helpful task management assistant...",
        tools=[
            create_task_tool,
            list_tasks_tool,
            update_task_tool,
            delete_task_tool,
            complete_task_tool,
        ],
    )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallOutputItem,
        context: Any,
    ) -> AsyncIterator[Event]:
        """Process user input and stream agent response.

        [From]: specs/010-chatkit-migration/research.md - Section 3
        """
        # Build agent context
        agent_context = AgentContext(
            thread_id=thread.id,
            user_id=context.get("user_id"),
            store=self.store,
        )

        # Convert ChatKit input to Agents SDK format
        input_item = await to_input_item(input, self.to_message_content)

        # Run agent with streaming
        result = Runner.run_streamed(
            self.assistant_agent,
            input_item,
            context=agent_context,
        )

        # Stream ChatKit events
        async for event in stream_agent_response(agent_context, result):
            yield event
```

### Store Interface Implementation

```python
from chatkit_contracts import Store, ThreadMetadata, MessageItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class PostgresStore(Store):
    """PostgreSQL implementation of ChatKit Store interface.

    [From]: specs/010-chatkit-migration/data-model.md - Store Interface
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_threads(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[ThreadMetadata]:
        """List threads for a user."""
        stmt = (
            select(Thread)
            .where(Thread.user_id == user_id)
            .order_by(Thread.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        threads = result.scalars().all()
        return [
            ThreadMetadata(
                id=str(t.id),
                user_id=str(t.user_id),
                title=t.title,
                metadata=t.metadata or {},
                created_at=t.created_at.isoformat(),
                updated_at=t.updated_at.isoformat(),
            )
            for t in threads
        ]

    async def create_message(
        self,
        thread_id: str,
        item: UserMessageItem | ClientToolCallOutputItem
    ) -> MessageItem:
        """Create a new message in a thread."""
        message = Message(
            thread_id=thread_id,
            role=item.type,  # "user" or "assistant"
            content=self._extract_content(item),
            tool_calls=self._extract_tool_calls(item),
        )
        self.session.add(message)
        await self.session.flush()

        return MessageItem(
            id=str(message.id),
            type="message",
            role=message.role,
            content=[{"type": "text", "text": message.content}],
            tool_calls=message.tool_calls,
            created_at=message.created_at.isoformat(),
        )
```

---

## Tool Contracts (MCP Integration)

### Tool Definition Format

Each MCP tool is wrapped as an Agents SDK function tool:

```python
from agents import function_tool
from agents import RunContextWrapper

@function_tool(
    name_override="create_task",
    description_override="Create a new task in the user's todo list"
)
async def create_task_tool(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str | None = None,
) -> str:
    """Create a task via MCP server.

    [From]: specs/010-chatkit-migration/research.md - Section 7
    """
    # Get user_id from agent context
    user_id = ctx.context.user_id

    # Call existing MCP tool
    from mcp_server.task_tools import create_task
    result = await create_task(
        user_id=user_id,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
    )

    return json.dumps({
        "success": True,
        "task_id": result.id,
        "title": result.title,
    })
```

### Tool Schema (OpenAI-Compatible)

```json
{
  "type": "function",
  "function": {
    "name": "create_task",
    "description": "Create a new task in the user's todo list",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The task title"
        },
        "description": {
          "type": "string",
          "description": "Optional task description"
        },
        "due_date": {
          "type": "string",
          "description": "Optional due date (ISO 8601 format)"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "Optional task priority"
        }
      },
      "required": ["title"]
    }
  }
}
```

---

## Authentication Contracts

### JWT Token Extraction

```python
from fastapi import Request, HTTPException
from core.security import verify_jwt_token

async def get_current_user_id(request: Request) -> str:
    """Extract user_id from JWT token in httpOnly cookie.

    [From]: backend/core/deps.py
    """
    # Try httpOnly cookie first
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify JWT
    payload = verify_jwt_token(auth_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id
```

### ChatKit Endpoint with Auth

```python
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse

app = FastAPI()
server = TaskManagerChatKitServer(store=postgres_store)

@app.post("/api/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Handle ChatKit requests with JWT authentication.

    [From]: specs/010-chatkit-migration/research.md - Section 4
    """
    # Parse request body
    body = await request.body()

    # Pass user_id via context (not via OpenAI Sessions API)
    context = {"user_id": user_id}

    # Process and stream response
    result = await server.process(body, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
        )

    # Non-streaming response (e.g., initial connection)
    return Response(content=result.json, media_type="application/json")
```

---

## Rate Limiting Contracts

### Rate Limiter Configuration

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chatkit")
@limiter.limit("100/hour")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """ChatKit endpoint with rate limiting.

    [From]: specs/004-ai-chatbot/spec.md - FR-015
    """
    # Implementation...
```

---

## Error Handling Contracts

### Error Response Format

```python
from fastapi.responses import JSONResponse

class ChatKitError(Exception):
    """Base error for ChatKit operations."""
    pass

class RateLimitError(ChatKitError):
    """Rate limit exceeded."""
    def __init__(self, resets_at: str):
        self.resets_at = resets_at

@app.exception_handler(RateLimitError)
async def rate_limit_handler(request: Request, exc: RateLimitError):
    """Handle rate limit errors.

    [From]: frontend/src/components/chat/ChatInterface.tsx - Error handling
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Daily message limit reached",
            "resets_at": exc.resets_at
        }
    )
```

---

## Testing Contracts

### Endpoint Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chatkit_streaming(
    async_client: AsyncClient,
    auth_token: str,
    test_thread_id: str
):
    """Test ChatKit SSE streaming endpoint.

    [From]: specs/010-chatkit-migration/spec.md - SC-001, SC-002
    """
    response = await async_client.post(
        "/api/chatkit",
        json={
            "event": "conversation_item_created",
            "conversation_id": test_thread_id,
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "text", "text": "List my tasks"}]
            }
        },
        cookies={"auth_token": auth_token}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

    # Verify SSE events
    events = response.text.split("\n\n")
    assert any("message_delta" in e for e in events)
    assert any("tool_call_created" in e for e in events)
```

---

## Migration Checklist

- [ ] Install `openai-chatkit` package
- [ ] Implement `ChatKitServer` class
- [ ] Implement `Store` interface for PostgreSQL
- [ ] Implement `FileStore` interface (if attachments needed)
- [ ] Create `/api/chatkit` SSE endpoint
- [ ] Configure Gemini client with custom base_url
- [ ] Wrap existing MCP tools as Agents SDK functions
- [ ] Add rate limiting to `/api/chatkit` endpoint
- [ ] Update error handling for SSE streaming
- [ ] Add integration tests for streaming endpoint
- [ ] Remove deprecated WebSocket endpoints
- [ ] Update documentation

---

## References

- [ChatKit Python API Reference](https://platform.openai.com/docs/api-reference/chatkit-python)
- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)
