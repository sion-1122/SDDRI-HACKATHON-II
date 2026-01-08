# Implementation Plan: Backend Task CRUD API

**Branch**: `001-backend-task-api` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)

## Summary

Implement a RESTful API for task CRUD operations using FastAPI, SQLModel, and Neon PostgreSQL. The system provides user-scoped task management with create, read, update, delete, and toggle completion operations. This phase focuses on core CRUD functionality without authentication enforcement, establishing the foundation for future multi-user web application.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI (web framework), SQLModel (ORM), Pydantic (validation), Uvicorn (ASGI server)
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest with httpx for async client testing
**Target Platform**: Linux server (container-ready)
**Project Type**: web (backend API)
**Performance Goals**:
- Create task: <500ms p95
- List tasks: <300ms p95 for 1k tasks
- Support 100 concurrent requests
- Handle 10k tasks per user
**Constraints**:
- User ID from path parameter (temporary, no authentication yet)
- All data persisted to PostgreSQL (no in-memory storage)
- RESTful API design with standard HTTP methods
- Consistent error responses with appropriate status codes
**Scale/Scope**:
- Single database, single-region deployment
- Expected: 100-1000 users, 10k tasks/user
- API surface: 6 endpoints (CRUD + toggle)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Persistent Storage ✅ PASS
**Requirement**: All state MUST be persisted in relational database during Phase II.
**Compliance**: All tasks stored in Neon PostgreSQL using SQLModel. No in-memory-only data persistence.
**Evidence**:
- Task model with SQLModel `table=True`
- Database engine configuration in `core/config.py`
- Session management with automatic commit/rollback
**Impact**: Full data durability, multi-user concurrency, scalable storage.

### Principle II: RESTful API Excellence ✅ PASS
**Requirement**: Backend MUST implement RESTful API using FastAPI with clear resource boundaries, standard HTTP methods.
**Compliance**: Implemented 6 RESTful endpoints under `/api` path with standard methods (GET, POST, PUT, DELETE, PATCH).
**Evidence**:
- `POST /api/{user_id}/tasks` - Create resource
- `GET /api/{user_id}/tasks` - List resources
- `GET /api/{user_id}/tasks/{id}` - Get specific resource
- `PUT /api/{user_id}/tasks/{id}` - Update resource
- `DELETE /api/{user_id}/tasks/{id}` - Delete resource
- `PATCH /api/{user_id}/tasks/{id}/complete` - Partial update (toggle)
- Consistent JSON responses with appropriate status codes (200, 201, 404, 400, 422, 500)
**Impact**: Standardized client-server communication, stateless interactions, clear contracts.

### Principle VI: Monorepo Structure Standard ✅ PASS
**Requirement**: Project MUST adhere to standardized monorepo folder structure.
**Compliance**: Following Phase II backend structure as defined in constitution.
**Evidence**:
```
backend/
├── models/       # SQLModel database models
├── api/          # FastAPI route handlers
├── core/         # Configuration, dependencies
├── tests/        # Test suite
└── CLAUDE.md     # Backend-specific instructions
```
**Impact**: Clear separation of concerns, scalable architecture, constitution compliance.

### Principle VII: Authentication & JWT Security ⚠️ DEFERRED
**Requirement**: All API endpoints MUST require valid JWT authentication.
**Compliance**: **NOT YET IMPLEMENTED** - User ID provided via path parameter temporarily.
**Justification**: Feature spec explicitly states "without authentication enforcement yet". Authentication deferred to future phase.
**Risk**: Unauthorized access possible if user IDs are discovered.
**Mitigation**: Document as temporary measure, authentication in backlog.
**Impact**: Medium risk but acceptable for initial development phase.

