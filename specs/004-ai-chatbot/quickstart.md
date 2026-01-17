# Quickstart Guide: Todo AI Chatbot

**Feature**: 004-ai-chatbot
**Phase**: III
**Last Updated**: 2025-01-15

## Overview

This guide helps you quickly set up and run the Phase III AI Chatbot system locally. The chatbot enables natural language task management through a conversational interface.

---

## Prerequisites

### System Requirements

- **Python**: 3.13+
- **Node.js**: 18+ (for frontend)
- **PostgreSQL**: Access to Neon Serverless PostgreSQL database
- **Gemini API Key**: Valid API key for Google Gemini models (free tier)

### Required Accounts

1. **Neon Database**: Free account at [neon.tech](https://neon.tech)
2. **Google AI Studio**: API key from [aistudio.google.com](https://aistudio.google.com) (free tier)

### Existing Phase II Setup

This guide assumes you have:
- Phase II backend (FastAPI) running
- Phase II frontend (Next.js) configured
- Better Auth authentication working
- Existing Task and User models in database

---

## Environment Variables

Create a `.env` file in the repository root:

```bash
# Database (existing from Phase II)
DATABASE_URL=postgresql://user:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication (existing from Phase II)
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Gemini API (new for Phase III)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Application (existing from Phase II)
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Getting Gemini API Key (Free Tier)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key" or navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `AIza`)
6. Add to `.env` file as `GEMINI_API_KEY`

**Note**: Gemini API offers free tier access with generous rate limits for development and testing.

---

## Installation

### Backend Setup

```bash
# Navigate to repository root
cd /path/to/todo-list-hackathon

# Install backend dependencies (if not already installed)
cd backend
uv sync

# Install Phase III dependencies
uv add "openai>=1.0.0" "mcp>=0.9.0"
uv add "google-generativeai>=0.8.0"  # For Gemini integration
uv add pydantic
```

### Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies (if not already installed)
npm install
# or
pnpm install

# Install ChatKit React (Phase III dependency)
npm install @openai/chatkit-react
# or
pnpm add @openai/chatkit-react
# or
yarn add @openai/chatkit-react
```

---

## Database Migration

Run the database migration to create Conversation and Message tables:

```bash
# From repository root
cd backend

# Run migration using Alembic (if using Alembic)
uv run alembic upgrade head

# Or run SQL migration manually
psql $DATABASE_URL < migrations/003_add_conversation_and_message_tables.sql
```

**Verify Migration**:
```bash
# Check tables exist
psql $DATABASE_URL

# In PostgreSQL shell:
\dt
# Should show: conversation, message tables

\d conversation
\d message
```

---

## Running the Backend

### Start FastAPI Server

```bash
cd backend

# Start with auto-reload (development)
uv run uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Or without auto-reload (production)
uv run uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

**Verify Backend**:
- Open browser: `http://localhost:8000/docs`
- Should see FastAPI auto-generated documentation
- Check that `/api/{user_id}/chat` endpoint is listed

### Backend Health Check

```bash
# Check API is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

---

## Running the Frontend

### Start Next.js Development Server

```bash
cd frontend

# Start development server
npm run dev
# or
pnpm dev
```

**Verify Frontend**:
- Open browser: `http://localhost:3000`
- Should see existing Phase II task management UI
- Navigate to: `http://localhost:3000/chat`
- Should see chat interface (if Chat UI component implemented)

---

## Testing the Chat API

### 1. Get JWT Token

First, authenticate via Better Auth to get a JWT token:

```bash
# Login endpoint (adjust based on your auth implementation)
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'

# Response includes JWT token
# Save the token for next steps
JWT="your-jwt-token-here"
USER_ID=123  # Extract from JWT payload or use known user ID
```

### 2. Create New Conversation

Send first message without `conversation_id`:

```bash
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

**Expected Response**:
```json
{
  "message_id": "msg-456-xyz",
  "conversation_id": "conv-abc-123",
  "role": "assistant",
  "content": "I've added the task 'buy groceries' to your list.",
  "created_at": "2025-01-15T10:30:45Z"
}
```

**Save `conversation_id` for next requests!**

### 3. Continue Conversation

Use `conversation_id` from previous response:

```bash
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my pending tasks?",
    "conversation_id": "conv-abc-123"
  }'
```

**Expected Response**:
```json
{
  "message_id": "msg-789-xyz",
  "conversation_id": "conv-abc-123",
  "role": "assistant",
  "content": "You have 1 pending task:\n1. Buy groceries",
  "created_at": "2025-01-15T10:31:15Z"
}
```

### 4. Test Task Operations

**Complete a Task**:
```bash
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark task 1 as complete",
    "conversation_id": "conv-abc-123"
  }'
```

**Delete a Task**:
```bash
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete the groceries task",
    "conversation_id": "conv-abc-123"
  }'
```

---

## Testing MCP Tools Independently

If you want to test MCP tools without the full AI agent:

### 1. Start MCP Server

```bash
cd backend/mcp_server

