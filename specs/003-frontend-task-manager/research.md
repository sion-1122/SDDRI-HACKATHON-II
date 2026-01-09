# Research: Frontend Technology Decisions

**Feature**: 003-frontend-task-manager
**Date**: 2026-01-09
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures technology research and decisions for implementing the authenticated frontend task management feature. All decisions align with the existing technology stack (Next.js 16, React 19, Better Auth, Tailwind CSS 4) and constitution requirements.

---

## 1. JWT Token Management Strategy

### Decision: Use Better Auth Session Management (Cookie-Based)

**Rationale**:
- Better Auth already handles session management using secure HttpOnly cookies
- This is more secure than localStorage (vulnerable to XSS attacks)
- Cookies are managed automatically by Better Auth - no manual token handling needed
- Session persistence across browser restarts is handled by Better Auth's cookie configuration
- Better Auth provides helper functions to check session status on both server and client

**Alternatives Considered**:

1. **LocalStorage** - Rejected because:
   - Vulnerable to XSS attacks (any JavaScript can access localStorage)
   - Requires manual token management (storage, retrieval, expiration)
   - Not secure for authentication tokens

2. **SessionStorage** - Rejected because:
   - Cleared when browser closes (poor UX for persistent login)
   - Still vulnerable to XSS attacks
   - No persistence across sessions

3. **HttpOnly Cookies (manual)** - Rejected because:
   - Requires custom implementation
   - Better Auth already provides this out of the box
   - Unnecessary complexity

**Implementation**:
- Use `authClient.$Infer.Session` from Better Auth for type-safe session access
- Use `authClient.getSession()` on server components to check authentication
- Use `useSession()` hook in client components for reactive session state
- Better Auth automatically handles JWT token storage in secure HttpOnly cookies

---

## 2. API Client Architecture

### Decision: Custom Fetch Wrapper with Better Auth Integration

**Rationale**:
- Native fetch API is sufficient for our needs (no heavy dependencies)
- Custom wrapper allows centralized JWT injection via Better Auth
- Consistent error handling across all API calls
- Type-safe with TypeScript generics
- Lightweight - adds minimal bundle size

**Alternatives Considered**:

1. **Axios** - Rejected because:
   - Adds 15KB+ to bundle size
   - Native fetch API provides same functionality
   - Unnecessary dependency for simple REST API

2. **Direct fetch calls** - Rejected because:
   - Code duplication (repeated headers, error handling)
   - Inconsistent error handling across components
   - Manual JWT injection in every call

**Implementation**:
- Create `lib/api-client.ts` with custom fetch wrapper
- Automatically inject `Authorization: Bearer <token>` header using Better Auth
- Centralized error handling (401 → redirect to login, 5xx → show error)
- Type-safe methods: `get<T>()`, `post<T>()`, `put<T>()`, `patch<T>()`, `delete<T>()`
- Support for request cancellation via AbortController
- Retry logic for network failures (max 3 retries with exponential backoff)

---

## 3. Form Validation Strategy

### Decision: Controlled Components with React State + Zod Validation

**Rationale**:
- Simple forms (login, register, task) don't need heavy form libraries
- Controlled components provide full control and predictability
- Zod provides runtime validation with TypeScript inference
- Lightweight - only adds Zod dependency (~10KB)
- Easy to integrate with Better Auth form helpers

**Alternatives Considered**:

1. **React Hook Form** - Rejected because:
   - Adds 25KB+ to bundle size
   - Overkill for simple forms (3-4 fields max)
   - Unreflected rewrites make controlled components equally performant
   - Steeper learning curve for simple use cases

2. **Formik** - Rejected because:
   - Heavier than React Hook Form (~40KB)
   - Older API patterns (less modern than React Hook Form)
   - Unnecessary complexity for our simple forms

3. **No validation library** - Rejected because:
   - Manual validation is error-prone
   - No TypeScript type inference
   - Duplicated validation logic

**Implementation**:
- Use controlled components (useState for form state)
- Use Zod schemas for validation rules
- Validate on submit and on blur (real-time feedback)
- Display field-specific error messages
- Use Better Auth's form utilities for authentication forms

---

## 4. State Management Approach

### Decision: React Server Components + URL Params for Filters

**Rationale**:
- Next.js 16 App Router optimizes for React Server Components (RSC)
- Task list data fetched in server component (initial load)
- Filter state in URL params (shareable, bookmarkable URLs)
- Client state minimized to UI-only state (modals, loading states)
- No need for global state management (Zustand, Redux) for this scope

**Alternatives Considered**:

1. **Zustand** - Rejected because:
   - Global state not needed for single-page app
   - URL params provide better UX (shareable filters)
   - Unnecessary dependency

2. **Jotai** - Rejected because:
   - Overkill for simple component state
   - React built-in useState is sufficient
   - Adds conceptual overhead

3. **Redux Toolkit** - Rejected because:
   - Massive overkill for simple task app
   - Heavy boilerplate and bundle size
   - Unnecessary for single-user task management

