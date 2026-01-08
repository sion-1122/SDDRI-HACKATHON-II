# Implementation Plan: User Authentication

**Branch**: `001-user-auth` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-user-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement user authentication system with BetterAuth on the frontend (Next.js 16) and JWT verification middleware on the backend (FastAPI). The system enables user registration, login, logout, and protects all API endpoints with JWT-based authentication. All data is scoped to the authenticated user, implementing multi-user tenancy with complete data isolation per Constitution Principle IX.

**Technical Approach**:
- Frontend: BetterAuth with email/password authentication, JWT plugin for token issuance
- Backend: Custom FastAPI middleware for JWT verification, dependency injection for user_id
- Integration: Shared `BETTER_AUTH_SECRET` environment variable for token signing/verification
- Database: BetterAuth manages `users` table, `tasks` table includes `user_id` foreign key

## Technical Context

**Language/Version**:
- Backend: Python 3.13+
- Frontend: TypeScript 5+ with Next.js 16+

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose[cryptography], passlib[bcrypt]
- Frontend: better-auth, @better-auth/prisma-adapter, better-auth/plugins/jwt
- Database: Neon Serverless PostgreSQL (or local PostgreSQL)

**Storage**:
- User accounts: PostgreSQL `users` table (managed by BetterAuth)
- JWT tokens: Stateless (client-side storage in httpOnly cookies or localStorage)
- Tasks: PostgreSQL `tasks` table with `user_id` foreign key

**Testing**:
- Backend: pytest for JWT verification, integration tests for protected endpoints
- Frontend: React Testing Library for auth components, E2E tests for login flows

**Target Platform**:
- Backend: Linux server (FastAPI)
- Frontend: Web browser (Next.js SSR + client components)

**Project Type**: Web application (full-stack monorepo)

**Performance Goals**:
- Registration completion: < 60 seconds (target: < 30 seconds)
- Login completion: < 15 seconds (target: < 5 seconds)
- JWT verification: < 50ms average latency (target: < 20ms)
- Concurrent auth requests: 100+ without degradation

**Constraints**:
- All API endpoints (except `/api/auth/*`) require valid JWT token
- JWT tokens expire after 7 days with no refresh mechanism (out of scope)
- Shared secret must be identical on frontend and backend
- All database queries must be scoped to authenticated user

**Scale/Scope**:
- Initial launch: Support for 1000+ users
- Database: Single PostgreSQL instance with connection pooling
- Authentication: Email/password only (no social login, no 2FA)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Persistent Storage (Phase II Non-Negotiable)
✅ **PASS** - All user accounts stored in PostgreSQL via BetterAuth. JWT tokens stateless (client-side only). No in-memory authentication state.

### Principle II: RESTful API Excellence
✅ **PASS** - Backend implements RESTful API with FastAPI. All endpoints under `/api` path. Returns JSON responses with consistent error handling. Appropriate HTTP status codes (200, 400, 401, 403, 404, 500).

### Principle III: Responsive Web UI
✅ **PASS** - Frontend uses Next.js 16 App Router with React Server Components. Mobile-first responsive design. Keyboard and mouse optimized.

### Principle IV: Multi-User Architecture with Authentication
✅ **PASS** - Every user authenticates via BetterAuth before accessing functionality. All data scoped to authenticated user. Users cannot access another user's data (enforced by JWT middleware + query scoping).

### Principle VI: Monorepo Structure Standard
✅ **PASS** - Follows standardized monorepo layout:
- `backend/` - FastAPI application
- `frontend/` - Next.js application
- `specs/001-user-auth/` - Feature specifications
- Component-specific CLAUDE.md files

### Principle VII: Authentication & JWT Security
✅ **PASS** - All API endpoints require valid JWT. JWTs issued by BetterAuth. Frontend sends via `Authorization: Bearer <token>` header. Backend verifies signature using `BETTER_AUTH_SECRET`. Extracts `user_id` from validated tokens. Returns 401 for invalid/missing tokens.

