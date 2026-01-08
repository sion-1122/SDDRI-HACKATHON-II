"""Task CRUD API endpoints.

Implements all task management operations:
- Create task
- List tasks
- Get task by ID
- Update task
- Delete task
- Toggle completion status
"""
import uuid
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select

from core.deps import SessionDep
from models.task import Task, TaskCreate, TaskUpdate, TaskRead

# Create API router with user_id prefix
router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    user_id: uuid.UUID,
    task: TaskCreate,
    session: SessionDep
):
    """Create a new task.

    Args:
        user_id: UUID of the user creating the task
        task: Task data from request body
        session: Database session

    Returns:
        Created task with generated ID and timestamps
    """
    # Create Task from TaskCreate with user_id
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
    user_id: uuid.UUID,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    completed: bool | None = None,
):
    """List all tasks for a user with pagination and filtering.

    Args:
        user_id: UUID of the user
        session: Database session
        offset: Number of tasks to skip (pagination)
        limit: Maximum number of tasks to return (default 50, max 100)
        completed: Optional filter by completion status

    Returns:
        List of tasks belonging to the user, filtered and paginated
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
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    """Get a specific task by ID.

    Args:
        user_id: UUID of the user
        task_id: UUID of the task to retrieve
        session: Database session

    Returns:
        Task details if found and owned by user

    Raises:
        HTTPException 404: If task not found or doesn't belong to user
    """
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
    """Update an existing task.

    Args:
        user_id: UUID of the user
        task_id: UUID of the task to update
        task_update: Fields to update (all optional)
        session: Database session

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
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    """Delete a task.

    Args:
        user_id: UUID of the user
        task_id: UUID of the task to delete
        session: Database session

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
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    session: SessionDep
):
    """Toggle task completion status.

    Args:
        user_id: UUID of the user
        task_id: UUID of the task to toggle
        session: Database session

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
