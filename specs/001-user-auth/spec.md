# Feature Specification: User Authentication

**Feature Branch**: `001-user-auth`
**Created**: 2026-01-08
**Updated**: 2026-01-09
**Status**: Draft
**Input**: User description: "Implement BetterAuth on frontend and JWT verification middleware in FastAPI. Update API behavior to require authentication."

**Architecture Clarification**: Next.js is frontend-only. All authentication logic (validation, JWT generation/verification, password hashing) is handled by FastAPI backend endpoints. Next.js only renders UI and sends requests to backend.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

A new user wants to create an account so they can start managing their tasks. They provide their email address, create a password, and complete the registration process.

**Why this priority**: Registration is the entry point for all users. Without it, no one can access the application. This is the foundation for multi-user data isolation (Constitution Principle IX).

**Independent Test**: Can be fully tested by a user navigating to the registration page, filling out the form, and verifying they can log in with the new credentials. Delivers immediate value by enabling user onboarding.

**Acceptance Scenarios**:

1. **Given** a user is on the registration page, **When** they submit a valid email and password, **Then** their account is created and they are redirected to the login page
2. **Given** a user is on the registration page, **When** they submit an email that already exists, **Then** they see an error message indicating the email is already registered
3. **Given** a user is on the registration page, **When** they submit an invalid email format, **Then** they see a validation error before the form is submitted
4. **Given** a user is on the registration page, **When** they submit a password with fewer than 8 characters, **Then** they see a validation error requiring a longer password
5. **Given** a user is on the registration page, **When** they successfully register, **Then** a confirmation message is displayed

---

### User Story 2 - User Login (Priority: P1)

A returning user wants to access their account and manage their existing tasks. They provide their email and password credentials to authenticate.

**Why this priority**: Login is the second critical flow. Without authentication, users cannot access their data or any protected features. This enables JWT token generation (Constitution Principle VII).

**Independent Test**: Can be fully tested by a registered user entering credentials and verifying they receive a valid JWT token and can access protected pages. Delivers immediate value by enabling secure access.

**Acceptance Scenarios**:

1. **Given** a registered user is on the login page, **When** they submit correct email and password, **Then** they receive a JWT token and are redirected to the main application page
2. **Given** a user is on the login page, **When** they submit an incorrect password, **Then** they see an error message indicating invalid credentials
3. **Given** a user is on the login page, **When** they submit an email that does not exist, **Then** they see an error message indicating invalid credentials (without revealing whether the email exists)
4. **Given** a user is on the login page, **When** they successfully log in, **Then** the JWT token is stored and sent with subsequent API requests
5. **Given** a user is on the login page, **When** authentication fails 3 times in a row, **Then** they see a message suggesting they reset their password or try again later

---

### User Story 3 - Protected Route Access (Priority: P1)

An authenticated user attempts to access protected pages in the application. The system verifies their JWT token before allowing access.

**Why this priority**: This is the security enforcement layer. Without it, authentication tokens have no value. This implements Constitution Principle VII (all API endpoints require valid JWT).

**Independent Test**: Can be fully tested by making API requests with and without valid JWT tokens and verifying the correct response codes. Delivers immediate value by securing all application data.

**Acceptance Scenarios**:

1. **Given** a user has a valid JWT token, **When** they access a protected API endpoint, **Then** the request succeeds and returns the requested data
2. **Given** a user has an expired JWT token, **When** they access a protected API endpoint, **Then** they receive a 401 Unauthorized response
3. **Given** a user has no JWT token, **When** they access a protected API endpoint, **Then** they receive a 401 Unauthorized response
4. **Given** a user has a tampered JWT token, **When** they access a protected API endpoint, **Then** they receive a 401 Unauthorized response
5. **Given** an authenticated user accesses a public page (login/register), **When** the page loads, **Then** they are redirected to the main application page

---

### User Story 4 - User Logout (Priority: P2)

An authenticated user wants to end their session securely. They click a logout button and their JWT token is invalidated.

**Why this priority**: Logout is important for security on shared devices, but users can also close their browser. The token will expire naturally, so this is lower priority than registration/login.

