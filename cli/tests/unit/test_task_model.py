"""Unit tests for Task model."""

import pytest

from cli.models.task import Task


class TestTaskValidation:
    """Test Task validation logic."""

    def test_create_valid_task(self):
        """Test creating a valid task."""
        task = Task(id=1, description="Buy groceries")
        assert task.id == 1
        assert task.description == "Buy groceries"
        assert task.completed is False

    def test_create_task_with_whitespace_description(self):
        """Test task with leading/trailing whitespace."""
        task = Task(id=1, description="  Buy groceries  ")
        assert task.description == "  Buy groceries  "

    def test_create_task_with_empty_description_fails(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task(id=1, description="")

    def test_create_task_with_whitespace_only_description_fails(self):
        """Test that whitespace-only description raises ValueError."""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task(id=1, description="   ")

    def test_create_task_with_too_long_description_fails(self):
        """Test that overly long description raises ValueError."""
        long_desc = "a" * 1001
        with pytest.raises(ValueError, match="Task description too long"):
            Task(id=1, description=long_desc)

    def test_create_task_with_non_string_description_fails(self):
        """Test that non-string description raises TypeError."""
        with pytest.raises(TypeError, match="Description must be a string"):
            Task(id=1, description=123)

    def test_create_task_with_zero_id_fails(self):
        """Test that zero ID raises ValueError."""
        with pytest.raises(ValueError, match="Task ID must be positive"):
            Task(id=0, description="Test")

    def test_create_task_with_negative_id_fails(self):
        """Test that negative ID raises ValueError."""
        with pytest.raises(ValueError, match="Task ID must be positive"):
            Task(id=-1, description="Test")

    def test_create_task_with_non_int_id_fails(self):
        """Test that non-integer ID raises TypeError."""
        with pytest.raises(TypeError, match="Task ID must be an integer"):
            Task(id="1", description="Test")  # type: ignore

    def test_create_completed_task(self):
        """Test creating a task with completed=True."""
        task = Task(id=1, description="Walk the dog", completed=True)
        assert task.completed is True


class TestTaskMethods:
    """Test Task methods."""

    def test_toggle_from_uncompleted_to_completed(self):
        """Test toggling from uncompleted to completed."""
        task = Task(id=1, description="Test task", completed=False)
        toggled = task.toggle()
        assert toggled.completed is True
        assert toggled.id == task.id
        assert toggled.description == task.description

    def test_toggle_from_completed_to_uncompleted(self):
        """Test toggling from completed to uncompleted."""
        task = Task(id=1, description="Test task", completed=True)
        toggled = task.toggle()
        assert toggled.completed is False
        assert toggled.id == task.id
        assert toggled.description == task.description

    def test_with_description_updates_description(self):
        """Test updating task description."""
        task = Task(id=1, description="Original description")
        updated = task.with_description("New description")
        assert updated.description == "New description"
        assert updated.id == task.id
        assert updated.completed == task.completed

    def test_with_description_validates_new_description(self):
        """Test that with_description validates the new description."""
        task = Task(id=1, description="Original")
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            task.with_description("")

    def test_task_immutability(self):
        """Test that Task is immutable (frozen dataclass)."""
        task = Task(id=1, description="Test")
        with pytest.raises(Exception):  # FrozenInstanceError
            task.id = 2  # type: ignore


class TestTaskConstants:
    """Test Task validation constants."""

    def test_min_description_length_constant(self):
        """Test MIN_DESCRIPTION_LENGTH constant."""
        assert Task.MIN_DESCRIPTION_LENGTH == 1

    def test_max_description_length_constant(self):
        """Test MAX_DESCRIPTION_LENGTH constant."""
        assert Task.MAX_DESCRIPTION_LENGTH == 1000
