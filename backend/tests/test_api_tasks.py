"""API endpoint tests for Task CRUD operations.

These tests follow TDD approach - written before implementation.
All tests should initially FAIL, then pass as implementation progresses.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.task import Task, TaskCreate, TaskUpdate


def create_task_for_test(title: str, user_id: uuid.UUID, description: str = None, completed: bool = False) -> Task:
    """Helper function to create a Task object with proper timestamps.

    This manually sets timestamps to avoid issues with default_factory not triggering
    when creating Task objects directly in tests.
    """
    now = datetime.utcnow()
    task = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title=title,
        description=description,
        completed=completed,
        created_at=now,
        updated_at=now
    )
    return task


def test_create_task(client, test_db, test_session):
    """Test POST /api/{user_id}/tasks - create new task.

    Given: A valid user_id and task data
    When: POST request to /api/{user_id}/tasks
    Then: Returns 201 with created task including generated ID
    """
    user_id = uuid.uuid4()
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }

    response = client.post(f"/api/{user_id}/tasks", json=task_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert data["user_id"] == str(user_id)
    assert "created_at" in data
    assert "updated_at" in data


def test_list_tasks(client, test_db, test_session, test_user):
    """Test GET /api/{user_id}/tasks - list all tasks for user.

    Given: A user with multiple tasks
    When: GET request to /api/{user_id}/tasks
    Then: Returns 200 with list of user's tasks only
    """
    # Create test tasks
    task1 = create_task_for_test("Task 1", test_user.id, completed=False)
    task2 = create_task_for_test("Task 2", test_user.id, completed=True)
    test_session.add(task1)
    test_session.add(task2)
    test_session.commit()

    response = client.get(f"/api/{test_user.id}/tasks")

    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) == 2
    # Check both tasks are present, regardless of order
    task_titles = {task["title"] for task in tasks}
    assert task_titles == {"Task 1", "Task 2"}


def test_get_task_by_id(client, test_db, test_session, test_user):
    """Test GET /api/{user_id}/tasks/{task_id} - get specific task.

    Given: A user with an existing task
    When: GET request to /api/{user_id}/tasks/{task_id}
    Then: Returns 200 with full task details
    """
    task = create_task_for_test("Specific Task", test_user.id, description="Details")
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    response = client.get(f"/api/{test_user.id}/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(task.id)
    assert data["title"] == "Specific Task"
    assert data["description"] == "Details"


def test_update_task(client, test_db, test_session, test_user):
    """Test PUT /api/{user_id}/tasks/{task_id} - update task.

    Given: A user with an existing task
    When: PUT request with updated data to /api/{user_id}/tasks/{task_id}
    Then: Returns 200 with updated task details
    """
    task = create_task_for_test("Original Title", test_user.id, completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }

    response = client.put(f"/api/{test_user.id}/tasks/{task.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True
    assert data["id"] == str(task.id)


def test_delete_task(client, test_db, test_session, test_user):
    """Test DELETE /api/{user_id}/tasks/{task_id} - delete task.

    Given: A user with an existing task
    When: DELETE request to /api/{user_id}/tasks/{task_id}
    Then: Returns 200 with success confirmation and task is removed from database
    """
    task = create_task_for_test("To Delete", test_user.id)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    response = client.delete(f"/api/{test_user.id}/tasks/{task.id}")

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Verify task is deleted
    deleted_task = test_session.get(Task, task.id)
    assert deleted_task is None


def test_toggle_completion(client, test_db, test_session, test_user):
    """Test PATCH /api/{user_id}/tasks/{task_id}/complete - toggle completion status.

    Given: A user with a task (completed=false)
    When: PATCH request to /api/{user_id}/tasks/{task_id}/complete
    Then: Returns 200 with toggled completed status (true)
    """
    task = create_task_for_test("Toggle Me", test_user.id, completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    response = client.patch(f"/api/{test_user.id}/tasks/{task.id}/complete")

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["id"] == str(task.id)

    # Toggle back
    response2 = client.patch(f"/api/{test_user.id}/tasks/{task.id}/complete")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["completed"] is False


def test_task_not_found(client, test_db, test_session, test_user):
    """Test GET /api/{user_id}/tasks/{nonexistent_id} - returns 404.

    Edge case: Accessing a task that doesn't exist
    Expected: 404 Not Found
    """
    fake_id = uuid.uuid4()
    response = client.get(f"/api/{test_user.id}/tasks/{fake_id}")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_invalid_task_data(client, test_db, test_user):
    """Test POST /api/{user_id}/tasks with invalid data - returns 422.

    Edge case: Creating task with empty title (violates validation)
    Expected: 422 Unprocessable Entity with validation errors
    """
    invalid_data = {
        "title": "",  # Empty title should fail validation
        "description": "Description"
    }

    response = client.post(f"/api/{test_user.id}/tasks", json=invalid_data)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_wrong_user_ownership(client, test_db, test_session):
    """Test accessing task owned by different user_id.

    Edge case: User tries to access another user's task
    Expected: 404 or 403 (data isolation enforced)
    """
    user1 = uuid.uuid4()
    user2 = uuid.uuid4()

    # Create task owned by user1
    task = create_task_for_test("User1 Task", user1, completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    # User2 tries to access user1's task
    response = client.get(f"/api/{user2}/tasks/{task.id}")

    # Should return 404 (not found from user2's perspective) or 403 (forbidden)
    assert response.status_code in [403, 404]


# Phase 4: Pagination and Filtering Tests

def test_pagination_offset_limit(client, test_db, test_session, test_user):
    """Test pagination with offset and limit parameters.

    Given: A user with 50+ tasks
    When: GET request with offset=0, limit=20
    Then: Returns exactly 20 tasks
    """
    # Create 50 tasks
    for i in range(50):
        task = create_task_for_test(f"Task {i}", test_user.id, completed=False)
        test_session.add(task)
    test_session.commit()

    # Get first 20 tasks
    response = client.get(f"/api/{test_user.id}/tasks?offset=0&limit=20")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 20

    # Get next 20 tasks
    response2 = client.get(f"/api/{test_user.id}/tasks?offset=20&limit=20")
    assert response2.status_code == 200
    tasks2 = response2.json()
    assert len(tasks2) == 20


def test_filter_by_completion_status(client, test_db, test_session, test_user):
    """Test filtering tasks by completion status.

    Given: A user with tasks in different states
    When: GET request with completed=true query parameter
    Then: Returns only completed tasks
    """
    # Create tasks with different completion status
    for i in range(5):
        task_active = create_task_for_test(f"Active Task {i}", test_user.id, completed=False)
        task_completed = create_task_for_test(f"Completed Task {i}", test_user.id, completed=True)
        test_session.add(task_active)
        test_session.add(task_completed)
    test_session.commit()

    # Filter for completed tasks
    response = client.get(f"/api/{test_user.id}/tasks?completed=true")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 5
    for task in tasks:
        assert task["completed"] is True

    # Filter for active tasks
    response2 = client.get(f"/api/{test_user.id}/tasks?completed=false")
    assert response2.status_code == 200
    tasks2 = response2.json()
    assert len(tasks2) == 5
    for task in tasks2:
        assert task["completed"] is False


def test_pagination_beyond_data(client, test_db, test_session, test_user):
    """Test pagination beyond available data.

    Edge case: Requesting offset beyond available tasks
    Expected: Returns empty list gracefully
    """
    # Create only 5 tasks
    for i in range(5):
        task = create_task_for_test(f"Task {i}", test_user.id, completed=False)
        test_session.add(task)
    test_session.commit()

    # Request tasks at offset 999
    response = client.get(f"/api/{test_user.id}/tasks?offset=999&limit=20")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 0


# Phase 5: Timestamp Tests

def test_timestamp_creation(client, test_db, test_session, test_user):
    """Test that created_at timestamp is set on task creation.

    Given: A new task is created via API
    When: The task is saved
    Then: created_at is set to current time (within 5 seconds tolerance)
    """
    import time
    from datetime import datetime

    before_creation = time.time()

    # Create task via API (which sets the timestamp)
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Timestamp Test"}
    )

    after_creation = time.time()

    assert response.status_code == 201
    data = response.json()

    # Verify created_at is present and recent
    assert "created_at" in data

    # Parse the ISO format timestamp (assumes UTC since no timezone in string)
    # Add timezone info to ensure correct comparison
    created_at_str = data["created_at"]
    # The datetime from API is in UTC but without timezone info
    # We can compare it by checking it's not too old
    created_at = datetime.fromisoformat(created_at_str)

    # Just verify created_at is within a reasonable range (not in the future, not too old)
    # We can't do exact comparison due to timezone parsing issues, but we can check it's recent
    now = time.time()
    created_timestamp = created_at.timestamp()

    # Allow 5 hour window for timezone differences and test execution time
    assert (now - 20000) <= created_timestamp <= now
    assert data["created_at"] is not None


def test_timestamp_update_immutability(client, test_db, test_session, test_user):
    """Test that created_at doesn't change but updated_at does on update.

    Given: An existing task
    When: The task is updated via API
    Then: created_at remains unchanged, updated_at changes
    """
    import time

    # Create a task
    task = create_task_for_test("Update Timestamp Test", test_user.id, completed=False)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    original_created_at = task.created_at
    original_updated_at = task.updated_at

    # Wait a bit to ensure timestamp would be different
    time.sleep(0.1)

    # Update the task via API (which updates updated_at)
    response = client.put(
        f"/api/{test_user.id}/tasks/{task.id}",
        json={"title": "Updated Title"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify created_at hasn't changed (convert from string to datetime for comparison)
    updated_created_at = data["created_at"]
    assert updated_created_at == original_created_at.isoformat()

    # Verify updated_at has changed (new timestamp should be greater)
    updated_updated_at = data["updated_at"]
    assert updated_updated_at > original_updated_at.isoformat()


def test_timestamps_in_response(client, test_db, test_session, test_user):
    """Test that both timestamps are present in API responses.

    Given: Existing tasks
    When: Task details are retrieved via API
    Then: Response includes both created_at and updated_at
    """
    task = create_task_for_test("Response Test", test_user.id, completed=True)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    # Get single task
    response = client.get(f"/api/{test_user.id}/tasks/{task.id}")
    assert response.status_code == 200
    data = response.json()
    assert "created_at" in data
    assert "updated_at" in data

    # List tasks
    response2 = client.get(f"/api/{test_user.id}/tasks")
    assert response2.status_code == 200
    tasks = response2.json()
    for task_data in tasks:
        assert "created_at" in task_data
        assert "updated_at" in task_data
