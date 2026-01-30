/* Form Zod validation schemas.

[Task]: T016, T038
[From]: specs/003-frontend-task-manager/data-model.md, specs/007-intermediate-todo-features/tasks.md
*/
import { z } from 'zod';

// Task Form Schema [T038] - extended with priority, due_date, tags
export const taskFormSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(255, 'Title must be less than 255 characters'),
  description: z.string()
    .max(2000, 'Description must be less than 2000 characters')
    .optional(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH'], {
    message: 'Priority must be LOW, MEDIUM, or HIGH',
  }),
  due_date: z.string().nullable().optional(),
  tags: z.array(z.string().max(50, 'Tag name must be less than 50 characters')).optional(),
});

export type TaskFormData = z.infer<typeof taskFormSchema>;

// Login Form Schema
export const loginFormSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z.string()
    .min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginFormSchema>;

// Register Form Schema
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

export type RegisterFormData = z.infer<typeof registerFormSchema>;
