# Frontend Development Guidelines

## Project Overview

This directory contains the frontend application for the Todo List app, built with Next.js 16, React 19, and TypeScript.

## Technology Stack

- **Framework**: Next.js 16.1.1 (App Router)
- **UI Library**: React 19.2.3
- **Authentication**: Custom FastAPI JWT client (httpOnly cookies)
- **Styling**: Tailwind CSS 4
- **Validation**: Zod
- **Notifications**: Sonner (toast notifications)
- **Language**: TypeScript 5+ with strict mode

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── (auth)/       # Auth route group (login, register)
│   │   ├── dashboard/    # Main dashboard page
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Homepage (redirect)
│   ├── components/       # React components
│   │   ├── ui/           # Reusable UI components
│   │   ├── auth/         # Authentication components
│   │   └── tasks/        # Task management components
│   ├── lib/              # Utilities and API clients
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
├── .env.example          # Environment variables template
├── next.config.ts        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

## Development Commands

```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run TypeScript compiler
pnpm type-check

# Run linter
pnpm lint

# Format code
pnpm format
```

## Architecture Patterns

### Next.js 16 App Router

This project uses the modern **App Router** (not Pages Router):

- **Server Components**: Default for all pages (no `use client` directive)
- **Client Components**: Add `'use client'` directive for interactive components
- **Route Groups**: Use parentheses for logical grouping without affecting URL
- **Layouts**: Root layout provides common structure (Toaster, navigation)
- **Loading States**: Use `loading.tsx` for route-level loading UI

**Example: Server Component**
```tsx
// app/dashboard/page.tsx - Server component (default)
import { taskApi } from '@/lib/task-api';

export default async function DashboardPage() {
  const tasks = await taskApi.listTasks(); // Server-side data fetching
  return <TaskList tasks={tasks} />;
}
```

**Example: Client Component**
```tsx
// components/tasks/TaskForm.tsx - Client component
'use client';

import { useState } from 'react';

export function TaskForm() {
  const [isOpen, setIsOpen] = useState(false); // Hooks allowed
  // ...
}
```

### Custom JWT Authentication (Not Better Auth)

**Important**: This project does NOT use Better Auth. Instead, it uses a custom FastAPI backend with JWT tokens stored in httpOnly cookies.

**Authentication Flow**:
1. User submits login/register form
2. Frontend calls FastAPI backend (`/api/auth/sign-in` or `/api/auth/sign-up`)
3. Backend validates credentials and creates JWT token
4. Backend sets `auth_token` in httpOnly cookie (secure, httpOnly)
5. Browser automatically includes cookie in subsequent requests
6. Backend validates JWT from cookie on protected routes

**API Client** (`lib/api/client.ts`):
```typescript
export const apiClient = async ({ url, method, data }) => {
  const response = await fetch(`http://localhost:8000${url}`, {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: 'include', // Critical: includes cookies
  });
  // ...
};
```

**No Authorization Headers**: JWT is in cookie, not Authorization header

**Backend Token Extraction** (`backend/core/deps.py`):
```python
async def get_current_user_id(request: StarletteRequest = None) -> uuid.UUID:
    # Try httpOnly cookie
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        token = auth_token
    # Decode and verify JWT...
```

### React Server Components Best Practices

**Use Server Components by Default**:
- Fetch data directly in components (no need for `useEffect`)
- Keep sensitive logic on server (tokens, API keys)
- Reduce JavaScript bundle size

**Use Client Components When**:
- Using React hooks (useState, useEffect, etc.)
- Handling user interactions (onClick, onChange, etc.)
- Using browser APIs (window, document, localStorage, etc.)

**Pattern: Pass Data from Server to Client**:
```tsx
// Server Component
export default function Page() {
  const tasks = await fetchTasks(); // Server-side
  return <TaskList tasks={tasks} />; // Pass to client
}
```

### Tailwind CSS 4 Utility Classes

Tailwind CSS 4 uses a new configuration system:

**Configuration** (`tailwind.config.ts`):
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
export default config;
```

**Import in CSS** (`app/globals.css`):
```css
@import "tailwindcss";
```

**Common Utility Classes**:
- Layout: `flex`, `grid`, `container`, `space-y-4`, `gap-2`
- Sizing: `w-full`, `h-screen`, `max-w-md`, `p-4`, `m-2`
- Typography: `text-sm`, `font-semibold`, `text-gray-900`
- Colors: `bg-blue-600`, `text-green-500`, `border-gray-300`
- States: `hover:bg-blue-700`, `disabled:opacity-50`, `focus:ring-2`

**Responsive Modifiers**:
- `md:flex-row` - apply flex-row on medium screens and up
- `lg:grid-cols-3` - 3 columns on large screens
- Mobile-first approach (default styles, then override for larger screens)

### TypeScript Strict Mode Requirements

This project uses **strict mode** for type safety:

**tsconfig.json**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**Best Practices**:
- Always define return types for functions
- Use `interface` for object shapes, `type` for unions/primitives
- Use `unknown` instead of `any` for untyped data
- Validate runtime data with Zod schemas
- Use type guards for narrowing types

**Example: Type-Safe API Client**:
```typescript
import type { Task } from '@/types/task';
import { taskSchema } from '@/lib/schemas/task';

async function getTask(id: string): Promise<Task> {
  const response = await fetch(`/api/tasks/${id}`);
  const data = await response.json();
  return taskSchema.parse(data); // Runtime validation
}
```

## Component Patterns

### Reusable UI Components

