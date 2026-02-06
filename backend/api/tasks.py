"""Task CRUD API endpoints with JWT authentication.

[Task]: T053-T059, T043, T065-T067
[From]: specs/001-user-auth/tasks.md (User Story 3), specs/007-intermediate-todo-features/tasks.md (User Story 4)

Implements all task management operations with JWT-based authentication:
- Create task with validation
- List tasks with filtering (status, priority, tags, due_date) [T043]
- Get task by ID
- Update task with validation
- Delete task
- Toggle completion status
- Search tasks (User Story 3)
- List tags

All endpoints require valid JWT token. user_id is extracted from JWT claims.
"""
import uuid
from datetime import datetime, timedelta
from typing import Annotated, List, Optional
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from sqlalchemy import func, and_, any_

from core.deps import SessionDep, CurrentUserDep
from models.task import Task, TaskCreate, TaskUpdate, TaskRead

# Create API router (user_id removed - now from JWT)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# Response models
class TaskListResponse(BaseModel):
    """Response model for task list with pagination."""
    tasks: list[TaskRead]
    total: int
    offset: int
    limit: int


class TagInfo(BaseModel):
    """Tag information with usage count."""
    name: str
    count: int


class TagsListResponse(BaseModel):
    """Response model for tags list."""
    tags: list[TagInfo]


class TaskSearchResponse(BaseModel):
    """Response model for task search results."""
    tasks: list[TaskRead]
    total: int
    page: int
    limit: int
    query: str


# Routes - IMPORTANT: Static routes MUST come before dynamic path parameters
# This ensures /tags and /search are matched before /{task_id}


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Create a new task for the authenticated user."""
    # Convert priority string to PriorityLevel enum (handles both upper/lowercase input)
    priority_enum = PriorityLevel(task.priority.upper()) if isinstance(task.priority, str) else task.priority

    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        priority=priority_enum,
        tags=task.tags,
        due_date=task.due_date,
        completed=task.completed,
        reminder_offset=task.reminder_offset,  # [T043] Add reminder_offset support
        reminder_sent=False  # Initialize reminder_sent to False
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    completed: bool | None = None,
    priority: str | None = None,
    tags: Annotated[List[str] | None, Query()] = None,
    due_date: str | None = None,
    due_before: str | None = None,  # [T028] Add due_before filter
    due_after: str | None = None,   # [T028] Add due_after filter
    timezone: str = "UTC",
    sort_by: str | None = None,
    sort_order: str = "asc",
):
    """List all tasks for the authenticated user with pagination and filtering."""
    count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        count_statement = count_statement.where(Task.completed == completed)
        statement = statement.where(Task.completed == completed)

    if priority is not None:
        count_statement = count_statement.where(Task.priority == priority)
        statement = statement.where(Task.priority == priority)

    if tags and len(tags) > 0:
        for tag in tags:
            # Use PostgreSQL ANY operator: tag = ANY(tags)
            count_statement = count_statement.where(tag == any_(Task.tags))
            statement = statement.where(tag == any_(Task.tags))

    # [T028] Add due_before and due_after filters
    if due_before:
        try:
            due_before_dt = datetime.fromisoformat(due_before)
            count_statement = count_statement.where(Task.due_date <= due_before_dt)
            statement = statement.where(Task.due_date <= due_before_dt)
        except ValueError:
            pass  # Invalid date format, ignore filter

    if due_after:
        try:
            due_after_dt = datetime.fromisoformat(due_after)
            count_statement = count_statement.where(Task.due_date >= due_after_dt)
            statement = statement.where(Task.due_date >= due_after_dt)
        except ValueError:
            pass  # Invalid date format, ignore filter

    if due_date:
        try:
            user_tz = ZoneInfo(timezone)
            now_utc = datetime.now(ZoneInfo("UTC"))
            now_user = now_utc.astimezone(user_tz)
            today_start = now_user.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            if due_date == "overdue":
                today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
                count_statement = count_statement.where(
                    and_(Task.due_date < today_start_utc, Task.completed == False)
                )
                statement = statement.where(
                    and_(Task.due_date < today_start_utc, Task.completed == False)
                )
            elif due_date == "today":
                today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
                today_end_utc = today_end.astimezone(ZoneInfo("UTC"))
                count_statement = count_statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < today_end_utc)
                )
                statement = statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < today_end_utc)
                )
            elif due_date == "week":
                week_end_utc = (today_start + timedelta(days=7)).astimezone(ZoneInfo("UTC"))
                today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
                count_statement = count_statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < week_end_utc)
                )
                statement = statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < week_end_utc)
                )
            elif due_date == "month":
                month_end_utc = (today_start + timedelta(days=30)).astimezone(ZoneInfo("UTC"))
                today_start_utc = today_start.astimezone(ZoneInfo("UTC"))
                count_statement = count_statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < month_end_utc)
                )
                statement = statement.where(
                    and_(Task.due_date >= today_start_utc, Task.due_date < month_end_utc)
                )
        except Exception:
            pass

    total = session.exec(count_statement).one()

    if sort_by == "due_date":
        if sort_order == "asc":
            statement = statement.order_by(Task.due_date.asc().nulls_last())
        else:
            statement = statement.order_by(Task.due_date.desc().nulls_last())
    elif sort_by == "priority":
        from sqlalchemy import case
        priority_case = case(
            *[(Task.priority == k, i) for i, k in enumerate(["high", "medium", "low"])],
            else_=3
        )
        if sort_order == "asc":
            statement = statement.order_by(priority_case.asc())
        else:
            statement = statement.order_by(priority_case.desc())
    elif sort_by == "title":
        if sort_order == "asc":
            statement = statement.order_by(Task.title.asc())
        else:
            statement = statement.order_by(Task.title.desc())
    else:
        if sort_order == "asc":
            statement = statement.order_by(Task.created_at.asc())
        else:
            statement = statement.order_by(Task.created_at.desc())

    statement = statement.offset(offset).limit(limit)
    tasks = session.exec(statement).all()

    return TaskListResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total=total,
        offset=offset,
        limit=limit
    )


@router.get("/tags", response_model=TagsListResponse)
def list_tags(
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Get all unique tags for the authenticated user with usage counts."""
    from sqlalchemy import text

    query = text("""
        SELECT unnest(tags) as tag, COUNT(*) as count
        FROM tasks
        WHERE user_id = :user_id
        AND tags != '{}'
        GROUP BY tag
        ORDER BY count DESC, tag ASC
    """)

    result = session.exec(query.params(user_id=str(user_id)))
    tags = [TagInfo(name=row[0], count=row[1]) for row in result]
    return TagsListResponse(tags=tags)


