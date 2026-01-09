# Implementation Tasks: User Authentication

**Feature**: 001-user-auth
**Branch**: `001-user-auth`
**Generated**: 2026-01-09
**Source**: [spec.md](./spec.md), [plan.md](./plan.md)

## Overview

This document breaks down the implementation of the authentication system into atomic, dependency-ordered tasks. Tasks are organized by user story to enable independent implementation and testing.

**Architecture**: FastAPI backend handles ALL authentication logic, Next.js frontend is pure UI client.

**Task Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- `[P]` = Parallelizable (can run concurrently with other [P] tasks)
- `[US1]`, `[US2]`, etc. = User Story label

---

## Task Summary

- **Total Tasks**: 47
- **Setup Tasks**: 8
- **Foundational Tasks**: 6
- **User Story 1 (Registration)**: 10 tasks
- **User Story 2 (Login)**: 10 tasks
- **User Story 3 (Protected Routes)**: 8 tasks
- **User Story 4 (Logout)**: 3 tasks
- **Polish**: 2 tasks

**Parallel Opportunities**: 18 tasks are parallelizable within their phases

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize project structure and dependencies for both backend and frontend.

### Backend Setup

- [x] T001 Create backend directory structure: backend/{models,api,core,tests}
- [x] T002 [P] Create backend/pyproject.toml with dependencies (fastapi, uvicorn, sqlmodel, python-jose, passlib, bcrypt, psycopg2-binary, pydantic, pytest)
- [x] T003 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, FRONTEND_URL, ENVIRONMENT
- [x] T004 [P] Create backend/.gitignore with __pycache__, .env, .pytest_cache, *.pyc

### Frontend Setup

- [x] T005 Create frontend directory structure: frontend/src/{app,components,lib,types}
- [x] T006 [P] Create frontend/package.json with dependencies (next, react, react-dom, typescript, tailwindcss, @types/react, @types/node)
- [x] T007 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL
- [x] T008 [P] Create frontend/.gitignore with .next, node_modules, .env.local, dist

**Parallel Execution Example**:
```bash
# T002, T003, T004 can run in parallel
# T006, T007, T008 can run in parallel
```

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement core infrastructure that all user stories depend on.

### Backend Foundation

- [x] T009 [P] Create backend/core/config.py with Settings class (pydantic-settings) for environment variables
- [x] T010 [P] Create backend/core/database.py with engine, Session, get_session dependency
- [x] T011 [P] Create backend/core/security.py with password hashing (passlib bcrypt) and JWT functions (python-jose)
- [x] T012 Create backend/models/__init__.py and backend/api/__init__.py and backend/core/__init__.py

### Frontend Foundation

- [x] T013 [P] Create frontend/src/types/auth.ts with TypeScript types (User, SignUpRequest, SignInRequest, etc.)
- [x] T014 [P] Create frontend/src/lib/api-client.ts with ApiClient class (fetch wrapper with credentials include)
- [x] T015 Create frontend/tsconfig.json with strict mode and path aliases

**Parallel Execution Example**:
```bash
# T009, T010, T011 can run in parallel
# T013, T014 can run in parallel
```

---

## Phase 3: User Story 1 - User Registration (P1)

**Goal**: Enable new users to register accounts with email and password.

**Independent Test**: User can navigate to /register, fill form, and see "Account created" message and redirect to /login.

### Backend Implementation

- [x] T016 [P] [US1] Create backend/models/user.py with User, UserBase, UserCreate, UserRead, UserLogin SQLModel classes
- [x] T017 [P] [US1] Create backend/api/auth.py with FastAPI router
- [x] T018 [US1] Implement POST /api/auth/sign-up endpoint in backend/api/auth.py (validate email format, check uniqueness, hash password, create user, return user data)
- [x] T019 [US1] Implement email validation helper in backend/api/auth.py (check for @ symbol and domain)
- [x] T020 [US1] Implement password validation in backend/api/auth.py (min 8 characters)
- [x] T021 [US1] Create database initialization script backend/scripts/init_db.py (create tables)

### Frontend Implementation

