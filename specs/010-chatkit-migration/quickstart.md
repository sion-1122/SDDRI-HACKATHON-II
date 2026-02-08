# ChatKit Migration Quick Start

**Feature**: 010-chatkit-migration
**Date**: 2026-02-06

## Prerequisites

- Python 3.13+
- Node.js 18+
- Existing FastAPI backend with chat functionality
- Gemini API key

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
uv add openai-chatkit openai-agents
```

### 2. Configure Environment Variables

Add to `.env`:
```bash
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Existing variables (no changes needed)
DATABASE_URL=your_database_url
JWT_SECRET=your_jwt_secret
```

### 3. Create ChatKit Server

Create `backend/chatkit_server.py`:

```python
"""
ChatKit server implementation for task management with Gemini LLM.

[From]: specs/010-chatkit-migration/contracts/backend.md
"""
from uuid import uuid4
from typing import Any, AsyncIterator
from openai import AsyncOpenAI
from agents import Agent, set_default_openai_client, function_tool, RunContextWrapper
from openai_chatkit import ChatKitServer, Event, ThreadMetadata
from sqlalchemy.ext.asyncio import AsyncSession

# Configure Gemini client
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
)
set_default_openai_client(gemini_client)

# Import your existing tools
from mcp_server.task_tools import (
    create_task,
    list_tasks,
    update_task,
    delete_task,
    complete_task,
)

# Wrap tools as Agents SDK functions
@function_tool
async def create_task_tool(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str | None = None,
) -> str:
    """Create a new task."""
    user_id = ctx.context.get("user_id")
    result = await create_task(user_id=user_id, title=title, description=description)
    return f"Task created: {result.title}"

@function_tool
async def list_tasks_tool(ctx: RunContextWrapper[AgentContext]) -> str:
    """List all tasks for the user."""
    user_id = ctx.context.get("user_id")
    tasks = await list_tasks(user_id=user_id)
    return f"Found {len(tasks)} tasks"

# Define the agent
assistant_agent = Agent[AgentContext](
    model="gemini-2.5-flash",
    name="TaskAssistant",
    instructions="You are a helpful task management assistant. Use tools to manage the user's tasks.",
    tools=[create_task_tool, list_tasks_tool, update_task_tool, delete_task_tool, complete_task_tool],
)

class TaskChatKitServer(ChatKitServer):
    """ChatKit server for task management."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallOutputItem,
        context: Any,
    ) -> AsyncIterator[Event]:
        """Process input and stream agent response."""
        # Extract user message
        if isinstance(input, UserMessageItem):
            content = input.content[0].text if input.content else ""
        else:
            content = input.output

        # Build context
        agent_context = AgentContext(
            thread_id=thread.id,
            user_id=context.get("user_id"),
            store=self.store,
        )

        # Run agent with streaming
        from agents import Runner, stream_agent_response

        result = Runner.run_streamed(
            assistant_agent,
            [{"role": "user", "content": content}],
            context=agent_context,
        )

        # Stream events
        async for event in stream_agent_response(agent_context, result):
            yield event
```

### 4. Implement Store Interface

Create `backend/chatkit_store.py`:

```python
"""
PostgreSQL Store implementation for ChatKit.

[From]: specs/010-chatkit-migration/data-model.md
"""
from typing import Optional
from chatkit_contracts import Store, ThreadMetadata, MessageItem
from models import Thread, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class PostgresChatKitStore(Store):
    """PostgreSQL implementation of ChatKit Store."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_thread(
        self,
        user_id: str,
        title: Optional[str],
        metadata: dict
    ) -> ThreadMetadata:
        thread = Thread(
            user_id=user_id,
            title=title,
            metadata=metadata,
        )
        self.session.add(thread)
        await self.session.commit()
        await self.session.refresh(thread)

        return ThreadMetadata(
            id=str(thread.id),
            user_id=user_id,
            title=thread.title,
            metadata=thread.metadata or {},
            created_at=thread.created_at.isoformat(),
            updated_at=thread.updated_at.isoformat(),
        )

    # Implement other Store methods...
    # See contracts/backend.md for full interface
```

### 5. Create ChatKit Endpoint

Add to `backend/api/chat.py`:

```python
"""
ChatKit SSE endpoint for streaming chat.

[From]: specs/010-chatkit-migration/contracts/backend.md
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from chatkit_server import TaskChatKitServer
from chatkit_store import PostgresChatKitStore
from core.deps import get_db, get_current_user_id

router = APIRouter()

# Initialize server
store = None  # Will be created per request
server = TaskChatKitServer(store=store)

@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Handle ChatKit streaming requests."""
    # Create store for this request
    store = PostgresChatKitStore(db)
    server.store = store

    # Parse request body
    body = await request.body()

    # Process with user context
    context = {"user_id": user_id}
    result = await server.process(body, context)

    if hasattr(result, '__aiter__'):
        # Streaming response
        return StreamingResponse(
            result,
            media_type="text/event-stream",
        )

    # Non-streaming response
    from fastapi.responses import Response
    return Response(content=result.json, media_type="application/json")