**Independent Test**: Can be fully tested by a logged-in user clicking logout and verifying their token is cleared and they are redirected to the login page. Delivers value by enabling explicit session termination.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** they click the logout button, **Then** their JWT token is cleared from storage
2. **Given** a user is logged in, **When** they click the logout button, **Then** they are redirected to the login page
3. **Given** a user just logged out, **When** they try to access a protected page, **Then** they are redirected to the login page
4. **Given** a user is logged in, **When** they log out and immediately try to use their old JWT token, **Then** the API returns 401 Unauthorized

---

### Edge Cases

- What happens when a user tries to register with an email that uses different casing (e.g., Test@Example.com vs test@example.com)?
- How does the system handle a user who registers but never verifies their email (if email verification is added later)?
- What happens when a user's JWT token expires in the middle of an active session?
- How does the system handle concurrent logins from different devices with the same user account?
- What happens when a user tries to access a protected page immediately after registering, before logging in?
- How does the system handle a user who tries to log in with an account that was recently deleted?
- What happens when the authentication service (frontend or backend) is temporarily unavailable?

## Architecture Overview

**Frontend (Next.js)**:
- Renders login and registration forms
- Collects user input (email, password)
- Sends authentication requests to FastAPI backend
- Stores JWT tokens returned by backend (in cookies or localStorage)
- Includes JWT tokens in Authorization header for API requests
- Redirects users based on authentication status
- **Does NOT**: Generate JWTs, validate credentials, hash passwords, or perform any authentication logic

**Backend (FastAPI)**:
- Receives authentication requests from frontend
- Validates email format and password strength
- Checks if email already exists in database
- Hashes passwords using secure algorithm (bcrypt/argon2)
- Generates and signs JWT tokens
- Verifies JWT signatures on API requests
- Extracts user_id from validated JWTs
- Returns HTTP 401 for invalid/expired/missing tokens
- Manages user database (PostgreSQL with SQLModel)
- **Handles ALL authentication logic**

**Data Flow**:
1. User fills login form → Next.js collects email/password
2. Next.js sends POST to `/api/auth/sign-in` → FastAPI validates credentials
3. FastAPI checks database → If valid, generates and signs JWT
4. FastAPI returns JWT token → Next.js stores token
5. Next.js includes JWT in Authorization header → FastAPI verifies on each request
6. FastAPI extracts user_id → Scopes all data queries to authenticated user

## Requirements *(mandatory)*

### Functional Requirements

**Frontend (Next.js) Requirements**:

- **FR-001**: Frontend MUST render registration form that accepts email and password
- **FR-002**: Frontend MUST render login form that accepts email and password
- **FR-003**: Frontend MUST send registration data to FastAPI backend endpoint `/api/auth/sign-up`
- **FR-004**: Frontend MUST send login credentials to FastAPI backend endpoint `/api/auth/sign-in`
- **FR-005**: Frontend MUST store JWT token returned by backend (in cookies or localStorage)
- **FR-006**: Frontend MUST include JWT token in Authorization header (`Bearer <token>`) for all API requests
- **FR-007**: Frontend MUST clear JWT token on logout
- **FR-008**: Frontend MUST redirect unauthenticated users to login page when accessing protected routes
- **FR-009**: Frontend MUST redirect authenticated users away from login/register pages
- **FR-010**: Frontend MUST display error messages returned by backend authentication API

**Backend (FastAPI) Requirements**:

