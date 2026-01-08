# Quickstart Guide: Backend Task CRUD API

**Feature**: 001-backend-task-api
**Date**: 2026-01-08
**Prerequisites**: Python 3.13+, UV package manager, Neon PostgreSQL account

## Setup (5 minutes)

### 1. Create Backend Directory Structure

```bash
cd /mnt/d/class/todo-list-hackathon/backend
mkdir -p src/{models,api,core}
mkdir -p tests/{unit,integration}
touch pyproject.toml
```

### 2. Initialize UV Project

```bash
cd backend
uv init --lib
```

### 3. Install Dependencies

```bash
uv add fastapi sqlmodel uvicorn[standard] psycopg2-binary python-dotenv
uv add --dev pytest pytest-asyncio httpx
```

### 4. Set Environment Variables

Create `.env` file:
```bash
DATABASE_URL=postgresql://user:password@ep-xyz.region.aws.neon.tech/dbname?sslmode=require
```

Get connection string from Neon dashboard (free tier: https://neon.tech).

---

## Project Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel classes
│   │   └── user.py          # User SQLModel classes
│   ├── api/
│   │   ├── __init__.py
│   │   └── tasks.py         # Task endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Database engine
│   │   └── deps.py          # Dependencies (get_session)
│   └── main.py              # FastAPI app
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api_tasks.py    # API endpoint tests
│   └── test_models.py       # Model tests
├── .env                     # Environment variables (not in git)
└── pyproject.toml           # UV project config
```

---

## Implementation Steps

### Step 1: Database Configuration

Create `src/core/config.py`:
```python
import os
from sqlmodel import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from sqlmodel import SQLModel
    from src.models.task import Task
    from src.models.user import User

    SQLModel.metadata.create_all(engine)
```

### Step 2: Dependency Injection

Create `src/core/deps.py`:
```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from src.core.config import engine

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

### Step 3: Define Models

Create `src/models/task.py`:
```python
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

Create `src/models/user.py`:
```python
import uuid
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
```

### Step 4: Implement API Endpoints

Create `src/api/tasks.py`:
```python
import uuid
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from src.core.deps import SessionDep
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    user_id: uuid.UUID,
    task: TaskCreate,
    session: SessionDep
):
    db_task = Task.model_validate(task)
    db_task.user_id = user_id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("", response_model=list[TaskRead])
def list_tasks(
    user_id: uuid.UUID,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    completed: bool | None = None
):
    statement = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        statement = statement.where(Task.completed == completed)
    statement = statement.offset(offset).limit(limit)
    tasks = session.exec(statement).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    session: SessionDep
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"ok": True}

@router.patch("/{task_id}/complete", response_model=TaskRead)
def toggle_complete(
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Step 5: Wire Up FastAPI App

Create `src/main.py`:
```python
from fastapi import FastAPI
from src.api.tasks import router as tasks_router
from src.core.config import init_db

app = FastAPI(title="Todo List API")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(tasks_router)
```

---

## Development Workflow

### Run Development Server

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

### Access API Documentation

Open browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Test API with cURL

```bash
# Create a task (replace USER_ID with actual UUID)
curl -X POST "http://localhost:8000/api/{USER_ID}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs"}'

# List all tasks
curl "http://localhost:8000/api/{USER_ID}/tasks"

# Get specific task
curl "http://localhost:8000/api/{USER_ID}/tasks/{TASK_ID}"

# Update task
curl -X PUT "http://localhost:8000/api/{USER_ID}/tasks/{TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title"}'

# Toggle completion
curl -X PATCH "http://localhost:8000/api/{USER_ID}/tasks/{TASK_ID}/complete"

# Delete task
curl -X DELETE "http://localhost:8000/api/{USER_ID}/tasks/{TASK_ID}"
```

---

## Testing

### Run Tests

```bash
cd backend
uv run pytest tests/ -v
```

### Example Test (tests/test_api_tasks.py)

```python
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from src.main import app
from src.models.task import Task, TaskCreate
from src.core.config import get_session

client = TestClient(app)

def test_create_task():
    user_id = uuid.uuid4()
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test task"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["completed"] is False

def test_list_tasks():
    user_id = uuid.uuid4()
    # Create test tasks...
    response = client.get(f"/api/{user_id}/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## Production Deployment

### Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
ENVIRONMENT=production
LOG_LEVEL=info
```

### Run with Gunicorn (Production)

```bash
uv add gunicorn
uv run gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "gunicorn", "src.main:app", "--host", "0.0.0.0"]
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection string
psql $DATABASE_URL

# Check SSL mode (Neon requires sslmode=require)
```

### Import Errors

```python
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### UUID Generation

```python
# Generate test UUID
import uuid
user_id = uuid.uuid4()
print(user_id)
```

---

## Next Steps

1. **Authentication**: Integrate JWT verification (Constitution Principle VII)
2. **Testing**: Add comprehensive test coverage
3. **Documentation**: Add API examples and guides
4. **Monitoring**: Add logging, metrics, health checks
5. **Frontend Integration**: Build Next.js frontend to consume API

---

## Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Docs](https://neon.tech/docs)
- [UV Package Manager](https://github.com/astral-sh/uv)
