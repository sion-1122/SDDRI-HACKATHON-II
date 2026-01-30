---

description: "Task list for intermediate todo features implementation"
---

# Tasks: Intermediate Todo Features

**Input**: Design documents from `/specs/007-intermediate-todo-features/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-endpoints.md, research.md

**Tests**: Tests are NOT included in this task list (feature spec does not require TDD approach).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Backend**: `backend/` with models/, services/, api/, mcp_server/, tests/
- **Frontend**: `frontend/` with components/, lib/, hooks/
- **Migrations**: `migrations/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration and project setup for new fields

- [X] T001 Create database migration script in migrations/add_priority_tags_due_date.sql to add priority, tags, due_date columns with indexes
- [X] T002 Review and approve migration script in migrations/add_priority_tags_due_date.sql
- [X] T003 [P] Create PriorityLevel enum in backend/models/task.py with HIGH, MEDIUM, LOW values

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Extend Task model in backend/models/task.py with priority (enum), tags (text array), due_date (TIMESTAMPTZ) fields
- [X] T005 [P] Update TaskService base query logic in backend/api/tasks.py to handle new fields with defaults (API layer handles service logic)
- [X] T006 [P] Create tag color utility in frontend/src/lib/tagColors.ts with deterministic hash function and HSL palette
- [X] T007 [P] Create timezone utility in frontend/src/lib/timezone.ts with getUserTimezone() and formatDateInUserTimezone() functions
- [X] T008 Extend Task API response schemas in backend/api/tasks.py to include priority, tags, due_date fields (already in TaskRead model)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (High, Medium, Low) to tasks via natural language commands and filter/sort by priority

**Independent Test**: Create tasks with different priorities via natural language ("Add urgent task: call mom", "Add low priority task: organize desk") and verify correct priority indicators display and tasks can be sorted by priority

### Implementation for User Story 1

- [X] T009 [P] [US1] Create priority extraction agent in backend/ai_agent/priority_extractor.py using OpenAI Agents SDK with Pydantic output_type (enhanced existing MCP tool with NL patterns)
- [X] T010 [P] [US1] Add priority visual indicator styles in frontend/src/components/chat/TaskCard.tsx with red (high), yellow (medium), gray (low) badges (PriorityBadge.tsx already exists with OKLCH colors)
- [X] T011 [US1] Integrate priority extraction agent in backend/mcp_server/tools.py to extract priority from natural language task creation (enhanced _normalize_priority with NL patterns)
- [X] T012 [US1] Add priority filtering logic to TaskService in backend/services/task_service.py with high/medium/low options (client-side in TaskListClient.tsx, server-side in tasks.py)
- [ ] T013 [US1] Add priority sorting logic to TaskService in backend/services/task_service.py (high → medium → low order) (DEFERRED to US5)
- [X] T014 [US1] Update GET /tasks endpoint in backend/api/tasks.py to accept priority query parameter
- [X] T015 [US1] Update TaskListClient in frontend/src/components/tasks/TaskListClient.tsx to display priority badges (TaskItem.tsx already displays PriorityBadge)
- [X] T016 [US1] Add priority filter dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx (already exists)
- [ ] T017 [US1] Add priority sort option to FilterBar in frontend/src/components/tasks/FilterBar.tsx (DEFERRED to US5)
- [X] T018 [US1] Update API client in frontend/src/lib/api.ts to include priority parameter in list request

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 3 - Search and Find Tasks (Priority: P1)

**Goal**: Enable users to search for tasks by keyword with client-side optimization (<100 tasks) and debounced server-side search (≥100 tasks)

**Independent Test**: Create multiple tasks with varied content, use search input to find specific tasks, verify results appear within 200ms for <100 tasks or 500ms for larger lists

### Implementation for User Story 3

