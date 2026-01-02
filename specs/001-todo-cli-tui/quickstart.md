# Quickstart Guide: Terminal-based Todo CLI with TUI

**Feature**: 001-todo-cli-tui
**Date**: 2026-01-02
**Phase**: Phase 1 - Design Artifacts

## Prerequisites

Before starting development, ensure you have the following installed:

1. **Python 3.13+**
   ```bash
   python --version  # Should show Python 3.13.0 or higher
   ```

2. **uv Package Manager**
   ```bash
   uv --version  # Should show uv version
   ```

   If not installed:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Git** (for version control)
   ```bash
   git --version
   ```

## Project Setup

### 1. Navigate to Project Directory

```bash
cd /path/to/todo-list-hackathon
```

### 2. Ensure You're on Correct Branch

```bash
git branch  # Should show * 001-todo-cli-tui
```

If not on the correct branch:
```bash
git checkout 001-todo-cli-tui
```

### 3. Create Project Structure

```bash
# Create cli directory structure
mkdir -p cli/models cli/ui cli/services tests/unit tests/integration tests/fixtures

# Create __init__.py files for Python packages
touch cli/__init__.py
touch cli/models/__init__.py
touch cli/ui/__init__.py
touch cli/services/__init__.py
```

### 4. Initialize Python Project with uv

```bash
cd cli
uv init --no-readme --name todo-cli-tui
```

This creates `pyproject.toml` with basic project metadata.

### 5. Update pyproject.toml

Edit `cli/pyproject.toml`:

```toml
[project]
name = "todo-cli-tui"
version = "0.1.0"
description = "A terminal-based Todo CLI with keyboard-driven TUI"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "textual>=0.80.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "textual[test]>=0.80.0",
]

[project.scripts]
todo = "todo_cli_tui.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["."]
omit = [
    "tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

### 6. Install Dependencies

```bash
cd cli
uv sync --extra dev
```

This installs:
- `textual` - TUI framework
- `pytest` - Test runner
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `textual[test]` - Textual testing utilities

### 7. Verify Installation

```bash
uv run python --version
uv run python -c "import textual; print(textual.__version__)"
```

Should print Textual version (e.g., `0.80.0`).

## Development Workflow

### Running the Application

```bash
# From cli directory
uv run python main.py

# Or using the script name (after installation)
uv run todo
```

**Expected behavior**:
- Application launches
- Greeting message displays
- Main menu appears with 5 options
- Arrow keys navigate menu
- Enter selects action
- Exit terminates cleanly

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=cli --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_task_model.py

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x
```

### Code Structure

```
cli/
├── main.py                  # Entry point, creates Textual App
├── models/
│   └── task.py             # Task dataclass
├── services/
│   └── task_service.py     # Task CRUD operations
├── ui/
│   ├── main_menu.py        # MainMenuScreen
│   ├── task_list.py        # TaskListScreen
│   ├── add_task.py         # AddTaskScreen
│   ├── edit_task.py        # EditTaskScreen
│   └── delete_task.py      # DeleteTaskScreen
└── tests/
    ├── unit/
    │   ├── test_task_model.py
    │   └── test_task_service.py
    └── integration/
        └── test_repl_flow.py
```

### Implementation Order

#### Phase 1: Foundation (Day 1)
1. Implement `models/task.py` - Task dataclass with validation
2. Implement `services/task_service.py` - Task CRUD operations
3. Write unit tests for Task model
4. Write unit tests for TaskService

#### Phase 2: UI Components (Day 2)
5. Implement `ui/main_menu.py` - Main menu screen with 5 buttons
6. Implement `ui/add_task.py` - Input prompt for new tasks
7. Wire up main.py to run MainMenuScreen first

#### Phase 3: Task Management (Day 2-3)
8. Implement `ui/task_list.py` - Display tasks with navigation
9. Implement `ui/edit_task.py` - Edit task description
10. Implement `ui/delete_task.py` - Delete task with confirmation
11. Connect all screens with TaskService

#### Phase 4: Polish & Testing (Day 3)
12. Add edge case handling (empty lists, long descriptions, etc.)
13. Write integration tests for REPL flow
14. Add visual polish (colors, styling, help text)
15. Test all user stories from spec

### Code Quality Standards

**Style Guide**: Follow PEP 8

```bash
# Install development tools (optional)
uv pip install ruff
```

**Type Hints**: Required for all functions

```python
def create_task(description: str) -> Task:
    """Create a new task."""
    ...
```

**Docstrings**: Google style for all public functions/classes

```python
def create_task(description: str) -> Task:
    """Create a new task and add to list.

    Args:
        description: Task description (1-1000 characters)

    Returns:
        Created Task object

    Raises:
        ValueError: If description validation fails
    """
    ...
```

