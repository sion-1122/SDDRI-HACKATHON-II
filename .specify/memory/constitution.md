<!--
Sync Impact Report
==================
Version change: 1.1.0 → 2.0.0
Modified principles:
  - Principle I: "In-Memory Execution (Phase 1)" → "Persistent Storage (Phase II)"
  - Principle IV: "Single User, Single Session" → "Multi-User Architecture with Authentication"
Added sections:
  - Principle VII: RESTful API Design
  - Principle VIII: Authentication & Authorization
  - Principle IX: Frontend Architecture (Next.js)
  - Principle X: Data Ownership & Isolation
Removed sections: N/A (Phase I principles preserved in Phase I section)
Templates requiring updates:
  ✅ constitution.md (this file)
  ✅ plan-template.md (reviewed - already supports web app structure)
  ✅ spec-template.md (reviewed - already supports web features)
  ✅ tasks-template.md (reviewed - already supports backend/frontend paths)
Follow-up TODOs:
  - Create /specs/features/ subdirectory if not exists
  - Create /specs/api/ subdirectory if not exists
  - Create /specs/database/ subdirectory if not exists
  - Create /specs/ui/ subdirectory if not exists
  - Create backend/CLAUDE.md with backend-specific instructions
  - Create frontend/CLAUDE.md with frontend-specific instructions
-->

# Todo List Hackathon Constitution

## Core Principles

### I. Persistent Storage (Phase II Non-Negotiable)
All state MUST be persisted in a relational database during Phase II. Every task, user account, and authentication state MUST be stored in Neon Serverless PostgreSQL using SQLModel. No in-memory-only data persistence is permitted beyond request-scoped caching. This constraint ensures data durability, multi-user concurrency, and scalability.

**Rationale**: Production applications require reliable data persistence. Database storage enables multi-user access, data durability across sessions, and establishes the foundation for advanced features (querying, relationships, analytics).

### II. RESTful API Excellence
The backend MUST implement a RESTful API using FastAPI with clear resource boundaries, standard HTTP methods (GET, POST, PUT, DELETE), and appropriate status codes. All endpoints MUST be under `/api` path, require valid JWT authentication, and return JSON responses with consistent error handling.

**Rationale**: RESTful APIs provide standardized client-server communication, enable stateless interactions, support multiple client types (web, mobile, CLI), and establish clear contracts for frontend development.

### III. Responsive Web UI
The frontend MUST provide a responsive, accessible web UI using Next.js App Router. All interactions MUST be optimized for keyboard and mouse input with intuitive navigation. The UI MUST work across desktop, tablet, and mobile viewports with mobile-first responsive design.

**Rationale**: Web UI provides universal access without installation, responsive design ensures usability across devices, and Next.js App Router delivers optimal performance with server-side rendering and modern React patterns.

### IV. Multi-User Architecture with Authentication
Phase II implements multi-user, multi-session semantics with authentication and authorization. Every user MUST authenticate via Better Auth before accessing any functionality. All data MUST be scoped to the authenticated user. Users cannot access another user's tasks under any circumstances.

**Rationale**: Multi-user support enables real-world usage scenarios. Authentication establishes identity, authorization enforces data boundaries, and session management enables secure, persistent access across devices.

### V. Incremental Phase Evolution
This constitution governs Phase II exclusively. Each subsequent phase (III-V) will amend this document to add constraints appropriate to that phase's technology stack (e.g., AI integration, orchestration, advanced features). Principles from earlier phases remain in force unless explicitly superseded. Phase I principles are preserved in the "Phase I Legacy" section for historical reference.

**Rationale**: Ensures each phase builds on solid foundations while enabling architectural evolution and preventing scope creep.

### VI. Monorepo Structure Standard (Project-Wide Non-Negotiable)
The project MUST adhere to the standardized monorepo folder structure defined below. This structure applies across ALL phases and is enforced at the repository root level. Deviations require explicit constitution amendment.

**Rationale**: Enforces consistency across phases, enables clear separation of concerns (specs vs. code vs. docs), supports scalable multi-service architecture, and aligns with Spec-Kit specification management best practices.

**Required Structure**:
```text
todo-list-hackathon/
├── .specify/                     # Spec-Kit configuration
│   └── memory/
│       └── constitution.md       # This file
├── specs/                        # Spec-Kit managed specifications
│   ├── overview.md               # Project overview
│   ├── features/                 # Feature specifications
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/                      # API specifications
│   │   └── rest-endpoints.md
│   ├── database/                 # Database specifications
│   │   └── schema.md
│   └── ui/                       # UI specifications
│       ├── components.md
│       └── pages.md
├── CLAUDE.md                     # Root Claude Code instructions
├── AGENTS.md                     # Agent behavior guidelines (SDD workflow)
├── frontend/                     # Frontend application (Phase II+)
│   ├── CLAUDE.md                 # Frontend-specific instructions
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utility functions and auth client
│   └── public/                   # Static assets
├── backend/                      # Backend application (Phase II+)
│   ├── CLAUDE.md                 # Backend-specific instructions
│   ├── app/                      # FastAPI application
│   ├── models/                   # SQLModel database models
│   ├── services/                 # Business logic layer
│   ├── api/                      # API route handlers
│   └── core/                     # Configuration, security, deps
├── cli/                          # CLI/TUI application (Phase I legacy)
│   └── ... (Python Textual app)
└── README.md                     # Project documentation
```