### Principle VIII: Frontend Architecture (Next.js)
✅ **PASS** - Uses Next.js 16 App Router with React Server Components. Authentication handled by BetterAuth. Client-side state minimized (JWT in cookie/localStorage). All API calls include JWT token. Server components by default, client components only for forms.

### Principle IX: Data Ownership & Isolation
✅ **PASS** - All database queries scoped to authenticated user from JWT. `user_id` stored as task owner. Queries filter by `user_id`. Users cannot access other users' data (returns 403/404). Cross-user access attempts blocked.

### Principle X: API Response Consistency
✅ **PASS** - All endpoints return consistent JSON responses. Success responses include requested data. Error responses include clear message and appropriate HTTP status code. Validation errors list field-specific messages.

**Constitution Compliance**: ✅ ALL PRINCIPLES SATISFIED

## Project Structure

### Documentation (this feature)

```text
specs/001-user-auth/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # OpenAPI specification
│   └── api-endpoints.md # Endpoint documentation
├── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
backend/
├── core/
│   ├── security.py      # JWT verification, JWTManager class
│   ├── middleware.py    # JWTMiddleware for global protection
│   ├── deps.py          # Dependency injection (CurrentUserDep)
│   └── config.py        # Database configuration
├── models/
│   ├── user.py          # User model (managed by BetterAuth)
│   └── task.py          # Task model with user_id foreign key
├── api/
│   ├── auth.py          # Auth endpoints (optional, BetterAuth handles)
│   └── tasks.py         # Task endpoints with JWT injection
├── tests/
│   ├── test_jwt.py      # JWT verification tests
│   └── test_tasks.py    # Protected endpoint tests
└── main.py              # FastAPI app with middleware

frontend/
├── lib/
│   ├── auth.ts          # BetterAuth configuration
│   ├── auth-client.ts   # BetterAuth client (createAuthClient)
│   └── api/
│       └── client.ts    # API client with JWT injection
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/route.ts  # BetterAuth API route
│   ├── login/
│   │   └── page.tsx     # Login page
│   ├── register/
│   │   └── page.tsx     # Registration page
│   └── dashboard/
│       └── page.tsx     # Protected page example
└── components/
    └── auth/
        ├── LoginForm.tsx    # Login form component
        └── RegisterForm.tsx # Registration form component
```

**Structure Decision**: Full web application (backend + frontend) per Constitution Principle VI. Backend handles JWT verification and data persistence. Frontend handles authentication UI and token management. Both services share `BETTER_AUTH_SECRET` for JWT signing/verification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. This section intentionally left blank.

## Phase 0: Research & Technology Decisions

**Status**: ✅ COMPLETE
**Output**: [research.md](./research.md)

### Research Tasks

1. **BetterAuth Integration with Next.js 16**
   - How to set up BetterAuth with Next.js App Router
   - Email/password authentication configuration
   - JWT token generation and storage
   - Integration with custom backend (FastAPI)
   - Route protection patterns
   - API client patterns with JWT injection

2. **FastAPI JWT Verification Middleware**
   - Middleware implementation for global JWT protection
   - JWT signature verification with shared secret
   - User ID extraction from JWT claims
   - Dependency injection patterns
   - Error handling (401 responses)
   - Integration with existing task endpoints

3. **Database Schema**
   - BetterAuth `users` table structure
   - Adding `user_id` foreign key to `tasks` table
   - Migration strategy for existing data

### Key Decisions

**Decision 1**: Use BetterAuth for Next.js authentication
- **Rationale**: Native Next.js 16 support, built-in JWT plugin, excellent DX
- **Alternatives Rejected**: NextAuth.js (heavier, complex for custom backends), Supabase Auth (overkill), Clerk (SaaS dependency)

**Decision 2**: Use HS256 algorithm with shared secret
- **Rationale**: Simple, secure, no additional infrastructure
- **Alternatives Rejected**: RS256 with JWKS (complexity not justified), third-party auth services (adds dependency)

