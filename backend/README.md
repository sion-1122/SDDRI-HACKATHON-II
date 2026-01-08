# Todo List Backend API

FastAPI-based REST API for managing tasks with PostgreSQL persistence.

## Features

- ✅ Full CRUD operations for tasks
- ✅ User-scoped data isolation
- ✅ Pagination and filtering
- ✅ Automatic timestamp tracking
- ✅ Input validation
- ✅ Error handling
- ✅ OpenAPI documentation

## Tech Stack

- Python 3.13+
- FastAPI (web framework)
- SQLModel (ORM)
- Neon PostgreSQL (database)
- UV (package manager)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### 3. Run Development Server

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

API will be available at http://localhost:8000

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks` | List tasks (with pagination/filtering) |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend tests/

# Run specific test file
uv run pytest tests/test_api_tasks.py -v
```

## Project Structure

```
backend/
├── models/          # SQLModel database models
│   ├── user.py      # User entity
│   └── task.py      # Task entity and I/O models
├── api/             # FastAPI route handlers
│   └── tasks.py     # Task CRUD endpoints
├── core/            # Configuration and dependencies
│   ├── config.py    # Database engine
│   └── deps.py      # Dependency injection
├── tests/           # Test suite
│   ├── conftest.py  # Pytest fixtures
│   └── test_api_tasks.py
├── main.py          # FastAPI application
└── pyproject.toml   # UV project configuration
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db?sslmode=require` |
| `ENVIRONMENT` | Environment name | `development` or `production` |
| `LOG_LEVEL` | Logging level | `INFO`, `DEBUG`, `WARNING`, `ERROR` |

## Development

### Code Style

- Follow PEP 8
- Type hints required
- Docstrings for public functions

### Database

Tables are automatically created on startup. For production, consider using Alembic for migrations.

## License

MIT
