# Implementation Plan: Todo AI Chatbot

**Branch**: `004-ai-chatbot` | **Date**: 2025-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chatbot/spec.md`

## Summary

Phase III extends the authenticated Todo web application into an AI-powered, stateless conversational system. Users can manage their todo lists using natural language through a chat interface. The AI agent interprets user intent and executes task operations (create, list, update, complete, delete) through MCP (Model Context Protocol) tools. All conversation history persists in the database, enabling context continuity across sessions. The architecture enforces strict statelessness - the backend holds no in-memory conversation state between requests, enabling horizontal scalability and server restarts without data loss.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend chat UI)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, AsyncOpenAI (openai>=1.0.0), Official MCP SDK, SQLModel, Pydantic
- Frontend: @openai/chatkit-react (OpenAI ChatKit), Next.js 15+, React 19+, Better Auth 1.4.10
- AI: Gemini API via OpenAI-compatible interface (google-generativeai>=0.8.0 with AsyncOpenAI adapter)

**Storage**:
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Schema extensions: Conversation, Message models (in addition to existing Task, User)

**Testing**: pytest (backend), React Testing Library (frontend), integration tests for AI agent flows

**Target Platform**: Web application (desktop and mobile browsers)

**Project Type**: Web application (stateless backend + reactive frontend)

**Performance Goals**:
- Chat API response time: <3 seconds (95th percentile)
- Task creation via chat: <5 seconds end-to-end
- Support 100 concurrent chat conversations
- AI intent recognition accuracy: 95%

**Constraints**:
- Stateless architecture: No in-memory conversation state between requests
- All state persisted in database
- AI agent MUST access database ONLY through MCP tools
- MCP tools MUST be stateless (no shared memory)
- JWT authentication required on every chat request
- User data isolation enforced at all layers

**Scale/Scope**:
- Single user context per conversation
- Conversations persist indefinitely
- Support unlimited messages per conversation
- Cross-device conversation continuity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase II Principle Compliance

**✓ Principle I: Persistent Storage**
- All conversation state (Conversation, Message entities) stored in Neon PostgreSQL
- No in-memory-only conversation data
- Database durability across server restarts

**✓ Principle II: RESTful API Excellence**
- Chat API endpoint follows REST patterns: POST /api/{user_id}/chat
- JSON responses with consistent error handling
- JWT authentication via Authorization header

**✓ Principle III: Responsive Web UI**
- Chat interface built on ChatKit (React-based)
- Works across desktop, tablet, mobile viewports
- Accessible keyboard and mouse interaction

**✓ Principle IV: Multi-User Architecture with Authentication**
- Every chat request authenticated via JWT (Better Auth)
- User ID extracted from validated token
- All conversations scoped to authenticated user
- Cross-user data isolation enforced

**✓ Principle VI: Monorepo Structure Standard**
- Chat API routes in `backend/api/`
- MCP server in `backend/mcp_server/`
- Chat UI integration in `frontend/components/chat/`
- Specs in `specs/004-ai-chatbot/`

**✓ Principle VII: Authentication & JWT Security**
- JWT verification on every chat request
- User ID extracted from token for data scoping
- Unauthorized requests return HTTP 401

**✓ Principle VIII: Frontend Architecture (Next.js)**
- Chat UI as Next.js App Router component
- Server component for initial load, client component for interactivity
- JWT passed via Authorization header from frontend

**✓ Principle IX: Data Ownership & Isolation**
- MCP tools enforce user_id filtering
- Conversations isolated per user
- Users cannot access other users' conversations or tasks

**✓ Principle X: API Response Consistency**
- Chat API returns standardized JSON responses
- Error responses include clear messages
- Consistent HTTP status codes (401, 404, 500)

### Phase III Extensions

This phase introduces new constitutional principles:

**✓ Principle XI: Stateless AI Architecture**
- Backend maintains no in-memory conversation state
- All conversation context loaded from database per request
- Enables horizontal scaling and fault tolerance

**✓ Principle XII: MCP Tool Isolation**
- AI agent interacts with system exclusively through MCP tools
- No direct database access by AI agent
- MCP tools enforce statelessness and user isolation

**✓ Principle XIII: Conversational Persistence**
- All user and AI messages persisted before/after processing
- Conversation history replayable after server restart
- Cross-device conversation continuity

**Gate Status**: ✅ PASSED - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
# Existing Phase II structure (preserved)
backend/
├── models/
│   ├── task.py          # Existing Task model
│   ├── user.py          # Existing User model
│   ├── conversation.py  # NEW: Conversation model
│   └── message.py       # NEW: Message model
├── services/
│   ├── auth.py          # Existing JWT verification
│   ├── task_service.py  # Existing task CRUD operations
│   └── chat_service.py  # NEW: Chat business logic
├── api/
│   ├── tasks.py         # Existing task endpoints
│   └── chat.py          # NEW: Chat API endpoint
├── mcp_server/          # NEW: MCP server implementation
│   ├── __init__.py
│   ├── server.py        # MCP server setup
│   └── tools/           # MCP tool implementations
│       ├── __init__.py
│       ├── add_task.py
│       ├── list_tasks.py
│       ├── update_task.py
│       ├── complete_task.py
│       └── delete_task.py
├── ai_agent/            # NEW: AI agent integration
│   ├── __init__.py
│   ├── agent.py         # OpenAI Agents SDK setup
│   └── prompts.py       # System prompts for AI
├── core/
│   ├── config.py        # Database, API, AI config
│   └── security.py      # JWT verification (existing)
└── tests/
    ├── test_chat_api.py
    ├── test_mcp_tools.py
    └── test_ai_agent.py

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx     # NEW: Chat interface page
├── components/
│   └── chat/            # NEW: Chat UI components
│       ├── ChatInterface.tsx
│       ├── MessageList.tsx
│       └── MessageInput.tsx
├── lib/
│   ├── auth.ts          # Existing Better Auth client
│   └── api.ts           # Existing API client
│   └── chat-api.ts      # NEW: Chat API client
└── tests/
    └── chat/
        └── ChatInterface.test.tsx
```