**Decision 3**: Global JWT middleware with selective exclusions
- **Rationale**: Protects all routes by default, flexible for public endpoints
- **Alternatives Rejected**: Per-route decorators (error-prone, manual), API gateway (adds infrastructure)

**Decision 4**: Stateless JWT with 7-day expiration
- **Rationale**: Simple, scales horizontally, no session storage required
- **Alternatives Rejected**: Session storage (complexity, scalability), Refresh tokens (out of scope per assumptions)

**Decision 5**: Client-side token storage in httpOnly cookies
- **Rationale**: Secure from XSS, BetterAuth default behavior
- **Alternatives Rejected**: localStorage only (vulnerable to XSS), server-side sessions (violates stateless design)

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE
**Output**: [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

### Data Model

**Entities Created**:
1. **User Account** (`users` table)
   - Fields: `id` (UUID), `email` (unique), `password_hash`, `created_at`, `updated_at`
   - Managed by BetterAuth
   - Validation: Email format, password min 8 characters, case-insensitive uniqueness

2. **Authentication Token (JWT)**
   - Stateless, not stored in database
   - Claims: `sub` (user_id), `iat`, `exp`, `iss`, `aud`
   - Algorithm: HS256 with `BETTER_AUTH_SECRET`
   - Expiration: 7 days

3. **Session**
   - Logical session tracked via JWT
   - States: Anonymous, Authenticated, Expired
   - Client-side storage only

4. **Credentials**
   - Transient data (never stored)
   - Email format validation, password min 8 characters

**Relationships**:
- User → Tasks (One-to-Many via `tasks.user_id` foreign key)
- Cascading delete: User deletion deletes associated tasks

**Validation Rules**:
- Email: Valid format (contains @ and domain)
- Password: Minimum 8 characters
- JWT: Signature verification, expiration check, `sub` claim required

### API Contracts

**Endpoints Designed**:
1. `GET /health` - Health check (public)
2. `POST /api/auth/sign-up` - User registration (public)
3. `POST /api/auth/sign-in` - User login (public)
4. `POST /api/auth/sign-out` - User logout (authenticated)
5. `GET /api/auth/session` - Get current session (authenticated)

**Contracts Created**:
- [openapi.yaml](./contracts/openapi.yaml) - OpenAPI 3.0 specification
- [api-endpoints.md](./contracts/api-endpoints.md) - Detailed endpoint documentation

### Implementation Guide

**Quickstart Created**: [quickstart.md](./quickstart.md)

**Backend Setup**:
1. Install dependencies (python-jose, passlib)
2. Create `core/security.py` with JWTManager
3. Create `core/middleware.py` with JWTMiddleware
4. Create `core/deps.py` with dependency injection
5. Update `main.py` to add middleware
6. Update task routes to inject `user_id`
7. Configure `.env` with `BETTER_AUTH_SECRET`

**Frontend Setup**:
1. Install better-auth
2. Create `lib/auth.ts` with BetterAuth config
3. Create `app/api/auth/[...all]/route.ts`
4. Create `lib/auth-client.ts` with auth client
5. Create login/register pages
6. Create protected dashboard page
7. Create API client with JWT injection
8. Configure `.env.local` with matching `BETTER_AUTH_SECRET`

## Architecture Overview

### Component Diagram

```
┌─────────────────┐
│   Browser       │
└────────┬────────┘
         │
         │ 1. Navigate to /register
         ▼
┌─────────────────┐
│  Next.js App    │
│  (frontend/)    │
└────────┬────────┘
         │
         │ 2. Submit email + password
         ▼
┌─────────────────┐
│   BetterAuth    │
│  - Validates    │
│  - Hashes pwd   │
│  - Creates user │
└────────┬────────┘
         │
         │ 3. User created, redirect to /login
         ▼
┌─────────────────┐
│  Login Page     │
└────────┬────────┘
         │
         │ 4. Submit email + password
         ▼
┌─────────────────┐
│   BetterAuth    │
│  - Verifies     │
│  - Issues JWT   │
└────────┬────────┘
         │
         │ 5. Store JWT (cookie/localStorage)
         ▼
┌─────────────────┐
│  Client Storage │
└────────┬────────┘
         │
         │ 6. Navigate to /dashboard
         ▼
┌─────────────────┐
│  Dashboard Page │
│  - Calls API    │
└────────┬────────┘
         │
         │ 7. API request with JWT
         ▼
┌─────────────────┐
│   FastAPI       │
│  (backend/)     │
└────────┬────────┘
         │
         │ 8. JWTMiddleware intercepts
         ▼
┌─────────────────┐
│ JWTMiddleware   │
│  - Verifies JWT │
│  - Extracts ID  │
└────────┬────────┘
         │
         │ 9. Inject user_id into request
         ▼
┌─────────────────┐
│  Route Handler  │
│  - Scopes query │
│  - Returns data │
└────────┬────────┘
         │
         │ 10. JSON response
         ▼
┌─────────────────┐
│   Dashboard     │
│  - Displays UI  │
└─────────────────┘
```

### Data Flow

**Registration Flow**:
1. User → Frontend: Submit email + password
2. Frontend → BetterAuth: `signUp.email({ email, password })`
3. BetterAuth → Database: Insert user (email, password_hash)
4. Database → BetterAuth: Success
5. BetterAuth → Frontend: User created
6. Frontend → User: Redirect to /login

**Login Flow**:
1. User → Frontend: Submit email + password
2. Frontend → BetterAuth: `signIn.email({ email, password })`
3. BetterAuth → Database: Select user by email
4. Database → BetterAuth: User record
5. BetterAuth: Verify password hash
6. BetterAuth: Generate JWT (sign with BETTER_AUTH_SECRET)
7. BetterAuth → Frontend: JWT token
8. Frontend → Client Storage: Store JWT
9. Frontend → User: Redirect to /dashboard

**Protected API Request Flow**:
1. Frontend: Include JWT in Authorization header
2. Request → FastAPI: Arrives at middleware
3. JWTMiddleware: Extract token from header
4. JWTMiddleware: Verify signature with BETTER_AUTH_SECRET
5. JWTMiddleware: Extract user_id from sub claim
6. JWTMiddleware: Inject user_id into request.state
7. Request → Route Handler: Access user_id via dependency
8. Route Handler → Database: Query with user_id filter
9. Database → Route Handler: Scoped results
10. Route Handler → Frontend: JSON response

## Implementation Order

### Priority 1: Core Authentication (P1 User Stories)

1. **Backend JWT Infrastructure**
   - Create `core/security.py` with JWTManager
   - Create `core/middleware.py` with JWTMiddleware
   - Create `core/deps.py` with dependency injection
   - Update `main.py` to add middleware
   - Test with existing task endpoints

2. **Frontend BetterAuth Setup**
   - Install better-auth
   - Create `lib/auth.ts` with BetterAuth config
   - Create `app/api/auth/[...all]/route.ts`
   - Create `lib/auth-client.ts`
   - Test API route handler

3. **Registration Flow**
   - Create `app/register/page.tsx`
   - Implement form validation (email, password length)
   - Integrate BetterAuth signUp.email()
   - Add error handling
   - Test registration end-to-end

4. **Login Flow**
   - Create `app/login/page.tsx`
   - Integrate BetterAuth signIn.email()
   - Implement JWT token storage
   - Add error handling
   - Test login end-to-end

5. **Protected Route Access**
   - Create `app/dashboard/page.tsx` as protected page
   - Implement session check with authClient.getSession()
   - Redirect unauthenticated users to /login
   - Test protected access

6. **Logout Flow**
   - Implement logout button
   - Call authClient.signOut()
   - Clear token from storage
   - Test logout

### Priority 2: API Integration (P2 User Stories)

7. **Backend Task Endpoint Updates**
   - Update all task routes to inject `user_id`
   - Add user_id to task queries (CREATE, READ, UPDATE, DELETE)
   - Test data isolation (users can't access other users' tasks)

8. **Frontend API Client**
   - Create `lib/api/client.ts`
   - Implement JWT token injection
   - Create task service methods
   - Test authenticated API calls

9. **Database Migration**
   - Add `users` table (BetterAuth auto-creates)
   - Add `user_id` column to `tasks` table
   - Create foreign key constraint
   - Migrate existing data (assign to default user or delete)
   - Test data isolation

### Priority 3: Testing & Polish

10. **Integration Tests**
    - Test JWT verification with valid token
    - Test JWT verification with invalid token
    - Test JWT verification with expired token
    - Test protected endpoint access
    - Test data isolation

11. **E2E Tests**
    - Test registration flow
    - Test login flow
    - Test logout flow
    - Test protected page access
    - Test API calls with authentication

12. **Performance Testing**
    - Measure JWT verification latency (< 50ms target)
    - Test concurrent auth requests (100+ target)
    - Optimize if needed

## Testing Strategy

### Backend Tests (pytest)

**Unit Tests**:
```python
# tests/test_jwt.py
def test_verify_valid_token():
    """Test JWT verification with valid token."""
    token = create_test_token()
    payload = JWTManager.verify_token(token)
    assert payload["sub"] == "test-user-id"

def test_verify_invalid_token():
    """Test JWT verification with invalid token."""
    with pytest.raises(HTTPException) as exc:
        JWTManager.verify_token("invalid-token")
    assert exc.value.status_code == 401

def test_verify_expired_token():
    """Test JWT verification with expired token."""
    token = create_expired_token()
    with pytest.raises(HTTPException) as exc:
        JWTManager.verify_token(token)
    assert exc.value.status_code == 401
```

**Integration Tests**:
```python
# tests/test_tasks_auth.py
def test_create_task_with_valid_jwt(client, valid_token):
    """Test task creation with valid JWT."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == "test-user-id"

def test_create_task_without_jwt(client):
    """Test task creation without JWT returns 401."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"}
    )
    assert response.status_code == 401

def test_list_tasks_scoped_to_user(client, valid_token):
    """Test task listing is scoped to authenticated user."""
    # Create tasks for user 1
    client.post("/api/tasks", json={"title": "User 1 Task"},
                headers={"Authorization": f"Bearer {user1_token}"})
    # Create tasks for user 2
    client.post("/api/tasks", json={"title": "User 2 Task"},
                headers={"Authorization": f"Bearer {user2_token}"})

    # List tasks for user 1
    response = client.get("/api/tasks",
                         headers={"Authorization": f"Bearer {user1_token}"})
    tasks = response.json()

    assert len(tasks) == 1
    assert tasks[0]["title"] == "User 1 Task"
```

### Frontend Tests (React Testing Library)

**Component Tests**:
```typescript
// components/auth/__tests__/LoginForm.test.tsx
describe("LoginForm", () => {
  it("submits email and password", async () => {
    const signIn = jest.spyOn(authClient, "signIn.email");

    render(<LoginForm />);

    await userEvent.type(screen.getByLabelText(/email/i), "user@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "SecurePass123");
    await userEvent.click(screen.getByRole("button", { name: /login/i }));

    expect(signIn).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "SecurePass123",
    });
  });

  it("displays error on failed login", async () => {
    signIn.mockRejectedValue(new Error("Invalid credentials"));

    render(<LoginForm />);

    // ... submit form

    expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)

```typescript
// e2e/auth.spec.ts
test("user registration flow", async ({ page }) => {
  await page.goto("/register");

  await page.fill('input[name="email"]', "newuser@example.com");
  await page.fill('input[name="password"]', "SecurePass123");
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL("/login");
  await expect(page.locator("text=account created")).toBeVisible();
});

test("user login flow", async ({ page }) => {
  await page.goto("/login");

  await page.fill('input[name="email"]', "user@example.com");
  await page.fill('input[name="password"]', "SecurePass123");
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL("/dashboard");
  await expect(page.locator("text=Welcome")).toBeVisible();
});

test("protected page requires authentication", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page).toHaveURL("/login");
});
```

## Migration Strategy

### Existing Database

**Current State**:
- `tasks` table exists without `user_id` column
- No `users` table
- All tasks are orphaned (no owner)

**Migration Steps**:

1. **Add users table** (BetterAuth auto-creates on first run)
2. **Add user_id column to tasks**:
```sql
ALTER TABLE tasks
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

