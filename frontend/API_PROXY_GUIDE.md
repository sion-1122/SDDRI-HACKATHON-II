# API Proxy Guide

## Overview

All authentication endpoints (`/api/auth/*`) MUST go through the Next.js proxy route to ensure cookies are set correctly on the frontend domain.

## Proxy Routes

- **Auth Proxy**: `/api/auth/[...all]/route.ts` - Handles all `/api/auth/*` endpoints
- **ChatKit Proxy**: `/api/chatkit/route.ts` - Handles `/api/chatkit` endpoint with SSE streaming

## How to Make API Calls

### ✅ CORRECT: Use Proxy for Auth Endpoints

```typescript
// Option 1: Use authClient (recommended for auth)
import { authClient } from '@/lib/auth-client';
const session = await authClient.getSession();

// Option 2: Use apiClient (automatically routes auth through proxy)
import { apiClient } from '@/lib/api-client';
const session = await apiClient.getSession();

// Option 3: Use apiClientFn (automatically routes auth through proxy)
import { apiClientFn } from '@/lib/api/client';
const session = await apiClientFn({ url: '/api/auth/session' });

// Option 4: Direct fetch to proxy route (works but not recommended)
const response = await fetch('/api/auth/session', { credentials: 'include' });
```

### ❌ WRONG: Direct Backend Calls for Auth

```typescript
// DON'T DO THIS for auth endpoints:
const API_URL = process.env.NEXT_PUBLIC_API_URL;
const response = await fetch(`${API_URL}/api/auth/session`); // ❌ WRONG
```

## Implementation Details

### Client-Side Code

All client-side API clients automatically detect auth endpoints and route them through the proxy:

- `apiClient` (`/lib/api-client.ts`) - Checks if endpoint starts with `/api/auth`
- `apiClientFn` (`/lib/api/client.ts`) - Checks if endpoint starts with `/api/auth`
- `authClient` (`/lib/auth-client.ts`) - Always uses proxy routes

### Server-Side Code

Server-side code (`/lib/api/server.ts`) calls the backend directly but forwards cookies properly. This is acceptable for server components, but auth endpoints should ideally be checked client-side using `useSession()` hook.

## Why Proxy is Needed

1. **Cookie Domain**: Backend sets cookies on backend domain, but frontend needs them on frontend domain
2. **Cross-Origin**: In production, frontend and backend are on different domains
3. **Cookie Security**: Proxy rewrites cookies with correct `Secure`, `SameSite`, and domain settings

## Testing

To verify proxy is working:

1. Check browser DevTools → Network tab
2. Auth requests should go to `/api/auth/*` (not `https://backend.com/api/auth/*`)
3. Check Application → Cookies - cookies should be set on frontend domain
4. Cookies should have `Secure` flag in production (HTTPS)

