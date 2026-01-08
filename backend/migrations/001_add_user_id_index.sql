-- Add index on tasks.user_id for improved query performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
