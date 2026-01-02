"""Unit tests for TaskService."""

import pytest

from cli.models.task import Task
from cli.services.task_service import TaskService


class TestTaskServiceCreate:
    """Test task creation operations."""

    def test_create_task_returns_task_with_auto_increment_id(self):
        """Test that create_task assigns auto-incrementing IDs."""
        service = TaskService()
        task1 = service.create_task("First task")
        task2 = service.create_task("Second task")

        assert task1.id == 1
        assert task2.id == 2

    def test_create_task_adds_to_internal_list(self):
        """Test that created tasks are added to internal list."""
        service = TaskService()
        service.create_task("New task")

        assert service.task_count() == 1
        assert not service.is_empty()

    def test_create_task_sets_completed_to_false(self):
        """Test that new tasks have completed=False."""
        service = TaskService()
        task = service.create_task("New task")

        assert task.completed is False

    def test_create_task_strips_description(self):
        """Test that description is stripped."""
        service = TaskService()
        task = service.create_task("  Buy groceries  ")

        # Note: The task stores the stripped version
        assert task.description == "Buy groceries"

    def test_create_task_with_empty_description_fails(self):
        """Test that empty description raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            service.create_task("")


class TestTaskServiceRetrieve:
    """Test task retrieval operations."""

    def test_get_all_tasks_returns_all_tasks(self):
        """Test that get_all_tasks returns all created tasks."""
        service = TaskService()
        service.create_task("Task 1")
        service.create_task("Task 2")

        tasks = service.get_all_tasks()

        assert len(tasks) == 2
        assert tasks[0].description == "Task 1"
        assert tasks[1].description == "Task 2"

    def test_get_all_tasks_returns_copy_not_internal_list(self):
        """Test that get_all_tasks returns a copy, not the internal list."""
        service = TaskService()
        service.create_task("Task 1")

        tasks = service.get_all_tasks()
        tasks.clear()  # Modify the returned list

        # Original should be unchanged
        assert service.task_count() == 1

    def test_get_all_tasks_returns_empty_list_initially(self):
        """Test that get_all_tasks returns empty list initially."""
        service = TaskService()

        tasks = service.get_all_tasks()

        assert tasks == []

    def test_get_task_by_id_with_valid_id(self):
        """Test getting a task by valid ID."""
        service = TaskService()
        task = service.create_task("Test task")

        found = service.get_task_by_id(task.id)

        assert found is not None
        assert found.description == "Test task"

    def test_get_task_by_id_with_invalid_id(self):
        """Test getting a task by invalid ID returns None."""
        service = TaskService()
        service.create_task("Test task")

        found = service.get_task_by_id(999)

        assert found is None


class TestTaskServiceUpdate:
    """Test task update operations."""

    def test_update_task_modifies_description(self):
        """Test that update_task changes task description."""
        service = TaskService()
        task = service.create_task("Original")

        updated = service.update_task(task.id, "Updated")

        assert updated.description == "Updated"
        # Verify the task in the list was updated
        retrieved = service.get_task_by_id(task.id)
        assert retrieved.description == "Updated"

    def test_update_task_preserves_id_and_completion(self):
        """Test that update_task preserves id and completed status."""
        service = TaskService()
        task = service.create_task("Original")

        updated = service.update_task(task.id, "Updated")

        assert updated.id == task.id
        assert updated.completed == task.completed

    def test_update_task_with_invalid_id_fails(self):
        """Test that updating non-existent task raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task 999 not found"):
            service.update_task(999, "New description")

    def test_update_task_with_empty_description_fails(self):
        """Test that updating with empty description raises ValueError."""
        service = TaskService()
        task = service.create_task("Original")

        with pytest.raises(ValueError, match="Task description cannot be empty"):
            service.update_task(task.id, "")


class TestTaskServiceDelete:
    """Test task deletion operations."""

    def test_delete_task_removes_from_list(self):
        """Test that delete_task removes the task."""
        service = TaskService()
        task = service.create_task("To be deleted")

        service.delete_task(task.id)

        assert service.task_count() == 0
        assert service.is_empty()

    def test_delete_task_with_invalid_id_fails(self):
        """Test that deleting non-existent task raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task 999 not found"):
            service.delete_task(999)


class TestTaskServiceToggle:
    """Test task completion toggle operations."""

    def test_toggle_task_completion_from_false_to_true(self):
        """Test toggling from uncompleted to completed."""
        service = TaskService()
        task = service.create_task("Test task")

        toggled = service.toggle_task_completion(task.id)

        assert toggled.completed is True
        # Verify the task in the list was updated
        retrieved = service.get_task_by_id(task.id)
        assert retrieved.completed is True

    def test_toggle_task_completion_from_true_to_false(self):
        """Test toggling from completed to uncompleted."""
        service = TaskService()
        task = Task(id=1, description="Test", completed=True)
        service._tasks.append(task)

        toggled = service.toggle_task_completion(task.id)

        assert toggled.completed is False

    def test_toggle_task_completion_with_invalid_id_fails(self):
        """Test that toggling non-existent task raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError, match="Task 999 not found"):
            service.toggle_task_completion(999)


class TestTaskServiceUtility:
    """Test TaskService utility methods."""

    def test_task_count_returns_zero_initially(self):
        """Test that task_count returns 0 initially."""
        service = TaskService()
        assert service.task_count() == 0

    def test_task_count_returns_number_of_tasks(self):
        """Test that task_count returns correct count."""
        service = TaskService()
        service.create_task("Task 1")
        service.create_task("Task 2")
        service.create_task("Task 3")

        assert service.task_count() == 3

    def test_is_empty_returns_true_initially(self):
        """Test that is_empty returns True initially."""
        service = TaskService()
        assert service.is_empty() is True

    def test_is_empty_returns_false_after_adding_task(self):
        """Test that is_empty returns False after adding task."""
        service = TaskService()
        service.create_task("Task")

        assert service.is_empty() is False
