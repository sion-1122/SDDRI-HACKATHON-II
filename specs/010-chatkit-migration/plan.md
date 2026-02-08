# Implementation Plan: ChatKit Migration with Gemini Compatibility

**Branch**: `010-chatkit-migration` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-chatkit-migration/spec.md`

## Summary

Migrate the custom chat system to use OpenAI's ChatKit UI framework while maintaining Gemini as the exclusive LLM provider. The migration uses ChatKit's **self-hosted integration** pattern, which involves:

1. **Frontend**: Replace ~600 lines of custom React chat components with ChatKit React UI
2. **Backend**: Implement custom `ChatKitServer` using ChatKit Python SDK
3. **LLM**: Continue using Gemini via OpenAI-compatible endpoint
4. **Orchestration**: Continue using OpenAI Agents SDK with custom AsyncOpenAI client
5. **Streaming**: Replace WebSocket with Server-Sent Events (SSE)
6. **Deletion**: Remove all WebSocket-related code (~350 lines backend)

**Key Benefits**:
- ~950 total lines of code removed
- Vendor-supported UI components with built-in streaming
- No OpenAI vendor lock-in (self-hosted pattern)
- Reduced maintenance burden
- Improved UX with ChatKit's polished interface

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**:
  - Backend: FastAPI, openai-chatkit, openai-agents, openai (AsyncOpenAI)
  - Frontend: Next.js 16, React 19, @openai/chatkit-react
**Storage**: Neon Serverless PostgreSQL (existing, threads table added)
**Testing**: pytest (backend), existing frontend tests
**Target Platform**: Web (browser with SSE support)
**Project Type**: Web application (backend + frontend)
**Performance Goals**:
  - < 2 second first token response time
  - < 500ms tool execution visibility
  - < 1 second session creation
**Constraints**:
  - MUST use Gemini exclusively (no OpenAI models)
  - MUST maintain existing authentication (JWT cookies)
  - MUST preserve all MCP tools functionality
  - MUST NOT use OpenAI-hosted workflows
**Scale/Scope**:
  - ~950 LOC removed from codebase
  - 7 task management tools preserved
  - Single chat execution surface maintained

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle II: RESTful API Excellence
**Status**: ✅ PASS (with modification)
**Analysis**: Migration replaces WebSocket with SSE streaming endpoint. SSE is a standard HTTP extension with `text/event-stream` content type. The `/api/chatkit` endpoint maintains RESTful principles for resource-oriented communication while using SSE for response streaming (an accepted pattern for real-time data).

**Justification**: SSE is a standardized protocol (RFC 6202) for server-to-client streaming over HTTP. Unlike WebSocket (which is a separate protocol upgrade), SSE maintains HTTP semantics and is compatible with RESTful architecture. ChatKit uses SSE exclusively for response streaming, not request handling.

### Principle III: Responsive Web UI
**Status**: ✅ PASS
**Analysis**: ChatKit React is a modern responsive component library. It provides responsive design out of the box and works across desktop, tablet, and mobile viewports.

### Principle IV: Multi-User Architecture with Authentication
**Status**: ✅ PASS
**Analysis**: Authentication remains JWT-based via httpOnly cookies. The custom `fetch` override in ChatKit configuration preserves existing authentication flow. User identity extracted from JWT and passed to agent context.

### Principle VI: Monorepo Structure Standard
**Status**: ✅ PASS
**Analysis**: No structural changes to monorepo layout. New files follow existing patterns:
- `backend/chatkit_server.py` (new)
- `backend/chatkit_store.py` (new)
- `frontend/src/components/chat/TaskChat.tsx` (new, replaces ChatInterface.tsx)

### Principle VII: Authentication & JWT Security
**Status**: ✅ PASS
**Analysis**: JWT authentication flow unchanged. Tokens still extracted from httpOnly cookies. No Authorization header modifications needed (ChatKit's custom fetch handles cookies automatically via `credentials: 'include'`).

### Principle VIII: Frontend Architecture (Next.js)
**Status**: ✅ PASS
**Analysis**: ChatKit React is compatible with Next.js App Router. The wrapper component is a client component (`"use client"`), which is appropriate for interactive UI. Server-side data fetching patterns preserved.

### Principle IX: Data Ownership & Isolation
**Status**: ✅ PASS
**Analysis**: All queries scoped to authenticated user's `user_id`. The new `threads` table includes `user_id` foreign key with CASCADE delete. ChatKit server receives `user_id` from JWT and enforces data isolation.

### Principle X: API Response Consistency
**Status**: ✅ PASS
**Analysis**: SSE events follow ChatKit's standardized event format. Error responses maintain JSON structure with appropriate status codes (401, 429, 500).

### Principle II Exceptions
**Modification**: Using SSE instead of pure REST for streaming responses
**Justification**: SSE is the documented and supported pattern for ChatKit streaming. It maintains HTTP semantics while enabling real-time response streaming. This is a targeted exception for a specific technical requirement (streaming AI responses).

### Phase III Compliance
**Status**: ✅ PASS
**Analysis**: Migration maintains Phase III capabilities (AI chat, MCP tools, streaming) while updating the implementation framework. All Phase III features preserved:
- Chat interface: ✅ (ChatKit UI)
- MCP tools: ✅ (wrapped as Agents SDK functions)
- Conversation persistence: ✅ (via Store interface)
- Streaming responses: ✅ (via SSE instead of WebSocket)

---

## Project Structure

### Documentation (this feature)

```text
specs/010-chatkit-migration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - ChatKit + Gemini compatibility research
├── data-model.md        # Phase 1 output - Thread/Message data model
├── quickstart.md        # Phase 1 output - Migration quick start guide
├── contracts/           # Phase 1 output - API contracts
│   ├── backend.md       # Backend ChatKit endpoint contracts
│   └── frontend.md      # Frontend ChatKit React integration
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
backend/
├── models/
│   └── thread.py        # NEW - Thread model for ChatKit
├── services/
│   └── chatkit_store.py # NEW - PostgreSQL Store implementation
├── api/
│   └── chat.py          # MODIFIED - Add /api/chatkit SSE endpoint
├── chatkit_server.py    # NEW - ChatKitServer implementation
├── ai_agent/            # MODIFIED - Update for ChatKit integration
│   └── agent.py         # Keep existing agent, wrap tools
├── ws_manager/          # DELETED - Remove entire directory
│   ├── manager.py       # DELETED
│   └── events.py        # DELETED
└── core/
    └── deps.py          # EXISTING - get_current_user_id() used by ChatKit endpoint

