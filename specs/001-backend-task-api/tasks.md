# Tasks: Backend Task CRUD API

**Input**: Design documents from `/specs/001-backend-task-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Tests**: Test tasks included per specification requirements (testing strategy defined in plan.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)** - Phase II Web Application:
- Backend: `backend/models/`, `backend/api/`, `backend/core/`, `backend/tests/`
- Paths follow implementation plan structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (models/, api/, core/, tests/)
- [ ] T002 Initialize UV project with pyproject.toml in backend/
- [ ] T003 [P] Install dependencies: FastAPI, SQLModel, Uvicorn, Pydantic, psycopg2-binary, python-dotenv
- [ ] T004 [P] Create .env.example template with DATABASE_URL, ENVIRONMENT, LOG_LEVEL variables
- [ ] T005 [P] Create .gitignore for backend/ (excluding .env, __pycache__, *.pyc, .pytest_cache/)
- [ ] T006 [P] Configure pytest in pyproject.toml with test paths and pythonpath settings

**Checkpoint**: Project structure ready, dependencies configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create database engine configuration in backend/core/config.py
- [ ] T008 [P] Implement get_session dependency generator in backend/core/deps.py
- [ ] T009 [P] Create init_db() function to create all tables on startup
- [ ] T010 Create FastAPI application instance in backend/main.py with startup event
- [ ] T011 [P] Create User model in backend/models/user.py (minimal: id only)
- [ ] T012 [P] Create pytest fixtures in backend/tests/conftest.py (test_db, test_session, test_user)
- [ ] T013 [P] Configure logging in backend/main.py with structured format

**Checkpoint**: Foundation ready - database, FastAPI app, and base models available

---

## Phase 3: User Story 1 - Create and Manage Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, view, update, and delete tasks through REST API

**Independent Test**:
- Create task via POST /api/{user_id}/tasks → verify 201 response with task ID
- List tasks via GET /api/{user_id}/tasks → verify task list returned
- Get task via GET /api/{user_id}/tasks/{id} → verify task details
- Update task via PUT /api/{user_id}/tasks/{id} → verify changes persisted
- Toggle completion via PATCH /api/{user_id}/tasks/{id}/complete → verify status flipped
- Delete task via DELETE /api/{user_id}/tasks/{id} → verify task removed
- All operations verify database persistence and correct user_id scoping

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Create test for POST /api/{user_id}/tasks in backend/tests/test_api_tasks.py
- [ ] T015 [P] [US1] Create test for GET /api/{user_id}/tasks in backend/tests/test_api_tasks.py
- [ ] T016 [P] [US1] Create test for GET /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py
- [ ] T017 [P] [US1] Create test for PUT /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py
- [ ] T018 [P] [US1] Create test for DELETE /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py
- [ ] T019 [P] [US1] Create test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/test_api_tasks.py
- [ ] T020 [P] [US1] Create edge case tests (404, invalid data, ownership) in backend/tests/test_api_tasks.py

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create Task database model in backend/models/task.py with all fields (id, user_id, title, description, completed, created_at, updated_at)
- [ ] T022 [P] [US1] Create TaskCreate input model in backend/models/task.py with validation
- [ ] T023 [P] [US1] Create TaskUpdate input model in backend/models/task.py (all optional)
- [ ] T024 [P] [US1] Create TaskRead output model in backend/models/task.py
- [ ] T025 [US1] Create API router for tasks in backend/api/tasks.py with /api/{user_id}/tasks prefix
- [ ] T026 [US1] Implement POST /api/{user_id}/tasks endpoint (create_task) in backend/api/tasks.py
- [ ] T027 [US1] Implement GET /api/{user_id}/tasks endpoint (list_tasks) in backend/api/tasks.py
- [ ] T028 [US1] Implement GET /api/{user_id}/tasks/{task_id} endpoint (get_task) in backend/api/tasks.py
- [ ] T029 [US1] Implement PUT /api/{user_id}/tasks/{task_id} endpoint (update_task) in backend/api/tasks.py
- [ ] T030 [US1] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint (delete_task) in backend/api/tasks.py
- [ ] T031 [US1] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint (toggle_complete) in backend/api/tasks.py
- [ ] T032 [US1] Wire up tasks router in backend/main.py with app.include_router()
- [ ] T033 [US1] Add HTTPException error handling for 404, 400, 422 status codes in backend/api/tasks.py
- [ ] T034 [US1] Add ownership verification (task.user_id == user_id) in backend/api/tasks.py

**Checkpoint**: At this point, User Story 1 should be fully functional - complete CRUD API operational

---

## Phase 4: User Story 2 - Task Organization with Filtering (Priority: P2)

**Goal**: Enable pagination, filtering, and search for large task lists

**Independent Test**:
- Create 50+ tasks for test user
- Request with offset=0, limit=20 → verify exactly 20 tasks returned
- Request with offset=20, limit=20 → verify next 20 tasks returned
- Request with completed=true query param → verify only completed tasks returned
- Request with completed=false query param → verify only active tasks returned
- Request beyond available data (offset=999) → verify empty list returned gracefully

### Tests for User Story 2

- [ ] T035 [P] [US2] Create pagination test (offset/limit) in backend/tests/test_api_tasks.py
- [ ] T036 [P] [US2] Create completion status filter test in backend/tests/test_api_tasks.py
- [ ] T037 [P] [US2] Create edge case test (pagination beyond data) in backend/tests/test_api_tasks.py

### Implementation for User Story 2

- [ ] T038 [US2] Add offset and limit query parameters to GET /api/{user_id}/tasks in backend/api/tasks.py
- [ ] T039 [US2] Add Query validation: limit max 100, default 50 in backend/api/tasks.py
- [ ] T040 [US2] Implement offset/limit in database query with .offset() and .limit() in backend/api/tasks.py
- [ ] T041 [US2] Add optional completed query parameter to GET /api/{user_id}/tasks in backend/api/tasks.py
- [ ] T042 [US2] Implement completed status filtering in database query with .where() in backend/api/tasks.py
- [ ] T043 [US2] Add ordering by created_at DESC (newest first) to list query in backend/api/tasks.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with pagination and filtering

---

## Phase 5: User Story 3 - Task Metadata and Timestamps (Priority: P3)

**Goal**: Ensure timestamps are correctly set and maintained through task lifecycle

**Independent Test**:
- Create new task → verify created_at set to current time (within 5s tolerance)
- Wait 2 seconds, update task → verify updated_at changed, created_at unchanged
- Get task details → verify both timestamps present in response
- List tasks → verify all tasks include timestamps
- Update multiple times → verify updated_at increments each time

### Tests for User Story 3

- [ ] T044 [P] [US3] Create timestamp creation test in backend/tests/test_api_tasks.py
- [ ] T045 [P] [US3] Create timestamp update test (created_at immutable, updated_at changes) in backend/tests/test_api_tasks.py
- [ ] T046 [P] [US3] Create timestamp presence test in all API responses in backend/tests/test_api_tasks.py

### Implementation for User Story 3

> **NOTE**: Timestamp fields already defined in Task model (Phase 3, T021). This phase ensures correct behavior.

- [ ] T047 [US3] Verify Task model has default_factory=datetime.utcnow for created_at in backend/models/task.py
- [ ] T048 [US3] Verify Task model has default_factory=datetime.utcnow for updated_at in backend/models/task.py
- [ ] T049 [US3] Add updated_at = datetime.utcnow() in update_task endpoint before session.commit() in backend/api/tasks.py
- [ ] T050 [US3] Add updated_at = datetime.utcnow() in toggle_complete endpoint before session.commit() in backend/api/tasks.py
- [ ] T051 [US3] Verify TaskRead model includes both created_at and updated_at fields in backend/models/task.py

**Checkpoint**: All user stories should now be independently functional with complete timestamp tracking

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T052 [P] Create health check endpoint /health in backend/main.py
- [ ] T053 [P] Add API versioning prefix or header if needed
- [ ] T054 [P] Create README.md in backend/ with setup and run instructions
- [ ] T055 [P] Verify all endpoints return consistent error response format {"detail": "message"}
- [ ] T056 Run backend/CLAUDE.md quickstart validation (start server, test all endpoints)
- [ ] T057 [P] Add request/response logging for debugging in backend/main.py
- [ ] T058 [P] Verify OpenAPI documentation accessible at /docs and /redoc
- [ ] T059 [P] Add database connection error handling with graceful degradation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T006) - **BLOCKS all user stories**
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion (T007-T013)
  - User Story 1 (Phase 3): P1 priority - no dependencies on other stories
  - User Story 2 (Phase 4): P2 priority - depends on US1 endpoints existing
  - User Story 3 (Phase 5): P3 priority - depends on US1 endpoints and Task model
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (T007-T013) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 endpoints created (T025-T032) - Extends list_tasks endpoint
- **User Story 3 (P3)**: Can start after US1 implementation - Verifies and ensures timestamp behavior

### Within Each User Story

**User Story 1 (Core CRUD)**:
- Tests (T014-T020) MUST be written and FAIL before implementation
- Models (T021-T024) before endpoints (T026-T031)
- Endpoints integrated before error handling (T033-T034)

**User Story 2 (Filtering)**:
- Tests (T035-T037) before implementation
- Extends existing list_tasks endpoint (T038-T043)

**User Story 3 (Timestamps)**:
- Tests (T044-T046) before implementation
- Verifies/updates existing models and endpoints (T047-T051)

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004, T005, T006 can run in parallel (different files, no dependencies)

**Foundational Phase (Phase 2)**:
- T008, T009, T011, T012, T013 can run in parallel after T007 and T010

**User Story 1 (Phase 3)**:
- All tests (T014-T020) can run in parallel
- All models (T021-T024) can run in parallel after tests written
- Endpoint implementations (T026-T031) can be done in any order after models

**User Story 2 (Phase 4)**:
- All tests (T035-T037) can run in parallel
- Implementation tasks (T038-T043) build on each other sequentially

**User Story 3 (Phase 5)**:
- All tests (T044-T046) can run in parallel
- Implementation tasks (T047-T051) mostly verification and updates

**Polish Phase (Phase 6)**:
- All tasks marked [P] (T052, T053, T054, T055, T057, T058, T059) can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# After foundational phase complete, launch all tests for User Story 1 together:
Task T014: "Create test for POST /api/{user_id}/tasks in backend/tests/test_api_tasks.py"
Task T015: "Create test for GET /api/{user_id}/tasks in backend/tests/test_api_tasks.py"
Task T016: "Create test for GET /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py"
Task T017: "Create test for PUT /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py"
Task T018: "Create test for DELETE /api/{user_id}/tasks/{id} in backend/tests/test_api_tasks.py"
Task T019: "Create test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/test_api_tasks.py"
Task T020: "Create edge case tests (404, invalid data, ownership) in backend/tests/test_api_tasks.py"

# After tests written, launch all models together:
Task T021: "Create Task database model in backend/models/task.py with all fields"
Task T022: "Create TaskCreate input model in backend/models/task.py with validation"
Task T023: "Create TaskUpdate input model in backend/models/task.py (all optional)"
Task T024: "Create TaskRead output model in backend/models/task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T014-T034)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Start server: `uv run uvicorn backend.main:app --reload`
   - Test all 6 CRUD endpoints with cURL or Postman
   - Verify database persistence
   - Check API documentation at http://localhost:8000/docs
5. Deploy/demo if ready

**MVP Scope**: Core task CRUD functionality - users can create, read, update, delete, and toggle tasks

### Incremental Delivery

1. Complete Setup + Foundational (T001-T013) → Foundation ready
2. Add User Story 1 (T014-T034) → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 (T035-T043) → Test independently → Deploy/Demo (pagination/filtering added)
4. Add User Story 3 (T044-T051) → Test independently → Deploy/Demo (timestamps verified)
5. Polish (T052-T059) → Production-ready

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T013)
2. **Once Foundational is done, parallelize**:
   - **Developer A**: User Story 1 (T014-T034) - Core CRUD
   - **Developer B**: Can start User Story 2 (T035-T043) only after US1 list_tasks endpoint exists (T027)
   - **Developer C**: Can start User Story 3 (T044-T051) only after US1 Task model complete (T021)
3. Stories complete and integrate independently

**Recommended**: Sequential approach (P1 → P2 → P3) for single developer or small team

---

## Task Count Summary

- **Total Tasks**: 59
- **Setup Phase**: 6 tasks
- **Foundational Phase**: 7 tasks (CRITICAL - blocks all stories)
- **User Story 1 (P1 - MVP)**: 21 tasks (7 tests + 14 implementation)
- **User Story 2 (P2)**: 9 tasks (3 tests + 6 implementation)
- **User Story 3 (P3)**: 8 tasks (3 tests + 5 implementation)
- **Polish Phase**: 8 tasks

**Parallel Opportunities**: 29 tasks marked [P] can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies within the phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests follow TDD approach: write tests first, verify they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for immediate execution
- User Story 1 alone delivers complete MVP value
- User Stories 2 and 3 add incremental value without breaking US1