- [x] T022 [P] [US1] Create frontend/src/app/register/page.tsx (server component rendering RegisterForm)
- [x] T023 [US1] Create frontend/src/components/auth/RegisterForm.tsx (client component with email/password fields, validation, submit handler, error display, success message)
- [x] T024 [US1] Implement form validation in RegisterForm.tsx (client-side email format, password length)
- [x] T025 [US1] Integrate api-client in RegisterForm.tsx (POST /api/auth/sign-up, handle 409 error, redirect to /login on success)

**Parallel Execution Example**:
```bash
# T016, T022 can run in parallel
# After T016: T017, T018, T019, T020, T021
# After T022: T023, T024, T025
```

---

## Phase 4: User Story 2 - User Login (P1)

**Goal**: Enable registered users to login and receive JWT tokens.

**Independent Test**: User can navigate to /login, enter credentials, receive JWT token, and redirect to dashboard.

### Backend Implementation

- [x] T026 [US2] Implement GET /api/auth/session endpoint in backend/api/auth.py (verify JWT, return user data or 401)
- [x] T027 [US2] Implement POST /api/auth/sign-in endpoint in backend/api/auth.py (verify credentials, generate JWT, set httpOnly cookie, return token and user)
- [x] T028 [US2] Implement verify_password function in backend/core/security.py (bcrypt verify)
- [x] T029 [US2] Implement create_access_token function in backend/core/security.py (JWT with 7-day expiration)
- [x] T030 [US2] Implement get_user_by_email helper in backend/api/auth.py (query database)

### Frontend Implementation

- [x] T031 [P] [US2] Create frontend/src/app/login/page.tsx (server component rendering LoginForm)
- [x] T032 [US2] Create frontend/src/components/auth/LoginForm.tsx (client component with email/password, validation, submit handler, error display)
- [x] T033 [US2] Implement form validation in LoginForm.tsx (client-side email format, password length)
- [x] T034 [US2] Integrate api-client in LoginForm.tsx (POST /api/auth/sign-in, handle 401 error, store token via cookie set by backend, redirect to /dashboard)
- [x] T035 [US2] Create frontend/src/app/dashboard/page.tsx (protected page example)

**Parallel Execution Example**:
```bash
# T031, T026 can run in parallel
# After T031: T032, T033, T034, T035
# After T026: T027, T028, T029, T030
```

---

## Phase 5: User Story 3 - Protected Route Access (P1)

**Goal**: Verify JWT tokens on all protected endpoints and enforce authentication.

**Independent Test**: API request without token returns 401, request with valid token succeeds.

### Backend Implementation

- [x] T036 [P] [US3] Create backend/api/deps.py with get_current_user dependency (extract JWT from cookie or header, verify signature, return user or 401)
- [x] T037 [P] [US3] Implement JWT verification middleware in backend/api/deps.py (decode token, extract user_id, query database)
- [x] T038 [US3] Create example protected endpoint GET /api/users/me in backend/api/auth.py (requires get_current_user dependency)
- [x] T039 [US3] Add CORS middleware to backend/main.py (allow origins from FRONTEND_URL, allow credentials)

### Frontend Implementation

- [x] T040 [P] [US3] Create frontend/src/lib/auth.ts with session check utilities (getServerSession, useSession hook)
- [x] T041 [US3] Implement ProtectedRoute wrapper component in frontend/src/components/auth/ProtectedRoute.tsx (check session, redirect to /login if not authenticated)
- [x] T042 [US3] Update frontend/src/app/dashboard/page.tsx to use ProtectedRoute wrapper

**Parallel Execution Example**:
```bash
# T036, T037, T040 can run in parallel
# After T036: T038
# After T040: T041, T042
```

---

## Phase 6: User Story 4 - User Logout (P2)

**Goal**: Enable users to logout by clearing JWT tokens.

**Independent Test**: User clicks logout, token cleared, redirected to /login.

### Backend Implementation

- [x] T043 [US4] Implement POST /api/auth/sign-out endpoint in backend/api/auth.py (return success message, clear httpOnly cookie)

### Frontend Implementation