All UI components in `src/components/ui/` follow these patterns:

1. **Button** (`components/ui/Button.tsx`)
   - Variants: `primary`, `secondary`, `danger`
   - Sizes: `sm`, `md`, `lg`
   - Disabled state handling

2. **Input** (`components/ui/Input.tsx`)
   - Label support
   - Error display
   - Ref forwarding
   - ARIA attributes

3. **Modal** (`components/ui/Modal.tsx`)
   - Open/close state
   - Backdrop click handling
   - Focus trap
   - ARIA attributes

### Form Validation with Zod

All forms use Zod schemas for validation:

**Schema Definition** (`lib/schemas/forms.ts`):
```typescript
import { z } from 'zod';

export const loginFormSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export type LoginFormSchema = z.infer<typeof loginFormSchema>;
```

**Form Component** (`components/auth/LoginForm.tsx`):
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginFormSchema, type LoginFormSchema } from '@/lib/schemas/forms';

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormSchema>({
    resolver: zodResolver(loginFormSchema),
  });

  const onSubmit = (data: LoginFormSchema) => {
    // data is fully typed
  };
}
```

### Error Handling

**API Errors** (`lib/api/client.ts`):
```typescript
if (!response.ok) {
  if (response.status === 401) {
    window.location.href = "/login"; // Redirect to login
  }
  throw new Error(`API Error: ${response.statusText}`);
}
```

**Toast Notifications** (`components/tasks/TaskForm.tsx`):
```typescript
import { toast } from 'sonner';

try {
  await taskApi.createTask(data);
  toast.success('Task created successfully');
} catch (error) {
  toast.error(error.message);
}
```

**Validation Errors**:
```typescript
// Zod validation errors
const fieldErrors = error.flatten().fieldErrors;
toast.error(`${fieldErrors.title?.[0] || 'Validation failed'}`);
```

## Data Fetching Patterns

### Server Components (Recommended)

```tsx
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const response = await taskApi.listTasks(); // Server-side
  return <TaskList tasks={response.tasks} />;
}
```

### Client Components (When Needed)

```tsx
'use client';

import { useEffect, useState } from 'react';

export function TaskListClient() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    taskApi.listTasks()
      .then(data => setTasks(data.tasks))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  return <TaskList tasks={tasks} />;
}
```

## State Management

This project uses **local component state** with React hooks:

- **useState**: For simple local state (modals, forms)
- **useSearchParams**: For URL-based state (filters, pagination)
- **No global state library**: Not needed for this app size

**URL-Based State** (Recommended):
```typescript
import { useSearchParams, useRouter } from 'next/navigation';

export function FilterBar() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const status = searchParams.get('status') || 'all';

  const setStatus = (newStatus: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('status', newStatus);
    router.push(`?${params.toString()}`);
  };

  return <Select value={status} onChange={setStatus} />;
}
```

## Environment Variables

**Required Variables** (`.env.local`):
```bash
# Backend API URL (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Usage**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Note**: Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## Performance Optimization

### Code Splitting

Next.js automatically code-splits by route. For additional optimization:

```typescript
// Dynamic import for large components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
});
```

### Image Optimization

If using images in the future:

```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={100}
  priority // For above-the-fold images
/>
```

### Font Optimization

Next.js automatically optimizes fonts:

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return <html className={inter.className}>{children}</html>;
}
```

## Testing

Tests are **OPTIONAL** for this feature. If adding tests later:

```bash
# Install testing dependencies
pnpm add -D @testing-library/react @testing-library/jest-dom jest-environment-jsdom

# Run tests
pnpm test
```

## Deployment

### Build for Production

```bash
cd frontend
pnpm build
```

This creates an optimized production build in the `.next/` directory.

### Environment Variables

Ensure production environment has `NEXT_PUBLIC_API_URL` set to the production backend URL.

### Start Production Server

```bash
pnpm start
```

Or deploy to Vercel, Netlify, or any Node.js hosting platform.

## Troubleshooting

### Common Issues

**Issue**: "Module not found: Can't resolve '@/components/..."
**Solution**: Check `tsconfig.json` has correct baseUrl and paths

**Issue**: "JWT token not being sent"
**Solution**: Ensure `credentials: 'include'` is set in fetch requests

**Issue**: "Server Component cannot use useState"
**Solution**: Add `'use client'` directive at top of file

**Issue**: "Type errors in production build"
**Solution**: Run `pnpm type-check` to fix all type errors

## Resources

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [Tailwind CSS 4 Documentation](https://tailwindcss.com/docs)
- [Zod Documentation](https://zod.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

## Related Specs

- Feature Specification: [specs/003-frontend-task-manager/spec.md](../specs/003-frontend-task-manager/spec.md)
- Implementation Plan: [specs/003-frontend-task-manager/plan.md](../specs/003-frontend-task-manager/plan.md)
- Backend API: [backend/api/](../backend/api/)


<claude-mem-context>
# Recent Activity

<!-- This section is auto-generated by claude-mem. Edit content outside the tags. -->

### Feb 4, 2026

| ID | Time | T | Title | Read |
|----|------|---|-------|------|
| #1110 | 12:01 PM | 🔵 | Research document establishes technical decisions for advanced features implementation | ~468 |
| #1108 | 11:56 AM | 🔵 | Frontend has react-day-picker and date-fns already installed for datetime functionality | ~282 |
| #1097 | 11:03 AM | 🔵 | Multiple feature specs organized with standardized documentation structure | ~371 |
</claude-mem-context>