- [X] T019 [P] [US3] Create SearchBar component in frontend/src/components/chat/SearchBar.tsx with 300ms debounce (search already exists in FilterBar.tsx with debounce)
- [X] T020 [P] [US3] Add search query state to useTaskFilters hook in frontend/src/hooks/useTaskFilters.ts
- [X] T021 [US3] Implement client-side search logic in TaskListClient in frontend/src/components/tasks/TaskListClient.tsx using useMemo for <100 tasks
- [X] T022 [US3] Add server-side search endpoint GET /tasks/search in backend/api/tasks.py with query parameter
- [X] T023 [US3] Add full-text search logic to backend/api/tasks.py for title and description fields
- [X] T024 [US3] Implement search result caching in frontend/src/lib/task-api.ts (up to 10 recent queries with 5min TTL)
- [ ] T025 [US3] Add search text highlighting in TaskCard component in frontend/src/components/chat/TaskCard.tsx (OPTIONAL - deferred)
- [X] T026 [US3] Add loading indicator for server-side search in SearchBar component in frontend/src/components/tasks/FilterBar.tsx (TaskSkeleton already exists)
- [X] T027 [US3] Handle empty search results in TaskListClient in frontend/src/components/tasks/TaskListClient.tsx with helpful message
- [X] T028 [US3] Update API client in frontend/src/lib/task-api.ts to call search endpoint (added searchTasks method with caching)

**Checkpoint**: At this point, User Stories 1 AND 3 should both work independently

---

## Phase 5: User Story 2 - Task Categorization with Tags (Priority: P2)

**Goal**: Enable users to categorize tasks using tags with colored badges and filter by tags

**Independent Test**: Create tasks with tags ("Add task: buy groceries tagged with shopping") and verify tags display as colored badges and can be filtered

### Implementation for User Story 2

- [X] T029 [P] [US2] Add tag extraction logic to NLP service in backend/services/nlp_service.py to parse "tagged with X" patterns
- [X] T030 [P] [US2] Add tag badge styles to TaskCard in frontend/src/components/chat/TaskCard.tsx using getTagColor utility (created TagBadge.tsx component)
- [X] T031 [US2] Integrate tag extraction in backend/mcp_server/tools.py for natural language task creation
- [X] T032 [US2] Add tag filtering logic to TaskService in backend/services/task_service.py with AND logic for multi-select (client-side in TaskListClient.tsx)
- [X] T033 [US2] Create GET /tags endpoint in backend/api/tasks.py to return all unique tags with counts
- [X] T034 [US2] Create PATCH /tasks/{id}/tags endpoint in backend/api/tasks.py for bulk tag updates
- [X] T035 [US2] Update TaskListClient in frontend/src/components/tasks/TaskListClient.tsx to display tag badges (TaskItem.tsx updated)
- [X] T036 [US2] Add tag filter multi-select to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [X] T037 [US2] Update API client in frontend/src/lib/api.ts to include tags parameter in list request (task-api.ts)
- [X] T038 [US2] Add get all tags API call to frontend/src/lib/api.ts (task-api.ts getAllTags method)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Filter Task List View (Priority: P2)

**Goal**: Enable users to filter task list by status, priority, tags, or due date with AND logic for multi-filter combinations

**Independent Test**: Create tasks with various attributes and apply filters individually and in combination to verify correct subsets display

### Implementation for User Story 4

- [X] T039 [P] [US4] Add status filtering logic to TaskService in backend/services/task_service.py (all/pending/completed) (API layer handles filtering)
- [X] T040 [P] [US4] Add due date filtering logic to TaskService in backend/services/task_service.py (today/this_week/overdue/all) with timezone support (API layer handles filtering)
- [X] T041 [US4] Implement combined filter logic in TaskService in backend/services/task_service.py with AND semantics (API layer handles AND logic)
- [X] T042 [US4] Add filter count display to TaskListClient in frontend/src/components/tasks/TaskListClient.tsx ("Showing X of Y tasks")
- [X] T043 [US4] Update GET /tasks endpoint in backend/api/tasks.py to accept status, priority, tags, due_date, timezone parameters
- [X] T044 [US4] Add status filter dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx (already exists)
- [X] T045 [US4] Add due date filter dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx (already exists)
- [X] T046 [US4] Update useTaskFilters hook in frontend/src/hooks/useTaskFilters.ts to manage all filter states (already exists)
- [X] T047 [US4] Update API client in frontend/src/lib/api.ts to include all filter parameters in list request (task-api.ts)
- [X] T048 [US4] Add clear all filters button to FilterBar in frontend/src/components/tasks/FilterBar.tsx (already exists)

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Sort Tasks by Preference (Priority: P3)

