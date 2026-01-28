<!--
Sync Impact Report
==================
Version change: 2.0.0 → 3.0.0
Modified principles:
  - No existing principles modified (all additions)
Added sections:
  - Principle XI: Containerization with Docker
  - Principle XII: Kubernetes Orchestration
  - Principle XIII: Helm Chart Packaging
  - Principle XIV: AI-Assisted DevOps
  - Principle XV: Cloud-Native Deployment Patterns
  - Principle XVI: AIOps and Blueprints
  - Phase IV Constraints section
Removed sections: N/A
Templates requiring updates:
  ✅ constitution.md (this file)
  ✅ plan-template.md (reviewed - already supports k8s structure)
  ✅ spec-template.md (reviewed - already supports deployment features)
  ✅ tasks-template.md (reviewed - already supports containerization tasks)
Follow-up TODOs:
  - Create specs/004-k8s-deployment/ subdirectory
  - Create k8s/ directory at repository root for Helm charts and manifests
  - Create deployment/CLAUDE.md with deployment-specific instructions
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
Phase II implements multi-user, multi-session semantics with authentication and authorization. Every user MUST authenticate via JWT-based auth before accessing any functionality. All data MUST be scoped to the authenticated user. Users cannot access another user's tasks under any circumstances.

**Rationale**: Multi-user support enables real-world usage scenarios. Authentication establishes identity, authorization enforces data boundaries, and session management enables secure, persistent access across devices.

### V. Incremental Phase Evolution
This constitution governs Phases II, III, and IV. Each subsequent phase adds constraints appropriate to that phase's technology stack (e.g., AI integration, orchestration, deployment). Principles from earlier phases remain in force unless explicitly superseded. Phase I principles are preserved in the "Phase I Legacy" section for historical reference.

**Rationale**: Ensures each phase builds on solid foundations while enabling architectural evolution and preventing scope creep.

### VI. Monorepo Structure Standard (Project-Wide Non-Negotiable)
The project MUST adhere to the standardized monorepo folder structure defined below. This structure applies across ALL phases and is enforced at the repository root level. Deviations require explicit constitution amendment.

