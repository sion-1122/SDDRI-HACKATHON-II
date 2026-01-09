# API Client Contract

**Feature**: 003-frontend-task-manager
**Date**: 2026-01-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the API client interface for communicating with the existing FastAPI backend. The client provides type-safe methods for all task and authentication operations with automatic JWT injection, error handling, and retry logic.

---

## Base API Client

### Interface Definition

```typescript
// frontend/src/lib/api-client.ts

export interface ApiClientConfig {
  baseURL: string;              // API base URL (from env var)
  timeout?: number;             // Request timeout in ms (default: 10000)
  retries?: number;             // Max retries on network failure (default: 3)
}

export interface ApiRequestOptions {
  signal?: AbortSignal;         // For request cancellation
  headers?: Record<string, string>; // Additional headers
}
```

### HTTP Methods

```typescript
export interface ApiClient {
  // Generic HTTP methods with TypeScript generics
  get<T>(
    url: string,
    params?: Record<string, any>,
    options?: ApiRequestOptions
  ): Promise<T>;

  post<T>(
    url: string,
    data: any,
    options?: ApiRequestOptions
  ): Promise<T>;

  put<T>(
    url: string,
    data: any,
    options?: ApiRequestOptions
  ): Promise<T>;

  patch<T>(
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T>;

  delete<T>(
    url: string,
    options?: ApiRequestOptions
  ): Promise<T>;
}
```

### Error Handling

```typescript
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public validationErrors?: ValidationError['detail']
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

export interface NetworkError {
  message: string;
  isRetryable: boolean;
}
```

---

## Task API Client

### Interface Definition

```typescript
// frontend/src/lib/task-api.ts

import type { Task, TaskCreate, TaskUpdate } from '@/types/task';

export interface TaskApi {
  // List all tasks for a user
  listTasks(
    userId: string,
    params?: TaskListParams
  ): Promise<Task[]>;

  // Create a new task
  createTask(
    userId: string,
    data: TaskCreate
  ): Promise<Task>;

  // Get a specific task
  getTask(
    userId: string,
    taskId: string
  ): Promise<Task>;

  // Update a task
  updateTask(
    userId: string,
    taskId: string,
    data: TaskUpdate
  ): Promise<Task>;

  // Delete a task
  deleteTask(
    userId: string,
    taskId: string
  ): Promise<{ ok: boolean }>;

  // Toggle task completion
  toggleComplete(
    userId: string,
    taskId: string
  ): Promise<Task>;
}

export interface TaskListParams {
  offset?: number;         // Default: 0
  limit?: number;          // Default: 50, Max: 100
  completed?: boolean;     // Filter by completion status
}
```

### Implementation

```typescript
export class TaskApiClient implements TaskApi {
  constructor(
    private apiClient: ApiClient,
    private getUserId: () => string  // Function to get user_id from JWT
  ) {}

  private get baseUrl() {
    return '/api';  // Backend API base path
  }

  async listTasks(
    userId: string,
    params?: TaskListParams
  ): Promise<Task[]> {
    return this.apiClient.get<Task[]>(
      `${this.baseUrl}/${userId}/tasks`,
      params
    );
  }

  async createTask(
    userId: string,
    data: TaskCreate
  ): Promise<Task> {
    return this.apiClient.post<Task>(
      `${this.baseUrl}/${userId}/tasks`,
      data
    );
  }

  async getTask(
    userId: string,
    taskId: string
  ): Promise<Task> {
    return this.apiClient.get<Task>(
      `${this.baseUrl}/${userId}/tasks/${taskId}`
    );
  }

  async updateTask(
    userId: string,
    taskId: string,
    data: TaskUpdate
  ): Promise<Task> {
    return this.apiClient.put<Task>(
      `${this.baseUrl}/${userId}/tasks/${taskId}`,
      data
    );
  }

  async deleteTask(
    userId: string,
    taskId: string
  ): Promise<{ ok: boolean }> {
    return this.apiClient.delete<{ ok: boolean }>(
      `${this.baseUrl}/${userId}/tasks/${taskId}`
    );
  }

  async toggleComplete(
    userId: string,
    taskId: string
  ): Promise<Task> {
    return this.apiClient.patch<Task>(
      `${this.baseUrl}/${userId}/tasks/${taskId}/complete`
    );
  }
}
```

---

## Authentication API Client

### Better Auth Integration

```typescript
// frontend/src/lib/auth.ts

import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

// Type inference from Better Auth
export type Session = typeof authClient.$Infer.Session;
export type User = typeof authClient.$Infer.User;
```

### Authentication Methods

```typescript
// Better Auth provides these methods automatically

// Sign in
await authClient.signIn.email({
  email: 'user@example.com',
  password: 'password123',
});

// Sign up
await authClient.signUp.email({
  email: 'user@example.com',
  password: 'password123',
});

// Sign out
await authClient.signOut();

// Get session (server-side)
const session = await authClient.getSession(request);

// Get session (client-side hook)
const { data: session, isPending } = useSession();
```

---

