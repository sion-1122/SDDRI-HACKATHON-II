"""Main menu screen for Todo CLI application."""

from textual.screen import Screen
from textual.widgets import Button, Header
from textual.containers import Vertical
from textual import on

from cli.services.task_service import TaskService
from cli.ui.add_task import AddTaskScreen
from cli.ui.task_list import TaskListScreen
from cli.ui.edit_task import EditTaskScreen
from cli.ui.delete_task import DeleteTaskScreen


class MainMenuScreen(Screen):
    """Main menu screen with action buttons."""

    def __init__(self, task_service: TaskService, return_callback):
        """Initialize main menu screen.

        Args:
            task_service: TaskService instance for task operations
            return_callback: Function to call when returning to main menu
        """
        super().__init__()
        self.task_service = task_service
        self.return_callback = return_callback

    def compose(self):
        """Compose the main menu UI."""
        with Vertical(id="main-menu"):
            yield Header()
            yield Button("Add Task", id="add-btn", variant="primary")
            yield Button("List Tasks", id="list-btn", variant="default")
            yield Button("Edit Task", id="edit-btn", variant="default")
            yield Button("Delete Task", id="delete-btn", variant="default")
            yield Button("Exit", id="exit-btn", variant="error")

    def on_mount(self) -> None:
        """Set initial focus when screen is mounted."""
        # Focus the first button so keyboard navigation works immediately
        self.set_focus(None, "add-btn")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "add-btn":
            self.app.push_screen(AddTaskScreen(self.task_service, self.return_callback))
        elif button_id == "list-btn":
            self.app.push_screen(TaskListScreen(self.task_service, self.return_callback))
        elif button_id == "edit-btn":
            self.app.push_screen(EditTaskScreen(self.task_service, self.return_callback))
        elif button_id == "delete-btn":
            self.app.push_screen(DeleteTaskScreen(self.task_service, self.return_callback))
        elif button_id == "exit-btn":
            self.app.exit()