**Rationale**: Enforces consistency across phases, enables clear separation of concerns (specs vs. code vs. deployment), supports scalable multi-service architecture, and aligns with Spec-Kit specification management best practices.

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
├── k8s/                          # Kubernetes manifests (Phase IV)
│   └── todo-list-hackathon/      # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── CLAUDE.md                     # Root Claude Code instructions
├── AGENTS.md                     # Agent behavior guidelines (SDD workflow)
├── frontend/                     # Frontend application (Phase II+)
│   ├── CLAUDE.md                 # Frontend-specific instructions
│   ├── Dockerfile                # Container image (Phase IV)
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utility functions and auth client
│   └── public/                   # Static assets
├── backend/                      # Backend application (Phase II+)
│   ├── CLAUDE.md                 # Backend-specific instructions
│   ├── Dockerfile                # Container image (Phase IV)
│   ├── ai_agent/                 # AI agent implementation (Phase III)
│   ├── mcp_server/               # MCP server tools (Phase III)
│   ├── models/                   # SQLModel database models
│   ├── services/                 # Business logic layer
│   ├── api/                      # API route handlers
│   ├── ws_manager/               # WebSocket manager (Phase III)
│   └── core/                     # Configuration, security, deps
├── cli/                          # CLI/TUI application (Phase I legacy)
│   └── ... (Python Textual app)
└── README.md                     # Project documentation
```

**Structure Enforcement Rules**:
1. **Specs Directory Hierarchy**: All specifications MUST be organized under `specs/` with appropriate subdirectories (features/, api/, database/, ui/). Phase-specific specs (e.g., 001-todo-cli-tui, 004-k8s-deployment) coexist with the global spec structure.
2. **Application Directories**: Each major application component (cli/, frontend/, backend/) MUST have its own CLAUDE.md with component-specific instructions that inherit from root CLAUDE.md.
3. **K8s Directory**: Phase IV introduces `k8s/` directory at root for Helm charts and Kubernetes manifests. This is separate from application code to enable environment-specific deployments.
4. **Configuration Management**: `.specify/` is the authoritative source for Spec-Kit configuration. Manual edits must be synchronized with constitution principles.
5. **Phase Compliance**: Phase I uses `cli/` directory. Phase II uses `backend/` and `frontend/` directories. Phase III adds AI components. Phase IV adds containerization and K8s manifests. All directories coexist in the monorepo.
6. **Documentation Hierarchy**: Root CLAUDE.md contains project-wide directives. Component CLAUDE.md files contain phase/technology-specific guidance that must not contradict root principles.

### VII. Authentication & JWT Security
All API endpoints MUST require valid JWT authentication. JWTs MUST be issued by the auth system on the frontend during login. The frontend MUST send JWTs via `Authorization: Bearer <token>` header. The backend MUST verify JWT signatures using the shared secret environment variable and extract `user_id` from validated tokens. Requests without valid JWT MUST return HTTP 401 Unauthorized.

**Rationale**: JWT provides stateless, secure authentication that scales horizontally. Shared secret ensures both services trust the same tokens. Extracting user_id from JWT enables scoping all data queries to the authenticated user, preventing unauthorized access.

### VIII. Frontend Architecture (Next.js)
The frontend MUST use Next.js App Router with React Server Components where appropriate. Authentication MUST be handled by JWT-based auth integrated with Next.js. Client-side state MUST be minimized and preferably managed through URL params, cookies, or server state. All API calls MUST include the JWT token in the Authorization header. Components SHOULD be server components by default, with client components only for interactivity (forms, modals, real-time updates).

**Rationale**: Next.js App Router provides optimal performance with server-side rendering, streaming, and built-in optimization. Server components reduce client-side JavaScript, improve SEO, and simplify data fetching. JWT auth provides seamless authentication with Next.js integration.

### IX. Data Ownership & Isolation
All database queries MUST be scoped to the authenticated user extracted from the JWT token. When a user creates a task, the `user_id` from the JWT MUST be stored as the task owner. When listing, updating, or deleting tasks, queries MUST filter by `user_id`. Users MUST NEVER be able to access, modify, or delete tasks owned by other users. Any attempt to access another user's data MUST return HTTP 403 Forbidden or HTTP 404 Not Found.

**Rationale**: Enforces data isolation, prevents unauthorized data access, ensures multi-user tenancy, and establishes clear ownership boundaries. This is a critical security requirement for multi-user applications.

### X. API Response Consistency
All API endpoints MUST return consistent JSON responses with a standardized structure. Success responses MUST include the requested data or confirmation. Error responses MUST include a clear error message and appropriate HTTP status code (400 for client errors, 401 for unauthorized, 403 for forbidden, 404 for not found, 500 for server errors). Validation errors MUST list all validation failures with field-specific messages.

**Rationale**: Consistent API responses enable predictable frontend error handling, improve debugging, and provide clear feedback to users. Standardized structures reduce client-side complexity and improve developer experience.

### XI. Containerization with Docker (Phase IV Non-Negotiable)
All applications MUST be containerized using Docker. Frontend (Next.js) and Backend (FastAPI) MUST each have optimized Dockerfiles using multi-stage builds for smaller production images. Images MUST be tagged with semantic version numbers. Use Docker AI Agent (Gordon) for intelligent Docker operations where available/accessible. Container images MUST be immutable and reproducible.

**Rationale**: Containerization ensures consistent runtime environments across development, testing, and production. Multi-stage builds minimize image size and attack surface. Version-tagged images enable rollback capabilities. Docker AI accelerates container development and optimization.

**Containerization Requirements**:
- Frontend Dockerfile: Multi-stage build with Node.js base, static asset optimization, nginx for serving
- Backend Dockerfile: Multi-stage build with Python slim base, dependency caching, non-root user
- Images MUST be buildable via `docker build -t <image>:<tag>`
- Images MUST be testable locally via `docker run`
- Container startup time MUST be under 10 seconds
- Image sizes MUST be optimized (frontend < 200MB, backend < 150MB compressed)

### XII. Kubernetes Orchestration (Phase IV Non-Negotiable)
The application MUST be deployable on Kubernetes. For local development, Minikube is used. For production, cloud-hosted Kubernetes (Azure AKS, Google GKE, or Oracle OKE) is used. Each component (frontend, backend) MUST have a Deployment with configurable replicas. Services MUST use ClusterIP for internal communication. ConfigMaps and Secrets MUST manage configuration separately from images. The application MUST be self-healing via replica management and health checks.

**Rationale**: Kubernetes provides declarative deployment, automatic scaling, self-healing, and rollbacks. Minikube enables local development parity with production. Cloud K8s provides managed infrastructure. Separation of config from code follows 12-factor app principles.

**Kubernetes Requirements**:
- Deployments: Frontend (2+ replicas), Backend (2+ replicas) in production
- Services: ClusterIP for internal communication, LoadBalancer/Ingress for external access
- ConfigMaps: Application configuration (API endpoints, feature flags)
- Secrets: Sensitive data (DATABASE_URL, JWT_SECRET, API keys)
- Resource limits: CPU and memory requests/limits defined
- Health probes: Liveness, readiness, and startup probes configured
- Rolling updates: MaxSurge and MaxUnavailable configured for zero-downtime deployments

### XIII. Helm Chart Packaging (Phase IV Non-Negotiable)
All Kubernetes manifests MUST be packaged as a Helm chart. The chart MUST support value overrides for different environments (local Minikube, cloud production). The chart MUST include templates for Deployments, Services, ConfigMaps, Secrets, and Ingress. Use kubectl-ai and/or kagent to assist with Helm chart generation and optimization. The chart MUST be installable via `helm install` and upgradable via `helm upgrade`.

**Rationale**: Helm charts provide templated, versioned, and reusable deployment packages. Value overrides enable environment-specific configuration without manifest duplication. AI-assisted generation accelerates chart development and ensures best practices.

**Helm Chart Requirements**:
- Chart structure: Chart.yaml, values.yaml, values-local.yaml, values-production.yaml
- Templates: Deployment, Service, ConfigMap, Secret, Ingress, HPA (if scaling needed)
- Values structure: Environment-specific overrides for image tags, replicas, resource limits
- Installable: `helm install todo-list ./k8s/todo-list-hackathon -f values-local.yaml`
- Upgradable: `helm upgrade todo-list ./k8s/todo-list-hackathon -f values-production.yaml`
- Versioned: Chart appVersion matches application semantic version

### XIV. AI-Assisted DevOps (Phase IV Non-Negotiable)
Leverage AI DevOps tools for intelligent operations throughout the deployment lifecycle. kubectl-ai for Kubernetes operations (deploy, scale, diagnose, manifest generation). kagent for cluster health analysis, resource optimization, and anomaly detection. Gordon (Docker AI) for Docker operations where available/accessible. These tools MUST be used to accelerate development while maintaining human oversight.

**Rationale**: AI-assisted DevOps reduces manual toil, accelerates troubleshooting, and ensures best practices. Tools like kubectl-ai generate optimal manifests, kagent provides predictive insights, and Gordon optimizes container configurations. Human oversight ensures safety and correctness.

**AI DevOps Usage**:
- kubectl-ai: Generate Kubernetes manifests from natural language, diagnose cluster issues, optimize resource configurations
- kagent: Monitor cluster health, suggest resource scaling, detect anomalies, provide remediation recommendations
- Gordon: Generate Dockerfile from application code, optimize image layers, suggest security improvements
- Fallback: Manual Kubernetes and Docker operations when AI tools are unavailable
- Validation: All AI-generated manifests MUST be reviewed for security and correctness before application

### XV. Cloud-Native Deployment Patterns (Phase IV Non-Negotiable)
Applications MUST follow cloud-native patterns to ensure scalability, resilience, and observability. Stateless application design, health probes (liveness, readiness, startup), resource limits and requests, graceful shutdown handling, and rolling updates with zero downtime. External services (database Neon) are accessed via configurable environment variables. All logs MUST be structured and stdout/stderr based.

**Rationale**: Cloud-native patterns enable applications to scale horizontally, recover from failures, and integrate with cloud platforms. Health checks enable self-healing. Resource limits prevent resource exhaustion. Graceful shutdown ensures clean connection termination. Structured logs enable aggregation and analysis.

**Cloud-Native Requirements**:
- Stateless design: No local state, all state in external services (database)
- Health probes: Liveness (restart if unhealthy), readiness (stop traffic if not ready), startup (delay liveness until app starts)
- Resource limits: CPU requests/limits, memory requests/limits defined for all containers
- Graceful shutdown: Handle SIGTERM, close connections, complete in-flight requests, exit within 30 seconds
- Rolling updates: MaxSurge=1, MaxUnavailable=0 for zero downtime
- Environment configuration: 12-factor app, all config via environment variables
- Structured logging: JSON format, log level, correlation ID, timestamp
- Observability: Metrics endpoints (/metrics, /health) for monitoring

### XVI. AIOps and Blueprints (Phase IV Non-Negotiable)
Use Claude Code Agent Skills and MCP servers for creating cloud-native blueprints. Reusable intelligence via MCP servers and subagents enables reproducible deployments across environments. Blueprints encapsulate best practices for infrastructure as code, security configurations, and deployment patterns. These blueprints MUST be version controlled and executable via AI agents.

**Rationale**: AIOps blueprints accelerate infrastructure provisioning, ensure consistency across environments, and encode operational best practices. MCP servers provide extensible tooling for infrastructure operations. Agent-based automation reduces manual errors and enables self-service deployments.

**AIOps Requirements**:
- MCP Server: Infrastructure tools for K8s operations (deploy, scale, status check)
- Agent Skills: Reusable skills for Helm chart generation, Dockerfile optimization, K8s manifest creation
- Blueprints: Version-controlled templates for common deployment patterns
- Executable: Blueprints MUST be executable via Claude Code agents
- Documented: Each blueprint MUST include usage instructions and parameters
- Versioned: Blueprints follow semantic versioning, backward compatibility maintained

## Phase II Constraints

**Technology Stack**:
- **Backend**: Python 3.13+ with FastAPI, SQLModel, Pydantic
- **Frontend**: Next.js 16+ with App Router, React 19+, TypeScript
- **Authentication**: JWT-based auth (custom implementation, not Better Auth)
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **Package Management**: `uv` for backend, `npm` for frontend
- **Execution**: Backend via `uv run uvicorn backend.main:app`, frontend via `npm run dev`

**Required Features** (All from Phase I, adapted for web):
1. **Add Task**: User creates task via web form, persisted to database with user ownership
2. **List Tasks**: Display all tasks for authenticated user, paginated and filterable
3. **Delete Task**: Remove task from database (only if owned by user)
4. **Edit Task**: Modify existing task description (only if owned by user)
5. **Toggle Completion**: Mark task as complete/incomplete (only if owned by user)

**Authentication Requirements**:
- User registration via email/password (handled by custom auth)
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

## Phase III Constraints

**Technology Stack Additions**:
- **AI Framework**: OpenAI Agents SDK (or alternative LangChain)
- **MCP Server**: Official MCP SDK (Python FastMCP)
- **Frontend Chat**: OpenAI ChatKit or custom React chat UI
- **WebSocket**: FastAPI WebSocket support for streaming
- **Stateless Chat**: Endpoint with database persistence for conversations

**Required Features**:
1. **Chat Interface**: AI-powered task management chat UI
2. **MCP Tools**: Add, list, update, delete, complete tasks via MCP
3. **Conversation Persistence**: Store chat history in database
4. **Streaming Responses**: Real-time AI response streaming via WebSocket

## Phase IV Constraints

**Technology Stack**:
- **Containerization**: Docker (Docker Desktop for local)
- **Docker AI**: Docker AI Agent (Gordon) where available
- **Orchestration**: Kubernetes (Minikube for local, AKS/GKE/OKE for production)
- **Package Manager**: Helm 3+
- **AI DevOps**: kubectl-ai, kagent
- **Application**: Phase III Todo Chatbot (backend + frontend)

**Required Features**:
1. **Containerized Applications**: Docker images for frontend and backend
2. **Kubernetes Deployment**: Deploy on Minikube locally
3. **Helm Charts**: Packaged manifests for easy deployment
4. **AI DevOps Integration**: Use kubectl-ai/kagent for operations
5. **Cloud-Native Patterns**: Health checks, resource limits, rolling updates
6. **Environment Configuration**: Separate values for local and production

**Containerization Requirements**:
- Frontend: Multi-stage Dockerfile with nginx, optimized static assets
- Backend: Multi-stage Dockerfile with Python slim, dependency caching
- Images MUST be buildable locally and pushable to registry
- Images MUST follow security best practices (non-root user, minimal base)

**Kubernetes Deployment Requirements**:
- Minikube deployment for local development
- Helm chart installable via `helm install`
- Services accessible via port-forward or ingress
- Configuration via ConfigMaps and Secrets
- Health checks configured and functional

**AI DevOps Requirements**:
- Use kubectl-ai for manifest generation and troubleshooting
- Use kagent for cluster health monitoring
- Use Gordon for Dockerfile optimization (where available)
- Document AI-assisted operations in deployment docs

**Deployment Verification**:
- Application accessible via browser
- All features functional (authentication, tasks, chat)
- Database connectivity working
- WebSocket connections established
- Health endpoints returning healthy status

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
- **Container Tests**: Test container images start correctly, health checks pass
- **K8s Deployment Tests**: Test Helm chart installation, upgrade, rollback
- **Test Coverage Target**: 70%+ for backend and frontend business logic

**Security Requirements**:
- All API endpoints MUST require valid JWT (no public endpoints except auth)
- User passwords MUST be hashed (handled by auth system)
- SQL injection prevention via SQLModel parameterized queries (no raw SQL)
- XSS prevention via React automatic escaping and Content Security Policy
- CSRF protection via SameSite cookies and JWT in Authorization header
- Environment variables MUST be used for secrets (DATABASE_URL, JWT_SECRET)
- Container security: Scan images for vulnerabilities, use non-root user, minimal base images
- K8s security: RBAC configured, secrets encrypted at rest, network policies where applicable

**Acceptance Criteria**:
- **Phase II**: Backend runs via `uv run uvicorn backend.main:app --reload`, frontend via `npm run dev`
- **Phase III**: Chat interface functional, MCP tools working, WebSocket streaming operational
- **Phase IV**: Containers build successfully, Minikube deployment works, Helm chart installs and upgrades
- User can register, login, and complete all 5 task actions in a single session
- API returns 401 for requests without JWT
- User cannot access another user's tasks (verified via integration tests)
- UI responds to user interactions within 200ms
- All data persists across page refreshes and browser restarts
- Container restart times under 10 seconds
- K8s rolling updates complete without downtime

## Governance

This constitution is the authoritative source for development decisions. Any deviation requires explicit team discussion and constitution amendment.

**Amendment Process**:
1. Propose change with rationale
2. Document impact on existing code/specifications
3. Update version number (semantic versioning)
4. Sync changes to all dependent templates (plan, spec, tasks)
5. Update CLAUDE.md files if technology stack changes

**Compliance**:
- All pull requests MUST reference applicable constitution principles
- Code reviews MUST verify constraint compliance (JWT auth, data ownership, monorepo structure, containerization, K8s best practices)
- Security violations MUST be addressed immediately (authentication bypasses, data leaks, container vulnerabilities)
- Violations MUST be addressed before merge

**Phase Transition**:
When moving to Phase V, this constitution will be amended to:
- Add Kafka event-driven architecture principles
- Add Dapr integration constraints
- Add advanced feature requirements (recurring tasks, advanced search)
- Add cloud K8s deployment requirements (AKS/GKE/OKE)
- Add CI/CD pipeline requirements
- Preserve Phase II, III, IV principles where applicable (code quality, testing, security, containerization, K8s)

**Version**: 3.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2025-01-27

---

## Phase I Legacy (Preserved for Reference)

The following principles governed Phase I (CLI/TUI application) and are preserved here for historical reference. These principles are **NOT active** in Phase II, III, or IV but may be referenced for understanding the project's evolution.

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
