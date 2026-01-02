# Tasks: Terminal-based Todo CLI with TUI

**Input**: Design documents from `/specs/001-todo-cli-tui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Testing tasks included per constitution requirements (70%+ coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **CLI application**: `cli/` for source code, `tests/` for tests (at repository root)
- This matches the single-project structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create cli/ directory structure (cli/models/, cli/ui/, cli/services/, tests/unit/, tests/integration/, tests/fixtures/)
- [X] T002 Initialize uv project in cli/ with pyproject.toml
- [X] T003 Add textual>=0.80.0 to dependencies in cli/pyproject.toml
- [X] T004 Add dev dependencies (pytest>=8.0.0, pytest-asyncio>=0.23.0, pytest-cov>=4.1.0, textual[test]>=0.80.0) in cli/pyproject.toml
- [X] T005 Configure pytest in cli/pyproject.toml (asyncio_mode=auto, testpaths=tests)
- [X] T006 Create __init__.py files for Python packages (cli/, cli/models/, cli/ui/, cli/services/)
- [X] T007 Run `uv sync` from cli/ directory to install all dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 [P] Implement Task dataclass in cli/models/task.py with id, description, completed fields (from data-model.md)
- [X] T009 [P] Implement Task validation logic (_validate_description, _validate_id, __post_init__) in cli/models/task.py
- [X] T010 [P] Implement Task methods (toggle, with_description) in cli/models/task.py
- [X] T011 [P] Implement TaskService class in cli/services/task_service.py with __init__ method (_tasks list, _next_id counter)
- [X] T012 [P] Implement TaskService CRUD methods (create_task, get_all_tasks, get_task_by_id, update_task, delete_task, toggle_task_completion) in cli/services/task_service.py
- [X] T013 [P] Implement TaskService utility methods (task_count, is_empty) in cli/services/task_service.py
- [X] T014 [P] Write unit tests for Task model in tests/unit/test_task_model.py (validation, toggle, with_description, immutability)
- [X] T015 [P] Write unit tests for TaskService in tests/unit/test_task_service.py (all CRUD operations, edge cases)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Interactive Task Management (Priority: P1) 🎯 MVP

**Goal**: Provide core keyboard-driven task management with main menu navigation, task creation, and task listing capabilities

**Independent Test**: Launch app, navigate main menu with arrow keys, add tasks, view task list - all features work without requiring edit/delete functionality

### Unit Tests for User Story 1

- [ ] T016 [P] [US1] Write unit tests for MainMenuScreen in tests/unit/test_main_menu.py (menu options, keyboard navigation)
- [ ] T017 [P] [US1] Write unit tests for AddTaskScreen in tests/unit/test_add_task.py (input prompt, task creation integration)
- [ ] T018 [P] [US1] Write unit tests for TaskListScreen in tests/unit/test_task_list.py (display tasks, completion indicators, navigation)

### UI Components for User Story 1

- [X] T019 [P] [US1] Create MainMenuScreen in cli/ui/main_menu.py (5 buttons: Add, List, Delete, Edit, Exit)
- [X] T020 [P] [US1] Implement keyboard navigation in MainMenuScreen (up/down arrows, Enter to select)
- [X] T021 [P] [US1] Create AddTaskScreen in cli/ui/add_task.py (Input widget for task description)
- [X] T022 [P] [US1] Implement input validation in AddTaskScreen (empty check, error display, retry prompt)
- [X] T023 [P] [US1] Create TaskListScreen in cli/ui/task_list.py (ListView for task display)
- [X] T024 [P] [US1] Implement task display formatting in TaskListScreen ([ ] for uncompleted, [x] for completed, task ID)
- [X] T025 [US1] Wire up Add button in MainMenuScreen to push AddTaskScreen in cli/ui/main_menu.py
- [X] T026 [US1] Wire up List button in MainMenuScreen to push TaskListScreen in cli/ui/main_menu.py
- [X] T027 [US1] Wire up Exit button in MainMenuScreen to call app.exit() in cli/ui/main_menu.py

### REPL Orchestration for User Story 1

- [X] T028 [US1] Create TodoApp class in cli/main.py (inherits from textual.App)
- [X] T029 [US1] Implement greeting message in TodoApp (display on startup, FR-001)
- [X] T030 [US1] Initialize TaskService instance in TodoApp
- [X] T031 [US1] Set MainMenuScreen as initial screen in TodoApp
- [X] T032 [US1] Implement AddTaskScreen callback: create task via TaskService, pop screen, return to main menu
- [X] T033 [US1] Implement TaskListScreen integration: fetch tasks from TaskService, display in ListView
- [X] T034 [US1] Implement TaskListScreen Enter key handler: pop screen, return to main menu (FR-012)
- [X] T035 [US1] Add screen navigation helpers (push_screen, pop_screen) to return to main menu after actions (FR-018)

### Integration Tests for User Story 1

- [ ] T036 [US1] Write integration test for add task flow in tests/integration/test_repl_flow.py (launch app, navigate to Add, enter task, verify creation)
- [ ] T037 [US1] Write integration test for list tasks flow in tests/integration/test_repl_flow.py (create tasks, navigate to List, verify display)
- [ ] T038 [US1] Write integration test for main menu navigation in tests/integration/test_repl_flow.py (arrow keys, Enter selection)
- [ ] T039 [US1] Write integration test for clean exit in tests/integration/test_repl_flow.py (select Exit, verify terminal restoration, SC-006)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add and list tasks, navigate menu, exit cleanly. MVP complete!

---

## Phase 4: User Story 2 - Task Modification and Cleanup (Priority: P2)

**Goal**: Enable users to edit task descriptions and delete tasks from their list

**Independent Test**: Create tasks, use Edit to modify descriptions, use Delete to remove tasks - all operations work independently

### Unit Tests for User Story 2

- [ ] T040 [P] [US2] Write unit tests for EditTaskScreen in tests/unit/test_edit_task.py (task selection, description editing)
- [ ] T041 [P] [US2] Write unit tests for DeleteTaskScreen in tests/unit/test_delete_task.py (task selection, deletion confirmation)

### UI Components for User Story 2

- [X] T042 [P] [US2] Create EditTaskScreen in cli/ui/edit_task.py (ListView for task selection, Input for new description)
- [X] T043 [P] [US2] Implement task selection in EditTaskScreen (arrow key navigation, Enter to select task)
- [X] T044 [P] [US2] Implement description editing in EditTaskScreen (Input prompt, validation, update on submit)
- [X] T045 [P] [US2] Create DeleteTaskScreen in cli/ui/delete_task.py (ListView for task selection, delete confirmation)
- [X] T046 [P] [US2] Implement task deletion in DeleteTaskScreen (select task, Enter to delete, remove from TaskService)

### Integration for User Story 2

- [X] T047 [US2] Wire up Edit button in MainMenuScreen to push EditTaskScreen in cli/ui/main_menu.py
- [X] T048 [US2] Wire up Delete button in MainMenuScreen to push DeleteTaskScreen in cli/ui/main_menu.py
- [X] T049 [US2] Implement EditTaskScreen callback: call TaskService.update_task, pop screen, return to main menu
- [X] T050 [US2] Implement DeleteTaskScreen callback: call TaskService.delete_task, pop screen, return to main menu
- [X] T051 [US2] Handle empty task list in EditTaskScreen (show message, return to main menu, FR-022)
- [X] T052 [US2] Handle empty task list in DeleteTaskScreen (show message, return to main menu, FR-022)

### Integration Tests for User Story 2

- [ ] T053 [US2] Write integration test for edit task flow in tests/integration/test_repl_flow.py (create task, navigate to Edit, modify description, verify update)
- [ ] T054 [US2] Write integration test for delete task flow in tests/integration/test_repl_flow.py (create task, navigate to Delete, confirm deletion, verify removal)
- [ ] T055 [US2] Write integration test for edit/delete with empty list in tests/integration/test_repl_flow.py (graceful handling, no crashes)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full CRUD task management available

---

## Phase 5: User Story 3 - Visual Feedback and Completion Tracking (Priority: P3)

**Goal**: Provide visual indicators for task completion status and allow users to toggle completion with Space bar

**Independent Test**: Create tasks, press Space to toggle completion, verify visual indicators update from [ ] to [x] and back

### UI Enhancement for User Story 3

- [X] T056 [US3] Add Space key handler to TaskListScreen in cli/ui/task_list.py (bind keys.Space to toggle method)
- [X] T057 [US3] Implement completion toggle logic in TaskListScreen (get selected task, call TaskService.toggle_task_completion, refresh display)
- [X] T058 [US3] Update task display formatting in TaskListScreen to show completion status (use [ ] vs [x] based on task.completed, FR-009)
- [ ] T059 [US3] Add visual styling to TaskListScreen (different colors for completed vs uncompleted tasks)
- [X] T060 [US3] Implement immediate visual feedback after toggle (refresh ListView, updated indicator displays instantly)

### Integration Tests for User Story 3

- [ ] T061 [US3] Write integration test for completion toggle in tests/integration/test_repl_flow.py (create task, navigate to List, press Space, verify status change)
- [ ] T062 [US3] Write integration test for multiple toggles in tests/integration/test_repl_flow.py (toggle on→off→on, verify each state)
- [ ] T063 [US3] Write integration test for mixed completion states in tests/integration/test_repl_flow.py (create tasks, toggle some, verify all display correctly)

**Checkpoint**: All user stories should now be independently functional - full task management with completion tracking

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case handling, validation enforcement, visual polish, performance optimization

### Edge Case Handling

- [ ] T064 [P] Add empty description validation to AddTaskScreen (FR-023, show error, don't create task)
- [ ] T065 [P] Add empty description validation to EditTaskScreen (FR-023, show error, don't update task)
- [ ] T066 [P] Handle very long task descriptions in TaskListScreen (truncate or wrap, prevent UI break, 1000+ char edge case)
- [ ] T067 [P] Handle unexpected key presses in all screens (ignore invalid keys, prevent crashes)
- [ ] T068 [P] Handle terminal resize in TodoApp (ensure UI reflows correctly, Textual auto-resize)
- [ ] T069 [P] Handle rapid key presses in all screens (debounce if needed, prevent state corruption)

### Error Handling & Messages

- [ ] T070 [P] Add user-friendly error messages to AddTaskScreen ("Task description cannot be empty")
- [ ] T071 [P] Add user-friendly error messages to EditTaskScreen ("Task not found", "Description cannot be empty")
- [ ] T072 [P] Add user-friendly error messages to DeleteTaskScreen ("Task not found")
- [ ] T073 [P] Add help text to MainMenuScreen ("Use arrow keys to navigate, Enter to select")
- [ ] T074 [P] Add help text to TaskListScreen ("Space to toggle completion, Enter to return to menu")

### Visual Polish

- [ ] T075 [P] Add colors and styling to MainMenuScreen (highlight selected option, improve readability)
- [ ] T076 [P] Add colors and styling to TaskListScreen (completed tasks dimmed, uncompleted highlighted)
- [ ] T077 [P] Add borders and layout improvements to all screens (consistent visual design)
- [ ] T078 [P] Add loading states or transitions if needed (smooth screen changes)

### Performance Testing

- [ ] T079 [US1-US3] Create performance test with 100 tasks in tests/integration/test_performance.py (verify no degradation, SC-003)
- [ ] T080 [US1-US3] Measure response time for all operations in tests/integration/test_performance.py (verify <100ms, SC-010)
- [ ] T081 [US1-US3] Test memory usage over extended session in tests/integration/test_performance.py (check for leaks)

### Coverage Validation

- [ ] T082 Run all tests with coverage: `uv run pytest --cov=cli --cov-report=html` from cli/ directory
- [ ] T083 Verify unit test coverage meets 90%+ target for models and services
- [ ] T084 Verify overall test coverage meets 70%+ target per constitution
- [ ] T085 Add additional unit tests if coverage below target

### Final Validation

- [ ] T086 [US1] Manually verify SC-001: Launch app and create first task within 30 seconds
- [ ] T087 [US1] Manually verify SC-002: Navigate main menu without errors
- [ ] T088 [US1-US3] Manually verify SC-003: Create 10+ tasks, verify no lag
- [ ] T089 [US3] Manually verify SC-004: Toggle completion, verify instant feedback
- [ ] T090 [US1-US2] Manually verify SC-005: Edit and delete tasks, verify updates
- [ ] T091 [US1] Manually verify SC-006: Exit app 10 times, verify 100% clean terminal restoration
- [ ] T092 [US1-US3] Manually verify SC-007: Perform all operations, verify no crashes
- [ ] T093 [US1-US3] Manually verify SC-008: First-time user test (no documentation needed)
- [ ] T094 [US1-US3] Manually verify SC-009: Test with empty task list, verify graceful handling
- [ ] T095 [US1-US3] Manually verify SC-010: Time all interactions, verify <100ms response

### Documentation

- [ ] T096 [P] Create README.md in cli/ with project description and usage instructions
- [ ] T097 [P] Add keyboard shortcuts reference to README.md (arrow keys, Enter, Space)
- [ ] T098 [P] Add example screenshots to README.md (optional, if easy to capture)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3), US2 (Phase 4), US3 (Phase 5) can proceed sequentially in priority order
  - Or US2 and US3 could start in parallel after US1 completes (if team capacity)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Phase 3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (Phase 5)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable

### Within Each User Story

- Unit tests MUST be written before implementation (TDD approach)
- Models before services before UI components
- UI components before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: All tasks T001-T007 can run sequentially (setup dependencies)
- **Foundational Phase**: All tasks T008-T015 can run in parallel (different files)
- **User Story 1**: T016-T018 (tests) in parallel; T019-T026 (UI components) in parallel; T027-T035 (integration/wiring) sequential
- **User Story 2**: T040-T041 (tests) in parallel; T042-T046 (UI components) in parallel; T047-T052 (integration) sequential
- **User Story 3**: T056-T060 (UI enhancements) mostly sequential (same file)
- **Polish Phase**: All tasks T064-T098 can run in parallel (different files/concerns)

---

## Parallel Example: User Story 1 Implementation

```bash
# After Foundational phase complete, launch User Story 1 tests together:
Task T016: "Write unit tests for MainMenuScreen in tests/unit/test_main_menu.py"
Task T017: "Write unit tests for AddTaskScreen in tests/unit/test_add_task.py"
Task T018: "Write unit tests for TaskListScreen in tests/unit/test_task_list.py"

