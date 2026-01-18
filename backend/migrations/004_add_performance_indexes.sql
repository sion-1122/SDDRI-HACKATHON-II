-- Database indexes for conversation and message queries
--
-- [Task]: T059
-- [From]: specs/004-ai-chatbot/tasks.md
--
-- These indexes optimize common queries for:
-- - Conversation lookup by user_id
-- - Message lookup by conversation_id
-- - Message ordering by created_at
-- - Composite indexes for filtering

-- Index on conversations for user lookup
-- Optimizes: SELECT * FROM conversations WHERE user_id = ?
CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);

-- Index on conversations for updated_at sorting (cleanup)
-- Optimizes: SELECT * FROM conversations WHERE updated_at < ? (90-day cleanup)
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at);

-- Composite index for user conversations ordered by activity
-- Optimizes: SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
    ON conversations(user_id, updated_at DESC);

-- Index on messages for conversation lookup
-- Optimizes: SELECT * FROM messages WHERE conversation_id = ?
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

-- Index on messages for user lookup
-- Optimizes: SELECT * FROM messages WHERE user_id = ?
CREATE INDEX IF NOT EXISTS idx_messages_user_id
    ON messages(user_id);

-- Index on messages for timestamp ordering
-- Optimizes: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC
CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at);

-- Composite index for conversation message retrieval
-- Optimizes: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
    ON messages(conversation_id, created_at ASC);

-- Index on messages for role filtering
-- Optimizes: SELECT * FROM messages WHERE conversation_id = ? AND role = ?
CREATE INDEX IF NOT EXISTS idx_messages_conversation_role
    ON messages(conversation_id, role);

-- Index on tasks for user lookup (if not exists)
-- Optimizes: SELECT * FROM tasks WHERE user_id = ?
CREATE INDEX IF NOT EXISTS idx_tasks_user_id
    ON tasks(user_id);

-- Index on tasks for completion status filtering
-- Optimizes: SELECT * FROM tasks WHERE user_id = ? AND completed = ?
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed
    ON tasks(user_id, completed);

-- Index on tasks for due date filtering
-- Optimizes: SELECT * FROM tasks WHERE user_id = ? AND due_date IS NOT NULL AND due_date < ?
CREATE INDEX IF NOT EXISTS idx_tasks_due_date
    ON tasks(due_date) WHERE due_date IS NOT NULL;

-- Composite index for task priority filtering
-- Optimizes: SELECT * FROM tasks WHERE user_id = ? AND priority = ?
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority
    ON tasks(user_id, priority);

-- Index on tasks for created_at sorting
-- Optimizes: SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_tasks_user_created
    ON tasks(user_id, created_at DESC);
