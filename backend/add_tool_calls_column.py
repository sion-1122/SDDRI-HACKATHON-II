#!/usr/bin/env python3
"""Add tool_calls column to message table."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_tool_calls_column():
    """Add tool_calls column to message table."""
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.connect() as conn:
        # Add tool_calls column if it doesn't exist
        conn.execute(text("""
            ALTER TABLE message
            ADD COLUMN IF NOT EXISTS tool_calls JSONB
        """))
        print("✅ Added tool_calls column to message table")

        conn.commit()

if __name__ == "__main__":
    add_tool_calls_column()