frontend/
├── components/
│   └── chat/
│       ├── TaskChat.tsx         # NEW - ChatKit wrapper component
│       ├── ChatInterface.tsx    # DELETED
│       ├── MessageList.tsx      # DELETED
│       ├── MessageInput.tsx     # DELETED
│       ├── ProgressBar.tsx      # DELETED
│       ├── ConnectionStatus.tsx # DELETED
│       └── useWebSocket.ts      # DELETED
├── lib/
│   └── api/
│       └── client.ts    # EXISTING - Custom fetch uses this pattern
└── app/
    └── dashboard/
        └── page.tsx     # MODIFIED - Use TaskChat instead of ChatInterface
```

**Structure Decision**: Selected Option 2 (Web Application) from plan template. The migration modifies existing backend and frontend directories without changing the overall monorepo structure. New files follow existing naming conventions (e.g., `chatkit_server.py` at backend root, `TaskChat.tsx` in components/chat). The deletion of `ws_manager/` directory removes ~350 LOC of WebSocket-specific code. Frontend chat components directory reduces from ~600 LOC to a single ~50 LOC wrapper component.

## Architecture Diagram

### Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                             │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐     │
│  │ ChatInterface  │  │ MessageList    │  │ useWebSocket      │     │
│  │ (286 LOC)      │  │ (~80 LOC)      │  │ (~100 LOC)        │     │
│  └────────┬───────┘  └────────┬───────┘  └────────┬─────────┘     │
│           │                   │                    │                │
│           └───────────────────┴────────────────────┘                │
│                               │                                     │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │ WebSocket             │ REST (HTTP POST)       │
        │ (ws://)               │ (/api/{user_id}/chat)   │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                           │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐     │
│  │ws_manager      │  │ AI Agent       │  │ MCP Tools         │     │
│  │ manager.py     │  │ agent_streaming│  │ (7 tools)         │     │
│  │ (196 LOC)      │  │ (~159 LOC)     │  │                   │     │
│  └────────────────┘  └────────┬───────┘  └──────────────────┘     │
│                               │                                    │
│                      ┌────────┴────────┐                          │
│                      │ AsyncOpenAI      │                          │
│                      │ (custom base_url)│                          │
│                      └────────┬────────┘                          │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
                       ┌────────────────┐
                       │  Gemini API    │
                       │ (OpenAI-compatible)
                       └────────────────┘
```

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                             │
│  ┌────────────────┐  ┌────────────────┐                          │
│  │ TaskChat       │  │ ChatKit React  │                          │
│  │ (~50 LOC)      │  │ (UI Library)   │                          │
│  │ Wrapper        │  │ Messages, Input│                          │
│  │                │  │ Tool Widgets   │                          │
│  └────────┬───────┘  └────────┬───────┘                          │
│           │ SSE (text/event-stream)                             │
│           │ Custom fetch with auth cookies                       │
└───────────┼───────────────────────────────────────────────────────┘
            │
            │ POST /api/chatkit
            │ Server-Sent Events
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                           │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐     │
│  │ChatKitServer   │  │ PostgresStore  │  │ Wrapped MCP       │     │
│  │ (custom impl)  │  │ (Thread/Message)│ │ Tools             │     │
│  │ (~150 LOC)     │  │ (~200 LOC)     │  │ (@function_tool)  │     │
│  └────────┬───────┘  └────────┬───────┘  └──────────────────┘     │
│           │                   │                                    │
│           └───────────────────┴────────────────┐                   │
│                      ┌────────┴────────┐        │                  │
│                      │ Agents SDK      │        │                  │
│                      │ + AsyncOpenAI   │        │                  │
│                      │ (Gemini client) │        │                  │
│                      └────────┬────────┘        │                  │
└───────────────────────────────┼─────────────────┼──────────────────┘
                                │                 │
                    ┌───────────┴─────────┐     │
                    │Gemini OpenAI-compatible│    │
                    │endpoint               │    │
                    └───────────┬───────────┘    │
                                │                │
                                ▼                ▼
                       ┌────────────────┐  ┌──────────┐
                       │  Gemini API    │  │ Neon DB  │
                       │ (LLM)          │  │ (Storage)│
                       └────────────────┘  └──────────┘