3. **Handle existing tasks** (choose one):
   - **Option A**: Assign all existing tasks to a default user
   - **Option B**: Delete all existing tasks (clean slate)
   - **Option C**: Require migration script to assign ownership

4. **Make user_id required**:
```sql
-- After assigning ownership to all tasks
ALTER TABLE tasks ALTER COLUMN user_id SET NOT NULL;
```

5. **Update all queries** to filter by `user_id`

### New Database

For new installations, BetterAuth creates the `users` table automatically. The `tasks` table should include `user_id` from the start:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

## Security Considerations

### JWT Security

**Secret Management**:
- Store `BETTER_AUTH_SECRET` in environment variables
- Minimum 32 characters recommended
- Must be identical on frontend and backend
- Never commit to version control

**Token Storage**:
- Preferred: httpOnly cookies (BetterAuth default)
- Alternative: localStorage (accessible to JavaScript)
- Never store in URL parameters

**Token Transmission**:
- Always use HTTPS in production
- Include in `Authorization: Bearer <token>` header
- Never include in request body or URL

### Password Security

**Hashing**:
- Bcrypt algorithm (handled by BetterAuth)
- Automatic salt generation
- Work factor: 10 rounds (BetterAuth default)

**Validation**:
- Minimum 8 characters (enforced by BetterAuth)
- No complexity requirements (per assumptions)
- Email format validation

