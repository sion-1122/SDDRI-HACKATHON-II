# API Contracts: Intermediate Todo Features

**Feature**: 007-intermediate-todo-features
**Date**: 2026-01-28
**Phase**: Phase 1 (Design)

## Overview

This document defines the API contracts for the intermediate todo features. All endpoints extend the existing RESTful API under `/api` path and require valid JWT authentication.

---

## Base URL

```
https://api.example.com/api
```

## Authentication

All requests MUST include a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "details": { ... }
  }
}
```

---

## Endpoints

### 1. List Tasks (Extended)

**Endpoint**: `GET /tasks`

**Description**: Retrieve tasks for the authenticated user with optional filtering, sorting, and search.

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | `all` | Filter by status: `all`, `pending`, `completed` |
| `priority` | string[] | No | `[]` | Filter by priority: `high`, `medium`, `low` (multi-select) |
| `tags` | string[] | No | `[]` | Filter by tags (AND logic: match all) |
| `due_date` | string | No | `all` | Filter by due date: `today`, `this_week`, `overdue`, `all` |
| `search` | string | No | - | Search query (searches title and description) |
| `sort_by` | string | No | `created_at` | Sort field: `due_date`, `priority`, `created_at`, `title` |
| `sort_order` | string | No | `desc` | Sort order: `asc`, `desc` |
| `page` | integer | No | `1` | Page number (for server-side search) |
| `limit` | integer | No | `50` | Items per page (for server-side search) |
| `timezone` | string | No | `UTC` | User's timezone for date calculations |

**Request Example**:

```http
GET /api/tasks?status=pending&priority=high&tags=work&due_date=today&sort_by=priority&sort_order=desc&timezone=America/New_York
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Example** (200 OK):

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project proposal",
        "description": "Finish the Q1 project proposal document",
        "completed": false,
        "priority": "high",
        "tags": ["work", "urgent"],
        "due_date": "2026-01-28T23:59:59Z",
        "created_at": "2026-01-27T10:00:00Z",
        "updated_at": "2026-01-27T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 50
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token
- `400 Bad Request`: Invalid query parameters

---

### 2. Create Task (Extended)

**Endpoint**: `POST /tasks`

**Description**: Create a new task with optional priority, tags, and due date.

**Request Body**:

```json
{
  "title": "string (required, 1-500 chars)",
  "description": "string (optional, max 5000 chars)",
  "priority": "string (optional, default: 'medium')",
  "tags": ["string"] (optional, default: []),
  "due_date": "string (optional, ISO 8601 datetime)"
}
```

**Priority Values**: `high`, `medium`, `low`

**Request Example**:

```http
POST /api/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and cheese",
  "priority": "medium",
  "tags": ["shopping", "home"],
  "due_date": "2026-01-30T18:00:00Z"
}
```

**Response Example** (201 Created):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and cheese",
    "completed": false,
    "priority": "medium",
    "tags": ["shopping", "home"],
    "due_date": "2026-01-30T18:00:00Z",
    "created_at": "2026-01-28T10:00:00Z",
    "updated_at": "2026-01-28T10:00:00Z"
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token
- `400 Bad Request`: Invalid request body (validation errors)

---

### 3. Update Task (Extended)

**Endpoint**: `PATCH /tasks/{task_id}`

**Description**: Update an existing task. All fields are optional.

**Path Parameters**:

- `task_id` (UUID): The task ID

**Request Body**:

```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)",
  "priority": "string (optional)",
  "tags": ["string"] (optional),
  "due_date": "string (optional, ISO 8601 datetime or null)"
}
```

**Request Example**:

```http
PATCH /api/tasks/550e8400-e29b-41d4-a716-446655440002
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "priority": "high",
  "tags": ["shopping", "home", "urgent"]
}
```

**Response Example** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and cheese",
    "completed": false,
    "priority": "high",
    "tags": ["shopping", "home", "urgent"],
    "due_date": "2026-01-30T18:00:00Z",
    "created_at": "2026-01-28T10:00:00Z",
    "updated_at": "2026-01-28T12:30:00Z"
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: Task belongs to another user
- `404 Not Found`: Task does not exist
- `400 Bad Request`: Invalid request body

---

### 4. Delete Task (Unchanged)

**Endpoint**: `DELETE /tasks/{task_id}`

**Description**: Delete a task. No changes required for this feature.

---

### 5. Get All Tags

**Endpoint**: `GET /tags`

**Description**: Get all unique tags used by the authenticated user.

**Response Example** (200 OK):

```json
{
  "success": true,
  "data": {
    "tags": [
      { "name": "work", "count": 15 },
      { "name": "shopping", "count": 8 },
      { "name": "home", "count": 5 },
      { "name": "urgent", "count": 3 }
    ]
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token

---

### 6. Bulk Update Tags

**Endpoint**: `PATCH /tasks/{task_id}/tags`

**Description**: Add or remove tags from a task.

**Path Parameters**:

- `task_id` (UUID): The task ID

**Request Body**:

```json
{
  "add": ["string"] (optional, tags to add),
  "remove": ["string"] (optional, tags to remove)
}
```

**Request Example**:

```http
PATCH /api/tasks/550e8400-e29b-41d4-a716-446655440002/tags
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "add": ["urgent"],
  "remove": ["home"]
}
```

**Response Example** (200 OK):

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "tags": ["shopping", "urgent"]
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: Task belongs to another user
- `404 Not Found`: Task does not exist

---

### 7. Search Tasks

**Endpoint**: `GET /tasks/search`

**Description**: Full-text search across task titles and descriptions. Uses server-side search for large lists.

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |

**Request Example**:

```http
GET /api/tasks/search?q=groceries&page=1&limit=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response Example** (200 OK):

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread, and cheese",
        "completed": false,
        "priority": "medium",
        "tags": ["shopping", "home"],
        "due_date": "2026-01-30T18:00:00Z",
        "created_at": "2026-01-28T10:00:00Z",
        "updated_at": "2026-01-28T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20,
    "query": "groceries"
  }
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or missing JWT token
- `400 Bad Request`: Missing or invalid query parameter

---

## Data Types

### Task Object

```typescript
interface Task {
  id: string;              // UUID
  user_id: string;         // UUID
  title: string;           // 1-500 chars
  description?: string;    // Optional, max 5000 chars
  completed: boolean;      // Completion status
  priority: 'high' | 'medium' | 'low';
  tags: string[];          // Array of tag names
  due_date?: string;       // ISO 8601 datetime or null
  created_at: string;      // ISO 8601 datetime
  updated_at: string;      // ISO 8601 datetime
}
```

### Tag Object

```typescript
interface Tag {
  name: string;    // Tag name
  count: number;   // Number of tasks with this tag
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing JWT token |
| `FORBIDDEN` | 403 | Access denied to resource |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INVALID_PRIORITY` | 400 | Invalid priority value |
| `INVALID_DATE` | 400 | Invalid date format |
| `TAG_TOO_LONG` | 400 | Tag name exceeds 50 characters |

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| GET /tasks | 100 requests | 1 minute |
| POST /tasks | 20 requests | 1 minute |
| PATCH /tasks/{id} | 50 requests | 1 minute |
| DELETE /tasks/{id} | 20 requests | 1 minute |
| GET /tasks/search | 50 requests | 1 minute |

---

## Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| List tasks (filtered) | < 200ms | Time to first byte |
| Search (client-side) | < 200ms | JavaScript execution |
| Search (server-side) | < 500ms | API response time |
| Create task | < 300ms | API response time |
| Update task | < 250ms | API response time |
