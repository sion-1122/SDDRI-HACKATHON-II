"""Database migration runner.

[Task]: T022, T023
[From]: specs/001-user-auth/tasks.md

This script runs SQL migrations against the database.

Usage:
    uv run python migrations/run_migration.py
"""
import os
import sys
from pathlib import Path
from sqlmodel import Session, text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import engine


def run_migration(migration_file: str):
    """Run a single SQL migration file.

    Args:
        migration_file: Name of the migration file in migrations/ directory
    """
    migration_path = Path(__file__).parent / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False

    print(f"📜 Running migration: {migration_file}")

    with open(migration_path, "r") as f:
        sql = f.read()

    try:
        with Session(engine) as session:
            # Execute the migration using text()
            session.exec(text(sql))
            session.commit()

        print(f"✅ Migration completed successfully: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Run pending migrations."""
    # Migration files in order
    migrations = [
        "001_add_user_id_index.sql",
        "002_add_conversation_and_message_tables.sql",  # Phase III: AI Chatbot
        "003_add_due_date_and_priority_to_tasks.sql",   # Phase III: UX Improvements
        "004_add_performance_indexes.sql",              # Phase III: UX Improvements
        "005_add_tags_to_tasks.sql",                    # Phase VII: Intermediate Features
        "008_add_advanced_features.sql",                # Phase VIII: Advanced Features
    ]

    print("🚀 Starting database migrations...\n")

    success_count = 0
    for migration in migrations:
        if run_migration(migration):
            success_count += 1
        print()

    print(f"✅ {success_count}/{len(migrations)} migrations completed successfully")

    if success_count == len(migrations):
        print("\n🎉 All migrations completed!")
        print("\n📊 Database schema is ready for authentication.")
        return 0
    else:
        print("\n⚠️  Some migrations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