**Structure Decision**: Option 2 (Web application) - This feature extends the existing Phase II web application with AI chat capabilities. The backend adds MCP server and AI agent integration. The frontend adds ChatKit-based chat UI. The monorepo structure follows Principle VI (Monorepo Structure Standard) by coexisting with Phase II backend/frontend directories.

## Component Architecture

### High-Level Data Flow

```
User
  ↓ (types message)
Chat UI (ChatKit)
  ↓ (POST /api/{user_id}/chat + JWT)
Chat API (FastAPI)
  ↓ (authenticate + load conversation history)
AI Agent (OpenAI Agents SDK)
  ↓ (select tools based on intent)
MCP Tools (Official MCP SDK)
  ↓ (enforce user isolation)
Database (Neon PostgreSQL)
  ↓ (return results)
AI Agent (generate response)
  ↓ (persist assistant message)
Chat API (return response)
  ↓ (display confirmation)
Chat UI
```

### Component Responsibilities

#### 1. Chat API Endpoint (`backend/api/chat.py`)

**Responsibilities**:
- Authenticate JWT token and extract user_id
- Validate user_id matches URL parameter
- Load conversation history from database (if conversation_id provided)
- Create new conversation if none exists
- Persist user message as Message(role="user")
- Invoke AI agent with full conversation history
- Persist AI response as Message(role="assistant")
- Return standardized JSON response

**Contract**:
```python
POST /api/{user_id}/chat
Authorization: Bearer <JWT>
Content-Type: application/json

Request:
{
  "message": "Add a task to buy groceries",
  "conversation_id": "uuid-or-null"
}

Response (200 OK):
{
  "message_id": "uuid",
  "conversation_id": "uuid",
  "role": "assistant",
  "content": "I've added the task 'buy groceries' for you.",
  "created_at": "2025-01-15T10:30:00Z"
}

Error (401 Unauthorized):
{
  "error": "Invalid or missing JWT token"
}

Error (403 Forbidden):
{
  "error": "user_id does not match authenticated user"
}
```

