# API Contracts: Advanced Todo Features

**Feature**: 008-advanced-features | **Date**: 2026-02-04 | **Status**: Complete

## Overview

This document defines the API contracts for advanced time-based task management features. All endpoints follow REST conventions and require JWT authentication.

---

## Base Configuration

**Base URL**: `http://localhost:8000` (development), `https://api.example.com` (production)
**API Prefix**: `/api`
**Authentication**: `Authorization: Bearer <JWT_TOKEN>` in header (or via httpOnly cookie)
**Content-Type**: `application/json`
**Character Encoding**: `UTF-8`

---

## Common Headers

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json
```

---

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Response

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR"
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | OK (successful GET, PUT, PATCH) |
| 201 | Created (successful POST) |
| 204 | No Content (successful DELETE) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing JWT) |
| 403 | Forbidden (not owner of resource) |
| 404 | Not Found (resource doesn't exist) |
| 422 | Unprocessable Entity (validation error) |
| 500 | Internal Server Error |

---

## Endpoints

### 1. Create Task (Extended)

**Endpoint**: `POST /api/tasks`
**Authentication**: Required
**Description**: Create a new task with optional due date, reminder, and recurrence.

#### Request

```http
POST /api/tasks HTTP/1.1
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "title": "Weekly team meeting",
  "description": "Discuss project progress",
  "priority": "HIGH",
  "tags": ["work", "meeting"],
  "due_date": "2026-02-11T14:00:00Z",
  "reminder_offset": 15,
  "recurrence": {
    "frequency": "weekly",
    "interval": 1
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task name (1-255 chars) |
| description | string | No | Task details (max 2000 chars) |
| priority | string | No | HIGH, MEDIUM, LOW (default: MEDIUM) |
| tags | array | No | Array of tag strings |
| due_date | string | No | ISO 8601 datetime (UTC) |
| reminder_offset | integer | No | Minutes before due_date (0 = at due time) |
| recurrence | object | No | Recurrence rule (see below) |

#### Response (201 Created)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Weekly team meeting",
  "description": "Discuss project progress",
  "priority": "HIGH",
  "tags": ["work", "meeting"],
  "due_date": "2026-02-11T14:00:00Z",
  "reminder_offset": 15,
  "reminder_sent": false,
  "completed": false,
  "recurrence": {
    "frequency": "weekly",
    "interval": 1
  },
  "parent_task_id": null,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T10:00:00Z"
}
```

#### Error Responses

**400 Bad Request** (invalid due date):
```json
{
  "detail": "Due date cannot be more than 10 years in the past"
}
```

**422 Unprocessable Entity** (validation error):
```json
{
  "detail": [
    {
      "loc": ["body", "recurrence", "interval"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```

---

### 2. List Tasks (Extended Filter)

**Endpoint**: `GET /api/tasks`
**Authentication**: Required
**Description**: List tasks with optional filtering by due date range.

#### Request

```http
GET /api/tasks?due_before=2026-02-15T23:59:59Z&due_after=2026-02-01T00:00:00Z&status=active
Authorization: Bearer <JWT_TOKEN>
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | `all`, `active`, `completed` (default: `all`) |
| priority | string | No | `HIGH`, `MEDIUM`, `LOW` |
| tags | string | No | Comma-separated tag list |
| search | string | No | Full-text search in title/description |
| due_before | string | No | ISO 8601 datetime (UTC) |
| due_after | string | No | ISO 8601 datetime (UTC) |
| sort_by | string | No | `created_at`, `due_date`, `priority`, `title` (default: `created_at`) |
| sort_order | string | No | `asc`, `desc` (default: `desc`) |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 50, max: 100) |

#### Response (200 OK)

```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Submit report",
      "description": null,
      "priority": "HIGH",
      "tags": [],
      "due_date": "2026-02-10T17:00:00Z",
      "reminder_offset": 60,
      "reminder_sent": false,
      "completed": false,
      "recurrence": null,
      "parent_task_id": null,
      "created_at": "2026-02-04T09:00:00Z",
      "updated_at": "2026-02-04T09:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50,
  "pages": 1
}
```

---

### 3. Get Task

**Endpoint**: `GET /api/tasks/{id}`
**Authentication**: Required
**Description**: Get a specific task by ID.

#### Request

```http
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <JWT_TOKEN>
```

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Submit report",
  "description": null,
  "priority": "HIGH",
  "tags": [],
  "due_date": "2026-02-10T17:00:00Z",
  "reminder_offset": 60,
  "reminder_sent": false,
  "completed": false,
  "recurrence": null,
  "parent_task_id": null,
  "created_at": "2026-02-04T09:00:00Z",
  "updated_at": "2026-02-04T09:00:00Z"
}
```

#### Error Response (404 Not Found)

```json
{
  "detail": "Task not found"
}
```

---

### 4. Update Task (Extended)

**Endpoint**: `PUT /api/tasks/{id}`
**Authentication**: Required
**Description**: Update a task's fields including due date, reminder, and recurrence.

#### Request

```http
PUT /api/tasks/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "due_date": "2026-02-11T10:00:00Z",
  "reminder_offset": 1440,
  "recurrence": {
    "frequency": "daily",
    "interval": 1,
    "count": 30
  }
}
```

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Submit report",
  "description": null,
  "priority": "HIGH",
  "tags": [],
  "due_date": "2026-02-11T10:00:00Z",
  "reminder_offset": 1440,
  "reminder_sent": false,
  "completed": false,
  "recurrence": {
    "frequency": "daily",
    "interval": 1,
    "count": 30
  },
  "parent_task_id": null,
  "created_at": "2026-02-04T09:00:00Z",
  "updated_at": "2026-02-04T11:30:00Z"
}
```

**Note**: Setting `recurrence: null` removes recurrence from the task.

---

### 5. Complete Task (Extended for Recurrence)

**Endpoint**: `POST /api/tasks/{id}/complete`
**Authentication**: Required
**Description**: Mark a task as complete. If the task has a recurrence rule, creates the next instance automatically.

#### Request

```http
POST /api/tasks/550e8400-e29b-41d4-a716-446655440000/complete
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "completed": true
}
```

#### Response (200 OK)

**Non-recurring task**:
```json
{
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "completed": true,
    ...
  },
  "next_instance": null
}
```

**Recurring task** (creates next instance):
```json
{
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "completed": true,
    ...
  },
  "next_instance": {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "title": "Submit report",
    "due_date": "2026-02-12T10:00:00Z",
    "parent_task_id": "550e8400-e29b-41d4-a716-446655440000",
    "completed": false,
    ...
  }
}
```

#### Error Response (400 Bad Request)

```json
{
  "detail": "Recurrence limit reached: maximum 100 instances"
}
```

---

### 6. Delete Task

**Endpoint**: `DELETE /api/tasks/{id}`
**Authentication**: Required
**Description**: Delete a task. If the task has recurring instances, they are NOT deleted (unless explicitly requested).

#### Request

```http
DELETE /api/tasks/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <JWT_TOKEN>
```

#### Response (204 No Content)

Empty response body.

---

### 7. Update Reminder Status

**Endpoint**: `PATCH /api/tasks/{id}/reminder`
**Authentication**: Required
**Description**: Mark reminder as sent (called by frontend after showing notification).

#### Request

```http
PATCH /api/tasks/550e8400-e29b-41d4-a716-446655440000/reminder
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
  "reminder_sent": true
}
```

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reminder_sent": true,
  ...
}
```

---

## Data Types

### RecurrenceRule

```typescript
interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  interval?: number;        // 1-365, default: 1
  count?: number;           // 1-100, max occurrences
  end_date?: string;        // ISO 8601 date
}
```

### Task

```typescript
interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  tags: string[];
  due_date: string | null;        // ISO 8601 datetime (UTC)
  reminder_offset: number | null; // Minutes before due_date
  reminder_sent: boolean;
  completed: boolean;
  recurrence: RecurrenceRule | null;
  parent_task_id: string | null;
  created_at: string;             // ISO 8601 datetime (UTC)
  updated_at: string;             // ISO 8601 datetime (UTC)
}
```

---

## Example Usage

### Creating a Daily Recurring Task with Reminder

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Take vitamins",
    "priority": "MEDIUM",
    "due_date": "2026-02-05T09:00:00Z",
    "reminder_offset": 0,
    "recurrence": {
      "frequency": "daily",
      "interval": 1
    }
  }'
```

### Filtering Tasks Due This Week

```bash
curl -X GET "http://localhost:8000/api/tasks?due_after=2026-02-03T00:00:00Z&due_before=2026-02-09T23:59:59Z" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Completing a Recurring Task

```bash
curl -X POST http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000/complete \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

---

**API Contracts Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Complete
