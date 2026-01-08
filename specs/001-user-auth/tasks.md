# Tasks: User Authentication

**Input**: Design documents from `/specs/001-user-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL for this feature. Test tasks are included for comprehensive coverage but can be skipped if not following TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Web app (Phase II)**: `backend/`, `frontend/` with their own structure
- Paths follow the full monorepo structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install backend dependencies (python-jose[cryptography], passlib[bcrypt]) in backend/ using uv
- [ ] T002 [P] Install frontend better-auth package in frontend/ using pnpm
- [ ] T003 [P] Create backend/core/ directory structure (security.py, middleware.py, deps.py, config.py)
- [ ] T004 [P] Create frontend/lib/ directory structure (auth.ts, auth-client.ts)
- [ ] T005 [P] Create frontend/app/api/auth/ directory for BetterAuth API route
- [ ] T006 [P] Create frontend/components/auth/ directory for auth components
- [ ] T007 [P] Create backend/tests/ directory for test files
- [ ] T008 [P] Set BETTER_AUTH_SECRET environment variable in backend/.env (generate secure 32+ character string)
- [ ] T009 [P] Set matching BETTER_AUTH_SECRET in frontend/.env.local (must match backend)
- [ ] T010 [P] Set DATABASE_URL in both backend/.env and frontend/.env.local

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend JWT Infrastructure

- [ ] T011 Implement JWTManager class in backend/core/security.py with verify_token(), get_user_id_from_token(), and get_token_from_header() methods
- [ ] T012 Implement JWTMiddleware in backend/core/middleware.py with dispatch() method for global JWT protection
- [ ] T013 [P] Implement get_current_user_id dependency function in backend/core/deps.py
- [ ] T014 [P] Create CurrentUserDep type alias in backend/core/deps.py for dependency injection
- [ ] T015 Update backend/main.py to add JWTMiddleware to FastAPI app with excluded_paths for public endpoints
- [ ] T016 [P] Add CORS middleware to backend/main.py allowing frontend origin (http://localhost:3000)
- [ ] T017 Test JWT middleware by accessing /api/tasks endpoint (should return 401 without token)

### Frontend BetterAuth Setup

- [ ] T018 Configure BetterAuth with email/password and JWT plugin in frontend/lib/auth.ts
- [ ] T019 [P] Create BetterAuth API route handler in frontend/app/api/auth/[...all]/route.ts
- [ ] T020 [P] Create BetterAuth client instance in frontend/lib/auth-client.ts using createAuthClient()
- [ ] T021 Test BetterAuth API route by accessing /api/auth/sign-in endpoint

### Database Migration

- [ ] T022 Create database migration to add user_id UUID column to tasks table with foreign key to users table
- [ ] T023 Create database migration to add idx_tasks_user_id index on tasks.user_id column
- [ ] T024 Update backend/models/task.py to add user_id: UUID field with foreign key to users table
- [ ] T025 Handle migration of existing tasks (assign to default user or delete - decision documented in migration SQL)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with email and password

**Independent Test**: Navigate to /register page, fill out form with valid email and password (min 8 chars), submit form, verify account created and redirected to /login

### Tests for User Story 1 (OPTIONAL - skip if not following TDD) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US1] Integration test in backend/tests/test_tasks_auth.py for user registration endpoint with valid email and password
- [ ] T027 [P] [US1] Integration test in backend/tests/test_tasks_auth.py for duplicate email registration (should return 409)
- [ ] T028 [P] [US1] Integration test in frontend/components/auth/__tests__/RegisterForm.test.tsx for registration form validation

### Frontend Implementation for User Story 1

- [ ] T029 [P] [US1] Create registration page component in frontend/app/register/page.tsx with email and password input fields
- [ ] T030 [P] [US1] Implement client-side email validation in frontend/app/register/page.tsx (must contain @ and domain)
- [ ] T031 [P] [US1] Implement client-side password validation in frontend/app/register/page.tsx (minimum 8 characters)
- [ ] T032 [US1] Integrate BetterAuth signUp.email() method in frontend/app/register/page.tsx form submission handler
- [ ] T033 [US1] Add error handling in frontend/app/register/page.tsx for registration failures (email already exists, invalid format)
- [ ] T034 [US1] Add success handling in frontend/app/register/page.tsx (redirect to /login after registration)
- [ ] T035 [P] [US1] Create RegisterForm component in frontend/components/auth/RegisterForm.tsx for reusable registration form
- [ ] T036 [US1] Style registration page with responsive layout and clear error messages in frontend/app/register/page.tsx

**Checkpoint**: At this point, User Story 1 (Registration) should be fully functional and testable independently

---

## Phase 4: User Story 2 - User Login (Priority: P1) 🎯 MVP

**Goal**: Enable returning users to authenticate and receive JWT tokens

**Independent Test**: Navigate to /login page, enter registered email and password, submit form, verify JWT token issued and redirected to /dashboard

### Tests for User Story 2 (OPTIONAL - skip if not following TDD) ⚠️

- [ ] T037 [P] [US2] Integration test in backend/tests/test_tasks_auth.py for user login endpoint with valid credentials
- [ ] T038 [P] [US2] Integration test in backend/tests/test_tasks_auth.py for login with invalid credentials (should return 401)
- [ ] T039 [P] [US2] Integration test in frontend/components/auth/__tests__/LoginForm.test.tsx for login form submission

### Frontend Implementation for User Story 2

- [ ] T040 [P] [US2] Create login page component in frontend/app/login/page.tsx with email and password input fields
- [ ] T041 [P] [US2] Implement client-side validation in frontend/app/login/page.tsx for email and password fields
- [ ] T042 [US2] Integrate BetterAuth signIn.email() method in frontend/app/login/page.tsx form submission handler
- [ ] T043 [US2] Add JWT token storage in frontend/app/login/page.tsx (BetterAuth handles storage automatically)
- [ ] T044 [US2] Add error handling in frontend/app/login/page.tsx for login failures (generic "Invalid credentials" message per FR-015)
- [ ] T045 [US2] Add success handling in frontend/app/login/page.tsx (redirect to /dashboard after login)
- [ ] T046 [P] [US2] Create LoginForm component in frontend/components/auth/LoginForm.tsx for reusable login form
- [ ] T047 [US2] Add link to /register page on frontend/app/login/page.tsx for new users

**Checkpoint**: At this point, User Stories 1 (Registration) AND 2 (Login) should both work independently

---

## Phase 5: User Story 3 - Protected Route Access (Priority: P1) 🎯 MVP

**Goal**: Enforce JWT authentication on all API endpoints and protected frontend pages

**Independent Test**: Make API request without JWT token (should return 401), make API request with valid JWT (should succeed), navigate to protected page without JWT (should redirect to /login)

### Tests for User Story 3 (OPTIONAL - skip if not following TDD) ⚠️

- [ ] T048 [P] [US3] Integration test in backend/tests/test_jwt.py for JWT verification with valid token (should succeed)
- [ ] T049 [P] [US3] Integration test in backend/tests/test_jwt.py for JWT verification with invalid token (should return 401)
- [ ] T050 [P] [US3] Integration test in backend/tests/test_jwt.py for JWT verification with expired token (should return 401)
- [ ] T051 [P] [US3] Integration test in backend/tests/test_tasks_auth.py for protected endpoint without JWT (should return 401)
- [ ] T052 [P] [US3] E2E test in frontend/e2e/auth.spec.ts for protected page redirecting to login when not authenticated

### Backend Implementation for User Story 3

- [ ] T053 [US3] Update backend/api/tasks.py to inject CurrentUserDep dependency into all route handlers (create_task, list_tasks, get_task, update_task, delete_task, toggle_complete)
- [ ] T054 [US3] Update backend/api/tasks.py create_task() to use injected user_id from JWT (task.user_id = user_id)
- [ ] T055 [US3] Update backend/api/tasks.py list_tasks() to filter tasks by injected user_id (WHERE user_id = $1)
- [ ] T056 [US3] Update backend/api/tasks.py get_task() to verify task ownership (WHERE id = $1 AND user_id = $2, return 404 if not found)
- [ ] T057 [US3] Update backend/api/tasks.py update_task() to verify task ownership before updating
- [ ] T058 [US3] Update backend/api/tasks.py delete_task() to verify task ownership before deleting
- [ ] T059 [US3] Update backend/api/tasks.py toggle_complete() to verify task ownership before toggling

### Frontend Implementation for User Story 3

- [ ] T060 [P] [US3] Create protected dashboard page in frontend/app/dashboard/page.tsx
- [ ] T061 [US3] Implement session check in frontend/app/dashboard/page.tsx using authClient.getSession()
- [ ] T062 [US3] Add redirect to /login in frontend/app/dashboard/page.tsx if session is not authenticated
- [ ] T063 [P] [US3] Create frontend/lib/api/client.ts with apiClient() function for authenticated API calls
- [ ] T064 [US3] Implement JWT token injection in frontend/lib/api/client.ts (authClient.token() gets JWT, added to Authorization header)
- [ ] T065 [P] [US3] Create task service in frontend/lib/api/client.ts with getTasks(), createTask(), updateTask(), deleteTask() methods
- [ ] T066 [US3] Test protected API access by calling /api/tasks with valid JWT token (should return empty array for new user)
- [ ] T067 [US3] Test API without JWT token (should return 401 Unauthorized)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently (core auth flow complete)

---

## Phase 6: User Story 4 - User Logout (Priority: P2)

**Goal**: Enable authenticated users to securely end their session

**Independent Test**: Click logout button on /dashboard, verify token cleared and redirected to /login, verify accessing /api/tasks after logout returns 401

### Tests for User Story 4 (OPTIONAL - skip if not following TDD) ⚠️

- [ ] T068 [P] [US4] E2E test in frontend/e2e/auth.spec.ts for logout flow (login, click logout, verify redirect and token cleared)

### Frontend Implementation for User Story 4

- [ ] T069 [US4] Add logout button to frontend/app/dashboard/page.tsx
- [ ] T070 [US4] Implement authClient.signOut() call in frontend/app/dashboard/page.tsx logout button handler
- [ ] T071 [US4] Add redirect to /login in frontend/app/dashboard/page.tsx after successful logout
- [ ] T072 [US4] Verify JWT token is cleared from storage after logout (BetterAuth handles this automatically)

**Checkpoint**: At this point, ALL User Stories (1-4) should be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Backend Polish

- [ ] T073 [P] Add comprehensive error logging to backend/core/middleware.py for JWT verification failures
- [ ] T074 [P] Add request ID tracking to backend/main.py for distributed tracing
- [ ] T075 [P] Update backend/.env.example with BETTER_AUTH_SECRET and DATABASE_URL documentation
- [ ] T076 [P] Create backend/CLAUDE.md with backend-specific development instructions
- [ ] T077 Add health check endpoint in backend/main.py that tests database connectivity (returns 503 if DB unavailable)

### Frontend Polish

- [ ] T078 [P] Add loading states to frontend/app/register/page.tsx during registration API call
- [ ] T079 [P] Add loading states to frontend/app/login/page.tsx during login API call
- [ ] T080 [P] Add loading states to frontend/app/dashboard/page.tsx during session check
- [ ] T081 [P] Improve error message display in frontend/app/register/page.tsx with styled error components
- [ ] T082 [P] Improve error message display in frontend/app/login/page.tsx with styled error components
- [ ] T083 [P] Update frontend/.env.local.example with BETTER_AUTH_SECRET, DATABASE_URL, and NEXT_PUBLIC_BASE_URL documentation
- [ ] T084 [P] Create frontend/CLAUDE.md with frontend-specific development instructions

### Documentation & Validation

- [ ] T085 [P] Update root CLAUDE.md with authentication technology stack (BetterAuth, JWT)
- [ ] T086 [P] Update specs/001-user-auth/quickstart.md with any implementation learnings or clarifications
- [ ] T087 Run quickstart.md validation: follow quickstart guide from scratch to verify all steps work
- [ ] T088 [P] Add comments to backend/core/security.py explaining JWT verification flow
- [ ] T089 [P] Add comments to frontend/lib/auth.ts explaining BetterAuth configuration
- [ ] T090 [P] Create README in backend/ directory with setup and run instructions
- [ ] T091 [P] Create README in frontend/ directory with setup and run instructions

### Cross-Functional Testing (OPTIONAL)

- [ ] T092 [P] Write backend unit tests in backend/tests/test_jwt.py for JWTManager.verify_token() method
- [ ] T093 [P] Write backend unit tests in backend/tests/test_jwt.py for JWTManager.get_user_id_from_token() method
- [ ] T094 [P] Write backend integration tests in backend/tests/test_tasks_auth.py for data isolation (user 1 cannot access user 2's tasks)
- [ ] T095 [P] Write frontend component tests in frontend/components/auth/__tests__/LoginForm.test.tsx for login form
- [ ] T096 [P] Write frontend component tests in frontend/components/auth/__tests__/RegisterForm.test.tsx for registration form
- [ ] T097 [P] Write E2E tests in frontend/e2e/auth.spec.ts for complete registration and login flow
- [ ] T098 [P] Write E2E tests in frontend/e2e/auth.spec.ts for protected page access control

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Registration): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Login): Can start after Foundational - No dependencies on other stories
  - User Story 3 (Protected Routes): Can start after Foundational - Depends on US1 and US2 being conceptually complete (users must exist and be able to login)
  - User Story 4 (Logout): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (Registration)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Login)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (Protected Routes)**: Can start after Foundational (Phase 2) - Requires users to exist (US1) and login capability (US2), but can be developed in parallel if testing waits for US1/US2
- **User Story 4 (Logout)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation (TDD approach)
- Models before services (not applicable - BetterAuth manages user model)
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: All tasks marked [P] (T002-T010) can run in parallel
- **Foundational Phase**:
  - Backend tasks T013-T014 can run in parallel
  - Backend task T017 can run in parallel with Frontend tasks T018-T021
- **User Story 1**: Tests T026-T028 can run in parallel; Frontend tasks T029-T031 can run in parallel
- **User Story 2**: Tests T037-T039 can run in parallel; Frontend tasks T040-T041 can run in parallel
- **User Story 3**: Tests T048-T052 can run in parallel; Frontend tasks T060, T063-T065 can run in parallel
- **User Story 4**: Test T068 can run in parallel with implementation
- **Polish Phase**: Most tasks marked [P] can run in parallel
- **Different user stories**: Can be worked on in parallel by different team members once Foundational phase is complete

---

## Parallel Example: User Story 1 (Registration)

```bash
# Launch all tests for User Story 1 together (if following TDD):
Agent 1: "Integration test for user registration endpoint with valid email and password in backend/tests/test_tasks_auth.py"
Agent 2: "Integration test for duplicate email registration in backend/tests/test_tasks_auth.py"
Agent 3: "Integration test for registration form validation in frontend/components/auth/__tests__/RegisterForm.test.tsx"