**Stateless Guarantee**:
- No global conversation state variables
- No session storage
- All conversation context loaded from database per request

#### 2. AI Agent Layer (`backend/ai_agent/agent.py`)

**Responsibilities**:
- Initialize OpenAI Agents SDK with Gemini model configuration
- Create AsyncOpenAI client configured for Gemini API
- Register MCP tools with agent
- Interpret user intent from conversation history
- Select appropriate tools (add_task, list_tasks, etc.)
- Chain multiple tools if needed
- Generate human-friendly natural language responses
- Handle tool errors gracefully

**Inputs**:
- Conversation history (list of Message objects)
- Current user message (string)
- User context (user_id for MCP tool scoping)

**Outputs**:
- Natural language response (string)
- Tool call results (for logging/audit)

**Implementation Pattern** (Gemini + OpenAI Agents SDK):
```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from backend.core.config import SETTINGS

# Create AsyncOpenAI client configured for Gemini API
gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=SETTINGS.gemini_api_key
)

# Initialize task management agent
task_agent = Agent(
    name="task_manager",
    instructions="""You are a helpful task management assistant.
    Users can create, list, update, complete, and delete tasks through natural language.
    Always confirm actions clearly and ask for clarification when requests are ambiguous.""",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=gemini_client,
    ),
)

# Execute agent with conversation history
result = await Runner.run(
    task_agent,
    input=conversation_history + [current_message],
    context={"user_id": user_id}
)
```

**Constraints**:
- NEVER accesses database directly
- ONLY interacts with system through MCP tools
- No memory between invocations (stateless)
- MUST use AsyncOpenAI adapter for Gemini API compatibility

#### 3. MCP Server (`backend/mcp_server/server.py`)

**Responsibilities**:
- Initialize MCP server with official SDK
- Register 5 task management tools
- Validate tool parameters (Pydantic schemas)
- Enforce user_id scoping on all operations
- Return structured JSON results

**Exposed Tools**:
1. `add_task(title: str, description: str | None, user_id: int) -> Task`
2. `list_tasks(user_id: int, completed: bool | None) -> List[Task]`
3. `update_task(task_id: int, user_id: int, title: str | None, description: str | None) -> Task`
4. `complete_task(task_id: int, user_id: int, completed: bool) -> Task`
5. `delete_task(task_id: int, user_id: int) -> SuccessResponse`

**Tool Execution Contract**:
- Each tool accepts user_id parameter
- All database queries filter by user_id
- Tools return structured success/error responses
- No tool maintains internal state between calls
- Tools are independently testable

#### 4. Chat UI (`frontend/components/chat/`)

**Responsibilities**:
- Render chat interface with message history using @openai/chatkit-react
- Send user messages to Chat API endpoint
- Pass conversation_id if available
- Display streaming or full AI responses
- Show loading states and error messages
- Auto-scroll to latest message

**Technology**: @openai/chatkit-react (OpenAI's official ChatKit React bindings)

**Component Implementation**:
```typescript
// frontend/components/chat/ChatInterface.tsx
'use client'

import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { useState } from 'react'

export default function ChatInterface({ userId, jwt }: { userId: number, jwt: string }) {
  const [messages, setMessages] = useState([])

  const handleSubmit = async (input: string) => {
    const response = await fetch(`/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: input,
        conversation_id: currentConversationId
      })
    })

    const data = await response.json()
    setMessages([...messages, { role: 'user', content: input }, { role: 'assistant', content: data.content }])
  }

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSubmit}
      style={{ height: '600px' }}
    />
  )
}
```

**Alternative: Using ChatKit Web Component Directly**:
```typescript
// In layout.tsx or _document.tsx
import '@openai/chatkit-react'

// Then use the web component
<openai-chatkit
  api-url={`/api/${userId}/chat`}
  headers={{ Authorization: `Bearer ${jwt}` }}
  style={{ height: '600px' }}
