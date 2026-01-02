---
id: 0002
title: todo-cli-tui-implementation-plan
stage: plan
date: 2026-01-02T00:00:00Z
surface: cli
model: claude-sonnet-4-5-20250929
feature: 001-todo-cli-tui
branch: 001-todo-cli-tui
user: ""
command: /sp.plan
labels: [planning, architecture, research, design]
links:
  spec: ../spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
- specs/001-todo-cli-tui/plan.md
- specs/001-todo-cli-tui/research.md
- specs/001-todo-cli-tui/data-model.md
- specs/001-todo-cli-tui/quickstart.md
- CLAUDE.md
tests:
[]
---

## Prompt

User executed /sp.plan command to generate implementation plan for the Terminal-based Todo CLI with TUI feature.

The plan workflow required:
1. Constitution check against .specify/memory/constitution.md
2. Phase 0: Research and technology decisions
3. Phase 1: Design artifacts (data model, quickstart guide)
4. Agent context update
5. Post-design constitution re-check

## Response snapshot

Successfully completed implementation plan with all phases:

**Phase 0 - Research & Technology Decisions** (research.md):
- Decision 1: Selected Textual 0.80.0+ as TUI framework (best widget library, keyboard navigation, cross-platform)
- Decision 2: Using Textual's built-in terminal state management (automatic cleanup, resize handling)
- Decision 3: List[Task] with auto-increment ID storage pattern (simple, ordered, performant for 10-100 tasks)
- Decision 4: Three-layer testing strategy (unit/component/integration with pytest + pytest-asyncio)
- Decision 5: Simple counter for ID generation (sequential, user-friendly, O(1) performance)
- Decision 6: Strip and validate approach for input validation (empty check, 1-1000 char limits)
- Decision 7: Screen stack architecture for REPL (MainMenuScreen → action screens → return to menu)

**Phase 1 - Design Artifacts**:
1. data-model.md: Complete Task entity definition with immutable dataclass, TaskService with CRUD operations, validation rules, and state transitions
2. quickstart.md: Comprehensive setup guide including prerequisites (Python 3.13+, uv), project initialization, development workflow, testing strategy, and troubleshooting

**Constitution Compliance**:
- Pre-design check: ALL GATES PASSED
- Post-design check: ALL GATES PASSED
- All 5 constitution principles validated
- Phase 1 constraints verified (in-memory, TUI excellence, REPL architecture, single-user, incremental evolution)

**Project Structure Defined**:
```
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
├── integration/
└── fixtures/
```

**Agent Context Updated**: CLAUDE.md updated with Python 3.13+, Textual framework, in-memory storage pattern.

## Outcome

- ✅ Impact: Complete implementation plan created with validated architecture, clear technology decisions, and comprehensive design artifacts ready for task generation and implementation
- 🧪 Tests: Testing strategy defined (three-layer approach: unit 90%+, component 70%+, overall 70%+)
- 📁 Files: Created plan.md (implementation plan), research.md (7 technology decisions), data-model.md (Task entity + TaskService), quickstart.md (setup & development guide); Updated CLAUDE.md (agent context)
- 🔁 Next prompts: User should run `/sp.tasks` to generate actionable implementation tasks from this plan
- 🧠 Reflection: All research questions resolved without ambiguities. Constitution provides excellent guardrails - every design decision reinforced Phase 1 constraints. Textual is ideal choice: modern, well-documented, async-first, perfect for keyboard-driven TUI. Screen stack architecture naturally satisfies REPL requirement (FR-018). Separation of concerns (models/services/ui) will support testability and future phases.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution gates: PASS (pre-design), PASS (post-design)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