# After tests written, launch UI components in parallel:
Task T019: "Create MainMenuScreen in cli/ui/main_menu.py"
Task T021: "Create AddTaskScreen in cli/ui/add_task.py"
Task T023: "Create TaskListScreen in cli/ui/task_list.py"

# After UI components complete, wire up integration (sequential):
Task T025: "Wire up Add button in MainMenuScreen to push AddTaskScreen"
Task T026: "Wire up List button in MainMenuScreen to push TaskListScreen"
# ... etc
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T016-T039)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Verify MVP works: Can add tasks, list tasks, navigate menu, exit cleanly
6. Demo if ready

**MVP Scope**: Tasks T001-T039 only (39 tasks)

### Incremental Delivery

1. **Foundation**: Phase 1 + Phase 2 (T001-T015) → Project structure and data model ready
2. **MVP**: Add Phase 3 - User Story 1 (T016-T039) → Test independently → **Deploy/Demo (MVP!)**
3. **Full CRUD**: Add Phase 4 - User Story 2 (T040-T055) → Test independently → Deploy/Demo
4. **Complete**: Add Phase 5 - User Story 3 (T056-T063) → Test independently → Deploy/Demo
5. **Polished**: Add Phase 6 - Polish (T064-T098) → Final validation

Each phase adds value without breaking previous phases.