**Structure Enforcement Rules**:
1. **Specs Directory Hierarchy**: All specifications MUST be organized under `specs/` with appropriate subdirectories (features/, api/, database/, ui/). Phase-specific specs (e.g., 001-todo-cli-tui) coexist with the global spec structure.
2. **Application Directories**: Each major application component (cli/, frontend/, backend/) MUST have its own CLAUDE.md with component-specific instructions that inherit from root CLAUDE.md.
3. **Configuration Management**: `.specify/` is the authoritative source for Spec-Kit configuration. Manual edits must be synchronized with constitution principles.
4. **Phase Compliance**: Phase I uses `cli/` directory. Phase II uses `backend/` and `frontend/` directories. All directories coexist in the monorepo.
5. **Documentation Hierarchy**: Root CLAUDE.md contains project-wide directives. Component CLAUDE.md files contain phase/technology-specific guidance that must not contradict root principles.

### VII. Authentication & JWT Security
All API endpoints MUST require valid JWT authentication. JWTs MUST be issued by Better Auth on the frontend during login. The frontend MUST send JWTs via `Authorization: Bearer <token>` header. The backend MUST verify JWT signatures using the shared `BETTER_AUTH_SECRET` environment variable and extract `user_id` from validated tokens. Requests without valid JWT MUST return HTTP 401 Unauthorized.

**Rationale**: JWT provides stateless, secure authentication that scales horizontally. Shared secret ensures both services trust the same tokens. Extracting user_id from JWT enables scoping all data queries to the authenticated user, preventing unauthorized access.

### VIII. Frontend Architecture (Next.js)
The frontend MUST use Next.js App Router with React Server Components where appropriate. Authentication MUST be handled by Better Auth integrated with Next.js. Client-side state MUST be minimized and preferrably managed through URL params, cookies, or server state. All API calls MUST include the JWT token in the Authorization header. Components SHOULD be server components by default, with client components only for interactivity (forms, modals, real-time updates).

**Rationale**: Next.js App Router provides optimal performance with server-side rendering, streaming, and built-in optimization. Server components reduce client-side JavaScript, improve SEO, and simplify data fetching. Better Auth provides seamless authentication with Next.js integration.

### IX. Data Ownership & Isolation
All database queries MUST be scoped to the authenticated user extracted from the JWT token. When a user creates a task, the `user_id` from the JWT MUST be stored as the task owner. When listing, updating, or deleting tasks, queries MUST filter by `user_id`. Users MUST NEVER be able to access, modify, or delete tasks owned by other users. Any attempt to access another user's data MUST return HTTP 403 Forbidden or HTTP 404 Not Found.

**Rationale**: Enforces data isolation, prevents unauthorized data access, ensures multi-user tenancy, and establishes clear ownership boundaries. This is a critical security requirement for multi-user applications.

### X. API Response Consistency
All API endpoints MUST return consistent JSON responses with a standardized structure. Success responses MUST include the requested data or confirmation. Error responses MUST include a clear error message and appropriate HTTP status code (400 for client errors, 401 for unauthorized, 403 for forbidden, 404 for not found, 500 for server errors). Validation errors MUST list all validation failures with field-specific messages.

**Rationale**: Consistent API responses enable predictable frontend error handling, improve debugging, and provide clear feedback to users. Standardized structures reduce client-side complexity and improve developer experience.

## Phase II Constraints

**Technology Stack**:
- **Backend**: Python 3.13+ with FastAPI, SQLModel, Pydantic
- **Frontend**: Next.js 15+ with App Router, React 19+, TypeScript
- **Authentication**: Better Auth (Next.js) with JWT
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **Package Management**: `uv` for backend, `npm` for frontend
- **Execution**: Backend via `uv run uvicorn backend.app:app`, frontend via `npm run dev`

**Required Features** (All from Phase I, adapted for web):
1. **Add Task**: User creates task via web form, persisted to database with user ownership
2. **List Tasks**: Display all tasks for authenticated user, paginated and filterable
3. **Delete Task**: Remove task from database (only if owned by user)
4. **Edit Task**: Modify existing task description (only if owned by user)
5. **Toggle Completion**: Mark task as complete/incomplete (only if owned by user)

**Authentication Requirements**:
- User registration via email/password (handled by Better Auth)
- User login via email/password (issues JWT)
- User logout (invalidates session)
- Protected routes: All pages except login/register require authentication
- API authentication: All `/api` endpoints require valid JWT

