# Backend Development Guidelines

## Project Overview

This directory contains the backend API for the Todo List application, built with Python FastAPI and SQLModel.

## Technology Stack

- **Language**: Python 3.13+
- **Web Framework**: FastAPI (modern, high-performance web framework for building APIs)
- **ORM**: SQLModel (combines SQLAlchemy and Pydantic for database interactions and validation)
- **Database**: Neon Serverless PostgreSQL
- **Package Manager**: UV
- **AI/Chat**: OpenAI ChatKit Python SDK, OpenAI Agents SDK, Gemini LLM (via OpenAI-compatible endpoint)

## Project Structure

```
backend/
├── src/                    # Application source code
│   ├── models/            # SQLModel database models
│   ├── api/               # API route handlers
│   ├── services/          # Business logic layer
│   ├── database.py        # Database connection and session management
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test suite
├── pyproject.toml         # UV project configuration
└── CLAUDE.md             # This file
```

## Development Commands

```bash
cd backend

# Install dependencies
uv sync

# Run development server
uv run python src/main.py

# Run tests
uv run pytest tests/

# Run with auto-reload during development
uv run uvicorn src.main:app --reload

# Check code quality
uv run ruff check .
```

## API Endpoints

The following REST API endpoints are implemented:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks for a user |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status |
| POST | `/api/chatkit` | ChatKit SSE endpoint for AI chat (Gemini) |

## Database Models

### Task Model
- `id`: Unique identifier (auto-generated)
- `user_id`: Foreign key to user (for data segregation)
- `title`: Task title (required, max 255 characters)
- `description`: Task description (optional, max 2000 characters)
- `completed`: Boolean status (default: false)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Key Features

- **FastAPI Auto-Documentation**: Interactive API docs available at `/docs` and `/redoc`
- **Validation**: Automatic request/response validation via Pydantic
- **Async Support**: Built-in async/await for high-performance I/O
- **Type Safety**: Full type hints with SQLModel and Pydantic
- **Database Migrations**: SQLModel schema management with Alembic (if needed)

## Development Notes

- Authentication is NOT enforced in this phase (user_id is passed as path parameter)
- Database connection string should be provided via `DATABASE_URL` environment variable
- Default pagination: 50 tasks per request, maximum 100
- All timestamps are in UTC
- Use dependency injection for database sessions

## Environment Variables

```bash
DATABASE_URL=postgresql://user:password@host/database
```

## Testing Strategy

- Unit tests for business logic
- Integration tests for API endpoints
- Database tests with test fixtures
- Use pytest for test runner
- Mock external dependencies where appropriate

## Code Style

- Follow Python 3.13+ standard conventions
- Use type hints for all function signatures
- Docstrings for all public functions and classes
- Ruff for linting and formatting

## Performance Considerations

- Use database indexing on frequently queried fields (user_id, created_at)
- Implement pagination for list endpoints to prevent large result sets
- Use async database operations for better concurrency
- Connection pooling for database connections

## Documentation Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Related Specs

- Feature Specification: [specs/001-backend-task-api/spec.md](../specs/001-backend-task-api/spec.md)
- Project Constitution: [constitution.md](../.memory/constitution.md)

---

## ChatKit Architecture (Phase 010-chatkit-migration)

### Overview

The backend now uses **OpenAI ChatKit** with **Gemini LLM** for AI-powered task management through natural language.