## Testing Strategy

### Unit Tests

Test business logic in isolation (no UI):

```python
# tests/unit/test_task_service.py
def test_create_task_increments_id():
    """Test that each new task gets a unique incrementing ID."""
    service = TaskService()
    task1 = service.create_task("First task")
    task2 = service.create_task("Second task")

    assert task1.id == 1
    assert task2.id == 2
```

### Integration Tests

Test user journeys with Textual test utilities:

```python
# tests/integration/test_repl_flow.py
from textual.app import App
from textual.widgets import Input

async def test_add_task_flow():
    """Test adding a task through the UI."""
    app = App()
    async with app.run_test() as pilot:
        # Navigate to Add option
        await pilot.press("down")  # Move to Add
        await pilot.press("enter")  # Select Add

        # Enter task description
        await pilot.press("B", "u", "y", " ", "m", "i", "l", "k")
        await pilot.press("enter")  # Submit

        # Verify task was created
        # ...assertions here
```

### Coverage Target

- **Unit tests**: 90%+ coverage on models and services
- **UI tests**: 70%+ coverage on UI components
- **Overall**: 70%+ coverage target (per constitution)

## Debugging

### Running Textual Dev Tools

Textual includes a built-in debugger:

```bash
uv run python main.py --devtools
```

Press `Ctrl+Shift+D` to toggle dev tools overlay.

### Debug Mode

Add debug output:

```python
from textual.log import Log

class MainMenuScreen(Screen):
    def on_mount(self) -> None:
        self.log("Main menu mounted")
```

### Common Issues

**Issue**: Terminal shows garbled text
- **Solution**: Use a modern terminal emulator (VS Code terminal, iTerm2, Windows Terminal)

**Issue**: Arrow keys not working
- **Solution**: Ensure terminal sends proper escape codes (avoid ancient terminals)

**Issue**: Tests hang
- **Solution**: Use `pytest-asyncio` with `asyncio_mode = "auto"`

**Issue**: Import errors
- **Solution**: Run `uv sync` to ensure dependencies installed

## Keyboard Navigation Reference

| Key | Action | Context |
|-----|--------|---------|
| ↑ / ↓ | Navigate menu/list options | Main menu, task list |
| Enter | Select action/confirm | All screens |
| Space | Toggle completion | Task list only |
| Esc | Cancel/return to menu | Input prompts |
| Ctrl+C | Exit application | Anywhere |

## Success Criteria Verification

After implementation, verify each success criterion:

- **SC-001**: Time yourself launching and creating first task (<30 seconds)
- **SC-002**: Navigate all menu options without errors
- **SC-003**: Create 10+ tasks and verify no lag
- **SC-004**: Measure response time with stopwatch (<100ms for all actions)
- **SC-005**: Edit and delete tasks, verify immediate UI updates
- **SC-006**: Run application 10 times, verify clean exit each time
- **SC-007**: Try all actions, verify no crashes
- **SC-008**: Ask a colleague to use it without documentation
- **SC-009**: Run app with empty task list, verify graceful handling
- **SC-010**: Use app for 5 minutes, verify responsiveness

## Resources

### Documentation

- **Textual Docs**: https://textual.textual.io/
- **Textual Widgets**: https://textual.textual.io/widgets/
- **Textual Testing**: https://textual.textual.io/guide/testing/
- **Python Dataclasses**: https://docs.python.org/3/library/dataclasses.html

### Community

- **Textual Discord**: https://discord.gg/Textual
- **Textual GitHub**: https://github.com/Textualize/textual
- **Python Discord**: https://discord.gg/python

### Example Projects

- Textual examples: https://github.com/Textualize/textual/tree/main/examples
- Textual blog tutorials: https://textual.textual.io/blog/

## Troubleshooting FAQ

**Q: uv command not found**
- A: Ensure uv is installed and in PATH. Restart terminal after installation.

**Q: ImportError: No module named 'textual'**
- A: Run `uv sync` from cli directory to install dependencies.

**Q: Tests fail with "asyncio" errors**
- A: Ensure `pytest-asyncio` is installed and `asyncio_mode = "auto"` in pyproject.toml

**Q: Terminal doesn't restore after exit**
- A: Use Textual's `app.exit()` method, never `sys.exit()` directly

**Q: Where do I report bugs or ask questions?**
- A: Use project issues or team chat. For Textual-specific issues, check Textual GitHub first.

## Next Steps

1. ✅ Complete project setup
2. ⏳ Implement Task model (see data-model.md)
3. ⏳ Implement TaskService
4. ⏳ Build UI screens
5. ⏳ Write tests
6. ⏳ Verify all success criteria
7. ⏳ Celebrate 🎉
