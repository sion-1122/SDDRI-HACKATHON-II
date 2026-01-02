"""Task data model for Todo CLI application."""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-incremented)
        description: Task description (1-1000 characters)
        completed: Completion status (defaults to False)
    """

    id: int
    description: str
    completed: bool = False

    # Constants for validation
    MIN_DESCRIPTION_LENGTH: Final[int] = 1
    MAX_DESCRIPTION_LENGTH: Final[int] = 1000

    def __post_init__(self):
        """Validate task constraints after initialization."""
        self._validate_description(self.description)
        self._validate_id(self.id)

    @staticmethod
    def _validate_description(description: str) -> None:
        """Validate task description meets constraints."""
        if not isinstance(description, str):
            raise TypeError("Description must be a string")

        cleaned = description.strip()
        if not cleaned:
            raise ValueError("Task description cannot be empty")
        if len(cleaned) < Task.MIN_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Task description too short "
                f"(min {Task.MIN_DESCRIPTION_LENGTH} character)"
            )
        if len(cleaned) > Task.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Task description too long "
                f"(max {Task.MAX_DESCRIPTION_LENGTH} characters)"
            )

    @staticmethod
    def _validate_id(id: int) -> None:
        """Validate task ID."""
        if not isinstance(id, int):
            raise TypeError("Task ID must be an integer")
        if id < 1:
            raise ValueError("Task ID must be positive")

    def toggle(self) -> "Task":
        """Return a new Task with completed status toggled.

        Returns:
            A new Task instance with flipped completed status
        """
        return Task(id=self.id, description=self.description, completed=not self.completed)

    def with_description(self, new_description: str) -> "Task":
        """Return a new Task with updated description.

        Args:
            new_description: New description for the task

        Returns:
            A new Task instance with updated description

        Raises:
            ValueError: If new_description fails validation
        """
        return Task(id=self.id, description=new_description, completed=self.completed)
