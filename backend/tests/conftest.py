"""Pytest configuration and fixtures."""
import os
import uuid
import sys
from pathlib import Path
from typing import Generator

# Set DATABASE_URL before any application imports
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, SQLModel, create_engine
import pytest
from fastapi.testclient import TestClient

from models.user import User
from models.task import Task
from main import app
from core.deps import get_session


@pytest.fixture(name="test_db")
def test_db_engine(tmp_path):
    """Create a file-based SQLite database for testing.

    This fixture provides a fresh database for each test.
    Uses file-based storage to avoid issues with in-memory database connection isolation.
    Also patches the global database engine to ensure the app uses this test database.
    """
    from core.database import engine as original_engine
    import core.database

    # Create test database file
    db_file = tmp_path / "test.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(test_engine)

    # Patch the global engine
    core.database.engine = test_engine

    yield test_engine

    # Restore original engine
    core.database.engine = original_engine


@pytest.fixture(name="test_session")
def test_session(test_db):
    """Create a database session for testing.

    The session is automatically cleaned up after each test.
    """
    with Session(test_db) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture():
    """Provide a test user with a random UUID.

    This fixture creates a User instance without persisting it to a database.
    """
    return User(id=uuid.uuid4())


@pytest.fixture(name="client")
def test_client(test_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with a test database session.

    This fixture overrides the database dependency to use the test database.
    """

    def override_get_session():
        """Override the database session dependency."""
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