### Principle IX: Data Ownership & Isolation ⚠️ PARTIAL
**Requirement**: All database queries MUST be scoped to authenticated user.
**Compliance**: **PARTIAL** - All queries filter by `user_id`, but no JWT verification yet.
**Evidence**:
- `Task.user_id` foreign key established
- All queries include `.where(Task.user_id == user_id)`
- Ownership checks in endpoints (404 if task doesn't belong to user)
**Gap**: User ID from path parameter, not verified JWT.
**Mitigation**: Same as Principle VII - authentication deferred.
**Impact**: Data isolation enforced at application layer, but no authentication gate.

### Principle X: API Response Consistency ✅ PASS
**Requirement**: All API endpoints MUST return consistent JSON responses.
**Compliance**: Implemented consistent response structure using SQLModel/Pydantic models.
**Evidence**:
- Success responses: Model instances serialized to JSON
- Error responses: `{"detail": "Error message"}` with HTTP status codes
- Validation errors: Structured `{"detail": [field_errors]}` with 422 status
**Impact**: Predictable frontend error handling, improved debugging, clear user feedback.

### Overall Assessment: ✅ PASS with Known Deferrals
**Critical**: All mandatory principles for Phase II are satisfied or explicitly deferred with justification.
**Action Items**:
1. Implement JWT authentication (Principle VII) - Future phase
2. Extract user_id from verified token instead of path parameter (Principle IX) - Future phase
3. Document authentication requirements in API spec

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-task-api/
├── plan.md              # This file
├── research.md          # Phase 0: Technical decisions and rationale
├── data-model.md        # Phase 1: Entity definitions and schema
├── quickstart.md        # Phase 1: Setup and implementation guide
├── contracts/           # Phase 1: API specifications
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── tasks.md             # Phase 2: Implementation tasks (future)
```

### Source Code (repository root)

```text
backend/
├── models/              # SQLModel database models
│   ├── __init__.py
│   ├── task.py          # Task entity and I/O models
│   └── user.py          # User entity (minimal)
├── api/                 # FastAPI route handlers
│   ├── __init__.py
│   └── tasks.py         # Task CRUD endpoints
├── core/                # Configuration and dependencies
│   ├── __init__.py
│   ├── config.py        # Database engine, init_db()
│   └── deps.py          # Dependency injection (get_session)
├── tests/               # Test suite
│   ├── conftest.py      # Pytest fixtures
│   ├── test_api_tasks.py
│   └── test_models.py
├── .env                 # Environment variables (not in git)
├── pyproject.toml       # UV project configuration
└── CLAUDE.md            # Backend-specific instructions (created)
```

**Structure Decision**: Selected Option 2 (Web application - Phase II backend) per constitution Principle VI. Backend directory coexists with existing `cli/` directory from Phase I. Structure aligns with FastAPI/SQLModel best practices and supports future scalability (adding services, additional API modules).

## Architecture Overview

### Layer Architecture

```
┌─────────────────────────────────────┐
│   HTTP Client (cURL, frontend)     │
└─────────────────┬───────────────────┘
                  │ HTTP/JSON
┌─────────────────▼───────────────────┐
│   FastAPI Route Handlers (api/)     │
│   - Input validation (Pydantic)     │
│   - Response serialization          │
└─────────────────┬───────────────────┘
                  │ Session
┌─────────────────▼───────────────────┐
│   SQLModel ORM (models/)            │
│   - Database models                 │
│   - Query construction              │
└─────────────────┬───────────────────┘
                  │ SQL
┌─────────────────▼───────────────────┐
│   Neon PostgreSQL Database          │
│   - Persistent storage              │
│   - ACID transactions               │
└─────────────────────────────────────┘
```

### Data Flow (Create Task Example)

```
1. POST /api/{user_id}/tasks
   Body: {"title": "Buy groceries", "description": "Milk, eggs"}

2. FastAPI receives request → Route handler: create_task()

3. Dependency injection → get_session() yields database session

4. Pydantic validation → TaskCreate validates input
   ✓ title: non-empty, max 255 chars
   ✓ description: optional, max 2000 chars

5. Business logic → Task.model_validate() creates instance
   db_task.user_id = user_id (from path)
   db_task.title, description from request body
   db_task.completed = False (default)
   db_task.created_at, updated_at = now (auto)

6. Database operation → session.add(db_task)
   session.commit() persists to PostgreSQL
   session.refresh(db_task) reloads with generated ID

7. Response serialization → TaskRead model
   FastAPI serializes to JSON automatically

8. HTTP 201 Created → Returns JSON to client
   {"id": "...", "user_id": "...", "title": "...", ...}
```

### Component Responsibilities

**models/**: Data modeling and validation
- Define database schema (SQLModel with `table=True`)
- Input validation models (TaskCreate, TaskUpdate)
- Output serialization models (TaskRead)

**api/**: HTTP request handling
- Route definitions with FastAPI decorators
- Request validation via Pydantic
- Response serialization
- HTTP status codes and error handling

**core/**: Cross-cutting concerns
- Database engine configuration
- Session management (dependency injection)
- Startup initialization (create tables)

**tests/**: Quality assurance
- Unit tests (model validation)
- Integration tests (API endpoints)
- Test fixtures (database setup)

## Integration Points

### External Dependencies

1. **Neon PostgreSQL**
   - **Purpose**: Persistent data storage
   - **Integration**: SQLModel engine with connection string from `DATABASE_URL` env var
   - **Protocol**: PostgreSQL wire protocol over SSL
   - **Location**: `core/config.py` - `create_engine(DATABASE_URL)`

2. **Future: Better Auth (Frontend)**
   - **Purpose**: JWT token generation and validation
   - **Integration**: Backend will verify JWT signatures
   - **Protocol**: HTTP `Authorization: Bearer <token>` header
   - **Status**: Deferred to future phase

### Internal Components

1. **FastAPI → SQLModel**
   - Pydantic models used for both validation and ORM
   - Automatic request/response serialization
   - Type safety throughout stack

2. **Database Session Management**
   - FastAPI dependency injection (`Depends(get_session)`)
   - Generator function ensures cleanup
   - Session lifecycle tied to request/response

3. **Error Handling**
   - HTTPException for application errors
   - RequestValidationError for input errors
   - Consistent error response format

## Security Considerations

### Current Phase (No Authentication)

**Risks**:
1. **Unauthorized Access**: Anyone with user ID can access tasks if ID is discovered
2. **Enumeration**: Sequential user IDs (if used) expose user count
3. **No Audit Trail**: No logging of who accessed what data

**Mitigations**:
1. **UUID for User IDs**: Non-enumerable, prevents guessing
2. **Data Isolation**: Queries scoped to user_id parameter
3. **Input Validation**: Pydantic prevents injection attacks
4. **Parameterized Queries**: SQLModel prevents SQL injection

### Future Enhancements

1. **JWT Authentication** (Constitution Principle VII)
   - Verify JWT signature on every request
   - Extract user_id from token, not path parameter
   - Return 401 Unauthorized for missing/invalid tokens

2. **Rate Limiting**
   - Prevent abuse/DoS
   - Per-user rate limits based on JWT

3. **Audit Logging**
   - Log all CRUD operations with user_id
   - Track access patterns for security monitoring

4. **HTTPS Only**
   - Enforce TLS in production
   - Redirect HTTP → HTTPS

## Performance Optimization

### Database Indexing

```python
# Automatically indexed
id: UUID          # Primary key (clustered index)
user_id: UUID     # Foreign key (non-clustered index)

# Manual index for sorting
created_at        # For ORDER BY queries
```

### Query Optimization

1. **Pagination**: `LIMIT/OFFSET` prevents large result sets
2. **Selective Columns**: `response_model` excludes sensitive fields
3. **Connection Pooling**: SQLAlchemy pool (default: 5 connections)
4. **Eager Loading**: Future - `selectinload()` for relationships

### Caching Strategy (Future)

1. **Application Cache**: Redis for frequent queries
2. **Database Cache**: Neon's automatic query caching
3. **CDN Cache**: Not applicable (API responses are dynamic)

## Testing Strategy

### Unit Tests

**Scope**: Model validation, business logic
**Tools**: pytest, SQLModel in-memory SQLite
**Examples**:
- TaskCreate validates title length
- Task model default values
- Toggle completion logic

### Integration Tests

**Scope**: API endpoints with test database
**Tools**: pytest, httpx TestClient, test PostgreSQL database
**Examples**:
- POST /api/{user_id}/tasks creates task
- GET /api/{user_id}/tasks returns user's tasks only
- PUT /api/{user_id}/tasks/{id} updates task
- DELETE /api/{user_id}/tasks/{id} removes task
- 404 for non-existent tasks
- 400 for invalid input

### Test Fixtures

```python
@pytest.fixture
def test_db():
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture
def test_session(test_db):
    with Session(test_db) as session:
        yield session

@pytest.fixture
def test_user():
    return User(id=uuid.uuid4())
```

### Test Coverage Target

- Unit tests: 80%+ for models, validation logic
- Integration tests: 70%+ for API endpoints
- Edge cases: 100% (all documented edge cases tested)

## Deployment Strategy

### Development

```bash
uv run uvicorn src.main:app --reload --port 8000
```

### Production

```bash
uv run gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
ENVIRONMENT=production
LOG_LEVEL=info
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "gunicorn", "src.main:app", "--host", "0.0.0.0"]
```

## Monitoring & Observability

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics (Future)

- Request rate (requests/second)
- Response times (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database connection pool utilization

### Health Checks

```python
@app.get("/health")
def health_check(session: SessionDep):
    try:
        session.exec(select(Task).limit(1))
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Database connection pool exhaustion | Low | High | Monitor pool metrics, configure pool size |
| SQL injection vulnerabilities | Low | Critical | Use SQLModel parameterized queries only |
| Performance degradation with 10k+ tasks | Medium | Medium | Add indexes, pagination, query optimization |
| UUID collision | Near-zero | Critical | Use uuid4 (128-bit entropy) |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Neon service outage | Low | High | Implement health checks, graceful degradation |
| Deployment failures | Low | Medium | Blue-green deployment, rollback plan |
| Environment variable misconfiguration | Medium | High | Validate on startup, use .env.example |

