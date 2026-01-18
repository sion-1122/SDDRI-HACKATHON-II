# Quickstart Guide: Todo AI Chatbot

**Feature**: 004-ai-chatbot
**Last Updated**: 2025-01-17

## Overview

This guide helps you quickly set up and run the AI Chatbot system locally. The chatbot enables natural language task management through a conversational interface with 7 integrated tools.

---

## Prerequisites

### System Requirements

- **Python**: 3.13+
- **Node.js**: 18+ (for frontend)
- **Package Manager**: UV (Python), pnpm (frontend)
- **PostgreSQL**: Neon Serverless PostgreSQL database
- **Gemini API Key**: Valid API key for Google Gemini models (free tier)

### Required Accounts

1. **Neon Database**: Free account at [neon.tech](https://neon.tech)
2. **Google AI Studio**: API key from [aistudio.google.com](https://aistudio.google.com) (free tier)

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require

# Gemini API (required for AI chatbot)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Application
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Getting Gemini API Key (Free Tier)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key" or navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `AIza`)
6. Add to `backend/.env` as `GEMINI_API_KEY`

---

## Installation

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
uv sync

# Verify installation
uv run python -c "from openai import AsyncOpenAI; print('OpenAI SDK ready')"
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
pnpm install
# or
npm install
```

---

## Database Migration

Run the database migration to create Conversation and Message tables:

```bash
# From backend directory
cd backend

# Run migrations
PYTHONPATH=. uv run python -c "
from migrations.run_migration import run_migration
run_migration()
"
```

**Verify Migration**:
```bash
# Check tables exist
psql $DATABASE_URL

# In PostgreSQL shell:
\dt
# Should show: conversations, messages, tasks, users

\d conversations
\d messages
```

---

## Running the Backend

```bash
cd backend

# Start with auto-reload (development)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or with custom config
uv run uvicorn uvicorn_config:app --reload
```

**Verify Backend**:
- Open browser: `http://localhost:8000/docs`
- Should see FastAPI auto-generated documentation
- Check that `/api/{user_id}/chat` endpoint is listed

---

## Running the Frontend

```bash
cd frontend

# Start development server
pnpm dev
# or
npm run dev
```

**Verify Frontend**:
- Open browser: `http://localhost:3000`
- Navigate to: `http://localhost:3000/chat`
- Should see chat interface

---

## Testing the Chatbot

### Using the Test Script

A comprehensive test script is included:

```bash
cd backend

# Run the test script
PYTHONPATH=. uv run python scripts/test_chatbot_prompts.py

# With custom options
PYTHONPATH=. uv run python scripts/test_chatbot_prompts.py \
  --base-url http://localhost:8000 \
  --user-id test-user-123
```

### Manual Testing with curl

```bash
# Set variables
USER_ID="test-user-123"
API_URL="http://localhost:8000"

# 1. Create a task
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# 2. List tasks (use returned conversation_id)
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my tasks?", "conversation_id": "returned-id"}'

# 3. Complete a task
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark the first task as complete", "conversation_id": "returned-id"}'

# 4. Delete all tasks (with confirmation)
curl -X POST "$API_URL/api/$USER_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Delete all tasks", "conversation_id": "returned-id"}'
```

---

## MCP Tools Available

The AI chatbot has access to 7 MCP tools:

1. **add_task**: Create tasks with title, description, due date, priority
2. **list_tasks**: List and filter tasks (all/pending/completed)
3. **update_task**: Modify existing tasks
4. **complete_task**: Toggle task completion
5. **delete_task**: Remove tasks
6. **complete_all_tasks**: Bulk completion with count reporting
7. **delete_all_tasks**: Bulk deletion with confirmation

---

## Troubleshooting

### Issue: "AI service temporarily unavailable"

**Cause**: Gemini API key missing or invalid

**Solution**:
```bash
# Check .env file
cat backend/.env | grep GEMINI_API_KEY

# Verify key format (should start with AIza)
```

### Issue: Rate limit errors

**Cause**: Daily message limit exceeded (100/day)

**Solution**: The limit resets daily. For development, you can adjust in `backend/services/rate_limiter.py`.

### Issue: Conversation not persisting

**Cause**: localStorage not available or cleared

**Solution**: Check browser console for storage errors. Ensure browser allows localStorage.

---

## Project Structure

```
backend/
├── ai_agent/              # AI agent with Gemini integration
│   └── agent_simple.py   # Main agent implementation
├── api/                   # FastAPI endpoints
│   └── chat.py           # Chat endpoint
├── mcp_server/           # MCP tools
│   └── tools/            # 7 task management tools
├── models/               # Database models
│   ├── conversation.py
│   └── message.py
├── services/             # Business logic
│   ├── conversation.py
│   ├── rate_limiter.py
│   ├── security.py
│   └── audit.py
└── migrations/           # Database migrations
    └── 002_add_conversation_and_message_tables.sql

frontend/
└── src/
    ├── app/chat/        # Chat page
    │   └── page.tsx
    └── components/chat/
        └── ChatInterface.tsx
```

---

## Getting Help

- **Backend Issues**: Check `backend/CLAUDE.md`
- **Frontend Issues**: Check `frontend/CLAUDE.md`
- **Spec/Plan**: Check `specs/004-ai-chatbot/`

---

**Quickstart Version**: 2.0.0
**Last Updated**: 2025-01-17
**Status**: ✅ Complete