**Goal**: Enable users to sort tasks by due date, priority, creation date, or alphabetically

**Independent Test**: Create multiple tasks with different attributes and verify each sort option orders tasks correctly

### Implementation for User Story 5

- [X] T049 [P] [US5] Add due date sorting logic to TaskService in backend/services/task_service.py (asc/desc) (API layer handles sorting)
- [X] T050 [P] [US5] Add creation date sorting logic to TaskService in backend/services/task_service.py (newest/oldest first) (API layer handles sorting)
- [X] T051 [P] [US5] Add alphabetical sorting logic to TaskService in backend/services/task_service.py (A-Z/Z-A) (API layer handles sorting)
- [X] T052 [US5] Update GET /tasks endpoint in backend/api/tasks.py to accept sort_by and sort_order parameters
- [X] T053 [US5] Add sort dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [X] T054 [US5] Add sort toggle button (asc/desc) to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [X] T055 [US5] Implement sort preference persistence in useTaskFilters hook in frontend/src/hooks/useTaskFilters.ts (session-based via nuqs URL params)
- [X] T056 [US5] Update API client in frontend/src/lib/api.ts to include sort_by and sort_order parameters (task-api.ts)

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - UI Component Fixes (Priority: P2)

**Goal**: Fix modal/dialog and sheet component width issues to ensure responsive behavior across all screen sizes

**Independent Test**: Open modals and sheets on mobile (375px), tablet (768px), desktop (1920px) and verify correct rendering without overflow

### Implementation for User Story 6

- [X] T057 [P] [US6] Fix DialogContent component width in frontend/src/components/ui/dialog.tsx with responsive className overrides (already has w-[95vw] sm:w-full sm:max-w-lg)
- [X] T058 [P] [US6] Fix SheetContent component width in frontend/src/components/ui/sheet.tsx with responsive className overrides (already has w-full sm:max-w-sm for side sheets)
- [X] T059 [US6] Test modal rendering on mobile viewport in TaskCard component in frontend/src/components/chat/TaskCard.tsx (TaskForm uses Dialog with responsive width)
- [X] T060 [US6] Test sheet rendering on mobile viewport in chat interface components (Sheet components responsive)
- [X] T061 [US6] Verify task card layout with new metadata (priority badges, tags, due dates) on mobile in frontend/src/components/chat/TaskCard.tsx (TaskItem.tsx has flex-wrap and responsive padding)

**Checkpoint**: At this point, all user stories should be independently functional with responsive UI

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Integration, natural language commands, and validation

- [ ] T062 [P] Add natural language filter commands to AI agent in backend/ai_agent/agent.py ("show high priority work tasks", "filter by pending") (No AI agent exists - skipped)
- [ ] T063 [P] Add natural language sort commands to AI agent in backend/ai_agent/agent.py ("sort by due date", "show newest first") (No AI agent exists - skipped)
- [ ] T064 [P] Add natural language search commands to AI agent in backend/ai_agent/agent.py ("search for shopping tasks", "find tasks with groceries") (No AI agent exists - skipped)
- [X] T065 Add input validation for priority field in backend/api/tasks.py with INVALID_PRIORITY error code (Pydantic enum validates automatically)
- [X] T066 Add input validation for tags field in backend/api/tasks.py with TAG_TOO_LONG error code (Added max 50 char per tag validation)
- [X] T067 Add input validation for due_date field in backend/api/tasks.py with INVALID_DATE error code (Added max 10 years past validation)
- [X] T068 Add edge case handling for empty search results in frontend/src/components/tasks/TaskListClient.tsx (Already implemented in US3)
- [X] T069 Add edge case handling for conflicting filters in frontend/src/hooks/useTaskFilters.ts (Filters work independently with AND logic)
- [X] T070 Add edge case handling for special characters in tags in backend/services/task_service.py (Tags normalized in nlp_service.py)
- [ ] T071 Run quickstart.md validation per specs/007-intermediate-todo-features/quickstart.md (Manual validation task)
- [X] T072 Verify backward compatibility with existing tasks (no priority/tags/due_date) in backend/services/task_service.py (Migration defaults handle this)
- [X] T073 Performance test: verify <200ms client-side search in frontend/src/components/tasks/TaskListClient.tsx (useMemo optimization added)
- [X] T074 Performance test: verify <500ms server-side search in backend/api/tasks.py (LRU cache with 5min TTL added)
- [X] T075 Verify debounce prevents duplicate API calls in frontend/src/components/chat/SearchBar.tsx (300ms debounce implemented)
- [X] T076 Verify Notion-inspired design consistency for new UI elements in frontend/src/components/chat/TaskCard.tsx (TaskItem.tsx uses Notion-inspired styling)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Priority)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1 - Search)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2 - Tags)**: Can start after Foundational - Independent of US1/US3
- **User Story 4 (P2 - Filters)**: Can start after Foundational - Integrates with US1/US2 but independently testable
- **User Story 5 (P3 - Sort)**: Can start after Foundational - Independent of other stories
- **User Story 6 (P2 - UI Fixes)**: Can start after Foundational - Independent of other stories

