-- Migration: Add advanced features to tasks table
-- Version: 008_advanced_features
-- Date: 2026-02-04
-- [Task]: T001

-- Step 1: Add new columns for reminders
ALTER TABLE tasks
  ADD COLUMN IF NOT EXISTS reminder_offset INTEGER,
  ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;

-- Step 2: Add new columns for recurrence
ALTER TABLE tasks
  ADD COLUMN IF NOT EXISTS recurrence JSONB,
  ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL;

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_reminder_sent ON tasks(reminder_sent) WHERE reminder_sent = FALSE;

-- Step 4: Add constraints (without IF NOT EXISTS - use DO blocks instead)
DO $$
BEGIN
  -- Add reminder offset positive constraint
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_reminder_offset_positive'
  ) THEN
    ALTER TABLE tasks
      ADD CONSTRAINT chk_reminder_offset_positive
        CHECK (reminder_offset IS NULL OR reminder_offset >= 0);
  END IF;

  -- Add recurrence no self-reference constraint
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_recurrence_no_self_reference'
  ) THEN
    ALTER TABLE tasks
      ADD CONSTRAINT chk_recurrence_no_self_reference
        CHECK (parent_task_id IS NULL OR id != parent_task_id);
  END IF;
END $$;

-- Step 5: Add comments for documentation
COMMENT ON COLUMN tasks.reminder_offset IS 'Minutes before due_date to send notification (0 = at due time)';
COMMENT ON COLUMN tasks.reminder_sent IS 'Whether notification has been sent for this task';
COMMENT ON COLUMN tasks.recurrence IS 'Recurrence rule as JSONB (frequency, interval, count, end_date)';
COMMENT ON COLUMN tasks.parent_task_id IS 'For recurring task instances, links to the original task';

-- Step 6: Create validation function for recurrence JSONB
CREATE OR REPLACE FUNCTION validate_recurrence(rule jsonb)
RETURNS boolean AS $$
BEGIN
  -- Check frequency is present and valid
  IF rule->>'frequency' NOT IN ('daily', 'weekly', 'monthly') THEN
    RETURN false;
  END IF;

  -- Check interval is valid if present
  IF (rule->>'interval') IS NOT NULL THEN
    IF (rule->>'interval')::integer < 1 OR (rule->>'interval')::integer > 365 THEN
      RETURN false;
    END IF;
  END IF;

  -- Check count is valid if present
  IF (rule->>'count') IS NOT NULL THEN
    IF (rule->>'count')::integer < 1 OR (rule->>'count')::integer > 100 THEN
      RETURN false;
    END IF;
  END IF;

  RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Step 7: Add recurrence valid constraint
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_recurrence_valid'
  ) THEN
    ALTER TABLE tasks
      ADD CONSTRAINT chk_recurrence_valid
        CHECK (recurrence IS NULL OR validate_recurrence(recurrence));
  END IF;
END $$;
