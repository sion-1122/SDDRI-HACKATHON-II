# Quickstart Guide: Intermediate Todo Features

**Feature**: 007-intermediate-todo-features
**Date**: 2026-01-28
**Phase**: Phase 1 (Design)

## Prerequisites

- Completed Phase III (004-ai-chatbot) with working AI chatbot interface
- Completed Phase V (005-ux-improvement) with Notion-inspired design
- Python 3.13+ installed
- Node.js 20+ installed
- PostgreSQL database (Neon) connection configured

---

## Development Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already done)
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Migration

```bash
# Run the migration to add new columns
uv run alembic upgrade head

# Or run SQL directly via psql
psql $DATABASE_URL -f migrations/add_priority_tags_due_date.sql
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Set environment variables
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

---

## Running the Application

### Development Mode

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Access Points

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Feature Testing

### 1. Priority Management

**Natural Language Commands**:
```
Add urgent task: Call mom about birthday party
Add high priority task: Finish project proposal
Add low priority task: Organize desk whenever
```

**Expected Results**:
- "urgent" and "ASAP" → High priority (red badge)
- "high priority" → High priority
- "low priority" / "whenever" → Low priority (gray badge)
- No priority mentioned → Medium priority (yellow badge)

### 2. Tag Management

**Natural Language Commands**:
```
Add work task: Submit report tagged with project-x, urgent
Add shopping task: Buy groceries tagged with home
```

**Expected Results**:
- Tasks display with colored tag badges
- Tags are consistent in color (same tag = same color)
- Filter by tag works correctly

### 3. Search Functionality

**Client-Side Search** (< 100 tasks):
1. Create 20+ tasks with varied content
2. Type in search box
3. Results appear instantly (< 200ms)
4. Matching text is highlighted

**Server-Side Search** (≥ 100 tasks):
1. Create 100+ tasks
2. Type in search box
3. Loading indicator appears
4. Results appear after 300ms debounce

### 4. Filtering

**Test Cases**:
```
Show high priority tasks
Show pending work tasks
Show tasks due today
Show tasks tagged with shopping AND urgent
```

**Expected Results**:
- Filters apply with AND logic
- Task count updates: "Showing 5 of 50 tasks"
- Filters persist in URL

### 5. Sorting

**Test Cases**:
```
Sort by due date (ascending)
Sort by priority (high to low)
Sort by newest first
Sort alphabetically A-Z
```

**Expected Results**:
- Tasks reorder correctly
- Sort preference remembered during session

### 6. UI Components

**Modal/Dialog Test**:
1. Open on mobile (375px width)
2. Should be 90-95% of screen width
3. No horizontal scroll
4. Content is legible

**Sheet Test**:
1. Open sheet in chatbot UI
2. Should render at appropriate width
3. No layout breakage

---

## API Testing

### Using cURL

```bash
# Set your JWT token
export TOKEN="your_jwt_token_here"

# List tasks with filters
curl -X GET "http://localhost:8000/api/tasks?status=pending&priority=high&due_date=today" \
  -H "Authorization: Bearer $TOKEN"

# Create task with priority and tags
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete feature spec",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-30T18:00:00Z"
  }'

# Update task priority
curl -X PATCH "http://localhost:8000/api/tasks/{task_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"priority": "low"}'

# Search tasks
curl -X GET "http://localhost:8000/api/tasks/search?q=work" \
  -H "Authorization: Bearer $TOKEN"

# Get all tags
curl -X GET "http://localhost:8000/api/tags" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Swagger UI

Navigate to http://localhost:8000/docs and use the interactive API documentation.

---

## File Structure

### Backend Files to Create/Modify

