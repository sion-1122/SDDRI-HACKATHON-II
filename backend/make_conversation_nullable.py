#!/usr/bin/env python3
"""Make conversation_id nullable in message table."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def make_conversation_nullable():
    """Make conversation_id column nullable in message table."""
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.connect() as conn:
        # Make conversation_id nullable to support threads
        conn.execute(text("""
            ALTER TABLE message
            ALTER COLUMN conversation_id DROP NOT NULL
        """))
        print("✅ Made conversation_id nullable in message table")

        conn.commit()

if __name__ == "__main__":
    make_conversation_nullable()
