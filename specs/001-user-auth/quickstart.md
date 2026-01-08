# Quickstart Guide: User Authentication Implementation

**Feature**: 001-user-auth
**Date**: 2026-01-08
**Phase**: Phase 1 - Quickstart Instructions

## Overview

This guide provides step-by-step instructions for implementing user authentication with BetterAuth (frontend) and JWT verification middleware (backend).

## Prerequisites

- **Backend**: Python 3.13+, UV package manager, FastAPI, SQLModel
- **Frontend**: Node.js 18+, PNPM, Next.js 16
- **Database**: Neon Serverless PostgreSQL (or local PostgreSQL)
- **Environment**: Shared `BETTER_AUTH_SECRET` between frontend and backend

## Phase 1: Backend Setup (FastAPI)

### Step 1.1: Install Dependencies

```bash
cd backend
uv add python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Dependencies**:
- `python-jose`: JWT encoding/decoding
- `passlib[bcrypt]`: Password hashing (for reference, BetterAuth handles this)
- `python-multipart`: Form data parsing

### Step 1.2: Create Security Module

Create `backend/core/security.py`:

```python
"""JWT security utilities for FastAPI."""
import os
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Get BetterAuth secret from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"


class JWTManager:
    """JWT token manager for BetterAuth integration."""

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """Extract user_id from JWT token claims."""
        payload = JWTManager.verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: user_id missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id

    @staticmethod
    def get_token_from_header(authorization: str) -> str:
        """Extract token from Authorization header."""
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
```

### Step 1.3: Create JWT Middleware

Create `backend/core/middleware.py`:

```python
"""JWT middleware for FastAPI."""
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import JWTManager


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware."""

    def __init__(self, app, excluded_paths: list[str] = None):
        """Initialize JWT middleware."""
        super().__init__(app)
        self.excluded_paths = excluded_paths or []
        self.public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        ] + self.excluded_paths

    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request with JWT validation."""
        # Skip JWT validation for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Extract Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Verify token and extract user_id
            token = JWTManager.get_token_from_header(authorization)
            user_id = JWTManager.get_user_id_from_token(token)

            # Add user_id to request state for route handlers
            request.state.user_id = user_id

            return await call_next(request)

        except HTTPException as e:
            raise e
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authentication"},
            )
```

### Step 1.4: Create Dependency Injection

Create `backend/core/deps.py`:

```python
"""Dependency injection for JWT authentication."""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from starlette.requests import Request as StarletteRequest


async def get_current_user_id(request: StarletteRequest) -> str:
    """Get current user ID from JWT token."""
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user_id


# Type alias for dependency
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]
```

### Step 1.5: Update Main Application

Update `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.middleware import JWTMiddleware

app = FastAPI(title="Todo List API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT middleware (protects all routes except public ones)
app.add_middleware(JWTMiddleware)

# Your existing routes...
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}
```

### Step 1.6: Update Task Routes

Update `backend/api/tasks.py` to use JWT authentication:

```python
from typing import Annotated
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from core.deps import SessionDep, CurrentUserDep
from models.task import Task, TaskCreate, TaskRead

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep,  # Injected from JWT
):
    """Create a new task for the authenticated user."""
    db_task = Task(
        user_id=user_id,  # Use authenticated user ID
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,  # Injected from JWT
):
    """List all tasks for the authenticated user."""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

### Step 1.7: Configure Environment

Create `backend/.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=your-super-secret-jwt-key-min-32-chars
ENVIRONMENT=development
```

**Important**: `BETTER_AUTH_SECRET` must match the frontend's secret.

### Step 1.8: Test Backend

```bash
# Run backend
cd backend
uv run uvicorn backend.app:app --reload

# Test health endpoint (public)
curl http://localhost:8000/health

# Test protected endpoint (should return 401 without token)
curl http://localhost:8000/api/tasks
```

## Phase 2: Frontend Setup (Next.js 16)

### Step 2.1: Install BetterAuth

```bash
cd frontend
pnpm add better-auth
```

### Step 2.2: Create Auth Configuration

Create `frontend/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { prisma } from "@better-auth/prisma";
import { jwt } from "better-auth/plugins/jwt";

export const auth = betterAuth({
  database: prisma(process.env.DATABASE_URL),
  emailAndPassword: {
    enabled: true,
    disableSignUp: false,
    requireEmailVerification: false,
    minPasswordLength: 8,
    autoSignIn: false,
  },
  plugins: [
    jwt({
      expiresIn: "7d",
      secret: process.env.BETTER_AUTH_SECRET,
    }),
  ],
});
```

**Note**: BetterAuth will create the `users` table automatically.

### Step 2.3: Create Auth API Route

Create `frontend/app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
```

### Step 2.4: Create Auth Client

Create `frontend/lib/auth-client.ts`:

```typescript
"use client";

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL + "/api/auth",
});
```

### Step 2.5: Create Register Page

Create `frontend/app/register/page.tsx`:

```typescript
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data, error } = await authClient.signUp.email({
        email,
        password,
      });

      if (error) {
        setError(error.message);
        return;
      }

      // Redirect to login page
      router.push("/login");
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-6">Register</h1>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block mb-2">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div className="mb-6">
        <label className="block mb-2">Password (min 8 characters)</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          minLength={8}
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
      >
        {loading ? "Creating account..." : "Register"}
      </button>
    </form>
  );
}
```

### Step 2.6: Create Login Page

Create `frontend/app/login/page.tsx`:

```typescript
"use client";

import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data, error } = await authClient.signIn.email({
        email,
        password,
      });

      if (error) {
        setError("Invalid credentials");
        return;
      }

      // Redirect to main application
      router.push("/dashboard");
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-6">Login</h1>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block mb-2">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div className="mb-6">
        <label className="block mb-2">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
      >
        {loading ? "Logging in..." : "Login"}
      </button>

      <p className="mt-4 text-center">
        Don't have an account? <a href="/register" className="text-blue-500">Register</a>
      </p>
    </form>
  );
}
```

### Step 2.7: Create Protected Page

Create `frontend/app/dashboard/page.tsx`:

```typescript
"use client";

import { useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  email: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data, error } = await authClient.getSession();
        if (error || !data) {
          router.push("/login");
          return;
        }
        setUser(data.user);
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = async () => {
    await authClient.signOut();
    router.push("/login");
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto mt-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <div className="bg-white p-6 rounded shadow">
        <p>Welcome, {user?.email}!</p>
        <p className="text-gray-600 mt-2">User ID: {user?.id}</p>
      </div>
    </div>
  );
}
```

### Step 2.8: Create API Client

Create `frontend/lib/api/client.ts`:

```typescript
import { authClient } from "@/lib/auth-client";

export interface ApiRequestConfig {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: any;
  requiresAuth?: boolean;
}

export const apiClient = async ({
  url,
  method = "GET",
  data,
  requiresAuth = true,
}: ApiRequestConfig) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Add JWT token if authentication is required
  if (requiresAuth) {
    const { data: tokenData } = await authClient.token();
    if (tokenData?.token) {
      headers["Authorization"] = `Bearer ${tokenData.token}`;
    }
  }

  const response = await fetch(url, {
    method,
    headers,
    ...(data && { body: JSON.stringify(data) }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
};

// Usage example
export const taskService = {
  getTasks: () => apiClient({ url: "/api/tasks" }),
  createTask: (task: any) =>
    apiClient({ url: "/api/tasks", method: "POST", data: task }),
};
```

### Step 2.9: Configure Environment

Create `frontend/.env.local`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=your-super-secret-jwt-key-min-32-chars
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

**Important**: `BETTER_AUTH_SECRET` must match the backend's secret.

### Step 2.10: Test Frontend

```bash
# Run frontend
cd frontend
pnpm dev

# Open browser to http://localhost:3000/register
```

## Phase 3: Integration Testing

### Test 1: User Registration

```bash
# 1. Navigate to http://localhost:3000/register
# 2. Enter email and password (min 8 characters)
# 3. Submit form
# Expected: Redirect to /login with success message
```

### Test 2: User Login

```bash
# 1. Navigate to http://localhost:3000/login
# 2. Enter registered email and password
# 3. Submit form
# Expected: Redirect to /dashboard with JWT token stored
```

### Test 3: Protected API Access

```bash
# Get JWT token from browser localStorage or cookies
TOKEN="your-jwt-token-here"

# Test protected endpoint
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected: Returns empty task array for new user
```

### Test 4: Invalid Token

```bash
# Test with invalid token
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer invalid-token"

# Expected: 401 Unauthorized
```

### Test 5: Logout

```bash
# 1. Click logout button on /dashboard
# Expected: Redirect to /login, token cleared
```

## Troubleshooting

### Common Issues

**Issue**: "Could not validate credentials"
- **Cause**: Invalid JWT signature or token
- **Fix**: Ensure `BETTER_AUTH_SECRET` matches on frontend and backend

**Issue**: "Not authenticated"
- **Cause**: Missing or invalid Authorization header
- **Fix**: Check that token is being sent in format: `Authorization: Bearer <token>`

**Issue**: CORS errors
- **Cause**: Frontend origin not allowed
- **Fix**: Update CORS middleware to include frontend URL

**Issue**: Token expires immediately
- **Cause**: System time mismatch or incorrect expiration
- **Fix**: Check system time and JWT expiration configuration

## Next Steps

1. **Add email verification**: Implement email confirmation flow
2. **Add password reset**: Implement forgot password functionality
3. **Add rate limiting**: Prevent brute force login attempts
4. **Add social login**: Integrate OAuth providers (Google, GitHub)
5. **Add 2FA**: Implement two-factor authentication

## Summary

This quickstart guide provides:

1. **Backend**: JWT verification middleware with dependency injection
2. **Frontend**: BetterAuth configuration with email/password authentication
3. **Integration**: Shared JWT secret between frontend and backend
4. **Testing**: Step-by-step integration tests

All functional requirements are met (FR-001 through FR-015), and the implementation follows Constitution Principles VII (JWT Security) and IX (Data Ownership & Isolation).