- **FR-011**: Backend MUST provide `/api/auth/sign-up` endpoint that accepts email and password
- **FR-012**: Backend MUST provide `/api/auth/sign-in` endpoint that accepts email and password
- **FR-013**: Backend MUST validate email format (must contain @ symbol and valid domain structure)
- **FR-014**: Backend MUST enforce minimum password length of 8 characters
- **FR-015**: Backend MUST check if email already exists in database (case-insensitive) before registration
- **FR-016**: Backend MUST hash passwords using secure irreversible algorithm (bcrypt or argon2) before storage
- **FR-017**: Backend MUST store user accounts in PostgreSQL database with unique email constraint
- **FR-018**: Backend MUST generate and sign JWT token upon successful login
- **FR-019**: Backend MUST verify JWT signature on every API request (except auth endpoints)
- **FR-020**: Backend MUST extract user_id from validated JWT token
- **FR-021**: Backend MUST return HTTP 401 Unauthorized for requests with invalid, expired, or missing JWT tokens
- **FR-022**: Backend MUST provide `/api/auth/sign-out` endpoint to invalidate sessions
- **FR-023**: Backend MUST provide `/api/auth/session` endpoint to verify current session
- **FR-024**: Backend MUST return clear error messages for authentication failures without revealing whether email exists

### Key Entities

- **User Account**: Represents a registered user with email, hashed password, unique ID, creation timestamp, and last login timestamp. This entity is the foundation for data ownership and isolation. **Stored and managed by FastAPI backend.**
- **Authentication Token (JWT)**: Represents a signed token issued by the **FastAPI backend** containing user ID, issuance timestamp, and expiration timestamp. This token is sent with API requests to prove identity. **JWT generation and signing happens on FastAPI backend only.**
- **Session**: Represents the period between login and logout for a specific user on a specific device. Sessions are tracked via JWT tokens stored by the **frontend client** (in cookies or localStorage), but **validated and verified by FastAPI backend** on every request.
- **Credentials**: Represents the email and password combination used for authentication. Passwords are never stored in plaintext.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete registration in under 60 seconds from landing on registration page to successful account creation
- **SC-002**: Users can complete login in under 15 seconds from entering credentials to accessing the main application
- **SC-003**: 100% of API endpoints without a valid JWT return HTTP 401 Unauthorized (verified by automated tests)
- **SC-004**: 100% of API requests with a valid JWT succeed and return data scoped to the authenticated user (verified by integration tests)
- **SC-005**: 95% of users successfully complete registration on their first attempt (measured by production analytics after launch)
- **SC-006**: JWT verification adds less than 50ms average latency to API requests (measured by performance monitoring)
- **SC-007**: System handles 100 concurrent authentication requests without errors or degradation (verified by load testing)
- **SC-008**: 0% of password data is stored in plaintext or reversible format (verified by security audit)
- **SC-009**: Users report an average satisfaction score of 4.5/5 for the login/registration experience (measured by user survey after launch)
- **SC-010**: Authentication system prevents all cross-user data access attempts (verified by security penetration testing)

## Assumptions

1. **Email as primary identifier**: We assume users will provide valid email addresses that they own. Email verification is not included in this feature but may be added later.
2. **Password complexity**: We assume a minimum 8-character password is sufficient for this phase. Additional complexity requirements (special characters, numbers, etc.) are not enforced.
3. **Token expiration**: We assume a standard JWT expiration time (e.g., 7 days) is appropriate. Token refresh mechanisms are not included in this feature.
4. **Single session type**: We assume a standard JWT-based session is sufficient. Advanced session management (concurrent session limits, device management) is not included.
5. **Frontend token storage**: We assume the **Next.js frontend** will store JWT tokens returned by FastAPI backend in httpOnly cookies or secure localStorage. This feature does not specify the exact storage mechanism.
6. **No social login**: We assume email/password authentication is sufficient. OAuth or social login providers are not included in this feature.
7. **No account recovery**: We assume users can always reset their password if needed. Password reset functionality is not included in this feature.
8. **User database**: We assume a **FastAPI backend with relational database** (Neon PostgreSQL) table exists for storing user accounts. The exact schema is defined during implementation planning.
9. **JWT signing secret**: We assume the **FastAPI backend** manages the JWT secret and signing process. The frontend does not participate in JWT generation or signing.
10. **No rate limiting**: We assume basic authentication without rate limiting is sufficient for initial launch. Rate limiting may be added in a future feature for security.
11. **No two-factor authentication**: We assume password-only authentication is sufficient for this phase. 2FA may be added in a future feature.
12. **Basic error handling**: We assume standard error messages (invalid credentials, email already exists) are sufficient. Detailed error codes or localization are not included.
