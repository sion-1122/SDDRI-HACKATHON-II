"""Delete task screen for Todo CLI application."""

from textual.screen import Screen
from textual.widgets import Header, Label, Button, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual import on

from cli.services.task_service import TaskService


class DeleteTaskScreen(Screen):
    """Screen for deleting an existing task."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter,d", "delete_selected", "Delete Selected"),
    ]

    def __init__(self, task_service: TaskService, return_callback):
        """Initialize delete task screen.

        Args:
            task_service: TaskService instance for task operations
            return_callback: Function to call after deleting task
        """
        super().__init__()
        self.task_service = task_service
        self.return_callback = return_callback
        self.selected_task_id = None
        self.task_id_map = {}  # Maps list index to task ID

    def compose(self):
        """Compose the delete task UI."""
        with Vertical():
            yield Header()
            yield Label("Select a task to delete:", id="select-label")

            # Get all tasks
            tasks = self.task_service.get_all_tasks()

            if not tasks:
                yield Label("No tasks to delete. Add some tasks first!", id="empty-label")
                with Horizontal():
                    yield Button("Return to Menu", id="return-btn", variant="primary")
            else:
                # Create list items for each task
                list_items = []
                for index, task in enumerate(tasks):
                    status = "[x]" if task.completed else "[ ]"
                    list_items.append(
                        ListItem(Label(f"{status} {task.id}: {task.description}"))
                    )
                    # Map index to task ID for easy lookup
                    self.task_id_map[index] = task.id

                yield ListView(*list_items, id="task-list-view")

                yield Label("Press Enter or D to delete selected task, Esc to cancel", id="help-label")

                with Horizontal():
                    yield Button("Delete Selected", id="delete-btn", variant="error")
                    yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        """Set focus when screen is mounted."""
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            self.set_focus(None, "return-btn")
        else:
            self.set_focus(None, "task-list-view")

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection from list."""
        try:
            # Get the selected index and lookup task ID from our map
            selected_index = event.list_view.index
            if selected_index in self.task_id_map:
                self.selected_task_id = self.task_id_map[selected_index]
                self.notify(f"Selected task {self.selected_task_id} - Press Enter to delete", severity="information")
            else:
                self.notify("Error selecting task", severity="error")
        except (ValueError, IndexError, AttributeError) as e:
            self.notify(f"Error selecting task: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "delete-btn":
            self.delete_selected_task()
        elif event.button.id == "cancel-btn" or event.button.id == "return-btn":
            self.return_callback()

    def action_cancel(self) -> None:
        """Cancel and return to main menu."""
        self.return_callback()

    def action_delete_selected(self) -> None:
        """Delete the selected task."""
        self.delete_selected_task()

    def delete_selected_task(self) -> None:
        """Delete the selected task with confirmation."""
        if self.selected_task_id is None:
            self.notify("Please select a task first!", severity="error")
            return

        try:
            # Get task for confirmation message
            task = self.task_service.get_task_by_id(self.selected_task_id)
            if task:
                description = task.description
                self.task_service.delete_task(self.selected_task_id)
                self.notify(f"Task deleted: {description}", severity="information")
            else:
                self.notify(f"Task {self.selected_task_id} not found!", severity="error")
            self.return_callback()
        except ValueError as e:
            self.notify(str(e), severity="error")