- [x] T044 [US4] Implement logout function in frontend/src/lib/auth.ts (call POST /api/auth/sign-out, clear cookie, redirect to /login)
- [x] T045 [US4] Add logout button to frontend/src/app/dashboard/page.tsx (call logout function)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Add final touches and ensure production readiness.

### Backend Polish

- [x] T046 [P] Add global exception handler to backend/main.py (catch 401, return consistent error format)
- [x] T047 [P] Create backend/main.py with FastAPI app, include all routers, CORS, exception handlers
- [x] T048 [P] Add health check endpoint GET /health in backend/main.py

### Frontend Polish

- [x] T049 [P] Update frontend/src/app/layout.tsx with basic HTML structure and metadata
- [x] T050 [P] Add error page frontend/src/app/error.tsx (handle errors gracefully)

**Parallel Execution Example**:
```bash
# T046, T047, T048, T049, T050 all parallel
```

---

## Dependencies

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1 - Registration) ← Independent
    ↓
Phase 4 (US2 - Login) ← Depends on US1 (need users to log in)
    ↓
Phase 5 (US3 - Protected Routes) ← Depends on US2 (need JWT tokens to protect)
    ↓
Phase 6 (US4 - Logout) ← Depends on US2 (need authenticated users to logout)
    ↓
Phase 7 (Polish)
```

### Task Dependencies Within Phases

**Phase 3 (US1 - Registration)**:
- T016 must complete before T017, T018
- T022 must complete before T023, T024, T025

**Phase 4 (US2 - Login)**:
- T026, T028, T029, T030 must complete before T027
- T031 must complete before T032, T033, T034, T035

**Phase 5 (US3 - Protected Routes)**:
- T036, T037 must complete before T038
- T040 must complete before T041, T042

**Phase 6 (US4 - Logout)**:
- T043 must complete before T044
- T044 must complete before T045

---

## Parallel Execution Strategy

### Maximum Parallelization

**Phase 1**: 4 parallel groups
- Group 1: T002, T003, T004 (backend config)
- Group 2: T006, T007, T008 (frontend config)

**Phase 2**: 2 parallel groups
- Group 1: T009, T010, T011 (backend foundation)
- Group 2: T013, T014 (frontend foundation)

**Phase 3 (US1)**: 2 parallel tracks
- Track 1: T016 → (T017, T019, T020) → T018
- Track 2: T022 → T023 → (T024, T025)

**Phase 4 (US2)**: 2 parallel tracks
- Track 1: (T026, T028, T029, T030) → T027
- Track 2: T031 → T032 → (T033, T034, T035)

**Phase 5 (US3)**: 2 parallel tracks
- Track 1: (T036, T037) → T038
- Track 2: T040 → (T041, T042)

**Phase 6 (US4)**: Sequential
- T043 → T044 → T045

**Phase 7**: 5 parallel tasks
- T046, T047, T048, T049, T050

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Delivers**: User registration and login (Phases 1-4)

**Tasks**: T001-T035 (35 tasks)

**Timeline**:
- Phase 1-2: 2 days (setup and foundation)
- Phase 3: 2 days (registration)
- Phase 4: 2 days (login)
- **Total**: 6 days

### Incremental Delivery

**Sprint 1**: Registration (Phase 3)
- Users can register accounts
- Independent test: Register new user

**Sprint 2**: Login (Phase 4)
- Users can login and receive tokens
- Independent test: Login and see dashboard

**Sprint 3**: Protected Routes (Phase 5)
- All endpoints protected by JWT
- Independent test: Access protected endpoint with token

**Sprint 4**: Logout (Phase 6)
- Users can logout
- Independent test: Logout and verify token cleared

**Sprint 5**: Polish (Phase 7)
- Production-ready error handling
- Independent test: All error cases return consistent format

---

## Testing Strategy

### Backend Tests (pytest)

```bash
# Unit tests
backend/tests/test_security.py  # Test password hashing, JWT functions
backend/tests/test_auth_api.py  # Test auth endpoints

