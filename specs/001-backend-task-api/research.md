# Research: Backend Task CRUD API

**Feature**: 001-backend-task-api
**Date**: 2026-01-08
**Phase**: Phase 0 - Research & Technical Decisions

## Overview

This document consolidates research findings for implementing a FastAPI-based task CRUD API with SQLModel and Neon PostgreSQL. All technical decisions are documented with rationale and alternatives considered.

## Technical Decisions

### 1. User ID Format

**Decision**: UUID (Universally Unique Identifier)

**Rationale**:
- UUIDs provide global uniqueness without coordination
- No risk of collision in distributed systems
- Better security than sequential integers (no enumeration attacks)
- Standard practice for multi-user applications
- SQLModel supports UUID primary keys natively with `default_factory=uuid.uuid4`
- PostgreSQL has excellent UUID support with dedicated UUID type

**Alternatives Considered**:
- **Sequential Integer**: Simpler but exposes user count and enables enumeration
- **ULID**: Combines UUID benefits with sortability, but less ecosystem support

**Implementation**:
```python
import uuid
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
```

---

### 2. Database Session Management

**Decision**: FastAPI dependency injection with generator function

**Rationale**:
- FastAPI's `Depends` system ensures proper session lifecycle
- Generator function (`yield`) handles cleanup automatically
- Type-safe with Python 3.10+ `Annotated` syntax
- Automatic request/response cycle integration
- Session committed/rolled back before response sent

**Alternatives Considered**:
- **Global session**: Thread-unsafe, causes connection leaks
- **Middleware**: Overkill for simple session management
- **Context managers in each endpoint**: Code duplication

**Implementation**:
```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

---

### 3. API Response Structure

**Decision**: Return model instances directly with consistent HTTP status codes

**Rationale**:
- FastAPI automatically serializes SQLModel/Pydantic models to JSON
- `response_model` parameter enables response filtering
- Standard HTTP status codes (200, 201, 404, 400, 422, 500)
- FastAPI's default validation error responses are excellent

**Alternatives Considered**:
- **Custom wrapper** (e.g., `{success: true, data: {...}}`): Unnecessary layer
- **Response classes**: Overkill for simple CRUD

**Implementation**:
```python
from fastapi import HTTPException

@app.post("/api/{user_id}/tasks", response_model=TaskRead)
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task  # Automatically serialized to JSON
```

---

### 4. Error Handling Strategy

**Decision**: HTTPException with custom error handlers for consistent responses

**Rationale**:
- FastAPI's `HTTPException` provides status code and detail message
- Custom handlers ensure consistent error response format
- Validation errors automatically return 422 with field details
- Database errors caught and converted to appropriate HTTP codes

**Alternatives Considered**:
- **Return error dictionaries**: Loses HTTP semantics
- **Custom exception hierarchy**: Overkill for this phase
- **Let exceptions propagate**: Poor UX, exposes internals

**Implementation**:
```python
from fastapi import HTTPException

@app.get("/api/{user_id}/tasks/{task_id}")
def read_task(task_id: uuid.UUID, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

---

### 5. Model Classes Pattern

**Decision**: Separate model classes for different use cases (table vs. input vs. output)

**Rationale**:
- **Table model**: Defines database schema with all fields
- **Create model**: Input validation (excludes auto-generated fields)
- **Update model**: Partial updates with `exclude_unset=True`
- **Read model**: Output filtering (excludes sensitive fields if needed)
- Follows FastAPI/SQLModel best practices
- Type safety and validation at boundaries

**Alternatives Considered**:
- **Single model**: No input/output validation, leaks implementation
- **Dictionary-based**: Loses type safety and auto-documentation

**Implementation**:
```python
from typing import Optional
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    completed: bool = False
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

---

### 6. Timestamp Management

**Decision**: UTC timestamps with `default_factory` for automatic population

**Rationale**:
- UTC avoids timezone confusion
- `default_factory` ensures Python-side generation
- `updated_at` manually updated on modifications
- Single source of truth (database)

**Alternatives Considered**:
- **Database triggers**: Complex to manage across migrations
- **Client-side timestamps**: Security risk (client can manipulate)

**Implementation**:
```python
from datetime import datetime

class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# In update endpoint:
task.updated_at = datetime.utcnow()
```

---

### 7. Pagination Strategy

**Decision**: Offset/limit pagination with query parameters

**Rationale**:
- Standard SQL pagination approach
- FastAPI's `Query` enables parameter validation
- Simple to implement and understand
- Adequate for expected data volumes (10k tasks/user)

**Alternatives Considered**:
- **Cursor-based**: More complex, not needed for this scale
- **Keyset pagination**: Better for large datasets, but adds complexity

**Implementation**:
```python
from fastapi import Query

@app.get("/api/{user_id}/tasks")
def list_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50
):
    tasks = session.exec(
        select(Task)
        .offset(offset)
        .limit(limit)
    ).all()
    return tasks
