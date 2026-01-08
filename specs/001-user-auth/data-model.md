# Data Model: User Authentication

**Feature**: 001-user-auth
**Date**: 2026-01-08
**Phase**: Phase 1 - Data Model Design

## Overview

This document defines the data model for user authentication, including entities, relationships, validation rules, and state transitions. The model integrates with the existing task management system.

## Entities

### User Account

**Table Name**: `users`
**Managed By**: BetterAuth (automatically created)
**Primary Key**: `id` (UUID)

**Attributes**:

| Field | Type | Constraints | Description | Source |
|-------|------|-------------|-------------|--------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique user identifier | BetterAuth auto-generated |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email address (case-insensitive) | FR-001, FR-004 |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hash of password | FR-014 |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation timestamp | Entity definition |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp | Entity definition |

**Validation Rules**:
- Email format: Must contain `@` symbol and valid domain structure (FR-002)
- Password length: Minimum 8 characters (FR-003)
- Email uniqueness: Case-insensitive comparison (FR-004)
- Password storage: Hashed with bcrypt, never plaintext (FR-014)

**Indexes**:
- `idx_users_email` on `email` (for fast lookups during login)

**Relationships**:
- One-to-Many: User → Tasks (via `tasks.user_id` foreign key)

### Authentication Token (JWT)

**Type**: Stateless token (not stored in database)
**Managed By**: BetterAuth
**Format**: JSON Web Token (JWT)

**Token Structure**:

```json
{
  "sub": "user-uuid-here",     // Subject (user_id)
  "iat": 1704700800,            // Issued at (Unix timestamp)
  "exp": 1705305600,            // Expiration (Unix timestamp, 7 days)
  "iss": "better-auth",         // Issuer
  "aud": "api"                  // Audience
}
```

**Claims**:

| Claim | Type | Description | Source |
|-------|------|-------------|--------|
| `sub` | String (UUID) | User ID from database | FR-009 |
| `iat` | Integer | Token issuance timestamp | JWT standard |
| `exp` | Integer | Token expiration timestamp | JWT standard (7 days) |
| `iss` | String | Token issuer | BetterAuth |
| `aud` | String | Token audience | API identifier |

**Validation Rules**:
- Signature verification: HS256 algorithm with `BETTER_AUTH_SECRET` (FR-008)
- Expiration check: Reject expired tokens (FR-010)
- Claim validation: Must contain `sub` (user_id) (FR-009)

**Storage**: Not in database (stateless)
- Client-side: httpOnly cookie or localStorage
- Server-side: Verified per request, not persisted

### Session

**Type**: Logical session (tracked via JWT token)
**Managed By**: BetterAuth + JWT middleware
**Storage**: Client-side only (no server-side session store)

**Session State**:

| State | Description | Transition Trigger |
|-------|-------------|-------------------|
| **Anonymous** | User not authenticated | Initial state, logout |
| **Authenticated** | User logged in with valid JWT | Successful login |
| **Expired** | JWT token expired | Token expiration (7 days) |

**State Transitions**:

```
[Anonymous] --(successful login)--> [Authenticated]
[Authenticated] --(logout)--> [Anonymous]
[Authenticated] --(token expires)--> [Expired] --(login)--> [Authenticated]
```

**Session Lifecycle**:

1. **Creation**: User logs in → BetterAuth issues JWT → Client stores token
2. **Active**: Client includes token in API requests → Middleware validates → Access granted
3. **Expiration**: Token expires after 7 days → Client must re-login
4. **Termination**: User logs out → Client clears token → Session ends

**Note**: No server-side session storage required (stateless JWT design)

### Credentials

**Type**: Transient data (not persisted)
**Managed By**: BetterAuth
**Storage**: Never stored (only hashed password in database)

**Credentials Structure**:

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `email` | String | Valid email format | User identifier |
| `password` | String | Min 8 characters | User password (plaintext during submission only) |

**Security Rules**:
- Password never stored in plaintext (FR-014)
- Password hashed with bcrypt before database storage (FR-014)
- Email case-insensitive for uniqueness checks (FR-004)
- Generic error messages (no information leakage) (FR-015)

## Entity Relationships

### Relationship Diagram

```
┌─────────────┐
│    User     │
│  (users)    │
└─────────────┘
       │
       │ 1 user
       │
       │ has many tasks
       │
       ▼
┌─────────────┐
│    Task     │
│  (tasks)    │
└─────────────┘
```

### Relationship Details

**User → Tasks (One-to-Many)**

- **Foreign Key**: `tasks.user_id` references `users.id`
- **Cardinality**: One user can have many tasks
- **Ownership**: All tasks must have a valid `user_id`
- **Isolation**: Users can only access their own tasks (Constitution Principle IX)
- **Cascading**: When user is deleted, associated tasks should be deleted (CASCADE)

**Query Pattern**:
```sql
-- Get all tasks for a user
SELECT * FROM tasks WHERE user_id = $1;

-- Create task with user ownership
INSERT INTO tasks (user_id, title, description) VALUES ($1, $2, $3);

-- Verify task ownership
SELECT * FROM tasks WHERE id = $1 AND user_id = $2;
```

## Validation Rules Summary

### Email Validation (FR-002)

**Format Rules**:
- Must contain `@` symbol
- Must have valid domain structure (e.g., `user@domain.com`)
- Case-insensitive uniqueness check (FR-004)

**Validation Logic**:
```typescript
// Frontend validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
  return { error: "Invalid email format" };
}

// Backend validation (BetterAuth)
// Ensures uniqueness with case-insensitive comparison
```

### Password Validation (FR-003)

