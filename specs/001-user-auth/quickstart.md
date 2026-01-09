# Quickstart Guide: User Authentication

**Feature**: 001-user-auth  
**Date**: 2026-01-09  
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide helps you set up and run the authentication system with FastAPI backend (handles all auth logic) and Next.js frontend (pure UI client).

---

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.13+** installed for backend
   ```bash
   python --version  # Should be 3.13+
   ```

2. **Node.js 18+** and **pnpm** for frontend
   ```bash
   node --version  # Should be v18+
   npm install -g pnpm
   ```

3. **PostgreSQL database** - Neon Serverless PostgreSQL account
   - Sign up at https://neon.tech
   - Create a new database
   - Copy the connection string

4. **uv** - Python package manager (if not using pip)
   ```bash
   pip install uv
   ```

---

## Backend Setup (FastAPI)

### 1. Install Dependencies

```bash
cd backend
uv sync
```

**Dependencies installed**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlmodel` - ORM and models
- `python-jose` - JWT generation/verification
- `passlib` - Password hashing
- `bcrypt` - Password hashing algorithm
- `python-multipart` - Form data parsing
- `pydantic` - Data validation
- `psycopg2-binary` - PostgreSQL driver

---

### 2. Environment Variables

Create `.env` file in the `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# JWT Secret (generate a secure random string)
JWT_SECRET=your-super-secret-jwt-key-here-change-this

# CORS Frontend URL (development)
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Generate JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 3. Initialize Database

```bash
cd backend
uv run python -c "from sqlmodel import SQLModel, create_engine; from models.user import User; engine = create_engine(os.getenv('DATABASE_URL')); SQLModel.metadata.create_all(engine)"
```

Or use the init script (if provided):
```bash
uv run python scripts/init_db.py
```

---

### 4. Run Backend Server

```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend API available at**: http://localhost:8000

---

## Frontend Setup (Next.js)

### 1. Install Dependencies

```bash
cd frontend
pnpm install
```

**Dependencies installed**:
- `next` - React framework
- `react` - UI library
- `react-dom` - React DOM renderer
- `typescript` - Type safety
- `tailwindcss` - Styling

---

### 2. Environment Variables

Create `.env.local` file in the `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 3. Run Frontend Server

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

**Frontend available at**: http://localhost:3000

---

## Testing the Authentication Flow

### Test 1: User Registration

1. Open http://localhost:3000/register
2. Fill in the registration form:
   - **Email**: `test@example.com`
   - **Password**: `password123` (minimum 8 characters)
3. Click "Sign Up"

**Expected result**:
- Success message displayed
- Redirected to login page
- User created in database

**Verify with cURL**:
```bash
curl -X POST http://localhost:8000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Expected response**:
```json
{
  "success": true,
  "message": "Account created successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-01-09T12:00:00Z",
    "updated_at": "2026-01-09T12:00:00Z"
  }
}
```

---

### Test 2: User Login

1. Open http://localhost:3000/login
2. Fill in the login form:
   - **Email**: `test@example.com`
   - **Password**: `password123`
3. Click "Sign In"

**Expected result**:
- Authentication successful
- JWT token stored in httpOnly cookie
- Redirected to dashboard
- User email displayed

**Verify with cURL**:
```bash
curl -X POST http://localhost:8000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Expected response**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-01-09T12:00:00Z",
    "updated_at": "2026-01-09T12:00:00Z"
  },
  "expires_at": "2026-01-16T12:00:00Z"
}
```

---

### Test 3: Session Verification

1. After logging in, navigate to http://localhost:3000/dashboard
2. The page should load successfully (not redirect to login)

**Verify with cURL**:
```bash
curl -X GET http://localhost:8000/api/auth/session \
  -b cookies.txt
```

**Expected response**:
```json
{
  "authenticated": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-01-09T12:00:00Z",
    "updated_at": "2026-01-09T12:00:00Z"
  },
  "expires_at": "2026-01-16T12:00:00Z"
}
```

---

### Test 4: Logout

1. Click the "Logout" button
2. Should be redirected to login page
3. Try to access http://localhost:3000/dashboard
4. Should redirect back to login page

**Verify with cURL**:
```bash
curl -X POST http://localhost:8000/api/auth/sign-out \
  -b cookies.txt
```

**Expected response**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### Test 5: Protected API Request (with Task API)

1. Login and get JWT token
2. Try to access tasks endpoint:

```bash
curl -X GET http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer <your_token>"
```

**Expected response**:
```json
[]
```

(Empty array because no tasks yet)

**Test without token**:
```bash
curl -X GET http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks
```

**Expected response**:
```json
{
  "detail": "Not authenticated"
}
```

---

## Troubleshooting

### Common Issues

**Issue**: "Database connection failed"

**Solution**:
1. Check `DATABASE_URL` in backend `.env`
2. Verify Neon PostgreSQL database is running
3. Test connection: `psql $DATABASE_URL`

---

**Issue**: "Invalid JWT token"

**Solution**:
1. Verify `JWT_SECRET` matches between requests
2. Check token hasn't expired (7 day expiry)
3. Ensure token is sent in `Authorization: Bearer <token>` header

---

**Issue**: "CORS error in browser"

**Solution**:
1. Check `FRONTEND_URL` in backend `.env`
2. Verify CORSMiddleware is configured in FastAPI
3. Ensure frontend origin is in `allow_origins`

---

**Issue**: "Email already registered"

**Solution**:
1. Use a different email address
2. Or check database directly: `SELECT * FROM users WHERE email = 'test@example.com'`

---

**Issue**: "Password verification fails"

**Solution**:
1. Ensure password is at least 8 characters
2. Check password hashing is working (check `hashed_password` in database)
3. Verify bcrypt cost factor is 12

---

### Development Tips

**Reset Database**:
```bash
# Connect to database
psql $DATABASE_URL

# Drop all tables
DROP TABLE IF EXISTS users CASCADE;

# Exit
\q

# Re-create tables
cd backend
uv run python scripts/init_db.py
```

**View Users in Database**:
```bash
psql $DATABASE_URL -c "SELECT id, email, created_at FROM users;"
```

**Check JWT Token Contents**:
```bash
# Decode JWT token (without verification)
echo "<your_token>" | jq -R 'split(".") | .[1]' | base64 -d | jq
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.

# Run specific test file
uv run pytest tests/test_auth_api.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run E2E tests
pnpm test:e2e
```

---

## Production Deployment

### Backend Deployment

1. **Set environment variables** (production values):
   ```bash
   DATABASE_URL=<production-database-url>
   JWT_SECRET=<production-secret-key>
   FRONTEND_URL=https://yourdomain.com
   ENVIRONMENT=production
   ```

2. **Run with production server**:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Or use Docker**:
   ```bash
   docker build -t todo-backend .
   docker run -p 8000:8000 --env-file .env todo-backend
   ```

### Frontend Deployment

1. **Build for production**:
   ```bash
   cd frontend
   pnpm build
   ```

2. **Run production server**:
   ```bash
   pnpm start
   ```

3. **Or deploy to Vercel**:
   ```bash
   vercel --prod
   ```

---

## Next Steps

After successful setup:

1. **Explore the code**: Read through backend and frontend code
2. **Add features**: Implement password reset, email verification, 2FA
3. **Write tests**: Add comprehensive unit and integration tests
4. **Configure CI/CD**: Set up automated testing and deployment
5. **Monitor**: Add logging, metrics, and error tracking

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com
- **JWT.io**: https://jwt.io (debug JWT tokens)
- **Neon PostgreSQL**: https://neon.tech/docs

---

**Last Updated**: 2026-01-09  
**Version**: 1.0.0