```

---

### 8. User Isolation Strategy

**Decision**: Query filtering by `user_id` at application layer

**Rationale**:
- Explicit user_id foreign key in Task model
- All queries filter by `user_id` from JWT (future)
- Application-layer enforcement (no row-level security needed yet)
- Clear ownership semantics

**Alternatives Considered**:
- **Row-level security**: Overkill for this phase
- **Separate tables per user**: Doesn't scale, complex queries

**Implementation**:
```python
@app.get("/api/{user_id}/tasks")
def list_tasks(user_id: uuid.UUID, session: SessionDep):
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
    ).all()
    return tasks
```

---

### 9. Concurrency Control

**Decision**: Optimistic concurrency control (last write wins)

**Rationale**:
- Simple implementation
- Adequate for task CRUD (low contention)
- SQLModel handles session locking automatically
- Future enhancement: add `version` field for optimistic locking if needed

**Alternatives Considered**:
- **Pessimistic locking**: Overkill, adds complexity
- **Full audit log**: Out of scope for this phase

---

### 10. Database Engine Configuration

**Decision**: Connection pooling with sensible defaults

**Rationale**:
- SQLModel/SQLAlchemy provides production-grade pooling
- Default pool size (5) adequate for development
- Environment variable for connection string
- Future: tune pool size based on load testing

**Implementation**:
```python
import os
from sqlmodel import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)  # echo=False in production
```

---

## Architecture Patterns

### Layer Separation

```
├── models/        # SQLModel database models (Task, User)
├── api/           # FastAPI route handlers (endpoints)
├── services/      # Business logic (empty in this phase - endpoints handle directly)
├── core/          # Configuration (database, dependencies)
└── tests/         # Test suite
```

### Dependency Flow

1. **HTTP Request** → FastAPI route handler
2. **Route Handler** → Validates input with Pydantic models
3. **Dependency Injection** → Provides database session
4. **Business Logic** → Database operations via SQLModel
5. **Response** → SQLModel serialized to JSON automatically

---

## Technology Stack Justification

### FastAPI
- Modern, high-performance web framework
- Automatic OpenAPI documentation (`/docs`, `/redoc`)
- Type-safe with Pydantic validation
- Async support (future enhancement)
- Excellent community and documentation

### SQLModel
- Combines SQLAlchemy (ORM) and Pydantic (validation)
- Single source of truth for models
- Pythonic API
- FastAPI integration (designed by same author)

### Neon PostgreSQL
- Serverless PostgreSQL (no infrastructure management)
- Automatic scaling
- Built-in connection pooling
- Full PostgreSQL feature set
- Free tier for development

### UV Package Manager
- Fast dependency resolution
- Modern Python packaging (PEP 621)
- Virtual environment management
- Lock files for reproducibility

---

## Performance Considerations

1. **Database Indexing**:
   - `user_id`: Foreign key, automatically indexed
   - `created_at`: Indexed for sorting and filtering
   - `title`: Full-text search if needed (future)

2. **Query Optimization**:
   - Pagination prevents large result sets
   - Selective columns with `response_model`
   - Eager loading for relationships (future)

3. **Connection Pooling**:
   - Reuse database connections
   - Configure pool size based on load

4. **Response Times**:
   - Target: <500ms for create, <300ms for list
   - Measured from request receipt to response

---

## Security Considerations

### Current Phase (No Authentication)
- User ID from path parameter (temporary)
- Basic input validation via Pydantic
- SQL injection prevention (SQLModel parameterized queries)

### Future Enhancements
- JWT authentication (Constitution Principle VII)
- User ID extracted from verified token
- Authorization checks (data ownership)

---

## Testing Strategy

### Unit Tests
- Model validation (Pydantic schemas)
- Business logic functions

### Integration Tests
- API endpoints with test database
- Database operations
- Error scenarios

### Test Database
- Use SQLite for tests (fast, in-memory)
- pytest fixtures for database setup
- Test data factories

---

## Open Questions for Next Phase

1. **Authentication Integration**: How will JWT verification be implemented?
2. **Migration Strategy**: Alembic or SQLModel's `create_all`?
3. **Logging**: Structured logging format and destination?
4. **Monitoring**: Metrics, tracing, or health checks?
5. **Deployment**: Containerization, environment configuration?

---

## References

- [FastAPI Tutorial - SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [SQLModel Advanced - UUIDs](https://sqlmodel.tiangolo.com/advanced/uuid/)
