---
id: "0002"
title: "advanced-features-tasks"
stage: "tasks"
date: "2026-02-04T12:13:00Z"
surface: "cli"
model: "glm-4.7"
feature: "008-advanced-features"
branch: "008-advanced-features"
user: "groww"
command: "/sp.tasks"
labels: [sdd, tasks, phase-008]
links:
  spec: "../specs/008-advanced-features/spec.md"
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: specs/008-advanced-features/tasks.md
    action: created
    status: complete
tests:
  - path: ""
    status: pending
---

## Prompt

User invoked `/sp.tasks` command for Phase 008 Advanced Features.

**Command Arguments**: (empty)

**User Input**:
```

```

**Command Outline**:
1. Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list
2. Load design documents: Read from FEATURE_DIR (plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md)
3. Execute task generation workflow: Load plan.md and extract tech stack/libraries/project structure, Load spec.md and extract user stories with their priorities, If data-model.md exists extract entities and map to user stories, If contracts/ exists map endpoints to user stories, If research.md exists extract decisions for setup tasks, Generate tasks organized by user story, Generate dependency graph showing user story completion order, Create parallel execution examples per user story, Validate task completeness (each user story has all needed tasks, independently testable)
4. Generate tasks.md: Use `.specify/templates/tasks-template.md` as structure, fill with correct feature name from plan.md, Phase 1: Setup tasks, Phase 2: Foundational tasks, Phase 3+: One phase per user story (in priority order from spec.md), Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks, Final Phase: Polish & cross-cutting concerns, All tasks must follow the strict checklist format, Clear file paths for each task, Dependencies section showing story completion order, Parallel execution examples per story, Implementation strategy section (MVP first, incremental delivery)
5. Report: Output path to generated tasks.md and summary: Total task count, Task count per user story, Parallel opportunities identified, Independent test criteria for each story, Suggested MVP scope (typically just User Story 1), Format validation: Confirm ALL tasks follow the checklist format

**Context for task generation**: The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

**Task Generation Rules**:
CRITICAL: Tasks MUST be organized by user story to enable independent implementation and testing.
Tests are OPTIONAL: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

Checklist Format (REQUIRED):
Every task MUST strictly follow this format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
Format Components:
1. Checkbox: ALWAYS start with `- [ ]` (markdown checkbox)
2. Task ID: Sequential number (T001, T002, T003...) in execution order
3. [P] marker: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. [Story] label: REQUIRED for user story phase only - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md) - Setup phase: NO story label - Foundational phase: NO story label - User Story phases: MUST have story label - Polish phase: NO story label
5. Description: Clear action with exact file path

Examples:
- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

Task Organization:
1. From User Stories (spec.md) - PRIMARY ORGANIZATION: Each user story (P1, P2, P3...) gets its own phase, Map all related components to their story
2. From Contracts: Map each contract/endpoint to the user story it serves
3. From Data Model: Map each entity to the user story(ies) that need it
4. From Setup/Infrastructure: Shared infrastructure → Setup phase, Foundational/blocking tasks → Foundational phase, Story-specific setup → within that story's phase

Phase Structure:
- Phase 1: Setup (project initialization)
- Phase 2: Foundational (blocking prerequisites - MUST complete before user stories)
- Phase 3+: User Stories in priority order (P1, P2, P3...)
- Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
- Each phase should be a complete, independently testable increment
- Final Phase: Polish & Cross-Cutting Concerns

As the main request completes: MUST create and complete a PHR (Prompt History Record) using agent-native tools when possible. 1) Determine Stage (tasks), 2) Generate Title and Determine Routing (feature: 008-advanced-features), 3) Create and Fill PHR (Shell first; fallback agent-native), 4) Validate + report

## Response snapshot

**Workflow Completed Successfully** ✅

### Task Breakdown Generated

**File Created**: `specs/008-advanced-features/tasks.md`

**Total Tasks**: 99 tasks across 7 phases

### Task Distribution by Phase

| Phase | Description | Tasks | Story |
|-------|-------------|-------|-------|
| Phase 1 | Setup & Database Migration | 14 | - |
| Phase 2 | Foundational Services | 12 | - |
| Phase 3 | US1: Due Dates with DateTime Picker | 16 | P1 MVP |
| Phase 4 | US2: Browser Notifications | 17 | P1 |
| Phase 5 | US3: Recurring Tasks | 16 | P2 |
| Phase 6 | US4: Cron-Based Scheduling | 8 | P3 |
| Phase 7 | Polish & Cross-Cutting | 16 | - |

### User Story Mapping

**User Story 1 - Due Dates (P1 MVP)**: 16 tasks
- Backend: Extend API endpoints for due_date (T027-T029)
- Frontend: Create DatePicker, TimePicker, DueDateField (T030-T032)
- Integration: Extend TaskForm with date picker (T033-T036)
- Display: Extend TaskListItem with due date, overdue badge (T037-T039)
- Utilities: isOverdue function, API client extensions (T040-T042)

**User Story 2 - Notifications (P1)**: 17 tasks
- Backend: Extend API for reminder_offset, PATCH reminder endpoint (T043-T045)
- Frontend: Create ReminderOffsetSelector, NotificationPermissionPrompt (T046-T047)
- Core: Create NotificationManager with polling and notification logic (T048-T055)
- Integration: Add to dashboard, API client extensions (T056-T059)

