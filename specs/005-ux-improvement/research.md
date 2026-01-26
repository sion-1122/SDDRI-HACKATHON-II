# Research: UI/UX Improvements

**Feature**: 005-ux-improvement
**Date**: 2026-01-24
**Status**: Complete

## Overview

This document consolidates research findings for the UX improvement feature. All technology decisions have been made based on user requirements and best practices for Next.js applications.

## Technology Choices

### 1. UI Component Library: shadcn/ui

**Decision**: Use shadcn/ui as the primary UI component library.

**Rationale**:
- **Not Radix**: shadcn/ui is built on Radix UI primitives which provide accessible, unstyled components
- **Copy-Paste Components**: Components are copied to the project codebase, not installed as dependencies
- **Full Customization**: Complete control over component code and styling
- **Tailwind Native**: Built specifically for Tailwind CSS (already in use)
- **Modern Design**: Clean, minimalistic aesthetic that aligns with Notion-inspired design
- **TypeScript First**: Full type safety out of the box
- **No Runtime Overhead**: No additional JavaScript bundle from npm packages

**User Requirement**: Matches "Notion inspired minimalistic theme" requirement

**Alternatives Considered**:
- **Material-UI (MUI)**: Too opinionated, heavy bundle size, doesn't match Notion aesthetic
- **Chakra UI**: Good but adds runtime dependencies, less customization
- **Headless UI**: Good but requires more custom styling work

**Key Components to Use**:
- `Button`, `Input`, `Textarea` - Form elements
- `Dialog`, `Sheet` - Modal and slide-over panels (for chatbot)
- `Toast` (via Sonner) - Notifications
- `Skeleton` - Loading states
- `Badge` - Status indicators
- `Command` - Search palette (optional enhancement)

**Installation**:
```bash
npx shadcn@latest init
npx shadcn@latest add button input textarea dialog sheet toast skeleton badge
```

---

### 2. Query State Management: nuqs

**Decision**: Use nuqs for URL query string state management.

**Rationale**:
- **Type-Safe**: Full TypeScript support for query parameters
- **React Hooks**: Simple `useQueryState` and `useQueryStates` hooks
- **Next.js App Router Compatible**: Designed specifically for Next.js 13+ App Router
- **Serializable State**: All filter/search state in URL (shareable, bookmarkable)
- **Debouncing Built-in**: Native support for debounced search input
- **No Hydration Mismatches**: Handles SSR correctly
- **Lightweight**: Tiny bundle size (~3KB)

**User Requirement**: Supports "Working task filtering" and "Task search" with URL-based state

**Alternatives Considered**:
- **Native useSearchParams**: Lacks type safety, requires manual serialization
- **Zustand with URL sync**: More complex, adds state management library
- **React Router URL state**: Not compatible with Next.js App Router

**Usage Example**:
```typescript
import { useQueryStates } from 'nuqs'

const [filters, setFilters] = useQueryStates({
  status: parseAsStringLiteral(['all', 'active', 'completed']).withDefault('all'),
  search: parseAsString.withDefault(''),
  page: parseAsInteger.withDefault(1)
})
```

**Installation**:
```bash
npm install nuqs
```

---

### 3. Toast Notifications: Sonner

**Decision**: Use Sonner for toast notifications.

**Rationale**:
- **Already in Use**: Sonner is already installed in the project (see package.json)
- **Standalone**: Works independently, minimal dependencies
- **Beautiful Defaults**: Modern, clean animations out of the box
- **Promise Support**: Built-in support for async toasts with loading states
- **Action Buttons**: Toasts can include action buttons
- **Position Control**: Easy to position (bottom-right, top-center, etc.)
- **Stacking**: Handles multiple toasts elegantly

**User Requirement**: "Toast notifications for every important action with relevant context and colors/states"

**Current Usage** (already in dashboard):
```typescript
import { toast } from 'sonner'

toast.success('Task created successfully')
toast.error('Failed to create task')
toast.promise(createTask(data), {
  loading: 'Creating...',
  success: 'Created!',
  error: 'Failed'
})
```

