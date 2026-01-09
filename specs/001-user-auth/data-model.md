# Data Model: User Authentication

**Feature**: 001-user-auth  
**Date**: 2026-01-09  
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data structures, database schema, and validation rules for the authentication system. All data is persisted in PostgreSQL via SQLModel on the FastAPI backend.

---

## Backend Data Models

### User Entity (SQLModel)

**File**: `backend/models/user.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class UserBase(SQLModel):
    """Base User model with common fields"""
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(UserBase, table=True):
    """Full User model with database table"""
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=255)  # bcrypt hash, not plaintext
    
    # Relationships (will be added when Task model exists)
    # tasks: list["Task"] = Relationship(back_populates="owner")

class UserCreate(SQLModel):
    """Schema for user registration"""
    email: str
    password: str  # Plaintext password, will be hashed before storage

class UserRead(SQLModel):
    """Schema for returning user data (excludes password)"""
    id: uuid.UUID
    email: str
    created_at: datetime
    updated_at: datetime

class UserLogin(SQLModel):
    """Schema for user login"""
    email: str
    password: str
```

**Database Schema** (PostgreSQL):

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Validation Rules**:
- `email`: Required, unique, valid email format, max 255 characters
- `password`: Required, min 8 characters (validated before hashing)
- `id`: Auto-generated UUID
- `created_at`, `updated_at`: Auto-generated timestamps

---

## JWT Token Structure

### JWT Payload

```python
{
    "sub": str(user_id),      # Subject: User's UUID as string
    "exp": int(timestamp),    # Expiration: Unix timestamp (7 days from issuance)
    "iat": int(timestamp),    # Issued At: Unix timestamp when token was created
}
```

**Token Properties**:
- **Algorithm**: HS256 (HMAC-SHA256)
- **Secret**: `JWT_SECRET` environment variable (must be kept secure)
- **Expiration**: 7 days (604800 seconds)
- **Issuer**: FastAPI backend (implicit)
- **Audience**: Frontend application (optional, can add for extra security)

**Example Token**:

```python
import jwt
from datetime import datetime, timedelta

payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
    "iat": int(datetime.utcnow().timestamp())
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
# Example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MjQxOTY0MDAsImlhdCI6MTcyMzU5MTYwMH0.signature"
```

---

## API Request/Response Schemas

### Registration (Sign Up)

**Request**: `POST /api/auth/sign-up`

```python
class SignUpRequest(SQLModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
```

**Response**: Success (200 OK)

```python
class SignUpResponse(SQLModel):
    success: bool
    message: str  # e.g., "Account created successfully"
    user: UserRead
```

**Error Responses**:
- 400 Bad Request: Invalid email format or password too short
- 409 Conflict: Email already registered
- 500 Internal Server Error: Database error

---

### Login (Sign In)

**Request**: `POST /api/auth/sign-in`

```python
class SignInRequest(SQLModel):
    email: str
    password: str
```

**Response**: Success (200 OK)

```python
class SignInResponse(SQLModel):
    success: bool
    token: str  # JWT access token
    user: UserRead
    expires_at: str  # ISO 8601 datetime (e.g., "2026-01-16T12:00:00Z")
```

