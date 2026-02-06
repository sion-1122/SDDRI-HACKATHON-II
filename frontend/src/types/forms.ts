/* Form data type definitions.

[Task]: T011, T048, T071
[From]: specs/003-frontend-task-manager/data-model.md, specs/005-ux-improvement/data-model.md, specs/008-advanced-features/tasks.md (User Story 2, User Story 3)
*/

import type { TaskPriority } from './task';
import type { RecurrenceRule } from './recurrence';

// Task Form
export interface TaskFormData {
  title: string;
  description: string;
  due_date: string | null;
  priority: TaskPriority;
  tags: string[];  // [T035] Array of tag names
  reminder_offset: number | null;  // [T048] Minutes before due date to notify (0 = at due time)
  recurrence: RecurrenceRule | null;  // [T071] Recurrence rule for repeating tasks
}

export interface TaskFormErrors {
  title?: string;
  description?: string;
}

// Login Form
export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginFormErrors {
  email?: string;
  password?: string;
}

// Register Form
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

// Generic form state
export interface FormState<T> {
  data: T;
  errors: Record<keyof T, string | undefined>;
  touched: Record<keyof T, boolean>;
  isSubmitting: boolean;
}
