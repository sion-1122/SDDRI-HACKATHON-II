# Research: Authentication Technology Decisions

**Feature**: 001-user-auth  
**Date**: 2026-01-09  
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures technology research and decisions for implementing the authentication system with clear separation: FastAPI backend handles ALL authentication logic, Next.js frontend is purely a UI client.

---

## 1. Password Hashing Algorithm

### Decision: bcrypt

**Rationale**:
- Proven, battle-tested algorithm with long history of security
- Automatic salt generation (no manual salt management)
- Configurable cost factor (we'll use 12 for good balance of security vs performance)
- Widely supported in Python via `passlib` library
- Recommended by OWASP for password hashing
- Resistant to rainbow table and brute force attacks

**Alternatives Considered**:

1. **argon2** - More modern and memory-hard, making it GPU/ASIC resistant
   - Rejected because: Less mature Python ecosystem, more complex setup, bcrypt is sufficient for our use case

2. **scrypt** - Memory-hard algorithm similar to argon2
   - Rejected because: Less widely used, bcrypt provides adequate security for web application

3. **PBKDF2** - NIST-standard key derivation function
   - Rejected because: Less resistant to GPU attacks than bcrypt, older algorithm

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(password)
verified = pwd_context.verify(plain_password, hashed_password)
```

---

## 2. JWT Library Selection

### Decision: python-jose

**Rationale**:
- Active maintenance and good community support
- Comprehensive JWT functionality (sign, verify, encode, decode)
- Supports multiple algorithms (HS256, RS256, etc.)
- Good type hints and Python 3.13+ compatibility
- Lightweight dependency footprint
- Clear API design

**Alternatives Considered**:

1. **PyJWT** - Very popular, simple API
   - Rejected because: Less actively maintained, fewer features, python-jose provides better developer experience

2. **PyJWT Extras** - Extension to PyJWT
   - Rejected because: Still based on PyJWT, python-jose is more comprehensive out of the box

3. **authlib** - Comprehensive auth library
   - Rejected because: Overkill for our needs (we only need JWT), heavier dependency

**Implementation**:
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HS256)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HS256])
        return payload
    except JWTError:
        return None
```

---

## 3. Frontend Token Storage

### Decision: httpOnly Cookies with Server-Side Setting

**Rationale**:
- **Most secure option**: httpOnly cookies cannot be accessed by JavaScript (XSS protection)
- **Backend sets cookie**: FastAPI backend sets cookie via Set-Cookie header
- **Automatic sending**: Browser automatically includes cookie with requests (no manual Authorization header management)
- **CSRF protection**: Add SameSite=Strict or SameSite=Lax for CSRF protection
- **Persistent**: Cookies persist across browser sessions if configured with max-age

**Alternatives Considered**:

1. **localStorage** - Client-side storage accessible via JavaScript
   - Rejected because: Vulnerable to XSS attacks (any JS can read localStorage), less secure

2. **sessionStorage** - Similar to localStorage but cleared on tab close
   - Rejected because: Still XSS-vulnerable, session persistence is poor UX

3. **Memory storage** - Store token in React state or variable
   - Rejected because: Lost on page refresh, terrible UX

**Implementation** (Backend - FastAPI):
```python
from fastapi import Response
from fastapi.responses import JSONResponse

response = JSONResponse({"token": token, "user": user_data})
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,  # HTTPS only in production
    samesite="lax",
    max_age=7 * 24 * 60 * 60  # 7 days
)
return response
```

**Frontend**: No special handling needed - browser automatically includes cookies

---

## 4. API Client Architecture

### Decision: Custom Fetch Wrapper with Automatic Cookie Handling

**Rationale**:
- Native fetch API (no additional dependencies)
- Custom wrapper provides consistent error handling
- Automatic cookie inclusion (browser handles httpOnly cookies)
- Type-safe with TypeScript generics
- Lightweight - minimal bundle size increase
- Centralized JWT error handling (401 redirects)

**Alternatives Considered**:

1. **axios** - Popular HTTP client with interceptors
   - Rejected because: Adds 15KB+ to bundle, fetch API is sufficient for our needs

2. **ky** - Modern fetch wrapper
   - Rejected because: Additional dependency, custom wrapper gives us more control

3. **React Query** - Data fetching library
   - Rejected because: Overkill for simple auth API calls, can add later if needed for data fetching

**Implementation** (Frontend):
```typescript
// lib/api-client.ts
export class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async post<T>(url: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',  // Include cookies automatically
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
      }
      throw new ApiError(response.status, await response.text());
    }

    return response.json();
  }
}
```

---

## 5. Form Validation Approach

### Decision: Controlled Components with React State + Client-Side Validation

**Rationale**:
- Simple and straightforward for basic auth forms (3-4 fields max)
- No additional library dependencies
- Full control over validation timing and error display
- React Server Components and Suspense make controlled components performant
- Easy to integrate with backend validation errors

**Alternatives Considered**:

1. **react-hook-form** - Popular form library
   - Rejected because: Overkill for simple auth forms, adds 25KB+, controlled components are sufficient

2. **Formik** - Older form library
   - Rejected because: Heavier than react-hook-form, older API patterns

3. **No validation (backend only)** - Rely solely on backend validation
   - Rejected because: Poor UX (round-trip for every error), slower feedback

**Implementation**:
```typescript
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
const [errors, setErrors] = useState({ email: '', password: '' });

const validate = () => {
  const newErrors = { email: '', password: '' };
  let isValid = true;

  if (!email.includes('@')) {
    newErrors.email = 'Invalid email format';
    isValid = false;
  }
  if (password.length < 8) {
    newErrors.password = 'Password must be at least 8 characters';
    isValid = false;
  }

  setErrors(newErrors);
  return isValid;
};
```

---

## 6. Database Migration Strategy

### Decision: SQLModel Automatic Migrations with Manual Initial Creation

**Rationale**:
- SQLModel provides simple create_engine() and table creation
- For initial development, automatic table creation is sufficient
- Production migrations can use Alembic when needed (more complex schema changes)
- Simplicity for initial implementation
- SQLModel is built on Pydantic, so models are type-safe

**Alternatives Considered**:

1. **Alembic** - Full-featured database migration tool
   - Rejected because: Overkill for initial simple User table, adds complexity. Can add later for production.

2. **Manual SQL** - Write raw SQL CREATE TABLE statements
   - Rejected because: Loses type safety, SQLModel provides better developer experience

**Implementation** (Initial):
```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)
```

**Future**: Add Alembic for production schema migrations

---

## 7. CORS Configuration

### Decision: FastAPI CORSMiddleware with Strict Origin Whitelist

**Rationale**:
- Security: Only allow requests from known frontend origins
- Development: http://localhost:3000 (Next.js dev server)
- Production: https://yourdomain.com (actual frontend domain)
- Support credentials (cookies, authorization headers)
- Prevents CSRF attacks from unauthorized origins

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourdomain.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Considerations**:
- Never use `allow_origins=["*"]` with credentials
- Always specify exact origins in production
- Use environment variables for production origins

---

## 8. Error Handling Pattern

### Decision: Standardized JSON Error Responses with Global Exception Handler

**Rationale**:
- Consistency: All errors follow same format
- Security: Don't leak sensitive information (e.g., "user not found" vs "invalid credentials")
- UX: Clear, actionable error messages
- Development: Centralized error logging and monitoring

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

**Implementation**:
```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Generic error message for 401 (no information leakage)
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

**Error Messages**:
- 400: "Invalid input data"
- 401: "Invalid credentials" (generic, doesn't reveal if email exists)
- 409: "Email already registered"
- 500: "Internal server error" (logged server-side, generic message to user)

---

## Summary of Key Decisions

| Decision | Technology | Rationale |
|----------|-----------|-----------|
| Password Hashing | bcrypt | Proven security, wide support |
| JWT Library | python-jose | Active maintenance, comprehensive features |
| Token Storage | httpOnly cookies | Most secure (XSS protection) |
| API Client | Custom fetch wrapper | Lightweight, full control |
| Form Validation | Controlled components | Simple, sufficient for auth forms |
| Migrations | SQLModel automatic | Simplicity for initial dev |
| CORS | Strict origin whitelist | Security, prevent CSRF |
| Error Handling | Global exception handler | Consistency, security |

---

## Next Steps

Proceed to Phase 1: Design & Contracts to create:
1. `data-model.md` - Complete data structures and validation rules
2. `contracts/openapi.yaml` - Full API specification
3. `quickstart.md` - Developer setup guide
