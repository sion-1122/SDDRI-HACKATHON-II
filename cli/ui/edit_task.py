"""Edit task screen for Todo CLI application."""

from textual.screen import Screen
from textual.widgets import Input, Header, Label, Button, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual import on

from cli.services.task_service import TaskService
from cli.models.task import Task


class EditTaskScreen(Screen):
    """Screen for editing an existing task."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, task_service: TaskService, return_callback):
        """Initialize edit task screen.

        Args:
            task_service: TaskService instance for task operations
            return_callback: Function to call after editing task
        """
        super().__init__()
        self.task_service = task_service
        self.return_callback = return_callback
        self.selected_task_id = None
        self.task_id_map = {}  # Maps list index to task ID

    def compose(self):
        """Compose the edit task UI."""
        with Vertical():
            yield Header()
            yield Label("Select a task to edit:", id="select-label")

            # Get all tasks
            tasks = self.task_service.get_all_tasks()

            if not tasks:
                yield Label("No tasks to edit. Add some tasks first!", id="empty-label")
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

                yield Label("Enter new description:", id="prompt-label")
                yield Input(
                    placeholder="Edit task description...",
                    id="edit-input",
                )
                yield Label("Press Enter to save, Esc to cancel", id="help-label")

                with Horizontal():
                    yield Button("Save Edit", id="save-btn", variant="primary")
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
                self.notify(f"Selected task {self.selected_task_id}", severity="information")
                # Move focus to input
                self.set_focus(None, "edit-input")
            else:
                self.notify("Error selecting task", severity="error")
        except (ValueError, IndexError, AttributeError) as e:
            self.notify(f"Error selecting task: {e}", severity="error")

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle edit input submission."""
        if self.selected_task_id is None:
            self.notify("Please select a task first!", severity="error")
            return
        self.save_edit(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            if self.selected_task_id is None:
                self.notify("Please select a task first!", severity="error")
                return
            input_widget = self.query_one("#edit-input", Input)
            self.save_edit(input_widget.value)
        elif event.button.id == "cancel-btn" or event.button.id == "return-btn":
            self.return_callback()

    def action_cancel(self) -> None:
        """Cancel and return to main menu."""
        self.return_callback()

    def save_edit(self, new_description: str) -> None:
        """Save the edited task with validation."""
        if not new_description or not new_description.strip():
            self.notify("Task description cannot be empty!", severity="error")
            return

        if self.selected_task_id is None:
            self.notify("No task selected!", severity="error")
            return

        try:
            self.task_service.update_task(self.selected_task_id, new_description)
            self.notify(f"Task {self.selected_task_id} updated: {new_description}", severity="information")
            self.return_callback()
        except ValueError as e:
            self.notify(str(e), severity="error")
