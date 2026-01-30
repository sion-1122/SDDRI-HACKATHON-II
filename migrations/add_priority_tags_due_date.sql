-- Migration: Add priority enum constraint, tags array, and ensure due_date is TIMESTAMPTZ
-- Feature: 007-intermediate-todo-features
-- Date: 2026-01-28
--
-- This migration adds:
-- 1. Tags column (TEXT array) for task categorization
-- 2. Ensures priority column has proper check constraint
-- 3. Ensures due_date is timezone-aware (TIMESTAMPTZ)
-- 4. Adds indexes for performance

-- ================================================================================
-- Step 1: Add tags column if it doesn't exist
-- ================================================================================

DO $$
BEGIN
    -- Check if tags column exists, if not add it
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        AND column_name = 'tags'
    ) THEN
        ALTER TABLE tasks
        ADD COLUMN tags TEXT[] NOT NULL DEFAULT '{}';

        RAISE NOTICE 'Added tags column to tasks table';
    ELSE
        RAISE NOTICE 'tags column already exists in tasks table';
    END IF;
END $$;

-- ================================================================================
-- Step 2: Ensure priority column has check constraint
-- ================================================================================

DO $$
BEGIN
    -- Drop existing check constraint if it exists (will recreate)
    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'check_priority'
    ) THEN
        ALTER TABLE tasks DROP CONSTRAINT check_priority;
        RAISE NOTICE 'Dropped existing check_priority constraint';
    END IF;

    -- Add the check constraint for priority values
    ALTER TABLE tasks
    ADD CONSTRAINT check_priority
    CHECK (priority IN ('high', 'medium', 'low'));

    RAISE NOTICE 'Added check_priority constraint';
END $$;

-- ================================================================================
-- Step 3: Ensure due_date is TIMESTAMPTZ (timezone-aware)
-- ================================================================================

DO $$
BEGIN
    -- Check if due_date column exists and is not TIMESTAMPTZ
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        AND column_name = 'due_date'
    ) THEN
        -- Get current data type of due_date
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            AND column_name = 'due_date'
            AND data_type = 'timestamp with time zone'
        ) THEN
            -- Convert to TIMESTAMPTZ (assume existing timestamps are UTC)
            ALTER TABLE tasks
            ALTER COLUMN due_date TYPE TIMESTAMPTZ
            USING due_date::timestamp with time zone;

            RAISE NOTICE 'Converted due_date to TIMESTAMPTZ';
        ELSE
            RAISE NOTICE 'due_date is already TIMESTAMPTZ';
        END IF;
    ELSE
        -- Add due_date column if it doesn't exist
        ALTER TABLE tasks
        ADD COLUMN due_date TIMESTAMPTZ;

        RAISE NOTICE 'Added due_date column to tasks table';
    END IF;
END $$;

-- ================================================================================
-- Step 4: Create indexes for performance
-- ================================================================================

-- Index on due_date for time-based queries
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Index on priority for filtering
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Index on completed status for filtering
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

-- Composite index for common filter combinations (user + priority + status)
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority_status
ON tasks(user_id, priority, completed);

-- GIN index for tag array searching
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN (tags);

RAISE NOTICE 'Created all indexes';

-- ================================================================================
-- Step 5: Backward compatibility - Set defaults for existing records
-- ================================================================================

-- Ensure all existing tasks have medium priority
UPDATE tasks
SET priority = 'medium'
WHERE priority IS NULL OR priority NOT IN ('high', 'medium', 'low');

-- Ensure all existing tasks have empty tags array
UPDATE tasks
SET tags = '{}'
WHERE tags IS NULL;

RAISE NOTICE 'Updated existing records with defaults';

-- ================================================================================
-- Migration Complete
-- ================================================================================

-- Verification query (uncomment to verify)
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'tasks'
-- AND column_name IN ('priority', 'tags', 'due_date')
-- ORDER BY column_name;
