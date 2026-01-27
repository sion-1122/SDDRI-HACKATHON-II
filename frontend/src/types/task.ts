/* Task type definitions for frontend task management.

[Task]: T009, T010, T011
[From]: specs/003-frontend-task-manager/data-model.md, specs/005-ux-improvement/data-model.md
*/

import type { TaskFormData } from './forms';

// Task urgency computed from due date (not from backend)
export type TaskUrgency = 'overdue' | 'due-today' | 'due-soon' | 'due-later' | 'none';

// Task priority levels
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;                  // UUID format
  user_id: string;             // UUID (from JWT, not displayed in UI)
  title: string;               // 1-255 characters, required
  description: string | null;  // Optional, max 2000 characters
  due_date: string | null;     // ISO 8601 datetime or null [T010]
  priority: TaskPriority;      // Priority level [T010]
  completed: boolean;          // Completion status
  created_at: string;          // ISO 8601 datetime (UTC)
  updated_at: string;          // ISO 8601 datetime (UTC)

  // Computed UI properties (not from backend) [T011]
  urgency?: TaskUrgency;
}

export type TaskCreate = Pick<TaskFormData, 'title' | 'description' | 'due_date' | 'priority'>;

export type TaskUpdate = Partial<Pick<Task, 'title' | 'description' | 'due_date' | 'priority' | 'completed'>>;

// Re-export TaskFormData for convenience
export type { TaskFormData } from './forms';
