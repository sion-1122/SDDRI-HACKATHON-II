<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0
Modified principles: N/A (no principles renamed)
Added sections:
  - Principle VI: Monorepo Structure Standard (new)
Removed sections: N/A
Templates requiring updates:
  ✅ constitution.md (this file)
  ✅ plan-template.md (reviewed for alignment)
  ✅ spec-template.md (reviewed for alignment)
  ✅ tasks-template.md (reviewed for alignment)
Follow-up TODOs:
  - Create .spec-kit/ directory structure if not exists
  - Create specs/ subdirectories (features/, api/, database/, ui/) if not exists
  - Consider creating frontend/ and backend/ directories for future phases
-->

# Todo List Hackathon Constitution

## Core Principles

### I. In-Memory Execution (Phase 1 Non-Negotiable)
All state MUST be maintained in memory during Phase 1. No persistence layer, database, or file-based storage is permitted. Tasks exist only for the duration of the REPL session. This constraint ensures focused learning of core Python and TUI patterns before introducing complexity.

**Rationale**: Forces mastery of fundamental data structures and application lifecycle without premature optimization.

### II. Terminal UI Excellence
The application MUST provide a beautiful, responsive TUI (Terminal User Interface). Use of established TUI libraries (e.g., `textual`, `rich`, `curses`) is encouraged. All interactions MUST be keyboard-driven with intuitive navigation (arrow keys for selection, space for toggling, enter for submission).

**Rationale**: Terminal UI skills are foundational for CLI tools and provide immediate visual feedback without browser dependencies.

### III. REPL Architecture
The application MUST implement a continuous Read-Eval-Print Loop. After every action completion, the user MUST return to the main menu. The loop persists until explicit exit. No action should terminate the application except "exit".

**Rationale**: REPL patterns teach state management and event-driven programming basics essential for later phases.

### IV. Single User, Single Session
Phase 1 implements single-user, single-session semantics. No authentication, authorization, or multi-user data isolation. All tasks belong to the current user in the current session.

**Rationale**: Removes security and data complexity to focus on core feature implementation and UI/UX.

### V. Incremental Phase Evolution
This constitution governs Phase 1 exclusively. Each subsequent phase (II-V) will amend this document to add constraints appropriate to that phase's technology stack (e.g., persistence, web APIs, AI integration, orchestration). Principles from earlier phases remain in force unless explicitly superseded.

**Rationale**: Ensures each phase builds on solid foundations while enabling architectural evolution.

### VI. Monorepo Structure Standard (Project-Wide Non-Negotiable)
The project MUST adhere to the standardized monorepo folder structure defined below. This structure applies across ALL phases and is enforced at the repository root level. Deviations require explicit constitution amendment.

**Rationale**: Enforces consistency across phases, enables clear separation of concerns (specs vs. code vs. docs), supports scalable multi-service architecture, and aligns with Spec-Kit specification management best practices.

**Required Structure**:
```text
hackathon-todo/
├── .spec-kit/                    # Spec-Kit configuration
│   └── config.yaml
├── specs/                        # Spec-Kit managed specifications
│   ├── overview.md               # Project overview
│   ├── architecture.md           # System architecture
│   ├── features/                 # Feature specifications
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── chatbot.md
│   ├── api/                      # API specifications
│   │   ├── rest-endpoints.md
│   │   └── mcp-tools.md
│   ├── database/                 # Database specifications
│   │   └── schema.md
│   └── ui/                       # UI specifications
│       ├── components.md
│       └── pages.md
├── CLAUDE.md                     # Root Claude Code instructions
├── frontend/                     # Frontend application (Phase 3+)
│   ├── CLAUDE.md                 # Frontend-specific instructions
│   └── ... (Next.js app)
├── backend/                      # Backend application (Phase 2+)
│   ├── CLAUDE.md                 # Backend-specific instructions
│   └── ... (FastAPI app)
├── cli/                          # CLI/TUI application (Phase 1)
│   └── ... (Python Textual app)
├── docker-compose.yml            # Container orchestration
└── README.md                     # Project documentation
```

**Structure Enforcement Rules**:
1. **Specs Directory Hierarchy**: All specifications MUST be organized under `specs/` with appropriate subdirectories (features/, api/, database/, ui/). Phase-specific specs (e.g., 001-todo-cli-tui) may coexist with the global spec structure.
2. **Application Directories**: Each major application component (cli/, frontend/, backend/) MUST have its own CLAUDE.md with component-specific instructions that inherit from root CLAUDE.md.
3. **Configuration Management**: `.spec-kit/config.yaml` is the authoritative source for Spec-Kit configuration. Manual edits must be synchronized with constitution principles.
4. **Phase Compliance**: Phase 1 uses `cli/` directory exclusively. Phases 2+ MAY add `backend/`, `frontend/`, and other directories as defined in their respective constitutions.
5. **Documentation Hierarchy**: Root CLAUDE.md contains project-wide directives. Component CLAUDE.md files contain phase/technology-specific guidance that must not contradict root principles.

## Phase 1 Constraints

**Technology Stack**:
- Python 3.13+ (as specified in pyproject.toml)
- Standard library plus TUI libraries only
- Package management via `uv`
- Execution via `uv run main.py` or equivalent

**Required Features**:
1. **Add Task**: Prompt user for task description, save to in-memory list
2. **List Tasks**: Display all tasks with completion status, browsable via arrow keys
3. **Delete Task**: Remove task from in-memory list
4. **Edit Task**: Modify existing task description
5. **Exit**: Terminate the REPL session

**Interaction Requirements**:
- Main menu: Browsable list of 5 actions, arrow key navigation, enter to select
- Task list view: Arrow key navigation, space bar to toggle completion status
- All views return to main menu after action completion (except Exit)

**Out of Scope for Phase 1**:
- Persistence (database, files, API storage)
- Authentication/multi-user support
- Task metadata (due dates, priorities, tags)
- Networking or external APIs
- Web interface or GUI

## Development Workflow

**Code Quality**:
- Follow PEP 8 style guidelines
- Type hints required for all function signatures
- Docstrings for all public functions and classes
- Maximum function complexity: if it needs more than 5 lines of explanation, break it down

**Testing Strategy**:
- Unit tests for business logic (task CRUD operations)
- Integration tests for REPL flow (menu navigation, action execution)
- Mock TUI interactions for testability
- Test coverage target: 70%+ (Phase 1)

**Acceptance Criteria**:
- Script runs without errors via `uv run main.py`
- User can complete all 5 actions in a single session
- TUI responds to keyboard inputs within 100ms
- No memory leaks during extended sessions (>100 actions)

## Governance

This constitution is the authoritative source for Phase 1 development decisions. Any deviation requires explicit team discussion and constitution amendment.

**Amendment Process**:
1. Propose change with rationale
2. Document impact on existing code/user stories
3. Update version number (semantic versioning)
4. Sync changes to all dependent templates (plan, spec, tasks)

**Compliance**:
- All pull requests MUST reference applicable constitution principles
- Code reviews MUST verify constraint compliance (no persistence in Phase 1, TUI requirements met, monorepo structure enforced)
- Violations MUST be addressed before merge

**Phase Transition**:
When moving to Phase 2, this constitution will be amended to:
- Add persistence principles
- Add web API constraints
- Revise technology stack principles
- Preserve Phase 1 principles where applicable (e.g., code quality, testing, monorepo structure)

**Version**: 1.1.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-06