# After tests fail, launch frontend components in parallel:
Agent 1: "Create registration page component in frontend/app/register/page.tsx with email and password input fields"
Agent 2: "Implement client-side email validation in frontend/app/register/page.tsx"
Agent 3: "Implement client-side password validation in frontend/app/register/page.tsx"
Agent 4: "Create RegisterForm component in frontend/components/auth/RegisterForm.tsx"
```

---

## Parallel Example: User Story 3 (Protected Routes)

```bash
# Launch all tests for User Story 3 together (if following TDD):
Agent 1: "Integration test for JWT verification with valid token in backend/tests/test_jwt.py"
Agent 2: "Integration test for JWT verification with invalid token in backend/tests/test_jwt.py"
Agent 3: "Integration test for JWT verification with expired token in backend/tests/test_jwt.py"
Agent 4: "Integration test for protected endpoint without JWT in backend/tests/test_tasks_auth.py"
Agent 5: "E2E test for protected page redirecting to login when not authenticated in frontend/e2e/auth.spec.ts"

# After tests fail, launch backend task route updates in parallel:
Agent 1: "Update backend/api/tasks.py create_task() to use injected user_id from JWT"
Agent 2: "Update backend/api/tasks.py list_tasks() to filter tasks by injected user_id"
Agent 3: "Update backend/api/tasks.py get_task() to verify task ownership"
Agent 4: "Update backend/api/tasks.py update_task() to verify task ownership before updating"
Agent 5: "Update backend/api/tasks.py delete_task() to verify task ownership before deleting"
Agent 6: "Update backend/api/tasks.py toggle_complete() to verify task ownership before toggling"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Login)
5. Complete Phase 5: User Story 3 (Protected Routes)
6. **STOP and VALIDATE**: Test complete auth flow (register → login → access protected page with JWT)
7. Deploy/demo MVP (core authentication complete)
8. Add User Story 4 (Logout) as enhancement
9. Complete Phase 7: Polish

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Registration) → Test independently → Users can create accounts
3. Add User Story 2 (Login) → Test independently → Users can login and get JWT tokens
4. Add User Story 3 (Protected Routes) → Test independently → API endpoints protected, data isolated
5. **MVP CHECKPOINT**: At this point, core authentication is complete (register, login, protected API)
6. Add User Story 4 (Logout) → Test independently → Users can securely end sessions
7. Add Polish → Documentation, error handling, loading states
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration)
   - Developer B: User Story 2 (Login)
   - Developer C: User Story 3 (Protected Routes) - Wait for US1/US2 conceptual completion