**Alternatives Considered**:
- **react-hot-toast**: Similar but Sonner has better animations
- **react-toastify**: Heavier, more configuration needed
- **shadcn/toast**: Uses Sonner under the hood

---

### 4. Notion-Inspired Color Palette

**Decision**: Implement a custom Notion-inspired color palette using CSS variables and Tailwind config.

**Rationale**:
- **Neutral Base**: Grays form the foundation (subtle backgrounds, borders)
- **Accent Colors**: Limited accent colors used sparingly (blue for primary actions)
- **High Contrast Text**: Dark text on light backgrounds for readability
- **Subtle Borders**: Light borders that don't dominate
- **Semantic Colors**: Green (success), Red (error), Yellow (warning) with muted tones

**Color Palette Definition**:

```css
/* Neutral Colors (Notion-like) */
--background: #FFFFFF;
--foreground: #37352F;
--muted: #F7F7F5;
--muted-foreground: #787774;
--border: #E9E9E7;
--input: #E9E9E7;
--card: #FFFFFF;
--card-foreground: #37352F;

/* Primary Accent */
--primary: #2383E2; /* Notion blue */
--primary-foreground: #FFFFFF;

/* Semantic Colors */
--success: #0F9B0F; /* Muted green */
--success-foreground: #FFFFFF;
--warning: #EAB308; /* Muted yellow */
--warning-foreground: #37352F;
--error: #E03E3E; /* Muted red */
--error-foreground: #FFFFFF;

/* Priority Colors */
--priority-high: #E03E3E;
--priority-medium: #EAB308;
--priority-low: #2383E2;

/* Due Date Urgency Colors */
--overdue: #E03E3E;
--due-today: #EAB308;
--due-soon: #0F7D0F;
--due-later: #787774;
```

**Typography**:
- Font: Inter or system-ui (sans-serif)
- Headings: 600-700 weight, tight tracking
- Body: 400 weight, relaxed line-height (1.6)

---

### 5. Server-Side Data Fetching Strategy

**Decision**: Use Next.js Server Components for initial data load with React Query for client-side cache invalidation.

**Rationale**:
- **Server Components by Default**: Dashboard page fetches data server-side on initial load
- **Streaming**: Use React Suspense for progressive loading
- **Cache Invalidation**: After optimistic updates, invalidate React Query cache
- **Revalidation**: Use `router.refresh()` for Next.js server component revalidation

**Implementation Pattern**:
```typescript
// Server Component (default)
async function DashboardPage() {
  const tasks = await fetchTasks() // Server-side
  return <TaskList initialTasks={tasks} />
}

// Client Component with optimistic updates
'use client'
function TaskList({ initialTasks }) {
  const [tasks, setTasks] = useState(initialTasks)

  const createTask = async (data) => {
    // Optimistic update
    const tempId = crypto.randomUUID()
    setTasks(prev => [...prev, { id: tempId, ...data }])

    try {
      const created = await api.createTask(data)
      setTasks(prev => prev.map(t => t.id === tempId ? created : t))
    } catch {
      // Rollback
      setTasks(prev => prev.filter(t => t.id !== tempId))
    }
  }
}
```

---

### 6. Chatbot Floating Dialog

**Decision**: Use shadcn Sheet component positioned as a floating dialog in bottom-right corner.

**Rationale**:
- **Sheet Component**: shadcn's Sheet provides slide-over panel functionality
- **Positioning**: Custom CSS to position in bottom-right corner
- **Resizable**: Can be expanded/collapsed
- **State Preservation**: Use React state + context to preserve chat across navigation
- **WebSocket**: Existing WebSocket connection from feature 004 will be reused

**Implementation**:
```typescript
<Sheet open={isOpen} onOpenChange={setIsOpen}>
  <SheetTrigger asChild>
    <FloatingButton className="fixed bottom-6 right-6" />
  </SheetTrigger>
  <SheetContent side="right" className="w-full sm:max-w-md">
    <ChatInterface />
  </SheetContent>
</Sheet>
```

---

### 7. Loading Animations

**Decision**: Use shadcn Skeleton components for content loading and custom animations for chatbot.

