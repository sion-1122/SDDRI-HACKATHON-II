"""Task CRUD API endpoints with JWT authentication.

[Task]: T053-T059
[From]: specs/001-user-auth/tasks.md (User Story 3)

Implements all task management operations with JWT-based authentication:
- Create task
- List tasks
- Get task by ID
- Update task
- Delete task
- Toggle completion status

All endpoints require valid JWT token. user_id is extracted from JWT claims.
"""
import uuid
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from core.deps import SessionDep, CurrentUserDep
from models.task import Task, TaskCreate, TaskUpdate, TaskRead

# Create API router (user_id removed - now from JWT)
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    session: SessionDep,
    user_id: CurrentUserDep  # Injected from JWT
):
    """Create a new task for the authenticated user.

    Args:
        task: Task data from request body
        session: Database session
        user_id: UUID from JWT token (injected)

    Returns:
        Created task with generated ID and timestamps
    """
    # Create Task from TaskCreate with injected user_id
    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    user_id: CurrentUserDep,  # Injected from JWT
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    completed: bool | None = None,
):
    """List all tasks for the authenticated user with pagination and filtering.

    Args:
        session: Database session
        user_id: UUID from JWT token (injected)
        offset: Number of tasks to skip (pagination)
        limit: Maximum number of tasks to return (default 50, max 100)
        completed: Optional filter by completion status

    Returns:
        List of tasks belonging to the authenticated user, filtered and paginated
    """
    statement = select(Task).where(Task.user_id == user_id)

    # Apply completion status filter if provided
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    # Apply pagination
    statement = statement.offset(offset).limit(limit)

    # Order by creation date (newest first)
    statement = statement.order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep  # Injected from JWT
):
    """Get a specific task by ID.

    Args:
        task_id: UUID of the task to retrieve
        session: Database session
        user_id: UUID from JWT token (injected)

    Returns:
        Task details if found and owned by authenticated user

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    session: SessionDep,
    user_id: CurrentUserDep  # Injected from JWT
):
    """Update an existing task.

    Args:
        task_id: UUID of the task to update
        task_update: Fields to update (all optional)
        session: Database session
        user_id: UUID from JWT token (injected)

    Returns:
        Updated task details

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: uuid.UUID,
    session: SessionDep,
    user_id: CurrentUserDep  # Injected from JWT
):
    """Delete a task.

    Args:
        task_id: UUID of the task to delete
        session: Database session
        user_id: UUID from JWT token (injected)

    Returns:
        Success confirmation

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
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
    user_id: CurrentUserDep  # Injected from JWT
):
    """Toggle task completion status.

    Args:
        task_id: UUID of the task to toggle
        session: Database session
        user_id: UUID from JWT token (injected)

    Returns:
        Task with toggled completion status

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