```
backend/
├── models/
│   └── task.py                    # [MODIFY] Add priority, tags, due_date
├── services/
│   ├── task_service.py            # [MODIFY] Add filter/sort/search logic
│   └── nlp_service.py             # [MODIFY] Add priority extraction
├── api/
│   └── tasks.py                   # [MODIFY] Add filter/sort/search endpoints
├── mcp_server/
│   └── tools.py                   # [MODIFY] Add MCP tools for new features
└── tests/
    └── test_task_service.py       # [MODIFY] Add tests for filter/sort/search
```

### Frontend Files to Create/Modify

```
frontend/
├── components/
│   ├── chat/
│   │   ├── TaskCard.tsx           # [MODIFY] Add priority badge, tag badges
│   │   ├── TaskList.tsx           # [MODIFY] Add filter/sort/search UI
│   │   └── SearchBar.tsx          # [ADD] Client-side search with debounce
│   └── ui/
│       ├── Modal.tsx              # [FIX/ADD] Responsive modal component
│       └── Sheet.tsx              # [FIX/ADD] Responsive sheet component
├── lib/
│   ├── api.ts                     # [MODIFY] Add filter/sort/search API calls
│   ├── tagColors.ts               # [ADD] Tag color utilities
│   └── timezone.ts                # [ADD] Timezone utilities
└── hooks/
    └── useTaskFilters.ts          # [ADD] Hook for filter/sort/search state
```

---

## Troubleshooting

### Database Migration Fails

**Issue**: Migration script fails with "column already exists"

**Solution**:
```sql
-- Check if columns already exist
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks';

-- If columns exist, rollback migration
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_priority;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
ALTER TABLE tasks DROP COLUMN IF EXISTS tags;
ALTER TABLE_tasks DROP COLUMN IF EXISTS due_date;
```

### Priority Not Extracting

**Issue**: Natural language commands don't extract priority

**Solution**:
1. Check OpenAI API key is set in `.env`
2. Verify agent configuration in `backend/ai_agent/agent.py`
3. Check agent logs for errors

### Tag Colors Inconsistent

**Issue**: Same tag shows different colors

**Solution**:
1. Ensure `getTagColor()` function uses deterministic hash
2. Check that color palette is constant
3. Clear browser cache and reload

### Search Too Slow

**Issue**: Search takes > 500ms

**Solution**:
1. Check database indexes are created
2. Verify query execution plan with `EXPLAIN ANALYZE`
3. Ensure client-side search is used for < 100 tasks

### Modal Width Issues

**Issue**: Modal too narrow or wide on mobile

**Solution**:
1. Add custom className: `<DialogContent className="sm:max-w-2xl">`
2. Check Tailwind classes are not overridden
3. Verify `twMerge` in `cn()` function

---

## Performance Testing

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks

# Expected: < 100ms median response time
```

### Database Query Performance

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = '...'
  AND priority = 'high'
  AND completed = false;

-- Expected: < 50ms execution time
```

---

## Deployment Checklist

- [ ] Database migration run on production database
- [ ] Environment variables configured (DATABASE_URL, JWT_SECRET, OPENAI_API_KEY)
- [ ] New indexes created for performance
- [ ] Frontend environment variables updated
- [ ] API endpoints tested with production JWT
- [ ] Natural language extraction tested with OpenAI API
- [ ] UI components tested on mobile devices
- [ ] Performance targets met (< 200ms client search, < 500ms server search)

---

## Rollback Plan

If issues occur after deployment:

```sql
-- Rollback database changes
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
ALTER TABLE tasks DROP COLUMN IF EXISTS tags;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_priority;
DROP INDEX IF EXISTS idx_tasks_completed;
DROP INDEX IF EXISTS idx_tasks_user_priority_status;
DROP INDEX IF EXISTS idx_tasks_tags;
```

```bash
# Revert frontend changes
git revert <commit-hash>

# Revert backend changes
git revert <commit-hash>
```

---

## Next Steps

After completing this feature:
1. Run all tests to verify functionality
2. Measure performance against success criteria
3. Update documentation with any changes
4. Create pull request for code review
5. Deploy to staging for final testing