```

### Key Changes

1. **Frontend**: ChatKit React replaces all custom chat components (~600 LOC → ~50 LOC)
2. **Streaming**: SSE replaces WebSocket (simpler protocol, HTTP-native)
3. **Backend**: ChatKitServer + PostgresStore replaces WebSocket manager (~350 LOC removed)
4. **Storage**: New `threads` table for ChatKit's thread-based conversation model
5. **Protocol**: SSE events (ChatKit standard) instead of custom WebSocket events

---

## Implementation Phases

### Phase 0: Research & Validation ✅ COMPLETE

**Status**: Completed via research agent

**Deliverables**:
- [x] `research.md` - Comprehensive ChatKit + Gemini compatibility analysis
- [x] Validated Gemini OpenAI-compatible endpoint support
- [x] Confirmed ChatKit self-hosted integration pattern
- [x] Documented all technical requirements and constraints

**Key Findings**:
- ✅ ChatKit CAN work with Gemini via self-hosted integration
- ✅ Custom `base_url` supported by OpenAI SDK and Agents SDK
- ✅ SSE streaming fully supported by ChatKit and Gemini
- ✅ No OpenAI Sessions API required for self-hosted mode
- ✅ All 7 MCP tools can be wrapped as Agents SDK functions

### Phase 1: Design & Contracts ✅ COMPLETE

**Status**: Completed

**Deliverables**:
- [x] `data-model.md` - Thread/Message data model with Store interface
- [x] `contracts/backend.md` - Backend API contracts for ChatKit endpoint
- [x] `contracts/frontend.md` - Frontend ChatKit React integration
- [x] `quickstart.md` - Step-by-step migration guide

**Design Decisions**:
1. **Store Interface**: PostgreSQL implementation for thread/message persistence
2. **Authentication**: Custom `fetch` override with JWT cookies (no OpenAI Sessions API)
3. **Tool Wrapping**: MCP tools wrapped with `@function_tool` decorator
4. **Streaming**: SSE via `/api/chatkit` endpoint (text/event-stream)
5. **Error Handling**: Maintains existing error response format

### Phase 2: Backend Implementation (Pending)

**Tasks**:
1. Install dependencies (`openai-chatkit`, `openai-agents`)
2. Configure Gemini AsyncOpenAI client
3. Implement `ChatKitServer` class
4. Implement `PostgresChatKitStore` class
5. Create `Thread` database model
6. Run database migration (threads table)
7. Create `/api/chatkit` SSE endpoint
8. Wrap existing MCP tools as Agents SDK functions
9. Update agent configuration for Gemini model
10. Add rate limiting to `/api/chatkit`
11. Write integration tests for streaming endpoint
12. Test tool execution through ChatKit

**Deletions**:
- `backend/ws_manager/` directory (entire directory)
- `backend/ai_agent/agent_streaming.py` (no longer needed)

### Phase 3: Frontend Implementation (Pending)

**Tasks**:
1. Install `@openai/chatkit-react` package
2. Create `TaskChat.tsx` wrapper component
3. Configure `useChatKit` with custom fetch
4. Update dashboard to use `TaskChat` instead of `ChatInterface`
5. Test chat interface with streaming
6. Test tool execution visualization
7. Test cross-tab synchronization
8. Test conversation persistence
9. Verify authentication works with custom fetch
10. Test error handling (rate limits, network errors)

**Deletions**:
- `frontend/src/components/chat/ChatInterface.tsx`
- `frontend/src/components/chat/MessageList.tsx`
- `frontend/src/components/chat/MessageInput.tsx`
- `frontend/src/components/chat/ProgressBar.tsx`
- `frontend/src/components/chat/ConnectionStatus.tsx`
- `frontend/src/components/chat/useWebSocket.ts`

### Phase 4: Cleanup & Documentation (Pending)

**Tasks**:
1. Update `backend/CLAUDE.md` with ChatKit architecture
2. Update `frontend/CLAUDE.md` with ChatKit integration
3. Delete all removed files from git
4. Update README with new chat architecture
5. Create migration rollback notes
6. Run full test suite to verify no regressions
7. Deploy to staging for final validation
8. Monitor Gemini API usage and costs
9. Document any Gemini-specific behaviors
10. Update project specification references

---

## Component Mapping

### Backend Components

| Component | Status | Replacement |
|-----------|--------|-------------|
| `ws_manager/manager.py` | DELETE | ChatKitServer (built-in SSE) |
| `ws_manager/events.py` | DELETE | ChatKit event protocol |
| `ai_agent/agent_streaming.py` | DELETE | Agents SDK streaming |
| `ai_agent/agent.py` | MODIFY | Wrap tools with @function_tool |
| `models/message.py` | MODIFY | Add thread_id foreign key |
| `models/thread.py` | NEW | Thread model for ChatKit |
| `services/chatkit_store.py` | NEW | PostgresChatKitStore |
| `chatkit_server.py` | NEW | ChatKitServer implementation |
| `api/chat.py` | MODIFY | Add /api/chatkit endpoint |

### Frontend Components

| Component | Status | Replacement |
|-----------|--------|-------------|
| `ChatInterface.tsx` | DELETE | TaskChat.tsx (wrapper) |
| `MessageList.tsx` | DELETE | ChatKit UI (built-in) |
| `MessageInput.tsx` | DELETE | ChatKit UI (built-in) |
| `ProgressBar.tsx` | DELETE | ChatKit widgets (built-in) |
| `ConnectionStatus.tsx` | DELETE | ChatKit status (built-in) |
| `useWebSocket.ts` | DELETE | SSE (built into ChatKit) |
| `TaskChat.tsx` | NEW | ChatKit wrapper (~50 LOC) |

---

## Data Migration

### Existing Data

**Current Schema**:
```sql
messages
  - id (UUID)
  - conversation_id (STRING) -- Legacy: stored as string
  - role (enum)
  - content (text)
  - created_at (timestamp)
