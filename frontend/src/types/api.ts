/* API response type definitions.

[Task]: T014
[From]: specs/003-frontend-task-manager/data-model.md
*/

import type { Task } from './task';

// Success Responses
export interface TaskListResponse {
  tasks: Task[];
  total: number;
  offset: number;
  limit: number;
}

export interface TaskResponse {
  task: Task;
}

export interface DeleteTaskResponse {
  ok: boolean;
}

// Authentication Responses (Better Auth handles these)
export interface SignUpRequest {
  email: string;
  password: string;
}

export interface SignUpResponse {
  user?: {
    id: string;
    email: string;
    created_at: string;
  };
  message?: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface SignInResponse {
  token?: string;
  user?: {
    id: string;
    email: string;
    created_at: string;
  };
}

export interface SignOutResponse {
  ok: boolean;
}

export interface SessionResponse {
  authenticated: boolean;
  user?: {
    id: string;
    email: string;
    created_at: string;
  };
}

// Error Responses
export interface ApiError {
  detail: string;          // Human-readable error message
}

export interface ValidationError {
  detail: Array<{
    loc: string[];         // Field path (e.g., ['body', 'title'])
    msg: string;           // Error message
    type: string;          // Error type (e.g., 'value_error.min_length')
  }>;
}

// Error Display Logic
export function displayError(error: ApiError | ValidationError): string {
  if ('detail' in error && typeof error.detail === 'string') {
    return error.detail;
  }
  if ('detail' in error && Array.isArray(error.detail)) {
    return error.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
  }
  return 'An unexpected error occurred';
}
