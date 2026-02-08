-- ChatKit Migration: Create threads table and update messages table
--
-- [From]: specs/010-chatkit-migration/data-model.md - Database Schema Migration
-- [Task]: T006
--
-- This migration:
-- 1. Creates the threads table for ChatKit conversation management
-- 2. Adds thread_id column to messages table
-- 3. Migrates existing conversation_id data to thread_id
-- 4. Creates indexes for query optimization
--
-- IMPORTANT: Run this migration after deploying the Thread model
--
-- To run: psql $DATABASE_URL < migrations/migrate_threads.sql

-- BEGIN;

-- 1. Create threads table
CREATE TABLE IF NOT EXISTS threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create indexes for threads table
CREATE INDEX IF NOT EXISTS idx_thread_user_id ON threads(user_id);
CREATE INDEX IF NOT EXISTS idx_thread_updated_at ON threads(user_id, updated_at DESC);

-- 3. Add thread_id column to messages table (nullable initially)
ALTER TABLE message ADD COLUMN IF NOT EXISTS thread_id UUID REFERENCES threads(id) ON DELETE CASCADE;

-- 4. Create index for thread_id in messages table
CREATE INDEX IF NOT EXISTS idx_message_thread_id ON message(thread_id, created_at ASC);

-- 5. Migrate existing conversation data to threads
-- This creates a thread for each unique conversation and links messages to it
-- Skip this step if starting fresh (no existing conversations)
INSERT INTO threads (id, user_id, created_at, updated_at)
SELECT DISTINCT
    c.id as id,           -- Use same ID as conversation for easy mapping
    c.user_id,
    c.created_at,
    c.updated_at
FROM conversation c
WHERE NOT EXISTS (SELECT 1 FROM threads t WHERE t.id = c.id);

-- 6. Update messages to point to the new thread_id
-- This maps existing messages to their corresponding threads
UPDATE message m
SET thread_id = m.conversation_id
WHERE m.conversation_id IS NOT NULL
  AND m.thread_id IS NULL;

-- 7. After migration, make thread_id NOT NULL (only after validating data)
-- Uncomment these lines after verifying successful migration:
-- ALTER TABLE message ALTER COLUMN thread_id SET NOT NULL;
-- ALTER TABLE message ADD CONSTRAINT message_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE;

-- Optional: Drop old conversation_id column after full migration
-- Uncomment ONLY after confirming ChatKit is working correctly:
-- ALTER TABLE message DROP COLUMN IF EXISTS conversation_id;
-- DROP INDEX IF EXISTS idx_message_conversation_created;

-- COMMIT;

-- Rollback commands (if needed):
-- BEGIN;
-- ALTER TABLE message DROP COLUMN IF EXISTS thread_id;
-- DROP INDEX IF EXISTS idx_message_thread_id;
-- DROP INDEX IF EXISTS idx_thread_user_id;
-- DROP INDEX IF EXISTS idx_thread_updated_at;
-- DROP TABLE IF EXISTS threads;
-- COMMIT;
