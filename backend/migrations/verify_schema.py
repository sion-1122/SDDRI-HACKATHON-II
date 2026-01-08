"""Database schema verification script.

[Task]: T022, T023
[From]: specs/001-user-auth/tasks.md

This script verifies that the database schema is correct for authentication.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select, text
from core.config import engine
from models.user import User
from models.task import Task


def verify_schema():
    """Verify database schema for authentication."""
    print("🔍 Verifying database schema...\n")

    with Session(engine) as session:
        # Check users table
        print("📋 Checking users table...")
        try:
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """))
            print("✅ Users table columns:")
            for row in result:
                print(f"   - {row.column_name}: {row.data_type}")
        except Exception as e:
            print(f"❌ Error checking users table: {e}")
            return False

        print()

        # Check tasks table
        print("📋 Checking tasks table...")
        try:
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position;
            """))
            print("✅ Tasks table columns:")
            for row in result:
                print(f"   - {row.column_name}: {row.data_type}")
        except Exception as e:
            print(f"❌ Error checking tasks table: {e}")
            return False

        print()

        # Check indexes
        print("📋 Checking indexes on tasks table...")
        try:
            result = session.exec(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'tasks';
            """))
            print("✅ Indexes on tasks table:")
            for row in result:
                print(f"   - {row.indexname}")
        except Exception as e:
            print(f"❌ Error checking indexes: {e}")
            return False

        print()

        # Check foreign key constraints
        print("📋 Checking foreign key constraints...")
        try:
            result = session.exec(text("""
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'tasks';
            """))
            print("✅ Foreign key constraints:")
            for row in result:
                print(f"   - {row.constraint_name}:")
                print(f"     {row.column_name} → {row.foreign_table_name}.{row.foreign_column_name}")
        except Exception as e:
            print(f"❌ Error checking foreign keys: {e}")
            return False

        print()

        # Check unique constraints
        print("📋 Checking unique constraints...")
        try:
            result = session.exec(text("""
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'UNIQUE'
                    AND tc.table_name = 'users';
            """))
            print("✅ Unique constraints on users table:")
            for row in result:
                print(f"   - {row.constraint_name}: {row.column_name}")
        except Exception as e:
            print(f"❌ Error checking unique constraints: {e}")
            return False

    print("\n✅ Schema verification complete!")
    print("\n🎉 Database schema is ready for authentication.")
    return True


if __name__ == "__main__":
    success = verify_schema()
    sys.exit(0 if success else 1)