**Minimum Requirements**:
- Minimum 8 characters (FR-003)
- No maximum limit (but BetterAuth defaults to 128)
- No complexity requirements (per assumptions)

**Validation Logic**:
```typescript
// Frontend validation
if (password.length < 8) {
  return { error: "Password must be at least 8 characters" };
}

// Backend hashing (BetterAuth)
const hashedPassword = await bcrypt.hash(password, 10);
```

### JWT Validation (FR-008, FR-009, FR-010)

**Validation Steps**:
1. Extract token from `Authorization: Bearer <token>` header
2. Verify signature with `BETTER_AUTH_SECRET` (FR-008)
3. Check expiration (reject if `exp` < current time) (FR-010)
4. Extract `sub` claim (user_id) (FR-009)
5. Return 401 Unauthorized if any step fails (FR-010)

**Validation Logic**:
```python
# Backend validation (FastAPI middleware)
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## State Transitions

### User Account States

| State | Description | Valid Transitions |
|-------|-------------|-------------------|
| **Does Not Exist** | User has never registered | → Registered (after sign up) |
| **Registered** | User account exists | → Deleted (if account deletion implemented) |
| **Deleted** | User account deleted | → Registered (re-sign up) |

### Authentication States

| State | Description | Valid Transitions | Trigger |
|-------|-------------|-------------------|---------|
| **Logged Out** | No active session | → Logged In | Successful login |
| **Logged In** | Active JWT token | → Logged Out | User logout |
| **Token Expired** | JWT past expiration | → Logged In | Re-login |

**State Machine**:

```
                    [Login Success]
[Logged Out] ──────────────────────────> [Logged In]
    ▲                                        │
    │                                        │
    │                                        │ [Token Expires]
    │                                        │
    │                                        ▼
    └────────────────────────────────── [Token Expired]
                    [Re-login]
```

## Data Access Patterns

### User Creation (Registration)

**Flow**:
1. User submits email and password
2. Frontend validates email format and password length
3. BetterAuth checks email uniqueness (case-insensitive)
4. BetterAuth hashes password with bcrypt
5. BetterAuth inserts user into `users` table
6. Returns success (no automatic login per design)

**SQL**:
```sql
INSERT INTO users (email, password_hash, created_at, updated_at)
VALUES ($1, $2, NOW(), NOW());
```

### User Authentication (Login)

**Flow**:
1. User submits email and password
2. BetterAuth finds user by email (case-insensitive)
3. BetterAuth compares password hash with bcrypt
4. If valid, BetterAuth issues JWT with user_id in `sub` claim
5. Client stores JWT token

**SQL**:
```sql
-- Find user by email
SELECT * FROM users WHERE email = LOWER($1);

-- Verify password (bcrypt comparison in application)
-- Issue JWT (no database operation)
```

### User Authorization (API Request)

**Flow**:
1. Client includes JWT in `Authorization: Bearer <token>` header
2. FastAPI middleware intercepts request
3. Middleware verifies JWT signature and extracts `user_id`
4. Middleware injects `user_id` into `request.state`
5. Route handler uses `user_id` to scope queries

**SQL**:
```sql
-- All queries scoped to authenticated user
SELECT * FROM tasks WHERE user_id = $1;  -- $1 is user_id from JWT
```

## Security Considerations

### Password Security

- **Hashing**: Bcrypt with automatic salt generation
- **Storage**: Only hash stored, never plaintext
- **Validation**: Minimum 8 characters, no complexity rules
- **Comparison**: Constant-time comparison to prevent timing attacks

### JWT Security

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret**: Shared `BETTER_AUTH_SECRET` from environment
- **Expiration**: 7 days (604800 seconds)
- **Storage**: Client-side only (httpOnly cookie preferred)
- **Transmission**: Always via HTTPS (Authorization header)

### Data Isolation

- **Query Scoping**: All database queries filtered by `user_id`
- **Ownership Verification**: Every operation checks `user_id` matches
- **Cross-User Access**: Returns 403 or 404 (never success)
- **JWT Binding**: User ID from JWT used for all data access

## Migration Strategy

### Existing Database

The task management system already has a `tasks` table. Adding authentication requires:

1. **Add `users` table** (BetterAuth auto-creates this)
2. **Add `user_id` column to `tasks` table** (foreign key)
3. **Migrate existing tasks** (assign to a default user or require re-login)
4. **Update all queries** to filter by `user_id`

**Migration SQL**:
```sql
-- Add users table (BetterAuth handles this)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Add user_id foreign key to tasks
ALTER TABLE tasks
ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;

-- Create index for faster queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Migrate existing tasks (optional: assign to default user or delete)
-- Option 1: Assign to a default user
UPDATE tasks
SET user_id = (SELECT id FROM users WHERE email = 'default@example.com')
WHERE user_id IS NULL;

-- Option 2: Require all users to re-login (tasks deleted)
-- DELETE FROM tasks WHERE user_id IS NULL;

-- Make user_id required after migration
ALTER TABLE tasks ALTER COLUMN user_id SET NOT NULL;
```

### New Database

For new installations, BetterAuth will create the `users` table automatically. The `tasks` table should include `user_id` from the start.

**Schema**:
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

## Summary

The data model for user authentication consists of:

1. **User Account**: Persistent entity with email, hashed password, timestamps
2. **Authentication Token**: Stateless JWT with user_id in `sub` claim
3. **Session**: Logical session tracked via JWT (no server-side storage)
4. **Credentials**: Transient data (never stored in plaintext)

All authentication operations are secured with bcrypt password hashing, JWT signature verification, and query scoping to the authenticated user. The model integrates seamlessly with the existing task management system via a one-to-many relationship between users and tasks.
