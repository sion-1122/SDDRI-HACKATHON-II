"""Add task screen for Todo CLI application."""

from textual.screen import Screen
from textual.widgets import Input, Header, Label, Button
from textual.containers import Vertical
from textual import on

from cli.services.task_service import TaskService


class AddTaskScreen(Screen):
    """Screen for adding a new task."""

    BINDINGS = [
        ("escape,c", "cancel", "Cancel"),
    ]

    def __init__(self, task_service: TaskService, return_callback):
        """Initialize add task screen.

        Args:
            task_service: TaskService instance for task operations
            return_callback: Function to call after adding task
        """
        super().__init__()
        self.task_service = task_service
        self.return_callback = return_callback

    def compose(self):
        """Compose the add task UI."""
        with Vertical():
            yield Header()
            yield Label("Enter task description:", id="prompt-label")
            yield Input(
                placeholder="What needs to be done?",
                id="task-input",
            )
            yield Label("Press Enter to save, Esc to cancel", id="help-label")
            yield Button("Save Task", id="save-btn", variant="primary")
            yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Set focus to input when screen is mounted."""
        self.set_focus(None, "task-input")

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle task input submission."""
        self.save_task(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            input_widget = self.query_one("#task-input", Input)
            self.save_task(input_widget.value)
        elif event.button.id == "cancel-btn":
            self.return_callback()

    def action_cancel(self) -> None:
        """Cancel and return to main menu."""
        self.return_callback()

    def save_task(self, description: str) -> None:
        """Save the task with validation."""
        if not description or not description.strip():
            self.notify("Task description cannot be empty!", severity="error")
            return

        try:
            self.task_service.create_task(description)
            self.notify(f"Task created: {description}", severity="information")
            self.return_callback()
        except ValueError as e:
            self.notify(str(e), severity="error")

