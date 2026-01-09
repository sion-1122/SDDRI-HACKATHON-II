# Quickstart Guide: Frontend Task Management

**Feature**: 003-frontend-task-manager
**Date**: 2026-01-09
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide helps you set up and run the authenticated frontend task management application. It covers prerequisites, installation, configuration, and testing.

---

## Prerequisites

Before you begin, ensure you have:

1. **Node.js**: Version 18+ installed
   ```bash
   node --version  # Should be v18+
   ```

2. **pnpm**: Package manager (already used in this project)
   ```bash
   npm install -g pnpm
   ```

3. **Backend API**: FastAPI backend running on port 8000
   - Follow backend setup from feature 001-backend-task-api
   - Ensure authentication endpoints are available

4. **Database**: Neon PostgreSQL database running
   - Should be configured in backend

---

## Installation

### 1. Install Dependencies

```bash
cd frontend
pnpm install
```

**Expected output**: Dependencies install successfully without errors.

**Dependencies installed**:
- `next@16.1.1` - React framework
- `react@19.2.3` - UI library
- `better-auth@1.4.10` - Authentication
- `tailwindcss@4` - Styling
- `typescript@5` - Type safety

---

## Configuration

### 2. Environment Variables

Create `.env.local` in the `frontend/` directory:

```bash
# frontend/.env.local

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (must match backend)
BETTER_AUTH_SECRET=your-secret-key-here

# App URL (for callbacks)
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Important**: The `BETTER_AUTH_SECRET` must match the backend's secret for JWT verification.

---

## Running the Application

### 3. Start Development Server

```bash
cd frontend
pnpm dev
```

**Expected output**:
```
  ▲ Next.js 16.1.1
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.5:3000

 ✓ Ready in 2.3s
```

**Application will be available at**: http://localhost:3000

---

## Testing the Application

### 4. Test Registration Flow

1. Open http://localhost:3000/register
2. Fill in the registration form:
   - **Email**: `test@example.com`
   - **Password**: `password123` (minimum 8 characters)
3. Click "Sign Up"

**Expected result**:
- Account created successfully
- Automatically logged in
- Redirected to `/tasks` page

---

### 5. Test Login Flow

1. Click "Logout" (if logged in)
2. Open http://localhost:3000/login
3. Fill in the login form:
   - **Email**: `test@example.com` (or your registered email)
   - **Password**: `password123`
4. Click "Sign In"

**Expected result**:
- Authentication successful
- Redirected to `/tasks` page
- See your tasks (empty list initially)

---

### 6. Test Task Creation

1. On the `/tasks` page, click "Create Task" button
2. Fill in the task form:
   - **Title**: `Buy groceries` (required)
   - **Description**: `Milk, eggs, bread` (optional)
3. Click "Create"

**Expected result**:
- Task created successfully
- Appears in the task list
- Success toast notification shown

---

### 7. Test Task Operations

**Mark task as complete**:
- Click the checkbox next to the task
- Task should show strikethrough
- Completion status toggled

**Edit task**:
- Click the "Edit" button on the task
- Modify title or description
- Click "Save"
- Task updated in list

**Delete task**:
- Click the "Delete" button on the task
- Confirm deletion in modal
- Task removed from list

---

### 8. Test Filters and Search

**Filter by status**:
- Click "Active" filter
- Only incomplete tasks shown
- Click "Completed" filter
- Only completed tasks shown

**Search tasks**:
- Type in search box
- Tasks matching title/description shown
- Clear search to see all tasks

---

### 9. Test Pagination

Create 60+ tasks to test pagination:
1. Create tasks until you have more than 50
2. Scroll to bottom of task list
3. Click "Next" page button
4. See next 50 tasks

**Expected result**:
- Pagination controls visible
- Navigate between pages
- Page indicator updates

---

## Troubleshooting

### Common Issues

**Issue**: "Cannot connect to backend API"

**Solution**:
1. Ensure backend is running: `cd backend && uv run uvicorn backend.app:app --reload`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify backend is accessible: `curl http://localhost:8000/health`

---

**Issue**: "Authentication failed"

**Solution**:
1. Check `BETTER_AUTH_SECRET` matches backend
2. Clear browser cookies and localStorage
3. Try registering a new account

---

**Issue**: "Tasks not loading"

**Solution**:
1. Open browser DevTools (F12)
2. Check Network tab for API calls
3. Look for errors in Console tab
4. Verify JWT token is sent in Authorization header

---

**Issue**: "Page not found (404)"

**Solution**:
1. Ensure you're on correct URL (`/tasks`, not `/task`)
2. Check Next.js is running: `pnpm dev`
3. Clear browser cache and reload

---

## Development Workflow

### Running Tests

```bash
cd frontend

# Unit tests (when implemented)
pnpm test

# E2E tests (when implemented)
pnpm test:e2e
```

### Building for Production

```bash
cd frontend

# Create production build
pnpm build

# Run production build
pnpm start
```

### Linting

```bash
cd frontend

# Run ESLint
pnpm lint

# Fix linting errors
pnpm lint --fix
```

---

## File Structure Reference

```
frontend/
├── src/
│   ├── app/
│   │   ├── login/page.tsx          # Login page
│   │   ├── register/page.tsx       # Registration page
│   │   └── tasks/page.tsx          # Task management (NEW)
│   ├── components/
│   │   ├── tasks/                  # Task components (NEW)
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── ...
│   │   └── ui/                     # Reusable UI components
│   ├── lib/
│   │   ├── auth.ts                 # Better Auth client
│   │   ├── api-client.ts           # HTTP client (NEW)
│   │   └── task-api.ts             # Task API calls (NEW)
│   └── types/
│       └── task.ts                 # TypeScript types (NEW)
├── .env.local                      # Environment variables
├── package.json
└── tsconfig.json
```

---

## Next Steps

After successful setup:

1. **Explore the code**: Read through component files
2. **Make changes**: Try modifying task list styling
3. **Add features**: Implement task categories or tags
4. **Write tests**: Add unit tests for components
5. **Contribute**: Follow the project's contribution guidelines

---

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review error messages in browser console
3. Check backend logs for API errors
4. Open an issue on GitHub (if applicable)
5. Contact the development team

---

## Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Better Auth Documentation**: https://www.better-auth.com
- **React Documentation**: https://react.dev
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **TypeScript Documentation**: https://www.typescriptlang.org/docs

---

**Last Updated**: 2026-01-09
**Version**: 1.0.0
