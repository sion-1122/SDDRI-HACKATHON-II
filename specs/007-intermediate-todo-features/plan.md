# Implementation Plan: Intermediate Todo Features

**Branch**: `007-intermediate-todo-features` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-intermediate-todo-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds intermediate task organization capabilities to the existing AI chatbot interface from Phase III (004-ai-chatbot). The primary requirements include: (1) Task priority management with three levels (High, Medium, Low) extracted from natural language, (2) Tag-based categorization with colored badges and filtering, (3) Fast search functionality with client-side optimization (<100 tasks) and debounced server-side search (≥100 tasks), (4) Multi-criteria filtering with AND logic (status, priority, tags, due date), (5) Flexible sorting options (due date, priority, creation date, alphabetical), and (6) UI component fixes for responsive modal/dialog and sheet components. The technical approach extends the existing FastAPI backend with new database fields, adds natural language processing for priority extraction using OpenAI Agents SDK, implements client-side search with React state for performance, and creates responsive UI components following the Notion-inspired design system from Phase V (005-ux-improvement).

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ with FastAPI
- Frontend: TypeScript 5+ with Next.js 16 and React 19

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Pydantic, OpenAI Agents SDK, Neon PostgreSQL (psycopg)
- Frontend: Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, nuqs (URL params), Sonner (toasts)
- UI Components: shadcn/ui components or custom replacements if needed
- Database: Neon Serverless PostgreSQL with SQLModel ORM

**Storage**: Neon Serverless PostgreSQL (existing)
- Task table: Extended with priority (enum), tags (text array), due_date (timestamp)
- Backward compatibility: Existing records default to Medium priority, empty tags, null due_date
- Migration required to add new columns with safe defaults

**Testing**:
- Backend: pytest for business logic, integration tests for API endpoints
- Frontend: React Testing Library for component behavior, Playwright for E2E
- Performance: Verify <200ms client search, <500ms server search with debounce

**Target Platform**: Web application (full-stack)
- Frontend: Next.js 16 with App Router, server and client components
- Backend: FastAPI with RESTful API under `/api` path
- Responsive: Mobile-first design (375px minimum width)

**Project Type**: Web application (backend + frontend)
- Extends existing Phase III AI chatbot interface
- No new standalone applications
- Full monorepo structure with existing backend/ and frontend/ directories

**Performance Goals**:
- Client-side search: <200ms for task lists under 100 items
- Server-side search: <500ms after 300ms debounce period
- Filter/sort operations: <100ms UI response time
- Debounce: Single API call per 300ms typing window
- First contentful paint: <100ms with task metadata rendering

**Constraints**:
- No breaking changes: All existing chatbot functionality must continue to work
- Backward compatibility: Existing tasks without new fields must default appropriately
- Mobile responsive: All UI components work on 375px+ width screens
- Natural language priority: Handle common phrases (urgent, ASAP, low priority) but not every variation
- Database migration: Must be reviewed and approved before execution
- Shadcn/ui components: Fix or replace with custom components matching Notion-inspired design

**Scale/Scope**:
- User base: Individual users (no multi-user task sharing)
- Task volume: Expected <1000 tasks per user for client-side optimization
- Tag count: UI displays reasonably for up to 10 tags per task
- Search results: Cached for up to 10 recent queries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicable Principles (Phases II-IV)

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Persistent Storage | ✅ PASS | Neon PostgreSQL with new columns (priority, tags, due_date) |
| II. RESTful API Excellence | ✅ PASS | New endpoints for filter/sort/search under `/api` |
| III. Responsive Web UI | ✅ PASS | Mobile-first responsive design with 375px minimum |
| IV. Multi-User Architecture | ✅ PASS | All queries scoped to authenticated user_id from JWT |
| VI. Monorepo Structure Standard | ✅ PASS | Using existing backend/ and frontend/ directories |
| VII. Authentication & JWT Security | ✅ PASS | All API endpoints require valid JWT |
| VIII. Frontend Architecture (Next.js) | ✅ PASS | Server components by default, client components for interactivity |
| IX. Data Ownership & Isolation | ✅ PASS | All queries filter by user_id from JWT |
| X. API Response Consistency | ✅ PASS | Standardized JSON responses with error handling |

### Phase III Constraints (AI Chatbot)

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| OpenAI Agents SDK | ✅ PASS | Extend existing agent for new natural language commands |
| MCP Server Tools | ✅ PASS | Add tools for priority, tag, filter, sort, search operations |
| WebSocket Streaming | ✅ PASS | Continue using existing WebSocket for real-time updates |
| Conversation Persistence | ✅ PASS | Store chat history in database |

### Phase V Constraints (Notion-Inspired Design)

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| Design System | ✅ PASS | Match existing colors, typography, spacing, border-radius |
| shadcn/ui Components | ⚠️ CONDITIONAL | Fix or replace with custom components if broken |

### Gates

**Pre-Phase 0 Gate**: ✅ PASS - All constitution principles satisfied
- No violations identified
- All technical choices align with existing architecture
- Natural language processing extends existing OpenAI Agents SDK

**Post-Phase 1 Gate**: Re-evaluate after design complete
- Verify database migration strategy preserves existing data
- Confirm UI component fixes don't violate design system
- Validate search performance meets <200ms/<500ms targets

## Project Structure

### Documentation (this feature)

```text
specs/007-intermediate-todo-features/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.md
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

Per Principle VI (Monorepo Structure Standard), this feature extends the existing full monorepo structure with backend and frontend modifications:

```text
backend/
├── models/
│   └── task.py              # [MODIFY] Add priority enum, tags array, due_date
├── services/
│   ├── task_service.py      # [MODIFY] Add filter/sort/search logic
│   └── nlp_service.py       # [MODIFY] Add priority extraction from natural language
├── api/
│   └── tasks.py             # [MODIFY] Add filter/sort/search endpoints
├── mcp_server/
│   └── tools.py             # [MODIFY] Add MCP tools for new features
└── tests/
    └── test_task_service.py # [MODIFY] Add tests for filter/sort/search

frontend/
├── components/
│   ├── chat/
│   │   ├── TaskCard.tsx     # [MODIFY] Add priority badge, tag badges, due date
│   │   ├── TaskList.tsx     # [MODIFY] Add filter/sort/search UI
│   │   └── SearchBar.tsx    # [ADD] Client-side search with debounce
│   └── ui/
│       ├── Modal.tsx        # [FIX/ADD] Responsive modal component
│       └── Sheet.tsx        # [FIX/ADD] Responsive sheet component
├── lib/
│   └── api.ts               # [MODIFY] Add filter/sort/search API calls
└── hooks/
    └── useTaskFilters.ts    # [ADD] Hook for filter/sort/search state

migrations/
└── add_priority_tags_due_date.sql  # [ADD] Database migration
```

**Structure Decision**: This feature follows the full monorepo structure (Option 3) with existing backend/ and frontend/ directories. Per Principle VI, the standardized monorepo layout is maintained with:
- Backend extensions: New service methods for filter/sort/search, extended task model
- Frontend extensions: New components for search/filter UI, fixed modal/sheet components
- Database: Migration scripts to add new columns with backward-compatible defaults
- No new directories created (extends existing structure from Phases II-III)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations identified. All additions are backward-compatible and align with existing architecture.
