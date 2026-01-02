"""Task list screen for Todo CLI application."""

from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Header, Button
from textual.containers import Vertical, Horizontal
from textual import on
from textual.events import Key

from cli.services.task_service import TaskService


class TaskListScreen(Screen):
    """Screen for listing and viewing tasks."""

    BINDINGS = [
        ("enter", "return_to_menu", "Return to Menu"),
        ("space", "toggle_completion", "Toggle Completion"),
    ]

    def __init__(self, task_service: TaskService, return_callback):
        """Initialize task list screen.

        Args:
            task_service: TaskService instance for task operations
            return_callback: Function to call when returning to menu
        """
        super().__init__()
        self.task_service = task_service
        self.return_callback = return_callback
        self.selected_task_id = None
        self.task_id_map = {}  # Maps list index to task ID

    def compose(self):
        """Compose the task list UI."""
        with Vertical():
            yield Header()
            yield Label("Your Tasks:", id="title-label")

            # Get all tasks
            tasks = self.task_service.get_all_tasks()

            if not tasks:
                yield Label("No tasks yet. Add some tasks to get started!", id="empty-label")
            else:
                yield Label("Select a task and press Space to toggle completion", id="help-label-top")

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

            with Horizontal():
                yield Button("Return to Menu", id="return-btn", variant="primary")

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle task selection from list."""
        try:
            # Get the selected index and lookup task ID from our map
            selected_index = event.list_view.index
            if selected_index in self.task_id_map:
                self.selected_task_id = self.task_id_map[selected_index]
        except (ValueError, IndexError, AttributeError):
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "return-btn":
            self.return_callback()

    def action_return_to_menu(self) -> None:
        """Action to return to main menu (triggered by Enter key)."""
        self.return_callback()

    def action_toggle_completion(self) -> None:
        """Toggle completion status of selected task (triggered by Space key)."""
        if self.selected_task_id is None:
            self.notify("Please select a task first!", severity="warning")
            return

        try:
            task = self.task_service.toggle_task_completion(self.selected_task_id)
            status = "completed" if task.completed else "uncompleted"
            self.notify(f"Task {task.id} marked as {status}", severity="information")
            # Refresh the screen to show updated status
            self.refresh_screen()
        except ValueError as e:
            self.notify(str(e), severity="error")

    def refresh_screen(self) -> None:
        """Refresh the task list display."""
        # Remove existing list view if present
        try:
            list_view = self.query_one("#task-list-view", ListView)
            list_view.remove()
        except:
            pass

        # Get all tasks
        tasks = self.task_service.get_all_tasks()

        if not tasks:
            # Show empty state
            return

        # Create new list items for each task
        list_items = []
        self.task_id_map = {}  # Reset the map
        for index, task in enumerate(tasks):
            status = "[x]" if task.completed else "[ ]"
            list_items.append(
                ListItem(Label(f"{status} {task.id}: {task.description}"))
            )
            # Rebuild the map
            self.task_id_map[index] = task.id

        # Mount new list view
        new_list_view = ListView(*list_items, id="task-list-view")
        self.mount(new_list_view, before="#return-btn")