/>
```

#### 5. Persistence Layer (`backend/models/`)

**New Models**:

**Conversation** (`backend/models/conversation.py`):
```python
class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    relationships:
      - has many Message
      - belongs to User
```

**Message** (`backend/models/message.py`):
```python
class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    user_id: int = Field(foreign_key="user.id")
    role: Literal["user", "assistant"] = Field(...)
    content: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    relationships:
      - belongs to Conversation
      - belongs to User
```

**Existing Models Extended**:
- Task: No changes needed (existing model sufficient)
- User: No changes needed (existing authentication sufficient)

## Complexity Tracking

> **No constitutional violations requiring justification**

All design decisions align with Phase II/III constitutional principles. The architecture introduces necessary complexity (AI agent, MCP tools, conversation persistence) to deliver conversational task management while maintaining statelessness, data isolation, and RESTful API design.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

**1. OpenAI Agents SDK Integration**
- Question: How to integrate OpenAI Agents SDK with FastAPI?
- Question: How to register MCP tools with OpenAI agent?
- Question: How to pass conversation history to agent?
- Decision: Research SDK documentation, examples, and best practices

**2. Official MCP SDK Usage**
- Question: How to create MCP server with Python SDK?
- Question: How to define tool schemas (Pydantic models)?
- Question: How to invoke MCP tools from AI agent?
- Decision: Review MCP SDK documentation and examples

**3. ChatKit Integration**
- Question: How to integrate ChatKit with Next.js App Router?
- Question: How to pass JWT with ChatKit API requests?
- Question: How to handle conversation persistence in ChatKit?
- Decision: Review ChatKit documentation and Next.js integration patterns

**4. Stateless Conversation Management**
- Question: How to efficiently load conversation history per request?
- Question: How to optimize database queries for conversation replay?
- Question: How to handle large conversations (1000+ messages)?
- Decision: Research pagination, lazy loading, and query optimization

**5. Error Handling Strategy**
- Question: How to handle AI service unavailability gracefully?
- Question: How to present AI errors to users without technical details?
- Question: How to retry failed tool invocations?
- Decision: Design error handling patterns for AI systems

### Research Deliverables

File: `specs/004-ai-chatbot/research.md`

Contents:
- Technology choices with rationale
- Alternative approaches considered
- Best practices for each technology
- Integration patterns between components
- Security considerations for AI systems
- Performance optimization strategies

---

## Phase 1: Design & Contracts

### Prerequisites

- `research.md` complete with all decisions documented
- No "NEEDS CLARIFICATION" items remaining

### Data Model Design

File: `specs/004-ai-chatbot/data-model.md`

Contents:
- Entity-Relationship diagram
- Complete field definitions for Conversation and Message models
- Validation rules (from FR-001 through FR-040)
- Indexes for query optimization
- Relationship mappings (foreign keys)
- State transitions (if applicable)

### API Contracts

Directory: `specs/004-ai-chatbot/contracts/`

File: `chat-api.yaml` (OpenAPI 3.0 specification)

Contents:
- POST /api/{user_id}/chat endpoint
- Request schemas (message, conversation_id)
- Response schemas (message, conversation_id, role, content, created_at)
- Error schemas (400, 401, 403, 404, 500)
- Authentication requirements (JWT)
- Rate limiting (if applicable)

### Quickstart Guide

File: `specs/004-ai-chatbot/quickstart.md`

Contents:
- How to run backend with chat API
- How to run MCP server
- How to run frontend with chat UI
- How to test chat endpoint manually (curl examples)
- How to test MCP tools independently
- Environment variables required
- Common troubleshooting steps

### Agent Context Update

Execute: `.specify/scripts/bash/update-agent-context.sh claude`

Purpose: Update CLAUDE.md with new Phase III technologies:
- OpenAI Agents SDK
- Official MCP SDK
- ChatKit
- Conversation and Message models

---

## Phase 2: Implementation Tasks

**NOTE**: This phase is executed by `/sp.tasks` command (NOT by `/sp.plan`).

The `/sp.tasks` command will:
1. Read `plan.md` (this file)
2. Read `data-model.md`
3. Read `contracts/chat-api.yaml`
4. Generate atomic, testable tasks for:
   - Database schema creation (Conversation, Message tables)
   - MCP server implementation (5 tools)
   - AI agent integration
   - Chat API endpoint
   - Chat UI components
   - Integration tests
   - End-to-end tests

Each task will include:
- Task ID
- Description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links to spec and plan sections

---

## Success Metrics

From spec success criteria (SC-001 through SC-010):

- **SC-001**: Task creation via chat in <5 seconds
- **SC-002**: AI responses in <3 seconds (95th percentile)
- **SC-003**: 90% of requests succeed without clarification
- **SC-004**: Conversation history accessible after 7+ days
- **SC-005**: Zero data loss after server restart
- **SC-006**: 95% intent recognition accuracy
- **SC-007**: Full task management via natural language
- **SC-008**: 100% MCP tool invocation logging
- **SC-009**: Zero unauthorized cross-user access
- **SC-010**: 100 concurrent conversations supported

---

## Dependencies & Integration Points

### External Dependencies
- OpenAI API (AI model)
- OpenAI Agents SDK (agent framework)
- Official MCP SDK (tool protocol)
- ChatKit (UI components)

### Internal Dependencies
- Phase II authentication (Better Auth, JWT)
- Phase II task API (task CRUD operations)
- Phase II database schema (User, Task models)
- Phase II frontend infrastructure (Next.js, API client)

### Integration Points
1. Chat API ↔ Auth service (JWT verification)
2. Chat API ↔ Database (conversation/message persistence)
3. AI Agent ↔ MCP Server (tool invocation)
4. MCP Server ↔ Task Service (task operations)
5. Chat UI ↔ Chat API (HTTP requests)
6. Chat UI ↔ Auth client (JWT retrieval)

---

## Security Considerations

### AI Security
- Prompt injection prevention (sanitize user messages)
- Tool authorization (user_id scoping on all MCP tools)
- Rate limiting (prevent AI abuse)
- Audit logging (all tool invocations logged)

### Data Security
- User isolation enforced at MCP tool layer
- Conversation data never exposed cross-user
- JWT validation on every request
- Database connection encryption

### Error Security
- No technical details in user-facing error messages
- No stack traces exposed
- Generic error messages for AI failures
- Secure error logging (server-side only)

---

## Testing Strategy

### Unit Tests
- MCP tool parameter validation
- AI agent intent recognition (mocked tool responses)
- Chat API request/response handling
- Message model creation and relationships

### Integration Tests
- End-to-end chat flow (user message → AI response)
- MCP tool execution with real database
- Conversation persistence and replay
- JWT authentication enforcement

### E2E Tests
- User creates task via natural language
- User lists tasks conversationally
- User updates and completes tasks
- Conversation persists across page refresh
- Unauthorized access blocked

### AI Testing
- Intent recognition accuracy test suite
- Tool selection test cases
- Error handling and fallback testing
- Response quality evaluation

---

## Rollout & Migration

### Database Migration
- Create Conversation table
- Create Message table
- Add foreign key constraints
- Create indexes for query optimization

### Backend Deployment
- Deploy MCP server alongside existing API
- Deploy AI agent integration
- Add chat API endpoint
- No breaking changes to existing task API

### Frontend Deployment
- Add chat UI components
- Add chat route (/chat)
- Update navigation to include chat link
- No changes to existing task management UI

---

## Monitoring & Observability

### Metrics to Track
- Chat API response times (p50, p95, p99)
- AI agent intent recognition accuracy
- MCP tool invocation success rate
- Conversation creation rate
- Error rates by type (auth, AI, database)

### Logging Strategy
- All chat requests logged with user_id
- All MCP tool invocations logged with parameters
- AI agent decisions logged (tool selection)
- Errors logged with full context

---

## Open Questions

**None** - All technical decisions documented in research.md

---

**Plan Version**: 1.0.0
**Last Updated**: 2025-01-15
**Status**: Ready for Phase 0 Research