@router.get("/search", response_model=TaskSearchResponse)
def search_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,
    q: Annotated[str, Query(min_length=1, max_length=200)] = "",
    page: int = 1,
    limit: Annotated[int, Query(le=100)] = 20,
):
    """Search tasks by keyword in title and description."""
    if not q:
        raise HTTPException(status_code=400, detail="Search query parameter 'q' is required")

    search_pattern = f"%{q}%"

    count_statement = select(func.count(Task.id)).where(
        (Task.user_id == user_id) &
        (Task.title.ilike(search_pattern) | Task.description.ilike(search_pattern))
    )
    total = session.exec(count_statement).one()

    offset = (page - 1) * limit
    statement = select(Task).where(
        (Task.user_id == user_id) &
        (Task.title.ilike(search_pattern) | Task.description.ilike(search_pattern))
    )
    statement = statement.offset(offset).limit(limit)
    statement = statement.order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()

    return TaskSearchResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total=total,
        page=page,
        limit=limit,
        query=q
    )


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Get a specific task by ID."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Update an existing task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        # Convert priority string to PriorityLevel enum
        if key == "priority" and isinstance(value, str):
            value = PriorityLevel(value.upper())
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Delete a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"ok": True}


@router.patch("/{task_id}/complete", response_model=TaskRead)
def toggle_complete(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep
):
    """Toggle task completion status and create next instance for recurring tasks.

    [Task]: T062-T065
    [From]: specs/008-advanced-features/tasks.md (User Story 3)

    When completing a recurring task:
    - T063: Checks if recurrence limit (count/end_date) is reached
    - T064: Handles count limit
    - T065: Handles end_date limit
    - Creates next instance if limits not reached
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    is_completing = not task.completed
    task.completed = is_completing
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    # [T062] Create next instance for recurring tasks when completing
    if is_completing and task.recurrence and task.due_date:
        from services.recurrence_service import RecurrenceService

        recurrence_service = RecurrenceService()

        # Parse recurrence rule
        recurrence_dict = task.recurrence if isinstance(task.recurrence, dict) else {"frequency": task.recurrence}
        if not isinstance(recurrence_dict, dict):
            recurrence_dict = {"frequency": str(task.recurrence)}

        # [T063] Check if we should create the next instance
        should_create_next = True
        current_count = 0

        # Count existing instances (tasks with same parent_task_id)
        if task.parent_task_id:
            # This is already an instance, count siblings
            count_statement = select(func.count(Task.id)).where(
                Task.parent_task_id == task.parent_task_id
            )
            current_count = session.exec(count_statement).one() + 1  # +1 for parent
        else:
            # This is the parent task, count its instances
            count_statement = select(func.count(Task.id)).where(
                Task.parent_task_id == task_id
            )
            current_count = session.exec(count_statement).one() + 1  # +1 for this task

        # [T064] Handle count limit
        max_count = recurrence_dict.get("count")
        if max_count is not None:
            if current_count >= max_count:
                should_create_next = False

        # [T065] Handle end_date limit
        end_date_str = recurrence_dict.get("end_date")
        if end_date_str and should_create_next:
            try:
                if isinstance(end_date_str, str):
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                else:
                    end_date = end_date_str

                # Calculate next occurrence date
                base_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00')) if isinstance(task.due_date, str) else task.due_date
                next_due_date = recurrence_service.calculate_next_occurrence(base_date, recurrence_dict)

                if next_due_date and next_due_date > end_date:
                    should_create_next = False
            except Exception:
                pass  # Invalid date format, skip check

        # Create next instance if limits not reached
        if should_create_next:
            base_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00')) if isinstance(task.due_date, str) else task.due_date
            next_due_date = recurrence_service.calculate_next_occurrence(base_date, recurrence_dict)

            if next_due_date:
                # Create next instance
                next_task = Task(
                    user_id=user_id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    tags=task.tags,
                    due_date=next_due_date.isoformat(),
                    completed=False,
                    reminder_offset=task.reminder_offset,
                    reminder_sent=False,
                    recurrence=task.recurrence,
                    parent_task_id=task.parent_task_id if task.parent_task_id else task.id,
                )
                session.add(next_task)
                session.commit()

    session.refresh(task)
    return task


@router.patch("/{task_id}/tags")
def update_task_tags(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep,
    tags_add: Optional[List[str]] = None,
    tags_remove: Optional[List[str]] = None,
):
    """Add or remove tags from a task."""
    from services.nlp_service import normalize_tag_name

    if tags_add is None and tags_remove is None:
        raise HTTPException(
            status_code=400,
            detail="Either 'tags_add' or 'tags_remove' must be provided"
        )

    if not tags_add and not tags_remove:
        raise HTTPException(
            status_code=400,
            detail="Either 'tags_add' or 'tags_remove' must contain at least one tag"
        )

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    current_tags = set(task.tags or [])

    if tags_add:
        normalized_add = [normalize_tag_name(tag) for tag in tags_add]
        current_tags.update(normalized_add)

    if tags_remove:
        normalized_remove = [normalize_tag_name(tag).lower() for tag in tags_remove]
        current_tags = {
            tag for tag in current_tags
            if tag.lower() not in normalized_remove
        }

    task.tags = sorted(list(current_tags))
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/reminder", response_model=TaskRead)
def update_reminder(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep,
    reminder_offset: int | None = None,
    reset_sent: bool = False
):
    """Update reminder settings for a task.

    [Task]: T045
    [From]: specs/008-advanced-features/tasks.md (User Story 2)

    Allows updating the reminder_offset and optionally resetting the reminder_sent flag.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update reminder_offset if provided
    if reminder_offset is not None:
        task.reminder_offset = reminder_offset

    # Reset reminder_sent flag if requested (e.g., when changing due date)
    if reset_sent:
        task.reminder_sent = False

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