**Implementation**:
- Server components for data fetching (tasks page)
- URL search params for filters (`?status=active&search=query`)
- useState for UI state (modals, loading, form inputs)
- Better Auth session state managed by library
- No global state management library

---

## 5. Error Handling Pattern

### Decision: Toast Notifications with Sonner

**Rationale**:
- Toast notifications are best practice for non-blocking errors
- Sonner is lightweight (~3KB), modern, and accessible
- Built-in support for promise states (loading, success, error)
- Easy integration with Better Auth error handling
- Consistent UX for all error types (network, auth, validation)

**Alternatives Considered**:

1. **React Hot Toast** - Rejected because:
   - Less actively maintained than Sonner
   - Sonner provides better TypeScript support
   - Sonner has better accessibility features

2. **React Toastify** - Rejected because:
   - Heavier (~12KB)
   - Older API patterns
   - Less modern design

3. **Alert() calls** - Rejected because:
   - Poor UX (blocking, not dismissible)
   - Not customizable
   - Unprofessional appearance

**Implementation**:
- Install `sonner` for toast notifications
- Use `<Toaster />` component in root layout
- Show toast for: network errors, auth failures, validation errors, success messages
- Automatic dismissal after 5 seconds
- Manual dismissal on click
- Error toasts: red color, error icon
- Success toasts: green color, checkmark icon

---

## 6. Loading States Strategy

### Decision: Per-Component Loading Indicators

**Rationale**:
- Provides clear feedback for specific operations
- Better UX than global loading overlay (users see what's loading)
- Optimistic UI updates where possible (toggle completion)
- Skeleton screens for initial load (better perceived performance)

**Alternatives Considered**:

1. **Global loading overlay** - Rejected because:
   - Blocks entire UI (poor UX)
   - Doesn't show what's loading
   - Feels slower than per-component indicators

2. **No loading indicators** - Rejected because:
   - Users don't know if action is working
   - Perceived slow performance
   - Confusing UX (did click register?)

**Implementation**:
- Loading spinner (small, inline) during API calls
- Skeleton screens for initial task list load
- Optimistic updates for toggle completion (instant feedback)
- Disabled button state during form submission
- Loading state for pagination

---

## 7. Pagination Implementation

### Decision: Server-Side Pagination with URL Params

**Rationale**:
- Backend API already supports offset/limit parameters
- Reduces initial payload (faster page loads)
- Better performance for large task lists (100+ tasks)
- Shareable URLs (page 2 linkable via URL)
- Scales better than client-side pagination

**Alternatives Considered**:

1. **Client-side pagination** - Rejected because:
   - Fetches all tasks upfront (slow for large lists)
   - Doesn't scale (1000+ tasks)
   - Wasted bandwidth (user only sees first page)

2. **Infinite scroll** - Rejected because:
   - Poor UX (can't jump to specific page)
   - URL loses context (refresh goes back to top)
   - Harder to implement correctly

**Implementation**:
- Use API's offset/limit parameters
- Page number in URL (`/tasks?page=2`)
- Previous/Next buttons
- Page indicator ("Page 2 of 5")
- Jump to page functionality
- Preserve filters when changing pages

---

## 8. Responsive Design Breakpoints

### Decision: Tailwind CSS Default Breakpoints

**Rationale**:
- Tailwind defaults match industry standards
- Mobile-first approach (default styles for mobile, `md:` for tablet, `lg:` for desktop)
- Sufficient for our simple layout
- No custom breakpoints needed

**Alternatives Considered**:

1. **Custom breakpoints** - Rejected because:
   - Tailwind defaults cover 95% of use cases
   - Custom breakpoints add complexity
   - Unnecessary for simple task app

**Implementation**:
- Mobile (default): < 768px - stacked layout, single column
- Tablet (md): 768px - 1024px - two columns for task list
- Desktop (lg): > 1024px - three columns, max-width container

**Responsive Patterns**:
- Task list: 1 column mobile, 2 columns tablet, 3 columns desktop
- Forms: Full width mobile, centered container with max-width desktop
- Filters: Stacked mobile, inline desktop
- Pagination: Stacked mobile, inline desktop

---

## Summary of Key Decisions

| Decision | Technology | Rationale |
|----------|-----------|-----------|
| JWT Token Management | Better Auth (cookies) | Secure, automatic, built-in |
| API Client | Custom fetch wrapper | Lightweight, type-safe, centralized |
| Form Validation | Controlled + Zod | Simple, type-safe, lightweight |
| State Management | RSC + URL params | No global state, shareable URLs |
| Error Notifications | Sonner toasts | Modern, accessible, lightweight |
| Loading States | Per-component indicators | Clear feedback, optimistic updates |
| Pagination | Server-side with URL params | Scalable, shareable, API-supported |
| Responsive Design | Tailwind defaults | Mobile-first, industry standard |

---

## Next Steps

Proceed to Phase 1: Design & Contracts to create:
1. `data-model.md` - TypeScript interfaces and validation schemas
2. `contracts/api-client.ts` - API client implementation
3. `quickstart.md` - Developer setup guide