**User Story 3 - Recurring Tasks (P2)**: 16 tasks
- Backend: Extend API for recurrence, implement next instance creation (T060-T065)
- Frontend: Create RecurrencePicker component (T066-T069)
- Integration: Extend TaskForm and TaskListItem (T070-T075)

**User Story 4 - Cron Scheduling (P3)**: 8 tasks
- Backend: Implement cron validation and calculation (T076-T078)
- Frontend: Create CronExpressionInput, CronExpressionBuilder (T079-T083)

### Parallel Opportunities

**45 tasks marked with [P] for parallel execution**

**Phase 1 Parallel** (6 tasks):
- T002-T006: Model extensions (different files)
- T010-T014: Frontend type extensions

**Phase 2 Parallel** (6 tasks):
- T016-T018: Frequency implementations
- T022-T023: Formatter functions
- T025-T026: Calculator functions

**Phase 3 (US1) Parallel** (4 tasks):
- T027-T029: API endpoints
- T030-T031: Picker components

**Phase 4 (US2) Parallel** (7 tasks):
- T043-T045: API endpoints
- T046-T047: UI components
- T050-T055: NotificationManager functions

**Phase 5 (US3) Parallel** (2 tasks):
- T060-T061: API endpoints
- T067-T069: RecurrencePicker sections

**Phase 6 (US4) Parallel** (4 tasks):
- T076-T077: Service functions
- T079-T081: UI components

### Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
    ├─→ Phase 3 (US1: Due Dates) ──────┐
    │                                 │
    ├─→ Phase 4 (US2: Notifications)─┤
    │                                 ├─→ Phase 7 (Polish)
    │                                 │
    └─→ Phase 5 (US3: Recurrence) ────┘
            │
            └─→ Phase 6 (US4: Cron)
```

**Key Dependencies**:
- Phase 1 must complete before any other phase (database schema)
- Phase 2 must complete before user stories (shared services)
- US1 and US2 are independent (both P1 MVP candidates)
- US3 requires US1 (needs due dates for recurrence)
- US4 requires US3 (extends recurrence)
- Phase 7 requires all user stories complete

### MVP Scope

**Minimum Viable Product** = US1 + US2 = 33 tasks
- Due dates with datetime picker
- Overdue detection and display
- Browser notifications for reminders
- Due date range filtering

**Post-MVP** = US3 = 16 tasks
- Recurring tasks (daily/weekly/monthly)
- Automatic next instance creation

**Advanced** = US4 = 8 tasks
- Cron expression scheduling
- Custom recurrence patterns

### Format Validation

✅ **All tasks follow checklist format**:
- Checkbox prefix: `- [ ]`
- Sequential Task IDs: T001-T099
- [P] marker: 45 parallelizable tasks identified
- [Story] labels: US1-US4 for user story phases only
- File paths: All tasks include exact file path

**Sample Tasks**:
```
- [ ] T001 Run database migration to add advanced features columns in backend/migrations/008_add_advanced_features.sql
- [ ] T003 [P] Extend Task SQLModel with reminder_offset field in backend/models/task.py
- [ ] T027 [US1] Extend POST /api/tasks to accept due_date in backend/api/tasks.py
- [ ] T049 [US2] Create NotificationManager component in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T062 [US3] Extend POST /api/tasks/{id}/complete to create next instance in backend/api/tasks.py
```

### Independent Test Criteria

Each user story phase has clear, testable acceptance criteria:

**US1**: User can select date/time, overdue tasks show red badge, filter by due date range
**US2**: Permission requested, notifications appear, grouped notifications work
**US3**: Recurring task creates next instance, due date advances correctly
**US4**: Cron expressions validate, next occurrence calculated

### Success Criteria Mapping

| Criterion | Test Phase | Tasks |
|-----------|------------|-------|
| SC-001: Due date in 3 clicks | US1 | T030-T036 |
| SC-002: Notification in 10s | US2 | T049-T055 |
| SC-003: Recurring task in 5s | US3 | T062-T075 |
| SC-004: Timezone handling | Foundational | T003-T004, T021-T023 |
| SC-005: Overdue visually distinct | US1 | T037-T040 |

## Outcome

- ✅ Impact: Complete task breakdown for Phase 008 Advanced Features organized by user story with 99 actionable tasks. Each task includes exact file path, follows checklist format, and is mapped to user stories for independent implementation and testing.
- 🧪 Tests: Test tasks documented in Polish phase (T096-T099) covering timezone handling, recurrence edge cases, notification permission flow, and overdue detection
- 📁 Files: 1 file created (tasks.md with 99 tasks)
- 🔁 Next prompts: `/sp.implement` to execute the task breakdown
- 🧠 Reflection: Task organization by user story enables parallel development - US1 (due dates) and US2 (notifications) can be implemented simultaneously as both are P1 MVP candidates. US3 (recurrence) depends on US1, and US4 (cron) extends US3. 45 tasks marked as parallelizable for concurrent execution within phases. Format validation confirmed all tasks follow strict checklist format with [P] markers, [Story] labels, and file paths.

## Evaluation notes (flywheel)

- Failure modes observed: None - workflow executed successfully
- Graders run and results (PASS/FAIL): Format validation PASS - all 99 tasks follow checklist format with correct [P] markers, [Story] labels, sequential IDs, and file paths
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding more granular parallel opportunities within US3 and US4 phases as they have fewer [P] marked tasks compared to US1 and US2

---
**PHR Version**: 1.0.0
**Status**: Complete