**Error Responses**:
- 401 Unauthorized: Invalid credentials (generic message, doesn't reveal if email exists)
- 500 Internal Server Error: Database or JWT generation error

---

### Session Verification

**Request**: `GET /api/auth/session`

Headers:
```
Authorization: Bearer <token>
```

**Response**: Success (200 OK)

```python
class SessionResponse(SQLModel):
    authenticated: bool
    user: Optional[UserRead]  # None if not authenticated
    expires_at: Optional[str]  # ISO 8601 datetime
```

**Error Responses**:
- 401 Unauthorized: Invalid, expired, or missing token

---

### Logout (Sign Out)

**Request**: `POST /api/auth/sign-out`

Headers:
```
Authorization: Bearer <token>
```

**Response**: Success (200 OK)

```python
class SignOutResponse(SQLModel):
    success: bool
    message: str  # e.g., "Logged out successfully"
```

**Note**: JWT tokens are stateless, so logout is client-side (clear cookie). This endpoint exists for consistency and potential future session blacklisting.

---

## Frontend TypeScript Types

**File**: `frontend/src/types/auth.ts`

```typescript
// User types
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

// Auth requests
export interface SignUpRequest {
  email: string;
  password: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

// Auth responses
export interface SignUpResponse {
  success: boolean;
  message: string;
  user: User;
}

export interface SignInResponse {
  success: boolean;
  token: string;
  user: User;
  expires_at: string;
}

export interface SessionResponse {
  authenticated: boolean;
  user: User | null;
  expires_at: string | null;
}

export interface SignOutResponse {
  success: boolean;
  message: string;
}

// Error types
export interface ApiError {
  detail: string;
}

// Auth state (for React Context or state management)
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

---

## Data Flow Examples

### User Registration Flow

```
1. Frontend: User fills register form
   { email: "user@example.com", password: "password123" }

2. Frontend: POST /api/auth/sign-up
   Body: { email: "user@example.com", password: "password123" }

3. Backend: Validate email format (contains @, valid domain)
   ✅ Valid

4. Backend: Validate password length
   ✅ 12 characters >= 8

5. Backend: Check if email already exists
   SELECT * FROM users WHERE email = 'user@example.com'
   ✅ Not found

6. Backend: Hash password with bcrypt
   hashed_password = bcrypt.hash("password123", cost=12)
   → "$2b$12$abcdefghijklmnopqrstuvwxyz123456"

7. Backend: Create user in database
   INSERT INTO users (id, email, hashed_password, created_at, updated_at)
   VALUES (uuid, 'user@example.com', '$2b$12$...', NOW(), NOW())

8. Backend: Generate response
   { success: true, message: "Account created successfully", user: {...} }

9. Frontend: Display success message
10. Frontend: Redirect to /login page
```

---

### User Login Flow

```
1. Frontend: User fills login form
   { email: "user@example.com", password: "password123" }

2. Frontend: POST /api/auth/sign-in
   Body: { email: "user@example.com", password: "password123" }

3. Backend: Find user by email
   SELECT * FROM users WHERE email = 'user@example.com'
   ✅ Found user

4. Backend: Verify password
   bcrypt.verify("password123", "$2b$12$...")
   ✅ Password matches

5. Backend: Generate JWT token
   payload = {
     sub: user.id,
     exp: now + 7 days,
     iat: now
   }
   token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

6. Backend: Set httpOnly cookie
   Set-Cookie: access_token=<token>; HttpOnly; Secure; SameSite=lax; Max-Age=604800

7. Backend: Return response
   { success: true, token: "...", user: {...}, expires_at: "2026-01-16T12:00:00Z" }

8. Frontend: Store token (automatically via cookie)
9. Frontend: Redirect to /dashboard
```

---

### Protected API Request Flow

```
1. Frontend: User navigates to protected page
   Page checks if token exists in cookie

2. Frontend: API call to protected endpoint
   GET /api/tasks
   Headers: (Cookies automatically included by browser)

3. Backend: Extract JWT from cookie
   access_token = request.cookies.get("access_token")

4. Backend: Verify JWT signature
   payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
   ✅ Token valid

5. Backend: Extract user_id from JWT
   user_id = payload["sub"]  # "550e8400-e29b-41d4-a716-446655440000"

6. Backend: Fetch user's data scoped to user_id
   SELECT * FROM tasks WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'

7. Backend: Return scoped data
   { tasks: [...] }

8. Frontend: Display user's tasks
```

---

## Security Considerations

### Password Storage
- ✅ Hashed with bcrypt (cost factor 12)
- ✅ Automatic salt generation
- ✅ Never stored in plaintext
- ✅ Never logged or printed

### JWT Security
- ✅ Signed with secure secret key
- ✅ Short expiration (7 days)
- ✅ Stored in httpOnly cookies (XSS protection)
- ✅ SameSite=Strict or Lax (CSRF protection)
- ✅ Secure flag in production (HTTPS only)

### Data Isolation
- ✅ All queries scoped to authenticated user_id
- ✅ No cross-user data access possible
- ✅ JWT verification middleware on all protected endpoints

### Error Messages
- ✅ Generic 401 "Invalid credentials" (doesn't reveal if email exists)
- ✅ No sensitive data in error responses
- ✅ Logged server-side for debugging, generic messages to users

---

## Migration Path

**Initial Setup** (Development):
```python
from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
```

**Future Production Migrations**:
```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Generate migration from SQLModel models
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head
```

---

## Testing Data

**Test User** (for development/testing):
```python
test_user = User(
    email="test@example.com",
    hashed_password="$2b$12$test",  # Will be replaced with real hash
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Example cURL Commands**:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Verify Session (with token)
curl -X GET http://localhost:8000/api/auth/session \
  -H "Authorization: Bearer <token>"

# Logout
curl -X POST http://localhost:8000/api/auth/sign-out \
  -H "Authorization: Bearer <token>"
```