### API Security

**Protection**:
- All `/api/*` routes require JWT (except `/api/auth/*`)
- Returns 401 for invalid/missing tokens
- Returns 403 for cross-user access attempts

**Data Isolation**:
- All queries scoped to `user_id` from JWT
- Ownership verification on all operations
- Prevents cross-user data access

### Error Handling

**Generic Messages**:
- Login failures: "Invalid credentials" (FR-015)
- No information leakage about email existence
- Detailed errors logged server-side only

## Performance Optimization

### Target Metrics

- Registration: < 30 seconds (target for < 60 second requirement)
- Login: < 5 seconds (target for < 15 second requirement)
- JWT verification: < 20ms (target for < 50ms requirement)
- Concurrent auth: 100+ requests (requirement)

### Optimization Strategies

**Backend**:
- JWT signature verification is fast (< 10ms typical)
- Database connection pooling (SQLModel)
- Async route handlers for concurrency
- Indexed queries on `user_id`

**Frontend**:
- React Server Components for initial page load
- Client components only for forms
- Optimistic UI updates
- Lazy loading of protected pages

### Caching

**Not Implemented**:
- No session caching (stateless JWT design)
- No token caching (client-side storage only)
- Future enhancement: Redis for rate limiting

## Rollout Plan

### Phase 1: Development
1. Implement backend JWT middleware
2. Implement frontend BetterAuth integration
3. Create login/register pages
4. Update task endpoints with user_id injection
5. Test locally with development database