**Interaction Requirements**:
- **Main UI**: Single-page application with task list view
- **Task List View**: Display all user's tasks with completion status
- **Add Task Form**: Input field for task description, submit button
- **Task Actions**: Buttons to edit, delete, and toggle completion
- **Responsive Design**: Mobile-first layout that works on all devices
- **Real-time Updates**: UI updates immediately after successful API calls

**Out of Scope for Phase II**:
- Task metadata (due dates, priorities, tags)
- Real-time collaboration (websockets, live updates)
- Task sharing between users
- File attachments to tasks
- Advanced filtering and search
- Task categories or projects
- Email notifications
- Export tasks to various formats

## Development Workflow

**Code Quality**:
- **Backend**: Follow PEP 8, type hints required, docstrings for public APIs
- **Frontend**: Follow ESLint rules, TypeScript strict mode, React best practices
- **Testing**: Unit tests for business logic, integration tests for API endpoints, E2E tests for critical user journeys
- **Code Reviews**: All changes MUST be reviewed before merge, MUST check constitution compliance

**Testing Strategy**:
- **Backend Unit Tests**: pytest for business logic (task CRUD operations, JWT verification)
- **Backend Integration Tests**: Test API endpoints with test database, mock JWT verification
- **Frontend Component Tests**: React Testing Library for component behavior
- **E2E Tests**: Playwright or Cypress for critical user journeys (login, create task, toggle completion)
- **Test Coverage Target**: 70%+ for backend and frontend business logic

**Security Requirements**:
- All API endpoints MUST require valid JWT (no public endpoints except auth)
- User passwords MUST be hashed (handled by Better Auth)
- SQL injection prevention via SQLModel parameterized queries (no raw SQL)
- XSS prevention via React automatic escaping and Content Security Policy
- CSRF protection via SameSite cookies and JWT in Authorization header
- Environment variables MUST be used for secrets (BETTER_AUTH_SECRET, DATABASE_URL)

**Acceptance Criteria**:
- Backend runs without errors via `uv run uvicorn backend.app:app --reload`
- Frontend runs without errors via `npm run dev`
- User can register, login, and complete all 5 task actions in a single session
- API returns 401 for requests without JWT
- User cannot access another user's tasks (verified via integration tests)
- UI responds to user interactions within 200ms
- All data persists across page refreshes and browser restarts

## Governance

This constitution is the authoritative source for Phase II development decisions. Any deviation requires explicit team discussion and constitution amendment.

**Amendment Process**:
1. Propose change with rationale
2. Document impact on existing code/specifications
3. Update version number (semantic versioning)
4. Sync changes to all dependent templates (plan, spec, tasks)
5. Update CLAUDE.md files if technology stack changes

**Compliance**:
- All pull requests MUST reference applicable constitution principles
- Code reviews MUST verify constraint compliance (JWT auth, data ownership, monorepo structure)
- Security violations MUST be addressed immediately (authentication bypasses, data leaks)
- Violations MUST be addressed before merge

**Phase Transition**:
When moving to Phase III, this constitution will be amended to:
- Add AI integration principles
- Add orchestration constraints (if applicable)
- Revise technology stack principles (if applicable)
- Preserve Phase II principles where applicable (code quality, testing, security, monorepo structure)

**Version**: 2.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-08

---

## Phase I Legacy (Preserved for Reference)

The following principles governed Phase I (CLI/TUI application) and are preserved here for historical reference. These principles are **NOT active** in Phase II but may be referenced for understanding the project's evolution.

### I. In-Memory Execution (Phase 1 - RETIRED)
All state was maintained in memory during Phase 1. No persistence layer, database, or file-based storage was permitted. Tasks existed only for the duration of the REPL session.

**Retirement Rationale**: Phase II requires persistent storage for multi-user web application. In-memory execution is no longer appropriate.

### II. Terminal UI Excellence (Phase 1 - RETIRED)
The application provided a beautiful, responsive TUI (Terminal User Interface) using Textual. All interactions were keyboard-driven with intuitive navigation.

**Retirement Rationale**: Phase II uses web UI instead of terminal UI. These principles are replaced by "Responsive Web UI" (Principle III in Phase II).

### III. REPL Architecture (Phase 1 - RETIRED)
The application implemented a continuous Read-Eval-Print Loop. After every action completion, the user returned to the main menu.

**Retirement Rationale**: Phase II uses request/response web architecture instead of REPL pattern. The REPL pattern is not applicable to web applications.

### IV. Single User, Single Session (Phase 1 - RETIRED)
Phase 1 implemented single-user, single-session semantics with no authentication or multi-user data isolation.

**Retirement Rationale**: Phase II requires multi-user architecture with authentication. This principle is replaced by "Multi-User Architecture with Authentication" (Principle IV in Phase II).
