# Research Findings: Terminal-based Todo CLI with TUI

**Feature**: 001-todo-cli-tui
**Date**: 2026-01-02
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for the Phase 1 Todo CLI TUI application. All decisions align with the constitution requirements and specification success criteria.

## Decision 1: TUI Library Selection

### Options Evaluated

1. **Textual** (https://github.com/Textualize/textual)
   - Modern, async-first TUI framework
   - Rich widget library (ListView, Input, Button, etc.)
   - Built-in keyboard navigation and event handling
   - Excellent documentation and examples
   - Active development and community
   - Requires Python 3.8+ (✅ compatible with 3.13)

2. **Rich** (https://github.com/Textualize/rich)
   - Primarily a terminal formatting library
   - Some interactive features but limited widget support
   - Better suited for output formatting than full TUI apps
   - Would require building custom widgets

3. **prompt_toolkit** (https://github.com/prompt-toolkit/python-prompt-toolkit)
   - Mature, battle-tested library
   - Used by popular tools (ipython, psql)
   - Lower-level than Textual, more manual work required
   - Steeper learning curve for complex layouts

### Decision: **Textual**

**Rationale**:
- Textual provides the most complete TUI framework with built-in widgets for our needs
- `ListView` widget perfect for main menu and task list navigation
- `Input` widget handles text input with validation
- Built-in keyboard navigation (arrow keys, enter, space) out of the box
- Event-driven architecture aligns with REPL pattern
- Excellent documentation reduces learning curve
- Async support allows for responsive UI even during operations
- Cross-platform compatibility (Linux, macOS, Windows)

**Alternatives Considered**: prompt_toolkit (too low-level, would require more code), Rich (not designed for interactive TUI apps)

**Impact**: This decision affects the entire UI architecture. All UI components will be built as Textual widgets/screens.

## Decision 2: Terminal State Management

### Best Practices Identified

1. **Use Textual's Built-in App Lifecycle**
   - Textual's `App.run()` handles terminal initialization
   - Automatic cleanup via context manager or `exit()` method
   - Signal handling (SIGINT, SIGTERM) built-in

2. **Terminal Resizing**
   - Textual automatically handles terminal resize events
   - Widgets reflow to fit new dimensions
   - No manual intervention required for basic layouts

3. **Clean Exit Strategy**
   - Use Textual's `app.exit()` method for graceful shutdown
   - Textual restores terminal state automatically
   - Register cleanup handlers if needed via `atexit` module

4. **Cross-Platform Compatibility**
   - Textual uses `curses` on Unix and `windows-curses` on Windows
   - Abstraction layer handles platform differences
   - No platform-specific code required for basic features

### Decision: **Rely on Textual's Built-in State Management**

**Rationale**:
- Textual has been battle-tested across platforms
- Built-in cleanup reduces risk of broken terminal state
- Automatic resize handling meets spec requirements
- Aligns with SC-006 (100% clean exit rate)

**Implementation Notes**:
- Use `app.push_screen()` and `app.pop_screen()` for navigation
- Call `app.exit()` to terminate application cleanly
- No manual terminal manipulation needed

## Decision 3: Task Storage Pattern

### Options Evaluated

1. **List of Task Objects**
   ```python
   tasks: List[Task] = []
   # Access by iteration
   # ID lookup requires O(n) search
   ```

2. **Dictionary Mapping ID to Task**
   ```python
   tasks: Dict[int, Task] = {}
   # O(1) access by ID
   # Requires maintaining separate ID counter
   ```

3. **Hybrid Approach**
   ```python
   tasks: List[Task] = []  # For ordered display
   _next_id: int = 1       # Auto-increment counter
   # Task objects carry their own ID
   ```

### Decision: **List of Task Objects with Auto-Increment ID**

**Rationale**:
- **Ordering**: List maintains insertion order, perfect for display
- **Simplicity**: Single data structure, no synchronization issues
- **Performance**: For 10-100 tasks (spec range), O(n) operations are negligible
- **ID Generation**: Simple counter starting at 1, incrementing on each add
- **Memory Efficiency**: Single list is most memory-efficient
- **Deletion**: List comprehension or `remove()` for deletion is straightforward

**Implementation Pattern**:
```python
class TaskService:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def create_task(self, description: str) -> Task:
        task = Task(id=self._next_id, description=description, completed=False)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        return self._tasks.copy()  # Return copy to prevent external modification
```

**Alternatives Considered**: Dictionary mapping (unnecessary complexity for small task count)

**Performance Considerations**:
- 10 tasks: All operations <1ms (well under 100ms requirement)
- 100 tasks: Still <1ms for all operations
- 1000 tasks: O(n) operations ~1-2ms (still acceptable)

## Decision 4: Testing TUI Applications

### Patterns Identified

1. **Separation of Concerns**
   - Business logic (TaskService) tested independently without UI
   - UI components tested with mock services
   - Integration tests use Textual's testing utilities

2. **Textual Testing Approach**
   - Textual provides `pip install textual[test]` with testing utilities
   - `app.press(keys)` simulates keyboard input
   - `app.query()` queries widget state
   - Async test runners (pytest-asyncio) required

3. **Mocking Strategy**
   - Mock TaskService for UI component tests
   - Use pytest fixtures for test data
   - Stub user input where needed

### Decision: **Three-Layer Testing Strategy**

**Layer 1: Unit Tests (Business Logic)**
- Test TaskService methods without any UI
- Test Task model validation
- Use standard pytest, no TUI dependencies
- Target: 90%+ coverage on business logic

**Layer 2: Component Tests (UI Widgets)**
- Test individual screens/widgets in isolation
- Mock TaskService responses
- Use Textual's testing utilities for keyboard/input simulation
- Target: 70%+ coverage on UI code

**Layer 3: Integration Tests (REPL Flow)**
- Test full user journeys (add task, list tasks, etc.)
- Test navigation between screens
- Test edge cases (empty lists, long descriptions, etc.)
- Use Textual's `app.run()` with async pytest

**Testing Stack**:
- `pytest` for test runner
- `pytest-asyncio` for async Textual tests
- `textual[test]` for TUI testing utilities
- `pytest-cov` for coverage reporting

**Alternatives Considered**: Manual testing (insufficient for CI), end-to-end scripting tests (too brittle for TUI)

## Decision 5: Auto-Increment ID Strategy

### Options Evaluated

1. **Simple Counter**
   ```python
   self._next_id: int = 1
   # Increment on each add
   ```

2. **Max Existing ID + 1**
   ```python
   self._next_id = max(task.id for task in tasks) + 1 if tasks else 1
   # Recalculate on each add
   ```

3. **UUID**
   ```python
   from uuid import uuid4
   task.id = str(uuid4())
   # Not user-friendly
   ```

### Decision: **Simple Counter with Persistence in Memory**

**Rationale**:
- **User-Friendly**: Sequential IDs (1, 2, 3...) are easier to reference
- **Simple**: Single integer variable, minimal code
- **Performance**: O(1) operation
- **Consistent**: No gaps in ID sequence during session
- **Spec-Aligned**: IDs reset each session (no persistence required)

**Implementation**:
```python
class TaskService:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def create_task(self, description: str) -> Task:
        task = Task(id=self._next_id, description=description, completed=False)
        self._tasks.append(task)
        self._next_id += 1
        return task
```

**Alternatives Considered**: UUID (not user-friendly for CLI), max+1 (unnecessary complexity)

## Decision 6: Input Validation Strategy

### Requirements from Spec

- FR-023: Validate that task descriptions are not empty before creating or updating
- Edge cases: Empty strings, whitespace-only strings, extremely long strings

### Decision: **Strip and Validate Approach**

**Validation Rules**:
1. Strip leading/trailing whitespace
2. Check if resulting string is empty
3. Check if string exceeds reasonable max length (e.g., 1000 chars)
4. Display user-friendly error messages

**Implementation**:
```python
def validate_task_description(description: str) -> str:
    """Validate and normalize task description."""
    cleaned = description.strip()
    if not cleaned:
        raise ValueError("Task description cannot be empty")
    if len(cleaned) > 1000:
        raise ValueError("Task description too long (max 1000 characters)")
    return cleaned
```

**Error Handling in UI**:
- Catch validation errors in UI layer
- Display error message in modal or inline
- Keep user on same screen to retry input

## Decision 7: REPL Architecture Pattern

### Options Evaluated

1. **Single Screen with State Machine**
   - One screen with state variable (menu, list, edit, etc.)
   - Conditional rendering based on state
   - Simple but can get complex

2. **Screen Stack (Textual Approach)**
   - Separate Screen classes for each view
   - Use `app.push_screen()` to navigate
   - Use `app.pop_screen()` to return
   - Native Textual pattern

### Decision: **Screen Stack Architecture**

**Rationale**:
- **Separation of Concerns**: Each screen is independent
- **Navigation**: Push/pop naturally implements "return to main menu" (FR-018)
- **State**: Screen parameters pass data between screens
- **Maintainability**: Easy to add new screens
- **Textual-Native**: Uses framework's intended architecture

**Screen Structure**:
- `MainMenuScreen`: Entry point with 5 action buttons
- `TaskListScreen`: Display tasks with toggle/delete/edit options
- `AddTaskScreen`: Input prompt for new task
- `EditTaskScreen`: Input prompt for editing task
- `DeleteConfirmationScreen`: Confirm before delete (optional UX enhancement)

**Navigation Flow**:
```
MainMenuScreen → TaskListScreen → (action) → MainMenuScreen
MainMenuScreen → AddTaskScreen → MainMenuScreen
MainMenuScreen → EditTaskScreen → TaskListScreen → MainMenuScreen
MainMenuScreen → DeleteTaskScreen → TaskListScreen → MainMenuScreen
MainMenuScreen → Exit → App Termination
```

## Technology Stack Summary

### Core Dependencies

```toml
[project]
name = "todo-cli-tui"
version = "0.1.0"
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
```

### Development Tools

- **Package Manager**: `uv` (as specified in user input)
- **Test Runner**: `pytest`
- **Coverage**: `pytest-cov`
- **Linting**: `ruff` (optional, for code quality)

### Platform Support

- **Primary**: Linux (WSL2 compatible)
- **Secondary**: macOS, Windows (via Textual's cross-platform support)
- **Terminal Requirements**: Any ANSI-compatible terminal

## Unresolved Questions

**None** - All research questions have been resolved with clear decisions.

## Next Steps

1. ✅ Research complete
2. ⏳ Create data-model.md (entity definitions, validation rules)
3. ⏳ Create quickstart.md (setup, development workflow)
4. ⏳ Re-validate constitution check with technology decisions
5. ⏳ Update agent context

## References

- Textual Documentation: https://textual.textual.io/
- Textual GitHub: https://github.com/Textualize/textual
- Python Packaging Guidelines: https://packaging.python.org/
- pytest-asyncio Documentation: https://pytest-asyncio.readthedocs.io/
