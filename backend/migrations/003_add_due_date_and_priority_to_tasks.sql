-- Add due_date and priority columns to tasks table
-- Migration: 003
-- [From]: specs/004-ai-chatbot/plan.md - Task Model Extensions

-- Add due_date column (nullable, with index for filtering)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Add priority column with default value
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