**[From]: specs/010-chatkit-migration/**

### Key Components

#### 1. ChatKit Server (`chatkit_server.py`)

- **TaskManagerChatKitServer**: Main orchestrator for ChatKit protocol
- **AgentContext**: Context object passed to agent with thread_id, user_id, store
- **SSE Streaming**: Server-Sent Events for real-time response streaming
- **Tool Integration**: MCP tools wrapped as Agents SDK functions

```python
# Usage
from chatkit_server import get_chatkit_server
from services.chatkit_store import PostgresChatKitStore

store = PostgresChatKitStore(db_session)
server = get_chatkit_server(store)
result = await server.process(body, {"user_id": user_id})
```

#### 2. ChatKit Store (`services/chatkit_store.py`)

- **PostgresChatKitStore**: Implements ChatKit's Store protocol for PostgreSQL
- **Thread Management**: create_thread, get_thread, list_threads, update_thread, delete_thread
- **Message Persistence**: create_message, get_message, list_messages, update_message, delete_message
- **Async Operations**: All database operations are async for performance

#### 3. Tool Wrappers (`ai_agent/tool_wrappers.py`)

- **7 MCP Tools Wrapped**: create_task, list_tasks, update_task, delete_task, complete_task, bulk_complete_tasks, bulk_delete_tasks
- **Agents SDK Functions**: Each tool wrapped with @function_tool decorator
- **JSON Response Format**: Tools return JSON strings for ChatKit compatibility

#### 4. SSE Endpoint (`api/chat.py`)

- **POST /api/chatkit**: Main ChatKit SSE endpoint
- **Authentication**: JWT via httpOnly cookie (auth_token)
- **Rate Limiting**: 100 messages/day per user
- **Error Handling**: Connection drop detection, timeout handling (120s)

### SSE Event Types

```typescript
// Streaming text
event: message_delta
data: {"type": "text", "text": "Hello!"}

// Tool execution
event: tool_call_created
data: {"tool": "create_task", "args": {...}}

// Message complete
event: message_done
data: {"message_id": "...", "role": "assistant"}

// Error
event: error
data: {"detail": "Error message"}
```

### Gemini LLM Integration

**OpenAI-Compatible Endpoint**: `https://generativelanguage.googleapis.com/v1beta/openai/`

**Configuration** (`.env`):
```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Client Setup** (`core/config.py`):
```python
from openai import AsyncOpenAI

def get_gemini_client():
    return AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
    )
```

### Database Schema

**Thread Model** (`models/thread.py`):
```python
class Thread(SQLModel, table=True):
    id: uuid.UUID (PK)
    user_id: uuid.UUID (FK)
    title: Optional[str]
    metadata: JSONB
    created_at: datetime
    updated_at: datetime
```

**Message Model** (extended in `models/message.py`):
```python
class Message(SQLModel, table=True):
    thread_id: Optional[uuid.UUID] (FK)  # NEW
    tool_calls: Optional[JSONB]  # NEW
    role: MessageRole (SYSTEM role added)
```

### Migration Notes

**WebSocket → SSE**: Legacy WebSocket streaming has been replaced with Server-Sent Events:
- Removed `backend/ws_manager/` directory
- Removed `@router.websocket("/ws/{user_id}/chat")` endpoint
- SSE is simpler, HTTP-based, and works better with ChatKit

**Frontend Components**: Legacy chat components replaced with ChatKit:
- Removed `ChatInterface.tsx`, `MessageList.tsx`, `MessageInput.tsx`
- Removed `ProgressBar.tsx`, `ConnectionStatus.tsx`, `useWebSocket.ts`
- New `TaskChat.tsx` wraps `@openai/chatkit-react`

### Performance Optimizations

- **Connection-Aware Streaming**: Handles client disconnects gracefully
- **Timeout Protection**: 120-second timeout for agent execution
- **Async Database**: All store operations use AsyncSession
- **Rate Limiting**: Prevents abuse (100 messages/day)
- **SSE Headers**: `X-Accel-Buffering: no` for real-time delivery

### Related Documentation

- [ChatKit Migration Spec](../specs/010-chatkit-migration/spec.md)
- [ChatKit Migration Plan](../specs/010-chatkit-migration/plan.md)
- [ChatKit Research](../specs/010-chatkit-migration/research.md)



<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

### Feb 6, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #1290 | 11:13 AM | 🔵 | Reviewed backend dependencies in pyproject.toml | ~198 |
| #1281 | 11:10 AM | 🔵 | Reviewed backend project dependencies in pyproject.toml | ~220 |
| #1222 | 10:29 AM | 🔵 | Configuration review: Database and API settings confirmed | ~268 |
| #1212 | 10:18 AM | 🔴 | Fixed SyntaxError in FastAPI route parameter ordering | ~278 |

### Feb 7, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #1518 | 12:51 PM | 🔵 | ChatKitServer Implementation with Agent Configuration | ~200 |
| #1517 | " | 🔴 | OpenAI Agents SDK Import Error in ChatKit Server | ~161 |
| #1507 | 12:33 PM | 🔵 | Verified SSE implementation in chatkit_server.py | ~221 |
| #1503 | 12:31 PM | 🔴 | Fixed Migration Script Database URL Handling | ~173 |
| #1501 | 12:27 PM | 🔵 | Database Configuration Verified | ~131 |
| #1463 | 11:57 AM | 🟣 | ChatKit Migration Complete - WebSocket Replaced with SSE | ~300 |
| #1458 | 11:55 AM | ✅ | Backend Documentation Updated with ChatKit Architecture | ~201 |
| #1457 | " | ✅ | Backend Documentation Updated with ChatKit Architecture | ~148 |
| #1436 | 11:44 AM | 🟣 | Added Timeout Handling for Agent Execution (T034) | ~178 |
| #1430 | 11:37 AM | 🟣 | OpenAI Agents SDK Integration for ChatKitServer | ~198 |
| #1428 | 11:36 AM | 🟣 | ChatKitServer Orchestrator Implementation | ~213 |
| #1429 | " | 🟣 | Phase 2 ChatKit Foundation Completed | ~191 |

### Feb 8, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #1538 | 12:05 PM | 🔴 | SSE JSON Parsing Error in TaskChat Frontend | ~192 |
| #1530 | 11:55 AM | 🟣 | Database Migration Executed Successfully | ~164 |
| #1529 | 11:54 AM | 🟣 | Database Migration Script for tool_calls Column | ~154 |
| #1519 | 11:41 AM | 🔴 | Removed Invalid stream_agent_response Import | ~175 |
</claude-mem-context>