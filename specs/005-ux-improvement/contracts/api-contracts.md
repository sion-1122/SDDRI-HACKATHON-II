# API Contracts: UI/UX Improvements

**Feature**: 005-ux-improvement
**Date**: 2026-01-24
**Status**: Complete

## Overview

This feature is primarily a frontend improvement. The backend API already supports all required endpoints. This document defines the expected API contracts for frontend consumption.

---

## Existing API Endpoints (No Changes Required)

All endpoints are already implemented in the backend. The frontend will consume these existing endpoints.

### Task Endpoints

#### List Tasks

```http
GET /api/tasks?limit={limit}&offset={offset}&completed={bool}&search={string}&priority={string}
```

**Request Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 50 | Max items per page (max 100) |
| offset | integer | No | 0 | Pagination offset |
| completed | boolean | No | - | Filter by completion status |
| search | string | No | - | Search in title/description |
| priority | string | No | - | Filter by priority (low/medium/high) |

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "due_date": "2025-01-25T10:00:00Z",
      "priority": "medium",
      "completed": false,
      "created_at": "2025-01-24T10:00:00Z",
      "updated_at": "2025-01-24T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### Create Task

```http
POST /api/tasks
```

**Request Body**:
```json
{
  "title": "New task",
  "description": "Optional description",
  "due_date": "2025-01-25T10:00:00Z",
  "priority": "medium"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "New task",
  "description": "Optional description",
  "due_date": "2025-01-25T10:00:00Z",
  "priority": "medium",
  "completed": false,
  "created_at": "2025-01-24T10:00:00Z",
  "updated_at": "2025-01-24T10:00:00Z"
}
```

#### Update Task

```http
PUT /api/tasks/{id}
```

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "due_date": "2025-01-26T10:00:00Z",
  "priority": "high",
  "completed": true
}
```

**Response** (200 OK): Same as Create Task response

#### Delete Task

```http
DELETE /api/tasks/{id}
```

**Response** (204 No Content): Empty body

#### Toggle Complete

```http
PATCH /api/tasks/{id}/complete
```

**Response** (200 OK): Same as Create Task response

---

### WebSocket Endpoint (Chatbot)

#### Chat Connection

```http
WS /api/ws/{user_id}/chat
```

**Message Format (Client → Server)**:
```json
{
  "type": "message",
  "content": "User message here"
}
```

**Message Format (Server → Client)**:
```json
{
  "type": "message" | "tool_starting" | "tool_complete" | "error",
  "content": "Response text or error message",
  "tool_name": "add_task",
  "timestamp": "2025-01-24T10:00:00Z"
}
```

---

### Authentication Endpoints

#### Get Session

```http
GET /api/auth/session
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

**Response** (401 Unauthorized): Session invalid or missing

---

## Frontend API Client Contracts

### TypeScript Interfaces

```typescript
// frontend/src/types/api.ts

interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}

interface TaskCreateInput {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: 'low' | 'medium' | 'high';
}

interface TaskUpdateInput {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: 'low' | 'medium' | 'high';
  completed?: boolean;
}

interface User {
  id: string;
  email: string;
}

interface SessionResponse {
  user: User;
}
```

### API Client Methods

```typescript
// frontend/src/lib/task-api.ts

class TaskAPI {
  // List tasks with filters
  listTasks(params: {
    limit?: number;
    offset?: number;
    completed?: boolean;
    search?: string;
    priority?: string;
  }): Promise<TaskListResponse>;

  // Create new task
  createTask(input: TaskCreateInput): Promise<Task>;

  // Update existing task
  updateTask(id: string, input: TaskUpdateInput): Promise<Task>;

  // Delete task
  deleteTask(id: string): Promise<void>;

  // Toggle completion
  toggleComplete(id: string): Promise<Task>;
}
```

---

## Error Response Contracts

All endpoints follow consistent error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes**:
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing session) |
| 403 | Forbidden (accessing another user's data) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## WebSocket Event Types

```typescript
type WebSocketEventType =
  | 'message'        // Chat message from AI
  | 'tool_starting'  // AI tool execution starting
  | 'tool_complete'  // AI tool execution complete
  | 'error';         // Error occurred

interface WebSocketEvent {
  type: WebSocketEventType;
  content: string;
  tool_name?: string;
  timestamp: string;
}
```

---

## Summary

**No new API endpoints required.** The frontend will consume existing endpoints:

1. **Task CRUD**: All endpoints already support due_date and priority
2. **Search**: `search` parameter already supported
3. **Filtering**: `completed`, `priority` parameters already supported
4. **WebSocket**: Chat endpoint already implemented
5. **Authentication**: Session endpoint already exists

The frontend enhancement involves:
- Displaying additional fields (due_date, priority)
- Implementing optimistic UI updates
- Adding integrated chatbot dialog
- Improving loading states