**Rationale**:
- **Skeleton Screens**: Better perceived performance than spinners
- **Contextual**: Skeletons show the structure of incoming content
- **Chatbot Typing**: Animated dots or pulsing indicator for "thinking" state
- **Progress Indicators**: Existing ProgressBar from feature 004 will be enhanced

**Loading States**:
1. **Dashboard Initial Load**: Full-page skeleton with task item skeletons
2. **Filter/Search**: Inline skeleton in task list area
3. **Chatbot Thinking**: Typing indicator animation
4. **Action Buttons**: Loading spinner inside button

---

### 8. Landing Page

**Decision**: Create a new `/app/page.tsx` (root route) with Notion-inspired design.

**Rationale**:
- **Current Redirect**: Root page currently redirects to dashboard or login
- **Marketing Page**: Needs to showcase app value for new visitors
- **Auth Redirect**: Logged-in users bypass landing page

**Sections**:
1. **Hero**: Value proposition + CTA (Sign Up)
2. **Features**: 3-4 key features with icons
3. **How It Works**: Simple 3-step process
4. **Footer**: Copyright + links

**Redirect Logic**:
```typescript
// app/page.tsx (Server Component)
import { redirect } from 'next/navigation'
import { authClient } from '@/lib/auth-client'

export default async function HomePage() {
  const session = await authClient.getSession()
  if (session) {
    redirect('/dashboard')
  }
  return <LandingPage />
}
```

---

## Dependency Summary

### New Dependencies to Install

```bash
# UI Library
npx shadcn@latest init
npx shadcn@latest add button input textarea dialog sheet skeleton badge

# Query State Management
npm install nuqs

# Note: Sonner is already installed
```

### Existing Dependencies to Reuse

- **Next.js 16.1.1**: App Router, Server Components
- **React 19.2.3**: Hooks, concurrent features
- **Tailwind CSS 4**: Styling
- **Better Auth 1.4.10**: Authentication
- **Sonner**: Toast notifications (already installed)

---

## Architecture Decisions

### 1. Optimistic Updates Pattern

```typescript
const updateWithOptimism = async (id: string, updates: Partial<Task>) => {
  // Store previous state
  const previous = tasks.find(t => t.id === id)

  // Apply optimistic update
  setTasks(prev => prev.map(t =>
    t.id === id ? { ...t, ...updates } : t
  ))

  try {
    // Send to server
    const result = await api.updateTask(id, updates)
    // Update with server response
    setTasks(prev => prev.map(t =>
      t.id === id ? result : t
    ))
  } catch (error) {
    // Rollback on error
    setTasks(prev => prev.map(t =>
      t.id === id ? previous : t
    ))
    toast.error('Update failed')
  }
}
```

### 2. Filter + Search Combination Logic

```typescript
// Both filters apply together (AND logic)
const filteredTasks = tasks.filter(task => {
  const matchesStatus =
    filterStatus === 'all' ||
    (filterStatus === 'active' && !task.completed) ||
    (filterStatus === 'completed' && task.completed)

  const matchesSearch =
    !searchQuery ||
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase())

  return matchesStatus && matchesSearch
})
```

### 3. Task Data Display

The backend already stores `due_date` and `priority` (from Task model). Frontend needs to:
- Display due dates in a formatted, human-readable way
- Add visual urgency indicators (color coding)
- Show priority badges

---

## Implementation Considerations

### P1 (Critical Path)
1. Server-side data fetching for dashboard
2. Fix broken filter functionality
3. Add task search
4. Display missing task data (due_date, priority)

### P2 (High Value)
1. Optimistic UI updates
2. Integrated chatbot dialog
3. Toast notifications enhancement

### P3 (Polish)
1. Notion-inspired theme implementation
2. Engaging loading animations
3. Landing page
4. Enhanced chatbot experience

---

## Summary

All technology decisions have been finalized. The implementation will use:
- **shadcn/ui** for UI components
- **nuqs** for query state management
- **Sonner** for toast notifications (already installed)
- **Custom Notion-inspired** color palette and design
- **Next.js Server Components** for performance

No further research or clarification needed.
