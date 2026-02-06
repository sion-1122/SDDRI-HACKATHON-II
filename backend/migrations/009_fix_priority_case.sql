-- Migration 009: Fix priority values to match enum (uppercase)
-- [Task]: Data fix for existing tasks
-- [From]: Issue with existing lowercase priority values

-- Update all priority values to uppercase to match PriorityLevel enum
UPDATE tasks
SET priority = CASE
    WHEN priority = 'low' THEN 'LOW'
    WHEN priority = 'medium' THEN 'MEDIUM'
    WHEN priority = 'high' THEN 'HIGH'
    ELSE priority
END
WHERE priority IN ('low', 'medium', 'high');

-- Verify the update
SELECT COUNT(*) as tasks_updated FROM tasks;