3. Stories complete and integrate independently
4. Team converges for Polish phase

---

## Notes

- **[P] tasks** = different files, no dependencies on incomplete tasks
- **[Story] label** maps task to specific user story for traceability
- **Each user story** should be independently completable and testable
- **Tests are OPTIONAL** - skip test tasks if not following TDD approach
- **BetterAuth manages users table** - no need to create user model manually
- **JWT middleware is global** - protects all /api/* routes except /api/auth/*
- **Data isolation is critical** - all queries MUST filter by user_id from JWT
- **Commit after each task or logical group** - small commits make rollback easier
- **Stop at any checkpoint** to validate story independently before proceeding
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

- **Total Tasks**: 98 (78 implementation + 20 optional tests)
- **Tasks per User Story**:
  - Setup (Phase 1): 10 tasks
  - Foundational (Phase 2): 15 tasks (BLOCKS all user stories)
  - User Story 1 - Registration: 11 tasks (3 optional tests + 8 implementation)
  - User Story 2 - Login: 11 tasks (3 optional tests + 8 implementation)
  - User Story 3 - Protected Routes: 20 tasks (5 optional tests + 15 implementation)
  - User Story 4 - Logout: 5 tasks (1 optional test + 4 implementation)
  - Polish (Phase 7): 26 tasks (7 optional tests + 19 implementation)
- **Parallel Opportunities**: ~50% of tasks can run in parallel within their phase/story
- **Independent Test Criteria**: Each user story has clear independent test criteria defined
- **MVP Scope**: User Stories 1-3 (Registration, Login, Protected Routes) - 56 tasks
- **Format Validation**: ✅ ALL tasks follow checklist format with [ID], [P?] marker, [Story] label, and file paths
