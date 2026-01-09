"""Database migration script: Drop old Better Auth tables and create new ones.

This script drops the old users table (from Better Auth) and recreates it
with the new schema for FastAPI JWT authentication.

[From]: specs/001-user-auth/plan.md
"""
import sys
import os

# Add parent directory to path to import from backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import SQLModel, Session, create_engine, text
from core.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(settings.database_url)


def drop_old_tables():
    """Drop old Better Auth tables."""
    print("Dropping old tables...")

    with Session(engine) as session:
        try:
            # Drop the old users table if it exists
            session.exec(text("DROP TABLE IF EXISTS users CASCADE"))
            session.commit()
            print("✓ Dropped old 'users' table")
        except Exception as e:
            print(f"✗ Error dropping tables: {e}")
            session.rollback()
            raise


def create_new_tables():
    """Create new tables with the updated schema."""
    print("\nCreating new tables...")

    from models.user import User  # Import to register with SQLModel

    SQLModel.metadata.create_all(engine)
    print("✓ Created new 'users' table with schema:")
    print("  - id: UUID (primary key)")
    print("  - email: VARCHAR(255) (unique, indexed)")
    print("  - hashed_password: VARCHAR(255)")
    print("  - created_at: TIMESTAMP")
    print("  - updated_at: TIMESTAMP")


def verify_schema():
    """Verify the new schema was created correctly."""
    print("\nVerifying schema...")

    with Session(engine) as session:
        result = session.exec(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))

        print("\nTable structure:")
        for row in result:
            print(f"  - {row.column_name}: {row.data_type}")


def main():
    """Run the migration."""
    print("=" * 60)
    print("DATABASE MIGRATION: Better Auth → FastAPI JWT")
    print("=" * 60)

    print("\n⚠️  WARNING: This will DELETE all existing user data!")
    print("    Old Better Auth tables will be dropped.\n")

    # Ask for confirmation
    response = input("Continue? (yes/no): ").strip().lower()

    if response not in ["yes", "y"]:
        print("\n❌ Migration cancelled.")
        sys.exit(0)

    try:
        # Step 1: Drop old tables
        drop_old_tables()

        # Step 2: Create new tables
        create_new_tables()

        # Step 3: Verify schema
        verify_schema()

        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart the backend server")
        print("2. Test registration at http://localhost:8000/docs")
        print("3. Create a new user account")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED!")
        print("=" * 60)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
