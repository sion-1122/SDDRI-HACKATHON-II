"""Database configuration and engine setup."""
import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Initialize database tables.

    Uses the current engine from config module to support testing.
    """
    from models.user import User
    from models.task import Task

    SQLModel.metadata.create_all(engine)
