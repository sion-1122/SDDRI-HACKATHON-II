# Data Model: Backend Task CRUD API

**Feature**: 001-backend-task-api
**Date**: 2026-01-08
**Phase**: Phase 1 - Design & Contracts

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
├─────────────────┤
│ id: UUID (PK)   │
└─────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│     Task        │
├─────────────────┤
│ id: UUID (PK)   │
│ user_id: UUID   │ (FK)
│ title: string   │
│ description:    │
│   string (opt)  │
│ completed: bool │
│ created_at:     │
│   timestamp     │
│ updated_at:     │
│   timestamp     │
└─────────────────┘
```

## Entities

### User

**Purpose**: Represents a user who owns tasks. Minimal entity for this phase (authentication deferred).

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique user identifier |

**Relationships**:
- One-to-many with `Task` (one user has many tasks)

**Notes**:
- Authentication not enforced in this phase
- User ID provided via path parameter temporarily
- Future enhancement: add email, password_hash, created_at

---

### Task

**Purpose**: Represents a to-do item with ownership tracking.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique task identifier |
| `user_id` | UUID | Foreign key → User.id, required | Task owner |
| `title` | string | Required, max 255 chars | Task title |
| `description` | string | Optional, max 2000 chars | Detailed description |
| `completed` | boolean | Required, default false | Completion status |
| `created_at` | timestamp | Required, auto-generated | Creation time (UTC) |
| `updated_at` | timestamp | Required, auto-updated | Last modification time (UTC) |

**Relationships**:
- Many-to-one with `User` (many tasks belong to one user)

**Indexes**:
- Primary key: `id`
- Foreign key: `user_id` (auto-indexed)
- Created timestamp: `created_at` (for sorting)

**Validation Rules**:
1. `title` must be non-empty if provided
2. `title` maximum length: 255 characters
3. `description` maximum length: 2000 characters
4. `user_id` must reference valid user (future: validated via foreign key)
5. `completed` defaults to `false` if not provided

**State Transitions**:

```
[Task Created] → completed: false
       │
       │ (toggle completion)
       ▼
[Task Completed] → completed: true
       │
       │ (toggle completion)
       ▼
[Task Reactivated] → completed: false
```

---

## SQLModel Class Definitions

### Base Model Classes

```python
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    """Database table model for Task entity."""

    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True
    )
    title: str = Field(max_length=255)
    description: Optional[str] = Field(
        default=None,
        max_length=2000
    )
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )
```

### Input/Output Models

```python
class TaskCreate(SQLModel):
    """Request model for creating a task."""

    title: str = Field(max_length=255, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = False


class TaskUpdate(SQLModel):
    """Request model for updating a task (all fields optional)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None


class TaskRead(SQLModel):
    """Response model for task data."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskToggle(SQLModel):
    """Request model for toggle completion endpoint."""

    completed: bool
```

---

## Database Schema (DDL)

```sql
-- Users table (minimal for this phase)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

---

## Data Flow Examples

### Create Task

```
1. Client POST /api/{user_id}/tasks
   Body: {"title": "Buy groceries", "description": "Milk, eggs, bread"}

2. FastAPI validates with TaskCreate model

3. Task instance created:
   {
     id: "550e8400-e29b-41d4-a716-446655440000",
     user_id: "123e4567-e89b-12d3-a456-426614174000",
     title: "Buy groceries",
     description: "Milk, eggs, bread",
     completed: false,
     created_at: "2026-01-08T20:45:00Z",
     updated_at: "2026-01-08T20:45:00Z"
   }

4. SQLModel persists to database

5. Response (TaskRead): Same as step 3, HTTP 201
```

### Update Task

```
1. Client PUT /api/{user_id}/tasks/{id}
   Body: {"title": "Buy groceries and cook dinner"}

2. FastAPI validates with TaskUpdate model

3. Existing task fetched from database

4. Fields updated (exclude_unset=True):
   - title: "Buy groceries and cook dinner"
   - updated_at: "2026-01-08T21:00:00Z" (auto-updated)

5. Database updated

6. Response (TaskRead): Updated task, HTTP 200
```

### Toggle Completion

```
1. Client PATCH /api/{user_id}/tasks/{id}/complete

2. Existing task fetched:
   completed: false

3. Toggle logic:
   completed = not completed  # Now true
   updated_at = current_time

4. Database updated

5. Response (TaskRead): completed: true, HTTP 200
```

---

## Query Patterns

### List Tasks (Filtered)

```python
# All tasks for user
select(Task).where(Task.user_id == user_id)

# Filter by completion status
select(Task).where(
    Task.user_id == user_id,
    Task.completed == True
)

# Order by creation date (newest first)
select(Task)
    .where(Task.user_id == user_id)
    .order_by(desc(Task.created_at))

# Paginated
select(Task)
    .where(Task.user_id == user_id)
    .offset(0)
    .limit(50)
```

### Get Single Task

```python
# By ID with user ownership check
task = session.get(Task, task_id)
if task.user_id != user_id:
    raise HTTPException(status_code=403)
```

### Delete Task

```python
# Get and verify ownership
task = session.get(Task, task_id)
if not task or task.user_id != user_id:
    raise HTTPException(status_code=404)
session.delete(task)
```

---

## Migration Strategy

### Initial Setup
```python
from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### Future Enhancements
- Use Alembic for versioned migrations
- Track schema changes over time
- Support rollback capabilities

---

## Data Integrity

### Foreign Key Constraints
- `tasks.user_id` references `users.id`
- Cascading deletes: **NOT** enabled (user cannot be deleted with tasks)
- Future enhancement: soft delete or cascade

### Check Constraints
- `title` NOT NULL
- `completed` NOT NULL (defaults to false)

### Transaction Management
- All database operations within session transaction
- Automatic rollback on error
- Explicit commit on success

---

## Performance Considerations

### Indexing Strategy
1. **Primary key** (`id`): Auto-indexed, unique lookups
2. **Foreign key** (`user_id`): Indexed for filtering by user
3. **Timestamp** (`created_at`): Indexed for sorting

### Query Optimization
- Pagination prevents full table scans
- Selective column retrieval with `response_model`
- Connection pooling reduces connection overhead

### Storage Estimates
- Task record: ~200 bytes average
- 10,000 tasks/user: ~2 MB per user
- Database growth: Linear with task count

---

## Security Considerations

### Data Isolation
- All queries filter by `user_id`
- User can only access their own tasks
- Future: JWT-based user authentication

### Input Validation
- Title: max 255 chars, non-empty
- Description: max 2000 chars, optional
- SQL injection prevented by SQLModel parameterized queries

### Authorization
- Current phase: User ID from path parameter (temporary)
- Future phase: User ID from verified JWT token
- Ownership check on every operation

---

## Testing Data

### Fixtures
```python
@pytest.fixture
def test_user():
    return User(id=uuid.uuid4())

@pytest.fixture
def test_task(test_user):
    return Task(
        user_id=test_user.id,
        title="Test task",
        description="Test description",
        completed=False
    )
```

### Test Scenarios
1. Create task with valid data
2. Create task with invalid data (empty title)
3. Update task partially (only title)
4. Toggle completion false → true → false
5. Delete task and verify removal
6. List tasks with pagination
7. Filter tasks by completion status
8. Access non-existent task (404)
9. Access another user's task (403, future)