### Solo Developer Strategy

1. Complete Setup (T001-T007) - ~30 minutes
2. Complete Foundational (T008-T015) - ~2 hours
3. Complete US1 (T016-T039) - ~4 hours → **MVP ready!**
4. Complete US2 (T040-T055) - ~2 hours
5. Complete US3 (T056-T063) - ~1 hour
6. Complete Polish (T064-T098) - ~2 hours

**Total Estimated Time**: ~11.5 hours for full implementation

---

## Notes

- **[P] tasks** = Different files, no dependencies on incomplete tasks, can run in parallel
- **[US1/US2/US3] labels** = Map task to specific user story for traceability
- **Each user story** should be independently completable and testable
- **TDD approach**: Tests written first, should fail before implementation
- **Commit frequently**: After each task or logical group of tasks
- **Stop at checkpoints**: Validate story independence before proceeding
- **Avoid**: Vague tasks (all have file paths), same file conflicts (parallel tasks use different files), cross-story dependencies that break independence

---

## Summary

- **Total Tasks**: 98
- **Setup**: 7 tasks (T001-T007)
- **Foundational**: 8 tasks (T008-T015)
- **User Story 1 (MVP)**: 24 tasks (T016-T039)
- **User Story 2**: 16 tasks (T040-T055)
- **User Story 3**: 8 tasks (T056-T063)
- **Polish**: 35 tasks (T064-T098)

**Parallel Opportunities**: 35+ tasks marked with [P] can run in parallel with appropriate team size

**Independent Test Criteria**:
- **US1**: Launch app, add tasks, list tasks, exit - all work without edit/delete
- **US2**: Create tasks, edit descriptions, delete tasks - full CRUD works
- **US3**: Toggle task completion, verify visual indicators - completion tracking works

**Suggested MVP**: User Story 1 only (tasks T001-T039) delivers core value as standalone task manager
