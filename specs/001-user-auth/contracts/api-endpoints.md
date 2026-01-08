# API Contracts: Authentication Endpoints

**Feature**: 001-user-auth
**Date**: 2026-01-08
**Phase**: Phase 1 - API Contract Design

## Overview

This document defines the API contracts for authentication endpoints. All endpoints are implemented by BetterAuth on the frontend and follow RESTful conventions.

## Base URL

```
Development: http://localhost:8000
Production: https://api.example.com
```

## Authentication

All endpoints except `/api/auth/*` require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <token>
```

The JWT token contains a `sub` claim with the user_id.

## Common Response Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input data (validation error) |
| 401 | Unauthorized | Missing, invalid, or expired JWT token |
| 403 | Forbidden | Access to another user's data |
| 404 | Not Found | Resource not found or doesn't belong to user |
| 409 | Conflict | Email already registered |
| 500 | Internal Server Error | Server error |

## Common Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health`
**Authentication**: Not required
**Description**: Verifies API and database connectivity

**Request**: None

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "detail": "Service unavailable - database connection failed"
}
```

---

### 2. User Registration

**Endpoint**: `POST /api/auth/sign-up`
**Authentication**: Not required (public endpoint)
**Description**: Creates a new user account with email and password

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation Rules**:
- Email must be valid format (contains `@` and domain)
- Password must be at least 8 characters
- Email must be unique (case-insensitive)

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-08T12:00:00Z"
  }
}
```

**Error Responses**:

- **400 Bad Request** (Invalid email):
```json
{
  "detail": "Invalid email format"
}
```

- **400 Bad Request** (Password too short):
```json
{
  "detail": "Password must be at least 8 characters"
}
```

- **409 Conflict** (Email already registered):
```json
{
  "detail": "Email already registered"
}
```

**Functional Requirements**: FR-001, FR-002, FR-003, FR-004

---

### 3. User Login

**Endpoint**: `POST /api/auth/sign-in`
**Authentication**: Not required (public endpoint)
**Description**: Authenticates a user and issues a JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  },
  "expires_at": "2026-01-15T12:00:00Z"
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid credentials"
}
```

**Notes**:
- Generic error message (no information leakage per FR-015)
- Token valid for 7 days (604800 seconds)
- Token must be included in subsequent requests via `Authorization: Bearer <token>`

**Functional Requirements**: FR-005, FR-006

---

### 4. User Logout

**Endpoint**: `POST /api/auth/sign-out`
**Authentication**: Required (JWT token)
**Description**: Invalidates the current session by clearing the JWT token

**Request Headers**:
```
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "success": true
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Notes**:
- JWT tokens are stateless, so this instructs the client to discard the token
- Tokens will naturally expire after 7 days
- Client should clear token from storage (cookie or localStorage)

**Functional Requirements**: FR-011

---

### 5. Get Current Session

**Endpoint**: `GET /api/auth/session`
**Authentication**: Required (JWT token)
**Description**: Returns the current user's session data if authenticated

**Request Headers**:
```
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "authenticated": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  },
  "expires_at": "2026-01-15T12:00:00Z"
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Use Case**: Verify authentication status and get user info

**Functional Requirements**: FR-009

---

## JWT Token Structure

### Token Format

JWT tokens issued by BetterAuth follow this structure:

```
Header: {"alg": "HS256", "typ": "JWT"}
Payload: {
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user_id
  "iat": 1704700800,                               // issued at
  "exp": 1705305600,                               // expiration (7 days)
  "iss": "better-auth",                            // issuer
  "aud": "api"                                     // audience
}
```

### Token Usage

**Include in API Requests**:
```bash
curl -X GET https://api.example.com/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Token Verification** (Backend):
1. Extract token from `Authorization` header
2. Verify signature with `BETTER_AUTH_SECRET`
3. Check expiration (reject if `exp` < current time)
4. Extract `sub` claim (user_id)
5. Inject user_id into request for route handlers

## Example API Calls

### Registration

```bash
curl -X POST http://localhost:8000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Authenticated Request

```bash
# Save token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get user session
curl -X GET http://localhost:8000/api/auth/session \
  -H "Authorization: Bearer $TOKEN"

# Logout
curl -X POST http://localhost:8000/api/auth/sign-out \
  -H "Authorization: Bearer $TOKEN"
```

## Integration with Task API

Once authenticated, the JWT token must be included in all task API requests:

```bash
# Create task (requires authentication)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "description": "Task description"
  }'
```

The backend will:
1. Verify JWT signature
2. Extract `user_id` from token
3. Scope all queries to this user
4. Return 401 if token is invalid or missing

## Security Considerations

### Token Storage

**Recommended**: httpOnly cookies (prevents XSS)
**Alternative**: localStorage (accessible to JavaScript)

### Token Transmission

- Always use HTTPS in production
- Include token in `Authorization: Bearer <token>` header
- Never include token in URL parameters

### Token Expiration

- Tokens expire after 7 days
- No refresh token implementation (out of scope)
- User must re-login after expiration

### Error Handling

- Generic error messages for login failures (no information leakage)
- Return 401 for all authentication failures
- Log detailed errors on server (not exposed to client)

## Summary

The authentication API provides:

1. **Registration**: `POST /api/auth/sign-up` (public)
2. **Login**: `POST /api/auth/sign-in` (public)
3. **Logout**: `POST /api/auth/sign-out` (authenticated)
4. **Session**: `GET /api/auth/session` (authenticated)
5. **Health**: `GET /health` (public)

All endpoints follow RESTful conventions with consistent error handling and JSON responses. JWT tokens are issued by BetterAuth and verified by FastAPI middleware, providing secure, stateless authentication for the application.