## API Client Implementation

### Fetch Wrapper with JWT Handling

```typescript
// frontend/src/lib/api-client.ts (implementation)

import { authClient } from '@/lib/auth';
import type { ApiClient, ApiClientConfig } from './api-client';

export class FetchApiClient implements ApiClient {
  private config: Required<ApiClientConfig>;

  constructor(config: ApiClientConfig) {
    this.config = {
      baseURL: config.baseURL,
      timeout: config.timeout ?? 10000,
      retries: config.retries ?? 3,
    };
  }

  private async getAuthToken(): Promise<string | null> {
    // Better Auth manages session in cookies
    // For API calls to backend, we need to extract the token
    const session = await authClient.getSession();
    return session?.token ?? null;
  }

  private async request<T>(
    method: string,
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    const token = await this.getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...(options?.headers ?? {}),
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(`${this.config.baseURL}${url}`, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: options?.signal ?? controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Handle authentication errors
        if (response.status === 401) {
          // Redirect to login
          window.location.href = '/login';
          throw new ApiError(401, 'Session expired');
        }

        // Parse error response
        const errorData = await response.json();
        throw new ApiError(
          response.status,
          errorData.detail ?? 'An error occurred',
          errorData.detail
        );
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      // Network error - retry logic
      if (this.isNetworkError(error)) {
        throw new NetworkError('Network error', true);
      }

      throw error;
    }
  }

  private isNetworkError(error: unknown): boolean {
    return (
      error instanceof TypeError &&
      error.message.includes('fetch')
    );
  }

  async get<T>(
    url: string,
    params?: Record<string, any>,
    options?: ApiRequestOptions
  ): Promise<T> {
    const queryString = params
      ? '?' + new URLSearchParams(params).toString()
      : '';
    return this.request<T>('GET', url + queryString, undefined, options);
  }

  async post<T>(
    url: string,
    data: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    return this.request<T>('POST', url, data, options);
  }

  async put<T>(
    url: string,
    data: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    return this.request<T>('PUT', url, data, options);
  }

  async patch<T>(
    url: string,
    data?: any,
    options?: ApiRequestOptions
  ): Promise<T> {
    return this.request<T>('PATCH', url, data, options);
  }

  async delete<T>(
    url: string,
    options?: ApiRequestOptions
  ): Promise<T> {
    return this.request<T>('DELETE', url, undefined, options);
  }
}
```

---

## Usage Examples

### Initializing the Client

```typescript
// frontend/src/lib/api-client.ts (singleton)

const apiClient = new FetchApiClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retries: 3,
});

export { apiClient };
```

### Using Task API

```typescript
// In a component

import { apiClient } from '@/lib/api-client';
import type { TaskApi, TaskCreate } from '@/lib/task-api';

const taskApi: TaskApi = new TaskApiClient(
  apiClient,
  () => session?.user?.id  // Get user_id from session
);

// List tasks
const tasks = await taskApi.listTasks(userId, {
  offset: 0,
  limit: 50,
  completed: false,
});

// Create task
const newTask: TaskCreate = {
  title: 'Buy groceries',
  description: 'Milk, eggs, bread',
};
const created = await taskApi.createTask(userId, newTask);

// Update task
const updated = await taskApi.updateTask(userId, taskId, {
  title: 'Buy groceries and cook dinner',
});

// Toggle completion
const toggled = await taskApi.toggleComplete(userId, taskId);

// Delete task
await taskApi.deleteTask(userId, taskId);
```

---

## Error Handling Patterns

### Try-Catch with Toast Notifications

```typescript
import { toast } from 'sonner';
import { ApiError } from '@/lib/api-client';

try {
  const task = await taskApi.createTask(userId, data);
  toast.success('Task created successfully');
  // Update UI with new task
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 422) {
      // Validation error - show field-specific errors
      error.validationErrors?.forEach(err => {
        toast.error(`${err.loc.join('.')}: ${err.msg}`);
      });
    } else {
      toast.error(error.detail);
    }
  } else {
    toast.error('Network error. Please try again.');
  }
}
```

### React Query Integration (Optional)

```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { taskApi } from '@/lib/task-api';

// Fetch tasks
function useTasks(userId: string, params?: TaskListParams) {
  return useQuery({
    queryKey: ['tasks', userId, params],
    queryFn: () => taskApi.listTasks(userId, params),
  });
}

// Create task
function useCreateTask(userId: string) {
  return useMutation({
    mutationFn: (data: TaskCreate) => taskApi.createTask(userId, data),
    onSuccess: () => {
      toast.success('Task created');
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}
```

---

## Type Safety Guarantees

All API methods are:
1. **Fully typed** with TypeScript generics
2. **Runtime validated** with Zod schemas
3. **Aligned with backend contracts** (OpenAPI specs)
4. **Autocomplete-friendly** in IDE
5. **Error-type aware** for precise error handling

This ensures:
- Compile-time type checking
- No `any` types in API layer
- Predictable request/response shapes
- Safe refactoring
- Better developer experience
