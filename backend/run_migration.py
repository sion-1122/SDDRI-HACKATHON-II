#!/usr/bin/env python3
"""Run the ChatKit migration to create threads table."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration():
    """Execute the migration SQL."""
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.connect() as conn:
        # Create threads table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS threads (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255),
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        print("✅ Created threads table")

        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_thread_user_id ON threads(user_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_thread_updated_at ON threads(user_id, updated_at DESC)
        """))
        print("✅ Created threads table indexes")

        # Add thread_id column to messages table
        conn.execute(text("""
            ALTER TABLE message ADD COLUMN IF NOT EXISTS thread_id UUID REFERENCES threads(id) ON DELETE CASCADE
        """))
        print("✅ Added thread_id column to message table")

        # Create index for thread_id in messages table
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_thread_id ON message(thread_id, created_at ASC)
        """))
        print("✅ Created message thread_id index")

        # Migrate existing conversations to threads
        result = conn.execute(text("""
            INSERT INTO threads (id, user_id, created_at, updated_at)
            SELECT DISTINCT
                c.id as id,
                c.user_id,
                c.created_at,
                c.updated_at
            FROM conversation c
            WHERE NOT EXISTS (SELECT 1 FROM threads t WHERE t.id = c.id)
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """))
        migrated_threads = result.fetchall()
        print(f"✅ Migrated {len(migrated_threads)} conversations to threads")

        # Update messages to point to the new thread_id
        result = conn.execute(text("""
            UPDATE message m
            SET thread_id = m.conversation_id
            WHERE m.conversation_id IS NOT NULL
              AND m.thread_id IS NULL
            RETURNING id
        """))
        updated_messages = result.fetchall()
        print(f"✅ Updated {len(updated_messages)} messages with thread_id")

        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
