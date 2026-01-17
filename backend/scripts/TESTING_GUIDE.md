# Chatbot Testing Guide

## Quick Start

### 1. Start the backend server

```bash
cd backend
uv run uvicorn main:app --reload
```

### 2. Run the test script (in a new terminal)

```bash
cd backend
PYTHONPATH=. uv run python scripts/test_chatbot_prompts.py
```

## Options

```bash
# Custom API URL
python scripts/test_chatbot_prompts.py --base-url http://localhost:8000

# Specific user ID
python scripts/test_chatbot_prompts.py --user-id "your-user-uuid-here"

# Custom output file
python scripts/test_chatbot_prompts.py --output my_test_report.json

# Longer timeout (for slow AI responses)
python scripts/test_chatbot_prompts.py --timeout 60
```

## Test Coverage

| Category | Tests | Description |
|----------|-------|-------------|
| add_task | 2 | Create tasks with various attributes |
| list_tasks | 2 | List all and filtered tasks |
| update_task | 1 | Modify existing task |
| complete_task | 2 | Mark single/all tasks complete |
| delete_task | 1 | Delete single task |
| delete_all_tasks | 1 | Delete all with confirmation |
| edge_case | 1 | Empty task list handling |
| ambiguous_reference | 1 | Position-based task references |

## Sample Output

```
============================================================
Chatbot Test Suite
Target: http://localhost:8000
User ID: 123e4567-e89b-12d3-a456-426614174000
Started at: 2025-01-17T10:30:00
============================================================

[1] Testing: add_task
    Prompt: "Add a task to buy groceries"
    ✓ PASS
    Response: "I've added the task 'buy groceries' for you."

...

============================================================
TEST REPORT
============================================================

Summary:
  Total Tests:  11
  Passed:       10 ✓
  Failed:       1 ✗
  Pass Rate:    90.9%
  Duration:     15.23s

Results by Category:
  add_task: Passed: 2/2
  list_tasks: Passed: 2/2
  ...

============================================================
Report saved to: test_chatbot_report.json
```

## Manual Testing (curl)

```bash
# Set variables
USER_ID="your-user-uuid"
API_URL="http://localhost:8000"

# Test 1: Add a task
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# Test 2: List tasks (using returned conversation_id)
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my tasks?", "conversation_id": "returned-uuid"}'

# Test 3: Complete all tasks
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark all tasks as complete", "conversation_id": "returned-uuid"}'
```
