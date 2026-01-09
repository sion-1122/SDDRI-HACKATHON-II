/* Form data type definitions.

[Task]: T011
[From]: specs/003-frontend-task-manager/data-model.md
*/

// Task Form
export interface TaskFormData {
  title: string;
  description: string;
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
