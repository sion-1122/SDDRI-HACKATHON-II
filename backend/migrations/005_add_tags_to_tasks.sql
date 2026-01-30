-- Add tags column to tasks table
-- Migration: 005_add_tags_to_tasks.sql
-- [Task]: T036, T037
-- [From]: specs/007-intermediate-todo-features/tasks.md

-- Add tags column as TEXT array (default: empty array)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT[] NOT NULL DEFAULT '{}';

-- Add index on tags for faster tag-based queries
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN (tags);

-- Add comment for documentation
COMMENT ON COLUMN tasks.tags IS 'Array of tag strings associated with the task';