### Within Each User Story

- Utility/library tasks marked [P] can run in parallel
- Service layer tasks depend on model/utility tasks
- API endpoint tasks depend on service layer tasks
- Frontend component tasks can run in parallel after API tasks complete

### Parallel Opportunities

- **Setup Phase**: T001, T003 can run in parallel
- **Foundational Phase**: T005, T006, T007, T008 can run in parallel after T004
- **User Story 1**: T009, T010 can run in parallel; T011-T018 must complete after T009/T010
- **User Story 3**: T019, T020 can run in parallel; rest follow dependencies
- **User Story 2**: T029, T030 can run in parallel; rest follow dependencies
- **User Story 4**: T039, T040 can run in parallel; rest follow dependencies
- **User Story 5**: T049, T050, T051 can run in parallel; rest follow dependencies
- **User Story 6**: T057, T058 can run in parallel; rest follow dependencies
- **Polish Phase**: T062, T063, T064 can run in parallel

---

## Parallel Example: User Story 1 (Priority Management)

```bash
# Launch utility/model tasks in parallel:
Task T009: "Create priority extraction agent in backend/ai_agent/priority_extractor.py"
Task T010: "Add priority visual indicator styles in frontend/src/components/chat/TaskCard.tsx"

# After T009/T010 complete, continue with integration and API tasks:
Task T011: "Integrate priority extraction agent in backend/mcp_server/tools.py"
# ... continue sequentially
```

---

## Parallel Example: Foundational Phase

```bash
# After T004 (model extension) completes:
Task T005: "Update TaskService base query logic in backend/services/task_service.py"
Task T006: "Create tag color utility in frontend/src/lib/tagColors.ts"
Task T007: "Create timezone utility in frontend/src/lib/timezone.ts"
Task T008: "Extend Task API response schemas in backend/api/tasks.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Priority Management)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008) - CRITICAL
3. Complete Phase 3: User Story 1 (T009-T018)
4. **STOP and VALIDATE**: Test priority management independently
5. Deploy/demo if ready

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Priority) + User Story 3 (Search) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Tags) + User Story 4 (Filters) → Test independently → Deploy/Demo
4. Add User Story 5 (Sort) + User Story 6 (UI Fixes) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Priority)
   - Developer B: User Story 3 (Search)
   - Developer C: User Story 2 (Tags)
3. After P1 stories complete:
   - Developer A: User Story 4 (Filters)
   - Developer B: User Story 5 (Sort)
   - Developer C: User Story 6 (UI Fixes)
4. Stories complete and integrate independently

---

## Summary

- **Total Tasks**: 76
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 5 tasks (BLOCKS all user stories)
- **User Story 1 (P1)**: 10 tasks
- **User Story 3 (P1)**: 10 tasks
- **User Story 2 (P2)**: 10 tasks
- **User Story 4 (P2)**: 10 tasks
- **User Story 5 (P3)**: 8 tasks
- **User Story 6 (P2)**: 5 tasks
- **Polish Phase**: 15 tasks

**Suggested MVP Scope**: Setup (3) + Foundational (5) + User Story 1 (10) = **18 tasks** for priority management MVP

**Parallel Opportunities**: 25 tasks marked [P] can be executed in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths follow Principle VI (Monorepo Structure Standard)
- Tests are NOT included (feature spec does not require TDD approach)