### Security Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Unauthorized access via user ID enumeration | Low | High | Use UUIDs (non-sequential) |
| Missing authentication (deferred) | High | High | Document as temporary, prioritize auth |
| Data leaks in error messages | Low | Medium | Sanitize error responses, no stack traces |

## Success Criteria (from spec)

- **SC-001**: Create task in <500ms ✅ Target: FastAPI + SQLModel overhead <50ms, network latency dominant
- **SC-002**: Handle 100 concurrent requests ✅ Target: Gunicorn with 4 workers, 25 req/worker
- **SC-003**: List 1k tasks in <300ms ✅ Target: Pagination (50 tasks) + indexed user_id queries
- **SC-004**: Appropriate HTTP status codes ✅ Target: FastAPI automatic validation + explicit error handling
- **SC-005**: Data consistency ✅ Target: SQLModel transactions, ACID guarantees
- **SC-006**: 10k tasks/user ✅ Target: Indexed queries, pagination, Neon scalability
- **SC-007**: Graceful error handling ✅ Target: HTTPException handlers, validation errors
- **SC-008**: 99.9% reliability ✅ Target: Connection pooling, retry logic, health checks

## Next Steps

### Immediate (This Feature)

1. ✅ Complete specification ([spec.md](./spec.md))
2. ✅ Research technical decisions ([research.md](./research.md))
3. ✅ Design data model ([data-model.md](./data-model.md))
4. ✅ Create API contracts ([contracts/openapi.yaml](./contracts/openapi.yaml))
5. ✅ Write quickstart guide ([quickstart.md](./quickstart.md))
6. ⏭️ Generate implementation tasks (`/sp.tasks`)

### Future Phases

1. **Authentication Feature** (Next)
   - Implement JWT verification
   - Extract user_id from token
   - Add authentication middleware
   - Update all endpoints to require JWT

2. **Frontend Integration**
   - Next.js app to consume API
   - Better Auth integration
   - Task management UI

3. **Advanced Features**
   - Task search and filtering
   - Categories and tags
   - Due dates and reminders
   - File attachments

## References

- [Constitution](../../.specify/memory/constitution.md) - Phase II principles and constraints
- [Feature Specification](./spec.md) - User stories, requirements, success criteria
- [Research Document](./research.md) - Technical decisions and rationale
- [Data Model](./data-model.md) - Entity definitions and database schema
- [Quickstart Guide](./quickstart.md) - Setup and implementation instructions
- [OpenAPI Spec](./contracts/openapi.yaml) - API contract and documentation
- [Backend Context](../../backend/CLAUDE.md) - Backend development guidelines
