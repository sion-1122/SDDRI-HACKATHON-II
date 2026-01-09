"""Database initialization script.

Creates all database tables.

[Task]: T021
[From]: specs/001-user-auth/plan.md
"""
import sys
import os

# Add parent directory to path to import from backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import init_db


def main():
    """Initialize database tables."""
    print("Initializing database...")

    try:
        init_db()
        print("✓ Database initialized successfully")
        print("✓ Tables created: users")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
