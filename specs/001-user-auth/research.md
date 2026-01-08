# Research: User Authentication Implementation

**Feature**: 001-user-auth
**Date**: 2026-01-08
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings for implementing user authentication using BetterAuth on the frontend (Next.js 16) and JWT verification middleware on the backend (FastAPI).

## Technology Choices

### Frontend Authentication: BetterAuth

**Decision**: Use BetterAuth for Next.js 16 App Router with email/password authentication

**Rationale**:
- Native Next.js 16 App Router support with React Server Components
- Built-in JWT plugin for custom backend integration
- Email/password authentication with secure password hashing
- Handles session management and token storage
- Provides TypeScript types and excellent developer experience
- No social login complexity (scope: email/password only)

**Alternatives Considered**:
- **NextAuth.js (Auth.js)**: More mature but heavier, complex configuration for custom backends
- **Supabase Auth**: Full backend service, overkill for our needs
- **Clerk**: SaaS solution, adds external dependency and cost

**Configuration**:
```typescript
// lib/auth.ts
export const auth = betterAuth({
  database: createPool({ connectionString: process.env.DATABASE_URL }),
  emailAndPassword: {
    enabled: true,
    disableSignUp: false,
    requireEmailVerification: false, // Out of scope per assumptions
    minPasswordLength: 8,
    maxPasswordLength: 128,
    autoSignIn: false, // Redirect to login after registration
  },
  plugins: [
    jwt({
      expiresIn: "7d", // Token expiration per assumptions
      secret: process.env.BETTER_AUTH_SECRET,
    }),
  ],
});
```

**JWT Token Structure**:
- Claims: `sub` (user_id), `iat` (issued at), `exp` (expiration)
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: Shared `BETTER_AUTH_SECRET` environment variable

### Backend JWT Verification: FastAPI Middleware

**Decision**: Use FastAPI middleware with python-jose for JWT verification

**Rationale**:
- FastAPI native middleware support
- python-jose provides comprehensive JWT handling
- Dependency injection pattern for flexible route protection
- Type-safe with Pydantic integration
- Handles signature verification, expiration checking, and claim extraction

**Alternatives Considered**:
- **Custom middleware without dependencies**: More code, maintenance burden
- **Authlib**: Good but heavier dependency
- **Passlib-only**: Doesn't handle JWT verification

**Implementation Pattern**:
```python
# core/security.py
class JWTManager:
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        return payload

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """Extract user_id from JWT token claims."""
        payload = JWTManager.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
```

**Middleware Strategy**:
- Global JWT middleware for all `/api/*` routes
- Excludes public endpoints (health check, docs, `/api/auth/*`)
- Injects `user_id` into `request.state` for route handlers
- Returns 401 Unauthorized for invalid/missing tokens

**Dependency Injection**:
```python
# core/deps.py
async def get_current_user_id(request: Request) -> str:
    """Get current user ID from JWT token."""
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user_id

# Type alias for dependency
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]

# Usage in routes
@router.get("/api/tasks")
def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,  # Injected from JWT
):
    ...
```

## Integration Architecture

### Authentication Flow

**Registration Flow**:
1. User navigates to `/register` page
2. Fills email and password form
3. Frontend calls `authClient.signUp.email({ email, password })`
4. BetterAuth creates user in database, hashes password with bcrypt
5. Returns success, redirects to `/login`
6. User enters credentials
7. Frontend calls `authClient.signIn.email({ email, password })`
8. BetterAuth verifies credentials, issues JWT token
9. Token stored in httpOnly cookie (or localStorage)
10. User redirected to main application page

**Login Flow**:
1. User navigates to `/login` page
2. Fills email and password form
3. Frontend calls `authClient.signIn.email({ email, password })`
4. BetterAuth verifies credentials, issues JWT token
5. Token stored and sent with subsequent API requests
6. User redirected to main application page

**Protected API Request Flow**:
1. Frontend makes API call with JWT token
2. JWT middleware intercepts request
3. Extracts `Authorization: Bearer <token>` header
4. Verifies signature using `BETTER_AUTH_SECRET`
5. Extracts `user_id` from `sub` claim
6. Injects `user_id` into `request.state`
7. Route handler accesses `user_id` via dependency injection
8. Returns 401 if any step fails

**Logout Flow**:
1. User clicks logout button
2. Frontend calls `authClient.signOut()`
3. Token cleared from storage
4. User redirected to `/login`

### Frontend-Backend Communication