### Phase 2: Testing
1. Write unit tests for JWT verification
2. Write integration tests for protected endpoints
3. Write E2E tests for auth flows
4. Performance test JWT verification
5. Load test concurrent auth requests

### Phase 3: Migration
1. Create migration script for existing database
2. Add `user_id` column to `tasks` table
3. Migrate existing data (assign or delete)
4. Deploy to staging environment
5. Test with staging database

### Phase 4: Production
1. Set production `BETTER_AUTH_SECRET` (secure random string)
2. Deploy backend with JWT middleware
3. Deploy frontend with BetterAuth
4. Run smoke tests (register, login, create task)
5. Monitor error rates and performance
6. Enable feature flag for all users

### Phase 5: Monitoring
1. Monitor JWT verification latency
2. Monitor authentication success/failure rates
3. Monitor API error rates (401, 403)
4. Set up alerts for anomalies
5. Collect user feedback on login experience

## Success Criteria Validation

### SC-001: Registration < 60 seconds
- **Test**: Measure time from landing on /register to successful account creation
- **Target**: < 30 seconds
- **Validation**: Manual testing + performance monitoring

### SC-002: Login < 15 seconds
- **Test**: Measure time from entering credentials to accessing /dashboard
- **Target**: < 5 seconds
- **Validation**: Manual testing + performance monitoring

