/* Task type definitions for frontend task management.

[Task]: T009
[From]: specs/003-frontend-task-manager/data-model.md
*/
export interface Task {
  id: string;                  // UUID format
  user_id: string;             // UUID (from JWT, not displayed in UI)
  title: string;               // 1-255 characters, required
  description: string | null;  // Optional, max 2000 characters
  completed: boolean;          // Completion status
  created_at: string;          // ISO 8601 datetime (UTC)
  updated_at: string;          // ISO 8601 datetime (UTC)
}

export type TaskCreate = Pick<TaskFormData, 'title' | 'description'>;

export type TaskUpdate = Partial<Pick<Task, 'title' | 'description' | 'completed'>>;

import type { TaskFormData } from './forms';
