# Implementation Plan: User Authentication

**Branch**: `001-user-auth` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-user-auth/spec.md`

## Summary

Implement a complete authentication system where FastAPI backend handles ALL authentication logic (validation, JWT generation/verification, password hashing, database management) and Next.js frontend serves as a pure UI client that renders forms, stores tokens, and sends API requests. The system provides user registration, login, logout, session verification, and JWT-protected API endpoints with secure password storage and comprehensive error handling.

## Technical Context

**Backend (FastAPI)**:
- **Language/Version**: Python 3.13+
- **Primary Dependencies**: FastAPI, SQLModel, Pydantic, python-jose (JWT), passlib (password hashing), bcrypt
- **Storage**: Neon Serverless PostgreSQL
- **Testing**: pytest for unit/integration tests
- **Target Platform**: Linux server (containerized)
- **Performance Goals**: <50ms average JWT verification, handle 100 concurrent auth requests
- **Constraints**: Stateless JWT verification, no session storage on backend
- **Scale/Scope**: Support 10k+ users, 4 auth endpoints, JWT middleware for all protected routes

**Frontend (Next.js)**:
- **Language/Version**: TypeScript 5+ with Next.js 16 and React 19
- **Primary Dependencies**: Next.js (App Router), React 19, Tailwind CSS 4
- **Storage**: No direct database access - all data via FastAPI backend
- **Testing**: React Testing Library for components, Playwright for E2E
- **Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge)
- **Performance Goals**: Page loads <2s, form submissions <1s
- **Constraints**: Must not perform authentication logic - only UI and API calls
- **Scale/Scope**: 3 main pages (login, register, protected), 5-10 React components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Evaluation

**Backend (FastAPI)**:
- ✅ **Principle I (Persistent Storage)**: Using Neon PostgreSQL with SQLModel for all user data
- ✅ **Principle II (RESTful API Excellence)**: All auth endpoints follow REST patterns (/api/auth/*), JSON responses, proper status codes
- ✅ **Principle VII (Authentication & JWT)**: Backend generates and signs JWTs, verifies signatures, extracts user_id
- ✅ **Principle IX (Data Ownership & Isolation)**: All queries scoped to authenticated user's user_id from JWT
- ✅ **Principle X (API Response Consistency)**: Standardized JSON responses, consistent error handling
- ✅ **Technology Stack**: Python 3.13+, FastAPI, SQLModel as per constitution

**Frontend (Next.js)**:
- ✅ **Principle III (Responsive Web UI)**: Next.js 16 App Router, mobile-first responsive design
- ✅ **Principle VIII (Frontend Architecture)**: Server components by default, client components for forms, pure frontend (no auth logic)
- ✅ **Principle VI (Monorepo Structure)**: Frontend code in `frontend/` directory as per constitution

**Gate Status**: ✅ **PASSED** - All constitution requirements satisfied

### Post-Design Re-evaluation

(After Phase 1 design completion - will verify implementation aligns with updated architecture)

## Project Structure

### Documentation (this feature)

```text
specs/001-user-auth/
├── spec.md              # Feature specification (updated with architecture clarification)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Data structures and validation rules
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml     # OpenAPI specification for auth endpoints
└── tasks.md             # Phase 2: Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── models/
│   ├── __init__.py
│   └── user.py              # User model (SQLModel with email, hashed_password)
├── api/
│   ├── __init__.py
│   ├── deps.py              # JWT dependency injection
│   └── auth.py              # Auth endpoints (sign-up, sign-in, sign-out, session)
├── core/
│   ├── __init__.py
│   ├── config.py            # Settings (JWT_SECRET, DATABASE_URL)
│   ├── security.py          # Password hashing, JWT generation/verification
│   └── database.py          # Database session management
├── tests/
│   ├── test_auth_api.py     # Auth endpoint tests
│   ├── test_security.py     # Password hashing, JWT tests
│   └── test_integration.py  # Full auth flow integration tests
└── main.py                  # FastAPI app with CORS middleware

frontend/
├── src/
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx      # Login page (client component)
│   │   ├── register/
│   │   │   └── page.tsx      # Registration page (client component)
│   │   ├── dashboard/
│   │   │   └── page.tsx      # Protected page example
│   │   └── layout.tsx        # Root layout with auth provider
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx       # Login form component
│   │   │   └── RegisterForm.tsx    # Registration form component
│   │   └── ui/                     # Reusable UI components
│   ├── lib/
│   │   ├── api-client.ts     # HTTP client with JWT handling
│   │   └── auth.ts           # Auth utilities (token storage, session check)
│   └── types/
│       └── auth.ts           # TypeScript types for auth
└── tests/
    ├── login.test.tsx
    └── register.test.tsx
