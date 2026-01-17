# AI Chatbot Integration Guide

[From]: Phase III Integration Setup

This guide explains how to integrate and test the AI chatbot feature.

## Prerequisites

1. **Python 3.13+** installed
2. **UV** package manager installed
3. **Gemini API key** from [Google AI Studio](https://aistudio.google.com)
4. **PostgreSQL database** (Neon or local)

## Setup Steps

### 1. Backend Configuration

#### Environment Variables

Add to your `backend/.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database

# Gemini API (Required for AI chatbot)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# JWT
JWT_SECRET=your-jwt-secret-here
JWT_ALGORITHM=HS256

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

#### Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key"
4. Copy the API key
5. Add it to your `.env` file as `GEMINI_API_KEY`

**Note**: Gemini API has a free tier that's sufficient for development and testing.

### 2. Database Migration

The chatbot requires two additional tables: `conversation` and `message`.

Run the migration:

```bash
cd backend
python migrations/run_migration.py
```

Expected output:
```
✅ 2/2 migrations completed successfully
🎉 All migrations completed!
```

### 3. Install Dependencies

```bash
cd backend
uv sync
```

This installs:
- `openai>=1.0.0` - OpenAI SDK (for AsyncOpenAI adapter)
- `agents` - OpenAI Agents SDK
- All other dependencies

### 4. Validate Integration

Run the integration validation script:

```bash
cd backend
python scripts/validate_chat_integration.py
```

This checks:
- ✅ Dependencies installed
- ✅ Environment variables configured
- ✅ Database tables exist
- ✅ MCP tools registered
- ✅ AI agent initialized
- ✅ Chat API routes registered

### 5. Start the Backend Server

```bash
cd backend
uv run python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the Chat API

#### Option A: Interactive API Docs

Open browser: `http://localhost:8000/docs`

Find the `POST /api/{user_id}/chat` endpoint and test it:

**Request:**
```json
{
  "message": "Create a task to buy groceries"
}
```

**Expected Response:**
```json
{
  "response": "I'll create a task titled 'Buy groceries' for you.",
  "conversation_id": "uuid-here",
  "tasks": []
}
```

#### Option B: cURL

```bash
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy groceries"
  }'
```

Replace `{user_id}` with a valid user UUID.

#### Option C: Python Test Script

```python
import requests
import uuid

# Replace with actual user ID from your database
user_id = "your-user-uuid-here"

response = requests.post(
    f"http://localhost:8000/api/{user_id}/chat",
    json={"message": "Create a task to buy groceries"}
)

print(response.json())
```

### 7. Frontend Integration (Optional)

If you have the frontend running:

1. Start the frontend:
   ```bash
   cd frontend
   pnpm dev
   ```

2. Open browser: `http://localhost:3000/chat`

3. Test the chat interface with messages like:
   - "Create a task to buy groceries"
   - "What are my tasks?"
   - "Show me my pending tasks"
   - "Create a high priority task to finish the report by Friday"

## API Endpoints

### Chat Endpoint

**POST** `/api/{user_id}/chat`

**Request Body:**
```json
{
  "message": "Create a task to buy groceries",
  "conversation_id": "optional-uuid-to-continue-conversation"
}
```

**Response:**
```json
{
  "response": "I'll create a task titled 'Buy groceries' for you.",
  "conversation_id": "uuid",
  "tasks": []
}
```

**Error Responses:**

- **400 Bad Request**: Invalid message (empty or >10,000 characters)
- **429 Too Many Requests**: Daily message limit exceeded (100/day)
- **503 Service Unavailable**: AI service not configured or unreachable
- **504 Gateway Timeout**: AI service timeout

## Troubleshooting

### "AI service not configured"

**Cause**: `GEMINI_API_KEY` not set in `.env`

**Fix**:
1. Get API key from https://aistudio.google.com
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Restart server

### "Database error: relation 'conversation' does not exist"

**Cause**: Migration not run

**Fix**:
```bash
cd backend
python migrations/run_migration.py
```

### "Daily message limit exceeded"

**Cause**: User has sent 100+ messages today

**Fix**: Wait until midnight UTC or use a different user ID for testing

### Import errors for `agents` or `openai`

**Cause**: Dependencies not installed

**Fix**:
```bash
cd backend
uv sync
```

## Testing Checklist

- [ ] Environment variables configured (especially `GEMINI_API_KEY`)
- [ ] Database migrations run successfully
- [ ] Validation script passes all checks
- [ ] Backend server starts without errors
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can send message via `/api/{user_id}/chat` endpoint
- [ ] AI responds with task creation confirmation
- [ ] Can list tasks via chat
- [ ] Conversation persists across requests (using `conversation_id`)
- [ ] Frontend chat page works (if applicable)

## Rate Limiting

The chatbot enforces a limit of **100 messages per user per day** (NFR-011).

This includes both user and assistant messages in conversations.

The limit resets at midnight UTC.

## Architecture Overview

```
Frontend (React)
    ↓
ChatInterface.tsx → POST /api/{user_id}/chat
    ↓
Backend (FastAPI)
    ↓
chat.py endpoint
    ├→ Rate limiting check (T021)
    ├→ Get/create conversation (T016)
    ├→ Persist user message (T017)
    ├→ Load conversation history (T016)
    ├→ Run AI agent (T014)
    │   ↓
    │   Agent → MCP Tools
    │       ├→ add_task (T013)
    │       └→ list_tasks (T024, T027)
    └→ Persist AI response (T018)
```

## MCP Tools

The AI agent has access to two MCP tools:

### add_task

Creates a new task.

**Parameters:**
- `user_id` (required): User UUID
- `title` (required): Task title
- `description` (optional): Task description
- `due_date` (optional): Due date (ISO 8601 or relative)
- `priority` (optional): "low", "medium", or "high"

### list_tasks

Lists and filters tasks.

**Parameters:**
- `user_id` (required): User UUID
- `status` (optional): "all", "pending", or "completed"
- `due_within_days` (optional): Filter by due date
- `limit` (optional): Max tasks to return (1-100, default 50)

## Next Steps

After successful integration:

1. **Test User Story 1**: Create tasks via natural language
2. **Test User Story 2**: List and filter tasks via natural language
3. **Monitor rate limiting**: Ensure 100/day limit works
4. **Test error handling**: Try without API key, with invalid user ID, etc.
5. **Proceed to User Story 3**: Task updates via natural language

## Support

For issues or questions:
- Check the validation script output: `python scripts/validate_chat_integration.py`
- Review API docs: http://localhost:8000/docs
- Check backend logs for detailed error messages
