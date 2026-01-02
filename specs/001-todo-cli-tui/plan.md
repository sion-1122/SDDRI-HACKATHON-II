# Implementation Plan: Terminal-based Todo CLI with TUI

**Branch**: `001-todo-cli-tui` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-cli-tui/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a single-user, in-memory Todo CLI application with a keyboard-driven Terminal User Interface (TUI). The application provides an interactive REPL (Read-Eval-Print Loop) where users can manage tasks through a main menu navigable via arrow keys. Core features include adding, listing, editing, deleting, and toggling completion status of tasks. All data is stored in memory only for the duration of the session.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: TUI library (textual, rich, or prompt_toolkit - to be determined in research phase)
**Storage**: In-memory only (no persistence, no database, no files per constitution)
**Testing**: pytest with TUI mocking capabilities
**Target Platform**: Terminal/CLI environment (Linux, macOS, Windows via WSL)
**Project Type**: Single-script CLI application
**Performance Goals**: <100ms response time for all interactions (SC-010)
**Constraints**:
- No persistence layer (Phase 1 constitution requirement)
- No authentication or multi-user support
- Keyboard-driven interface only (no mouse interaction)
- Clean terminal state restoration on exit
**Scale/Scope**:
- Single user session
- Support for 10+ tasks without performance degradation
- Session-limited data (all tasks lost on exit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: In-Memory Execution (Phase 1 Non-Negotiable)
✅ **PASS** - Specification explicitly requires in-memory storage (FR-019, FR-020, FR-021) with no persistence layer. All tasks exist only during the application session.

### Principle II: Terminal UI Excellence
✅ **PASS** - Specification requires TUI with keyboard-driven navigation (FR-003, FR-010), arrow keys for selection (FR-003, FR-010), space for toggling (FR-011), and enter for submission (FR-004). Research phase will select appropriate TUI library.

### Principle III: REPL Architecture
✅ **PASS** - Specification requires main menu return after all actions (FR-018), continuous loop until explicit exit (FR-017), and separate exit action that terminates the session.

### Principle IV: Single User, Single Session
✅ **PASS** - Specification is explicitly single-user with no authentication requirements (from user input). All tasks belong to current user in current session.

### Principle V: Incremental Phase Evolution
✅ **PASS** - This is Phase 1 implementation. No principles from earlier phases need superseding.

### Phase 1 Constraints Verification

**Technology Stack**:
✅ Python 3.13+ - Specified in user input
✅ Package management via `uv` - Specified in user input
✅ Execution via `uv run main.py` - Specified in user input
✅ TUI library - Textual 0.80.0+ (selected in research phase, Decision 1)

**Required Features**:
✅ Add Task - FR-005, FR-006, FR-007
✅ List Tasks - FR-008, FR-009
✅ Delete Task - FR-015, FR-016
✅ Edit Task - FR-013, FR-014
✅ Exit - FR-017

**Interaction Requirements**:
✅ Main menu with 5 actions - FR-002
✅ Arrow key navigation - FR-003, FR-010
✅ Enter to select - FR-004
✅ Space bar to toggle completion - FR-011
✅ Return to main menu after actions - FR-018

**Out of Scope for Phase 1**:
✅ No persistence - FR-019, FR-020, FR-021
✅ No authentication/multi-user - User input specification
✅ No task metadata (due dates, priorities, tags) - Only basic task model
✅ No networking/external APIs - Single-user CLI
✅ No web interface or GUI - Terminal-based only

**Gate Result**: ✅ **ALL GATES PASSED** - Proceed to Phase 0 research

### Post-Phase 1 Design Re-Check

*After completing research, data model, and design artifacts*

**Technology Stack Decisions**:
✅ Textual 0.80.0 selected - Provides keyboard navigation, widget library, cross-platform support
✅ In-memory List[Task] storage - Simple, ordered, performant for 10-100 tasks
✅ pytest + pytest-asyncio - Testing strategy aligned with constitution requirements

**Architecture Verification**:
✅ Screen stack architecture - Supports "return to main menu" requirement (FR-018)
✅ Immutable Task model - Prevents accidental state corruption
✅ TaskService separation - Business logic independent of UI (testable)

**Constitution Compliance After Design**:
✅ Principle I: Data model uses in-memory List only, no persistence
✅ Principle II: Textual provides excellent TUI with keyboard-driven navigation
✅ Principle III: Screen stack architecture naturally implements REPL loop
✅ Principle IV: Single TaskService instance, no user/auth concepts
✅ Principle V: Phase 1 scope maintained, no scope creep

**Final Gate Result**: ✅ **ALL GATES PASSED** - Design validated, proceed to task generation

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-cli-tui/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (TBD)
├── data-model.md        # Phase 1 output (TBD)
├── quickstart.md        # Phase 1 output (TBD)
├── contracts/           # Not applicable (no API contracts for CLI app)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
cli/
├── main.py              # Entry point with REPL loop
├── models/
│   └── task.py          # Task data model
├── ui/
│   ├── main_menu.py     # Main menu TUI component
│   ├── task_list.py     # Task list TUI component
│   └── input.py         # Input prompts and validation
├── services/
│   └── task_service.py  # Business logic for task CRUD operations
└── __init__.py

tests/
├── unit/
│   ├── test_task_model.py
│   └── test_task_service.py
├── integration/
│   └── test_repl_flow.py
└── fixtures/
    └── task_fixtures.py
```

**Structure Decision**: Selected single-project structure (Option 1) with clear separation of concerns:
- `models/`: Data structures (Task entity)
- `ui/`: All TUI components and user interaction handling
- `services/`: Business logic and state management
- `tests/`: Unit and integration tests with mocked TUI interactions

This structure aligns with Python best practices and supports the single-script requirement (`main.py` as entry point importing from modules).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | All gates passed | No violations to justify |

## Phase 0: Research & Technology Decisions

### Research Questions

1. **TUI Library Selection**: Evaluate textual vs. rich vs. prompt_toolkit for terminal UI
   - Criteria: Keyboard navigation ease, widget availability, documentation quality, learning curve
   - Decision impact: Affects entire UI architecture

2. **Terminal State Management**: Best practices for clean terminal restoration
   - How to handle terminal resizing during operation
   - Proper cleanup on exit (signals, exceptions)
   - Cross-platform compatibility (Linux/macOS/Windows)

3. **Task Storage Pattern**: Optimal in-memory data structure for task list
   - List vs. dict for task storage
   - Auto-increment ID generation approach
   - Performance considerations for 10+ tasks

4. **Testing TUI Applications**: Patterns for testing interactive terminal apps
   - Mocking strategies for keyboard input
   - Testing REPL flow without actual terminal
   - Coverage measurement for TUI code

### Research Output

✅ **COMPLETED** - See [research.md](./research.md) for detailed findings and decisions.

**Key Decisions**:
- TUI Library: Textual 0.80.0+ (Decision 1)
- Terminal Management: Textual's built-in lifecycle (Decision 2)
- Storage Pattern: List[Task] with auto-increment ID (Decision 3)
- Testing Strategy: Three-layer approach (unit/component/integration) (Decision 4)
- ID Strategy: Simple counter (Decision 5)
- Validation: Strip and validate approach (Decision 6)
- Architecture: Screen stack pattern (Decision 7)

## Phase 1: Design Artifacts

### Data Model

✅ **COMPLETED** - See [data-model.md](./data-model.md) for complete entity definitions, validation rules, and state transitions.

**Entities Defined**:
- Task: Immutable dataclass with id, description, completed
- TaskService: In-memory CRUD operations on List[Task]
- Validation rules: Empty check, length limits, type safety

### API Contracts

**Not Applicable**: This is a CLI application with no external API. Internal service interfaces will be documented in code and quickstart guide.

### Quickstart Guide

✅ **COMPLETED** - See [quickstart.md](./quickstart.md) for complete setup and development instructions.

**Contents**:
- Prerequisites (Python 3.13+, uv)
- Project setup (directory structure, pyproject.toml)
- Development workflow (running, testing, debugging)
- Implementation order (4 phases)
- Code quality standards (PEP 8, type hints, docstrings)
- Troubleshooting FAQ

### Agent Context Update

✅ **COMPLETED** - Agent context updated with technology stack decisions.

**Updated**: CLAUDE.md with:
- Python 3.13+ language
- Textual TUI framework
- In-memory storage pattern
- Single-project structure

## Phase 2: Implementation Tasks

**NOTE**: Tasks will be generated by `/sp.tasks` command based on this plan and research findings.

Expected task categories:
1. Project initialization (uv setup, directory structure)
2. Task model implementation
3. Task service implementation (CRUD operations)
4. TUI components (main menu, task list, input prompts)
5. REPL orchestration (main loop, state management)
6. Testing (unit tests, integration tests)
7. Edge case handling and validation
8. Documentation and polish

## Dependencies & Blocking

**External Dependencies**:
- Python 3.13+ (must be installed)
- uv package manager (must be installed)
- TUI library (to be selected in research phase)

**Internal Dependencies**:
- research.md must be completed before data-model.md
- data-model.md must be completed before task generation
- quickstart.md must be completed before agent context update

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| TUI library learning curve | Medium | Select library with good documentation and examples |
| Terminal compatibility issues | Medium | Test on multiple platforms, use cross-platform patterns |
| State management complexity in REPL | Low | Keep state simple (in-memory list), clear lifecycle |
| Testing TUI interactions | Medium | Use mocking libraries, separate UI from business logic |
| Performance degradation with many tasks | Low | Use efficient data structures, test with 100+ tasks |

## Success Metrics

From specification success criteria:
- SC-001: First task creation within 30 seconds of launch
- SC-002: Error-free navigation
- SC-003: Support for 10+ tasks without performance issues
- SC-004: <100ms response time for all interactions
- SC-006: 100% clean exit rate
- SC-009: Graceful handling of empty task lists

## Next Steps

1. ✅ Constitution check completed (pre-design)
2. ✅ Phase 0 research completed (research.md)
3. ✅ Phase 1 design completed (data-model.md, quickstart.md)
4. ✅ Agent context updated (CLAUDE.md)
5. ✅ Constitution re-check completed (post-design)
6. ⏳ Generate implementation tasks via `/sp.tasks`
7. ⏳ Implement tasks following order in quickstart.md