# Run MCP server in stdio mode (for testing)
uv run python server.py
```

### 2. Test Tool Invocation

```python
# test_mcp_tools.py
import asyncio
from backend.mcp_server.server import app
from backend.mcp_server.tools import add_task, list_tasks

async def test_tools():
    # Test add_task
    result = await add_task(
        title="Test task via MCP",
        description="Testing MCP tool directly",
        user_id=123
    )
    print("add_task result:", result)

    # Test list_tasks
    tasks = await list_tasks(user_id=123, completed=None)
    print("list_tasks result:", tasks)

# Run test
asyncio.run(test_tools())
```

---

## Troubleshooting

### Issue: "Invalid or missing JWT token"

**Cause**: JWT not passed or expired

**Solution**:
```bash
# Verify JWT is valid
echo $JWT

# Get fresh JWT by logging in again
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Issue: "Conversation not found"

**Cause**: `conversation_id` doesn't exist or belongs to different user

**Solution**:
- Verify `conversation_id` from previous response
- Check you're using same `user_id` in URL path
- Try omitting `conversation_id` to create new conversation

### Issue: "AI service temporarily unavailable"

**Cause**: Gemini API key missing, invalid, or API down

**Solution**:
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Verify key format (should start with AIza)
# Test key manually:
curl "https://generativelanguage.googleapis.com/v1beta/models" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

### Issue: "Database connection failed"

**Cause**: DATABASE_URL incorrect or database not accessible

**Solution**:
```bash
# Test database connection
psql $DATABASE_URL

# Check connection string format
# Should be: postgresql://user:pass@host/db?sslmode=require
```

### Issue: Migration fails with "table already exists"

**Cause**: Migration already run

**Solution**:
```bash
# Check if tables exist
psql $DATABASE_URL -c "\dt"

# If tables exist, migration already applied
# Can skip migration step
```

### Issue: Frontend chat UI not loading

**Cause**: @openai/chatkit-react not installed or component not implemented

**Solution**:
```bash
# Verify ChatKit installed
cd frontend
npm list | grep @openai/chatkit-react

# If not installed:
npm install @openai/chatkit-react
# or
pnpm add @openai/chatkit-react

# Check browser console for errors
# Open DevTools → Console tab
```

---

## Development Tips

### 1. View Database Records

```sql
-- Connect to database
psql $DATABASE_URL

-- View conversations
SELECT * FROM conversation WHERE user_id = 123;

-- View messages for a conversation
SELECT * FROM message WHERE conversation_id = 'conv-abc-123';

-- View tasks created via chat
SELECT * FROM task WHERE user_id = 123 ORDER BY created_at DESC;
```

### 2. Monitor Backend Logs

```bash
# Backend logs will show:
# - Incoming chat requests
# - AI agent decisions
# - MCP tool invocations
# - Database queries
# - Errors with stack traces

# Example output:
INFO:     127.0.0.1:54321 - "POST /api/123/chat HTTP/1.1" 200 OK
INFO:     AI agent invoked with tools: add_task
INFO:     MCP tool executed: add_task(title="buy groceries", user_id=123)
INFO:     Task created: id=456
```

### 3. Test AI Agent Response Quality

```bash
# Test various natural language inputs:
- "Create a task to call mom tonight at 7pm"
- "Show me my tasks"
- "What do I need to do today?"
- "I finished the groceries task"
- "Remove the meeting task"
- "Update task 1 to say buy milk and eggs"
```

---

## Performance Testing

### Load Testing Chat Endpoint

```bash
# Using Apache Bench (ab)
ab -n 100 -c 10 \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -p chat_request.json \
  http://localhost:8000/api/123/chat

# chat_request.json:
# {"message": "Add a test task", "conversation_id": null}

# Expected: <3s response time (95th percentile)
```

---

## Next Steps

Once the system is running:

1. **Implement Chat UI**: Build React components for chat interface
2. **Add Error Handling**: Improve error messages and retries
3. **Implement Rate Limiting**: Add per-user rate limits
4. **Add Monitoring**: Track response times and error rates
5. **Test E2E**: Write end-to-end tests for chat flows
6. **Deploy**: Deploy to production environment

---

## Useful Commands Reference

```bash
# Backend
cd backend
uv sync                              # Install dependencies
uv run uvicorn backend.app:app --reload  # Start dev server
uv run pytest tests/                 # Run tests
uv run alembic upgrade head          # Run migrations

# Frontend
cd frontend
npm install                          # Install dependencies
npm run dev                          # Start dev server
npm run build                        # Build for production
npm run test                         # Run tests

# Database
psql $DATABASE_URL                   # Connect to database
pg_dump $DATABASE_URL > backup.sql   # Backup database
psql $DATABASE_URL < backup.sql     # Restore database
```

---

## Getting Help

- **Backend Issues**: Check `backend/CLAUDE.md`
- **Frontend Issues**: Check `frontend/CLAUDE.md`
- **Spec/Plan**: Check `specs/004-ai-chatbot/`
- **Constitution**: Check `.specify/memory/constitution.md`

---

**Quickstart Version**: 1.0.0
**Last Updated**: 2025-01-15
**Status**: ✅ Complete
