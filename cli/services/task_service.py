"""Task service for managing in-memory task storage."""

from typing import List, Optional

from cli.models.task import Task


class TaskService:
    """Manages in-memory task storage and operations."""

    def __init__(self) -> None:
        """Initialize empty task list and ID counter."""
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def create_task(self, description: str) -> Task:
        """Create a new task and add to list.

        Args:
            description: Task description

        Returns:
            Created Task object

        Raises:
            ValueError: If description validation fails
        """
        task = Task(id=self._next_id, description=description.strip(), completed=False)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in insertion order.

        Returns:
            List of all tasks (copy to prevent external modification)
        """
        return self._tasks.copy()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, new_description: str) -> Task:
        """Update task description.

        Args:
            task_id: ID of task to update
            new_description: New description

        Returns:
            Updated Task object

        Raises:
            ValueError: If task not found or description invalid
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                updated_task = task.with_description(new_description)
                self._tasks[i] = updated_task
                return updated_task
        raise ValueError(f"Task {task_id} not found")

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID.

        Args:
            task_id: ID of task to delete

        Raises:
            ValueError: If task not found
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return
        raise ValueError(f"Task {task_id} not found")

    def toggle_task_completion(self, task_id: int) -> Task:
        """Toggle task completion status.

        Args:
            task_id: ID of task to toggle

        Returns:
            Updated Task with toggled completion status

        Raises:
            ValueError: If task not found
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                toggled_task = task.toggle()
                self._tasks[i] = toggled_task
                return toggled_task
        raise ValueError(f"Task {task_id} not found")

    def task_count(self) -> int:
        """Get total number of tasks.

        Returns:
            Count of tasks in list
        """
        return len(self._tasks)

    def is_empty(self) -> bool:
        """Check if task list is empty.

        Returns:
            True if no tasks, False otherwise
        """
        return len(self._tasks) == 0