```

### 6. Update Main App

Add the router to `backend/main.py`:

```python
from api.chat import router as chatkit_router

app.include_router(chatkit_router, prefix="/api", tags=["chatkit"])
```

---

## Frontend Setup

### 1. Install ChatKit React

```bash
cd frontend
npm install @openai/chatkit-react
```

### 2. Create ChatKit Wrapper

Create `frontend/src/components/chat/TaskChat.tsx`:

```typescript
/**
 * ChatKit wrapper for task management chat.

[From]: specs/010-chatkit-migration/contracts/frontend.md
*/
"use client";

import { ChatKit, useChatKit } from '@openai/chatkit-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function customFetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  return fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
    },
  });
}

interface TaskChatProps {
  userId: string;
  initialThreadId?: string;
}

export function TaskChat({ userId, initialThreadId }: TaskChatProps) {
  const { control } = useChatKit({
    api: {
      apiURL: `${API_URL}/api/chatkit`,
      fetch: customFetchWithAuth,
    },
    initialThreadID: initialThreadId,
  });

  return (
    <div className="flex flex-col h-full w-full border rounded-lg shadow-sm bg-card">
      <ChatKit control={control} className="h-full w-full" />
    </div>
  );
}
```

### 3. Replace ChatInterface

Update `frontend/src/app/dashboard/page.tsx`:

**Before**:
```typescript
import { ChatInterface } from '@/components/chat/ChatInterface';

// ...

<ChatInterface userId={userId} />
```

**After**:
```typescript
import { TaskChat } from '@/components/chat/TaskChat';

// ...

<TaskChat userId={userId} />
```

### 4. Delete Old Components

```bash
cd frontend/src/components/chat
rm ChatInterface.tsx MessageList.tsx MessageInput.tsx ProgressBar.tsx ConnectionStatus.tsx useWebSocket.ts
```

---

## Database Migration

### 1. Create Threads Table

```sql
-- Add to migrations/migrate_threads.sql
CREATE TABLE IF NOT EXISTS threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_thread_user_id ON threads(user_id);
CREATE INDEX IF NOT EXISTS idx_thread_updated_at ON threads(user_id, updated_at DESC);

-- Add thread_id to messages table
ALTER TABLE messages ADD COLUMN IF NOT EXISTS thread_id UUID REFERENCES threads(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_message_thread_id ON messages(thread_id, created_at ASC);
```

### 2. Run Migration

```bash
cd backend
psql $DATABASE_URL -f migrations/migrate_threads.sql
```

---

## Testing

### 1. Start Services

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Test Chat

1. Open http://localhost:3000
2. Login to your account
3. Open the chat interface
4. Send: "Create a task called test migration"
5. Verify:
   - Response streams in real-time
   - Tool execution is visible
   - Task appears in task list
   - Conversation persists after refresh

### 3. Test Authentication

1. Open browser DevTools
2. Check Network tab for `/api/chatkit` requests
3. Verify `auth_token` cookie is sent
4. Verify SSE connection established

### 4. Test Cross-Tab Sync

1. Open app in two browser tabs
2. Send message in tab A
3. Verify tab B shows the new message

---

## Verification Checklist

- [ ] Backend starts without errors
- [ ] ChatKit server initializes with Gemini client
- [ ] `/api/chatkit` endpoint accepts POST requests
- [ ] SSE streaming works (visible in DevTools)
- [ ] Frontend ChatKit component renders
- [ ] Messages send and receive correctly
- [ ] Tool executions display properly
- [ ] Conversation persists across page refreshes
- [ ] Authentication works (JWT cookies)
- [ ] No WebSocket connections in DevTools
- [ ] Old chat components are deleted
- [ ] Code reduction achieved (~600+ LOC removed)

---

## Troubleshooting

### Issue: "Module not found: @openai/chatkit-react"

**Solution**:
```bash
cd frontend
npm install @openai/chatkit-react
```

### Issue: "Invalid base_url"

**Solution**: Verify `GEMINI_BASE_URL` in `.env`:
```
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

### Issue: SSE connection closes immediately

**Solution**: Check backend logs for errors. Verify `user_id` is extracted correctly from JWT.

### Issue: Tools not executing

**Solution**: Verify tools are wrapped with `@function_tool` decorator and added to agent's `tools` list.

### Issue: "Thread not found"

**Solution**: Ensure threads table is created and `thread_id` is properly passed from frontend.

---

## Rollback Plan

If migration fails, rollback steps:

1. **Backend**: Remove ChatKit code, restore WebSocket endpoints
2. **Frontend**: Restore `ChatInterface.tsx` and related components
3. **Database**: Keep `threads` table (can be used later)

**Git Rollback**:
```bash
git checkout main
git branch -D 010-chatkit-migration
```

---

## Next Steps

After successful migration:

1. Monitor Gemini API usage and costs
2. Set up rate limiting alerts
3. Add analytics for tool usage
4. Consider adding widget customization
5. Document any Gemini-specific behaviors

---

## Support Resources

- [ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents)