```

**Structure Decision**: Full monorepo with backend/ and frontend/ directories (Option 3 from template). Backend handles all authentication logic, frontend is pure UI client. Complies with Principle VI (Monorepo Structure Standard).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None | Architecture cleanly separates concerns with no violations |

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Password Hashing Algorithm**
   - Decision: bcrypt vs argon2 for password hashing
   - Considerations: Security, computational cost, library support
   - Need to select algorithm for production use

2. **JWT Library Selection**
   - Decision: python-jose vs PyJWT for JWT generation/verification
   - Considerations: Performance, API design, maintenance status
   - Need to select JWT library for FastAPI backend

3. **Frontend Token Storage**
   - Decision: httpOnly cookies vs localStorage vs sessionStorage
   - Considerations: XSS protection, persistence, ease of implementation
   - Need to select secure token storage mechanism

4. **API Client Architecture**
   - Decision: fetch API vs axios vs custom wrapper
   - Considerations: Bundle size, interceptors, error handling
   - Need to design API client for JWT injection

5. **Form Validation Approach**
   - Decision: Client-side validation strategy (controlled components vs form library)
   - Considerations: User experience, bundle size, developer experience
   - Need to select validation approach for login/register forms

6. **Database Migration Strategy**
   - Decision: How to handle User table creation and migrations
   - Considerations: Alembic vs SQLModel automatic migrations
   - Need to select migration tool for user schema

7. **CORS Configuration**
   - Decision: CORS policy for frontend-backend communication
   - Considerations: Security, development vs production
   - Need to configure CORS headers properly

8. **Error Handling Pattern**
   - Decision: Global error handling vs per-endpoint error handling
   - Considerations: Consistency, user experience, security (no info leakage)
   - Need to design error response format

### Research Output

Will be documented in `research.md` with decisions, rationale, and alternatives considered for each unknown above.

---

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

**User Entity** (backend SQLModel):

```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**JWT Token Structure**:

```python
{
    "sub": str(user_id),  # Subject (user ID)
    "exp": int(expires_at),  # Expiration timestamp
    "iat": int(issued_at)  # Issued at timestamp
}
```

**Request/Response Schemas**:

- `SignUpRequest`: { email: str, password: str }
- `SignInRequest`: { email: str, password: str }
- `SignUpResponse`: { success: bool, message: str, user: UserResponse }
- `SignInResponse`: { success: bool, token: str, user: UserResponse, expires_at: str }
- `SessionResponse`: { authenticated: bool, user: UserResponse, expires_at: str }
- `ErrorResponse`: { detail: str }

### API Contracts (`contracts/openapi.yaml`)

**Endpoints**:

1. `POST /api/auth/sign-up` - Register new user
2. `POST /api/auth/sign-in` - Login and receive JWT
3. `POST /api/auth/sign-out` - Logout (clear session)
4. `GET /api/auth/session` - Verify current session

**Authentication Middleware**:

All protected endpoints (except auth endpoints) require:
- Header: `Authorization: Bearer <token>`
- JWT verification middleware extracts `user_id`
- Returns 401 if token invalid/expired/missing

**Security Specifications**:

- Passwords hashed with bcrypt (cost factor 12)
- JWT signed with HS256 algorithm
- JWT expires after 7 days
- CORS allows requests from frontend origin only
- Rate limiting on auth endpoints (future enhancement)

### Component Architecture

**Frontend Components**:

1. `login/page.tsx` - Server component that renders LoginForm
2. `register/page.tsx` - Server component that renders RegisterForm
3. `LoginForm.tsx` - Client component with email/password form
4. `RegisterForm.tsx` - Client component with email/password/password-confirmation form
5. `ProtectedRoute.tsx` - Wrapper component that checks auth and redirects
6. `AuthProvider.tsx` - Context provider for auth state (optional)

**Backend Modules**:

1. `models/user.py` - User SQLModel definition
2. `api/deps.py` - JWT authentication dependency for FastAPI routes
3. `api/auth.py` - Auth endpoint handlers
4. `core/security.py` - Password hashing and JWT functions
5. `core/config.py` - Environment variables and settings

### Authentication Flow

**Registration Flow**:
```
User → /register → RegisterForm.tsx
  ↓ (submit email/password)
POST /api/auth/sign-up → FastAPI backend
  ↓ (validate email format, password length)
  ↓ (hash password with bcrypt)
  ↓ (store in PostgreSQL)
Return user data → Frontend
  ↓ (display success message)
Redirect to /login → LoginForm.tsx
```

**Login Flow**:
```
User → /login → LoginForm.tsx
  ↓ (submit email/password)
POST /api/auth/sign-in → FastAPI backend
  ↓ (verify email exists)
  ↓ (verify password hash matches)
  ↓ (generate and sign JWT)
Return { token, user, expires_at } → Frontend
  ↓ (store token in localStorage/cookie)
Redirect to /dashboard → Protected page
```

**Protected API Request Flow**:
```
Component → API call with Authorization header
  ↓ (Bearer <token>)
FastAPI JWT middleware
  ↓ (verify signature)
  ↓ (extract user_id)
Pass user_id to route handler → Process request scoped to user
```

### Quickstart Guide (`quickstart.md`)

Will include:
1. Backend setup (uv sync, .env configuration, database initialization)
2. Frontend setup (pnpm install, .env.local configuration)
3. Running both services locally
4. Testing registration flow
5. Testing login flow
6. Testing protected routes
7. Troubleshooting common issues

---

## Agent Context Update

After Phase 1 completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update `.claude/commands/` with backend and frontend-specific context.

---

## Phase 2: Implementation Tasks

(To be generated by `/sp.tasks` command based on this plan)

Will include task breakdown for:
1. Backend setup (models, security utilities, config)
2. Backend auth endpoints implementation
3. Backend JWT middleware
4. Backend testing (unit, integration)
5. Frontend API client
6. Frontend auth pages
7. Frontend auth utilities
8. Frontend testing
9. End-to-end testing
10. Documentation and code review
