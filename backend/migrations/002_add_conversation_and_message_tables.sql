-- Migration: Add conversation and message tables for AI Chatbot (Phase III)
-- [Task]: T007
-- [From]: specs/004-ai-chatbot/plan.md

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversation table
CREATE TABLE IF NOT EXISTS conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index on user_id for conversation lookup
CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversation(updated_at DESC);

-- Create composite index for user's conversations ordered by update time
CREATE INDEX IF NOT EXISTS idx_conversation_user_updated ON conversation(user_id, updated_at DESC);

-- Create message table
CREATE TABLE IF NOT EXISTS message (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for message queries
CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON message(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_user_id ON message(user_id);
CREATE INDEX IF NOT EXISTS idx_message_role ON message(role);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at DESC);

-- Create composite index for conversation messages (optimization for loading conversation history)
CREATE INDEX IF NOT EXISTS idx_message_conversation_created ON message(conversation_id, created_at ASC);

-- Add trigger to update conversation.updated_at when new message is added
-- This requires PL/pgSQL
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists to avoid errors
DROP TRIGGER IF EXISTS trigger_update_conversation_updated_at ON message;

-- Create trigger
CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT ON message
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();

-- Add comment for documentation
COMMENT ON TABLE conversation IS 'Stores chat sessions between users and AI assistant';
COMMENT ON TABLE message IS 'Stores individual messages in conversations';
COMMENT ON COLUMN message.role IS 'Either "user" or "assistant" - who sent the message';
COMMENT ON COLUMN message.content IS 'Message content with max length of 10,000 characters';
