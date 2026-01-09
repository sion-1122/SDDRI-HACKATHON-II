/* Task Zod validation schema.

[Task]: T015
[From]: specs/003-frontend-task-manager/data-model.md
*/
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
