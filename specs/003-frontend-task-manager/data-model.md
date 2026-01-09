# Data Model: Frontend Task Management

**Feature**: 003-frontend-task-manager
**Date**: 2026-01-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data structures, TypeScript interfaces, and validation schemas for the frontend task management feature. All types align with the existing API contracts (001-backend-task-api and 001-user-auth).

---

## Core Entities

### Task

**TypeScript Interface**:

```typescript
// frontend/src/types/task.ts

export interface Task {
  id: string;                    // UUID format
  user_id: string;               // UUID (from JWT, not displayed in UI)
  title: string;                 // 1-255 characters, required
  description: string | null;    // Optional, max 2000 characters
  completed: boolean;            // Completion status
  created_at: string;            // ISO 8601 datetime (UTC)
  updated_at: string;            // ISO 8601 datetime (UTC)
}
```

**Zod Validation Schema**:

```typescript
// frontend/src/lib/schemas/task.ts
import { z } from 'zod';

export const taskSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  title: z.string().min(1).max(255),
  description: z.string().max(2000).nullable(),
  completed: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type Task = z.infer<typeof taskSchema>;
```

**Display Format**:
- `title`: Displayed as task heading
- `description`: Displayed as paragraph (if not null)
- `completed`: Visual indicator (checkbox/strikethrough)
- `created_at`: Formatted as "Created Jan 9, 2026"
- `updated_at`: Formatted as "Last edited 2 hours ago" (relative time)

---

### User (Session)

**TypeScript Interface**:

```typescript
// frontend/src/types/auth.ts

export interface User {
  id: string;                    // UUID
  email: string;                 // Email address
  created_at: string;            // ISO 8601 datetime
}

export interface Session {
  user: User;
  token: string;                 // JWT (managed by Better Auth)
  expires_at: string;            // ISO 8601 datetime
}
```

**Better Auth Session Type**:

```typescript
// Better Auth provides inferred types
import { authClient } from '@/lib/auth';

type Session = typeof authClient.$Infer.Session;
```

---

## Form Data Structures

### Task Form

**TypeScript Interface**:

```typescript
// frontend/src/types/forms.ts

export interface TaskFormData {
  title: string;
  description: string;
}

export interface TaskFormErrors {
  title?: string;
  description?: string;
}
```

**Zod Validation Schema**:

```typescript
// frontend/src/lib/schemas/forms.ts
import { z } from 'zod';

export const taskFormSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(255, 'Title must be less than 255 characters'),
  description: z.string()
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),
});

export type TaskFormData = z.infer<typeof taskFormSchema>;
```

**Validation Rules**:
- `title`: Required, 1-255 characters
- `description`: Optional, max 2000 characters
- Validation on submit and on blur
- Real-time error display

---

### Login Form

**TypeScript Interface**:

```typescript
export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginFormErrors {
  email?: string;
  password?: string;
}
```

**Zod Validation Schema**:

```typescript
export const loginFormSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z.string()
    .min(1, 'Password is required'),
});
```

**Better Auth Integration**:
- Use `authClient.signIn.email()` for form submission
- Better Auth handles validation and error responses
- On success: redirect to `/tasks`
- On failure: display error message from response

---

### Register Form

**TypeScript Interface**:

```typescript
export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterFormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}
```

**Zod Validation Schema**:

```typescript
export const registerFormSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
    .min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});
```

**Better Auth Integration**:
- Use `authClient.signUp.email()` for form submission
- Better Auth handles validation and error responses
- On success: auto-login, redirect to `/tasks`
- On failure: display error message (email already registered, etc.)

---

## UI State Structures

### Filter State

**TypeScript Interface**:

```typescript
// frontend/src/types/filters.ts

export type TaskFilter = 'all' | 'active' | 'completed';

export interface FilterState {
  status: TaskFilter;
  searchQuery: string;
}

export interface FilterActions {
  setStatus: (status: TaskFilter) => void;
  setSearchQuery: (query: string) => void;
  clearFilters: () => void;
}
```

**URL Representation**:
- `status`: `?status=active` or `?status=completed` (all = no param)
- `searchQuery`: `?search=query+string`
- Both: `?status=active&search=query`

---

### Pagination State

**TypeScript Interface**:

```typescript
// frontend/src/types/pagination.ts

export interface PaginationState {
  offset: number;          // Current offset (0-based)
  limit: number;           // Items per page (default: 50)
  total: number;           // Total number of tasks
}

export interface PaginationActions {
  nextPage: () => void;
  prevPage: () => void;
  goToPage: (page: number) => void;
}

export interface PaginationComputed {
  currentPage: number;     // Current page (1-based)
  totalPages: number;      // Total pages
  hasNextPage: boolean;    // Has next page?
  hasPrevPage: boolean;    // Has previous page?
}
```

**URL Representation**:
- Page number: `?page=2` (1-based)
- Converted to offset: `offset = (page - 1) * limit`

---

### Loading State

**TypeScript Interface**:

```typescript
// frontend/src/types/loading.ts

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface TaskListLoadingState {
  tasks: LoadingState;
  createTask: LoadingState;
  updateTask: LoadingState;
  deleteTask: LoadingState;
  toggleComplete: LoadingState;
}
```

**UI Representation**:
- `idle`: No operation in progress
- `loading`: Show loading spinner
- `success`: Show success toast (if applicable)
- `error`: Show error toast

---

## API Response Types

### Success Responses

**Task List Response**:

```typescript
export interface TaskListResponse {
  tasks: Task[];
  total: number;
  offset: number;
  limit: number;
}
```

**Create/Update Task Response**:

```typescript
export interface TaskResponse {
  task: Task;
}
```

**Delete Task Response**:

```typescript
export interface DeleteTaskResponse {
  ok: boolean;
}
```

**Authentication Responses**:

```typescript
// Better Auth handles these types automatically
type SignInResponse = typeof authClient.$Infer.signIn;
type SignUpResponse = typeof authClient.$Infer.signUp;
```

---

### Error Responses

**Generic Error**:

```typescript
export interface ApiError {
  detail: string;          // Human-readable error message
}
```

**Validation Error**:

```typescript
export interface ValidationError {
  detail: Array<{
    loc: string[];         // Field path (e.g., ['body', 'title'])
    msg: string;           // Error message
    type: string;          // Error type (e.g., 'value_error.min_length')
  }>;
}
```

**Error Display Logic**:

```typescript
function displayError(error: ApiError | ValidationError): string {
  if ('detail' in error && typeof error.detail === 'string') {
    return error.detail;
  }
  if ('detail' in error && Array.isArray(error.detail)) {
    return error.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
  }
  return 'An unexpected error occurred';
}
```

---

## Utility Types

### Optional Fields

```typescript
export type TaskUpdate = Partial<Pick<Task, 'title' | 'description' | 'completed'>>;

export type TaskCreate = Pick<TaskFormData, 'title' | 'description'>;
```

### Form State

```typescript
export interface FormState<T> {
  data: T;
  errors: Record<keyof T, string | undefined>;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
}
```

### API Call State

```typescript
export interface ApiCallState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
}
```

---

## Data Flow Examples

### Creating a Task

```
1. User fills form → TaskFormData { title, description }
2. Validate with taskFormSchema → validated data or errors
3. Show errors if validation fails
4. Call API: taskApi.createTask(userId, validated data)
5. API returns Task or ApiError
6. Update task list on success, show error toast on failure
```

### Filtering Tasks

```
1. User selects filter → FilterState { status: 'active' }
2. Update URL: ?status=active
3. URL change triggers data fetch
4. Call API: taskApi.listTasks(userId, { completed: true })
5. API returns Task[]
6. Update task list display
```

### Pagination

```
1. User clicks "Next" → nextPage()
2. Calculate new offset: offset + limit
3. Update URL: ?page=2
4. URL change triggers data fetch
5. Call API: taskApi.listTasks(userId, { offset: 50, limit: 50 })
6. API returns Task[]
7. Update task list display
```

---

## Type Safety Guarantees

All types are:
1. **Validated at runtime** with Zod schemas
2. **Inferred from Zod** to ensure consistency
3. **Aligned with API contracts** (backend OpenAPI specs)
4. **Type-safe throughout** the stack (frontend → backend)

This ensures:
- No `any` types in data layer
- Compile-time type checking
- Runtime validation for API responses
- Autocomplete in IDE
- Refactoring safety