### SC-003: 100% API endpoints require JWT
- **Test**: Try accessing /api/tasks without JWT token
- **Expected**: 401 Unauthorized
- **Validation**: Automated test in CI/CD

### SC-004: 100% JWT requests return scoped data
- **Test**: Create tasks as user 1, verify user 2 can't access them
- **Expected**: 403 Forbidden or 404 Not Found
- **Validation**: Integration test suite

### SC-006: JWT verification < 50ms
- **Test**: Measure JWT verification latency with load testing
- **Target**: < 20ms average
- **Validation**: Performance benchmark test

### SC-007: 100 concurrent auth requests
- **Test**: Send 100 concurrent login requests
- **Expected**: All requests succeed without errors
- **Validation**: Load test with Locust or k6

### SC-008: 0% plaintext passwords
- **Test**: Inspect database `users` table
- **Expected**: All passwords are bcrypt hashes
- **Validation**: Security audit

### SC-010: Prevent cross-user data access
- **Test**: Try to access another user's tasks with valid JWT
- **Expected**: 403 Forbidden or 404 Not Found
- **Validation**: Integration test suite + security penetration testing

## Risks & Mitigations

### Risk 1: Shared Secret Compromise
- **Impact**: Attacker can forge JWT tokens
- **Probability**: Low
- **Mitigation**: Secure secret storage, regular rotation, monitor for anomalies

### Risk 2: JWT Token Theft
- **Impact**: Attacker can access user's data until token expires
- **Probability**: Low (if using httpOnly cookies)
- **Mitigation**: Use httpOnly cookies, HTTPS only, short expiration (7 days)

### Risk 3: Database Breach
- **Impact**: User passwords exposed if not properly hashed
- **Probability**: Low
- **Mitigation**: Bcrypt hashing (already implemented by BetterAuth), slow hash function

### Risk 4: Performance Degradation
- **Impact**: Slow JWT verification affects all API requests
- **Probability**: Low
- **Mitigation**: JWT verification is fast (< 10ms), load testing, monitoring

### Risk 5: Migration Issues
- **Impact**: Existing tasks orphaned or lost
- **Probability**: Medium
- **Mitigation**: Backup database before migration, test migration script, choose ownership strategy

## Future Enhancements

### Out of Scope (Per Assumptions)
- Email verification
- Password reset
- Social login (OAuth)
- Two-factor authentication (2FA)
- Token refresh mechanism
- Rate limiting
- Session management (concurrent limits)
- Account recovery

### Phase 3+ Enhancements
1. Add email verification with confirmation links
2. Implement password reset via email
3. Add OAuth providers (Google, GitHub)
4. Implement rate limiting for login attempts
5. Add refresh token rotation
6. Support concurrent session management
7. Add account deletion and data export

## Summary

This implementation plan provides a complete, constitution-compliant approach to user authentication with BetterAuth (frontend) and JWT verification middleware (backend). The design is secure, performant, and scalable, meeting all functional requirements (FR-001 through FR-015) and success criteria (SC-001 through SC-010).

**Key Deliverables**:
- [x] Research findings ([research.md](./research.md))
- [x] Data model design ([data-model.md](./data-model.md))
- [x] API contracts ([contracts/](./contracts/))
- [x] Quickstart guide ([quickstart.md](./quickstart.md))

**Next Phase**: `/sp.tasks` to generate actionable implementation tasks.
