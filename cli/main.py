"""Main entry point for Todo CLI TUI application."""

from textual.app import App
from textual.widgets import Header, Footer

from cli.services.task_service import TaskService
from cli.ui.main_menu import MainMenuScreen


class TodoApp(App):
    """Todo CLI TUI application."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def __init__(self):
        """Initialize the Todo application."""
        super().__init__()
        self.task_service = TaskService()

    def on_mount(self) -> None:
        """Display greeting and show main menu on startup."""
        # Display greeting message
        self.notify(
            "Welcome to Todo CLI! Use arrow keys to navigate, Enter to select.",
            title="Todo CLI",
            severity="information",
            timeout=5,
        )
        # Set main menu as initial screen
        self.push_screen(MainMenuScreen(self.task_service, self.return_to_main_menu))

    def return_to_main_menu(self) -> None:
        """Return to the main menu."""
        self.pop_screen()
        if len(self.screen_stack) == 0:
            self.push_screen(MainMenuScreen(self.task_service, self.return_to_main_menu))


def main():
    """Main entry point for the application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