**API Client Pattern**:
```typescript
// lib/api/client.ts
export const apiClient = async ({ url, method, data, requiresAuth = true }) => {
  const headers = { "Content-Type": "application/json" };

  if (requiresAuth) {
    const { data: tokenData } = await authClient.token();
    headers["Authorization"] = `Bearer ${tokenData.token}`;
  }

  const response = await fetch(url, { method, headers, body: JSON.stringify(data) });
  return response.json();
};
```

**Token Retrieval**:
- BetterAuth provides `authClient.token()` method
- Returns current JWT token or error
- Client includes token in `Authorization: Bearer <token>` header

## Database Schema

### User Account Table

**Table**: `users` (managed by BetterAuth)

**Schema**:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Fields**:
- `id`: UUID primary key (BetterAuth default)
- `email`: Unique email address (case-insensitive per FR-004)
- `password_hash`: Bcrypt hash of password
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Constraints**:
- `email` unique constraint (prevents duplicates per FR-004)
- `password` minimum 8 characters (enforced by BetterAuth per FR-003)

**Relationships**:
- One user → Many tasks (via `tasks.user_id` foreign key)

## Security Considerations

### JWT Security

**Secret Management**:
- Shared `BETTER_AUTH_SECRET` between frontend and backend
- Stored in environment variables (never in code)
- Minimum 32 characters recommended
- Must be identical on both services

**Token Storage**:
- httpOnly cookies (preferred, prevents XSS)
- localStorage (fallback, accessible to JavaScript)
- Token sent in `Authorization: Bearer <token>` header

**Token Expiration**:
- 7 days per assumptions
- No refresh token implementation (out of scope)
- User must re-login after expiration

### Password Security

**Hashing**:
- Bcrypt algorithm (handled by BetterAuth)
- Automatic salt generation
- Irreversible one-way hash

**Validation**:
- Minimum 8 characters (FR-003)
- Email format validation (FR-002)
- No complexity requirements (per assumptions)

### API Security

**Protection**:
- All `/api/*` routes require JWT (FR-007)
- Public endpoints: `/`, `/health`, `/docs`, `/api/auth/*`
- Returns 401 Unauthorized for invalid tokens (FR-010)

**User Isolation**:
- All queries scoped to `user_id` from JWT (Constitution Principle IX)
- Users cannot access other users' data (FR-009, FR-010)
- 403 Forbidden or 404 Not Found for cross-user access attempts

### Error Handling

**Generic Error Messages**:
- Login failures: "Invalid credentials" (FR-015)
- Registration failures: "Email already registered"
- No information leakage about email existence

## Performance Targets

### Success Criteria Mapping

- **SC-001**: Registration < 60 seconds → Target: < 30 seconds
- **SC-002**: Login < 15 seconds → Target: < 5 seconds
- **SC-006**: JWT verification < 50ms → Target: < 20ms
- **SC-007**: 100 concurrent auth requests → Load test required

### Optimization Strategies

**Frontend**:
- React Server Components for initial page load
- Client components only for forms (login, register)
- Optimistic UI updates for better perceived performance

**Backend**:
- JWT signature verification is fast (< 10ms typical)
- Database connection pooling (SQLModel)
- Async route handlers for concurrent requests

## Known Limitations

### Out of Scope (Per Assumptions)

1. **Email Verification**: Not implementing email confirmation flow
2. **Password Reset**: No reset password functionality
3. **Social Login**: OAuth providers not included
4. **Two-Factor Authentication**: 2FA not implemented
5. **Token Refresh**: No refresh token mechanism
6. **Rate Limiting**: No attempt limiting for login
7. **Session Management**: No concurrent session limits
8. **Account Recovery**: No recovery flow

### Future Enhancements

1. Add email verification with confirmation links
2. Implement password reset via email
3. Add OAuth providers (Google, GitHub)
4. Implement rate limiting for login attempts
5. Add refresh token rotation
6. Support concurrent session management
7. Add account deletion and data export

## Implementation Phases

**Phase 1**: Core authentication (current scope)
- User registration with email/password
- User login with JWT issuance
- JWT verification middleware
- Protected route access control

**Phase 2**: Enhanced security (future)
- Email verification
- Password reset
- Rate limiting
- Session management

**Phase 3**: Advanced features (future)
- Social login (OAuth)
- Two-factor authentication
- Account recovery
- Audit logging

## Conclusion

BetterAuth with FastAPI JWT middleware provides a robust, secure authentication system that meets all functional requirements and success criteria. The implementation is straightforward, well-documented, and follows best practices for JWT-based authentication in full-stack applications.

**Key Decisions**:
- BetterAuth for frontend (Next.js native, excellent DX)
- HS256 algorithm with shared secret (simple, secure)
- Global JWT middleware with selective protection (flexible)
- Dependency injection for user_id (type-safe, clean)
- 7-day token expiration (per assumptions, no refresh needed)