# Integration tests
backend/tests/test_integration.py  # Test full auth flows
```

### Frontend Tests (React Testing Library)

```bash
# Component tests
frontend/tests/login.test.tsx     # Test LoginForm
frontend/tests/register.test.tsx  # Test RegisterForm
```

### End-to-End Tests (Playwright)

```bash
# Full flow tests
- Register new user
- Login with credentials
- Access protected page
- Logout
```

---

## File Checklist

### Backend Files (19 files)

```
backend/
├── pyproject.toml                    # T002
├── .env.example                       # T003
├── .gitignore                         # T004
├── main.py                            # T047
├── models/
│   ├── __init__.py                   # T012
│   └── user.py                       # T016
├── api/
│   ├── __init__.py                   # T012
│   ├── auth.py                       # T017, T018, T026, T027, T043
│   └── deps.py                       # T036
├── core/
│   ├── __init__.py                   # T012
│   ├── config.py                     # T009
│   ├── database.py                   # T010
│   └── security.py                   # T011, T028, T029
├── scripts/
│   └── init_db.py                    # T021
└── tests/
    ├── test_security.py              # (future)
    ├── test_auth_api.py              # (future)
    └── test_integration.py           # (future)
```

### Frontend Files (13 files)

```
frontend/
├── package.json                       # T006
├── .env.local.example                 # T007
├── .gitignore                         # T008
├── tsconfig.json                      # T015
├── src/
    ├── types/
    │   └── auth.ts                    # T013
    ├── lib/
    │   ├── api-client.ts              # T014
    │   └── auth.ts                    # T040, T044
    ├── components/
    │   └── auth/
    │       ├── RegisterForm.tsx       # T023
    │       ├── LoginForm.tsx          # T032
    │       └── ProtectedRoute.tsx     # T041
    ├── app/
    │   ├── layout.tsx                 # T049
    │   ├── register/
    │   │   └── page.tsx               # T022
    │   ├── login/
    │   │   └── page.tsx               # T031
    │   ├── dashboard/
    │   │   └── page.tsx               # T035, T042, T045
    │   └── error.tsx                  # T050
    └── tests/
        ├── login.test.tsx             # (future)
        └── register.test.tsx          # (future)
```

---

## Acceptance Criteria by Story

### User Story 1 - Registration

- [ ] User can access /register page
- [ ] User can submit email and password
- [ ] System validates email format (contains @)
- [ ] System validates password length (min 8 chars)
- [ ] System creates user in database
- [ ] System shows "Account created" message
- [ ] System redirects to /login
- [ ] System returns 409 if email already exists
- [ ] System hashes password with bcrypt
- [ ] System returns user data (excluding password)

### User Story 2 - Login

- [ ] User can access /login page
- [ ] User can submit email and password
- [ ] System verifies email exists
- [ ] System verifies password matches hash
- [ ] System generates JWT token (7-day expiry)
- [ ] System sets httpOnly cookie with token
- [ ] System returns token and user data
- [ ] System redirects to /dashboard
- [ ] System returns 401 if credentials invalid
- [ ] System includes token in cookie automatically

### User Story 3 - Protected Routes

- [ ] Request without token returns 401
- [ ] Request with expired token returns 401
- [ ] Request with invalid token returns 401
- [ ] Request with valid token succeeds
- [ ] System extracts user_id from token
- [ ] System scopes data to authenticated user
- [ ] System redirects unauthenticated to /login
- [ ] System allows authenticated to access protected pages

### User Story 4 - Logout

- [ ] User can click logout button
- [ ] System calls POST /api/auth/sign-out
- [ ] System clears httpOnly cookie
- [ ] System redirects to /login
- [ ] System returns success message
- [ ] Protected pages redirect to /login after logout

---

## Next Steps

1. **Start with MVP**: Complete Phases 1-4 (Tasks T001-T035)
2. **Test Registration**: Verify US1 acceptance criteria
3. **Test Login**: Verify US2 acceptance criteria
4. **Add Protection**: Complete Phase 5 (US3)
5. **Add Logout**: Complete Phase 6 (US4)
6. **Production Polish**: Complete Phase 7

**Ready to implement**: Execute tasks sequentially, or use parallel execution groups for faster development.

---

**Total Tasks**: 50
**Estimated Effort**: 8-10 days (depending on parallelization)
**Team Size**: 1-2 developers (full-stack)