```

**Target Schema**:
```sql
threads
  - id (UUID) -- NEW
  - user_id (UUID) -- NEW
  - title (varchar, optional)
  - metadata (JSONB)
  - created_at (timestamp)
  - updated_at (timestamp)

messages
  - id (UUID)
  - thread_id (UUID) -- NEW: foreign key to threads
  - role (enum)
  - content (text)
  - tool_calls (JSONB) -- NEW: store tool call metadata
  - created_at (timestamp)
```

### Migration Strategy

1. **Create threads table** (new)
2. **Add thread_id column to messages** (nullable initially)
3. **Migrate existing conversation_ids to threads**:
   - For each unique `conversation_id`, create a `thread` record
   - Update `messages.thread_id` to reference the new thread
   - Extract `user_id` from existing JWT context or message metadata
4. **Make thread_id NOT NULL** after migration
5. **Drop legacy conversation_id column** (optional, can keep for rollback)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini compatibility gaps | Medium | High | Thorough testing; have rollback plan ready |
| SSE streaming format differences | Low | Medium | Agents SDK handles abstraction; test edge cases |
| Tool calling parameter validation | Low | Medium | Use OpenAI-compatible schema; validate each tool |
| Model capability differences | Medium | Medium | Adjust prompts for Gemini behavior |
| Database migration failures | Low | High | Backup database before migration; test on staging |
| ChatKit library bugs | Low | High | Pin specific version; monitor GitHub issues |
| Rate limiting differences | Low | Low | Monitor Gemini quota separately; set alerts |
| Authentication integration issues | Low | High | Test custom fetch thoroughly; verify cookie handling |

---

## Success Criteria Verification

| Criterion | How to Verify |
|-----------|---------------|
| < 2s first token response | Measure time from message send to first SSE event |
| < 500ms tool visibility | Measure time from tool_call_created to UI update |
| 100% Gemini LLM usage | Verify model ID in logs; no OpenAI model IDs |
| Zero WebSocket code | Search codebase for WebSocket references |
| 95% conversation persistence | Test refresh/reopen scenarios; verify thread loading |
| 600+ LOC reduction | Count LOC before/after with `cloc` tool |
| All 7 tools execute | Test each tool individually via chat |
| Graceful error handling | Test 429, 503, 504 responses; verify UI doesn't freeze |
| < 1s session creation | No OpenAI Sessions API call; measure thread creation time |

---

## Rollback Plan

If migration fails:

1. **Backend**: Restore from git backup (before ChatKit changes)
2. **Frontend**: Restore from git backup (before component deletion)
3. **Database**: Keep `threads` table (can be used later or dropped)
4. **Dependencies**: Remove ChatKit packages

**Git Rollback Commands**:
```bash
# Save current work first
git commit -am "Save ChatKit migration progress"

# Rollback if needed
git reset --hard <commit_before_migration>

# Remove branches
git branch -D 010-chatkit-migration
```

**Partial Rollback** (if only some features fail):
- Keep ChatKit UI but restore WebSocket for streaming
- Keep Store implementation but use custom client instead of ChatKit server

---

## Dependencies

### New Dependencies Required

**Backend**:
```bash
uv add openai-chatkit openai-agents
```

**Frontend**:
```bash
npm install @openai/chatkit-react
```

### Existing Dependencies Preserved

- `openai` - OpenAI Python SDK (for custom AsyncOpenAI client)
- `fastapi` - Web framework
- `sqlmodel` - ORM
- React 19, Next.js 16 - Frontend framework
- All existing MCP tools

---

## References

- [ChatKit Main Guide](https://platform.openai.com/docs/guides/chatkit)
- [ChatKit Python API](https://platform.openai.com/docs/api-reference/chatkit-python)
- [ChatKit React API](https://platform.openai.com/docs/api-reference/chatkit-react)
- [OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [SSE Specification (RFC 6202)](https://datatracker.ietf.org/doc/html/rfc6202)
