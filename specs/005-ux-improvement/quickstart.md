# Quickstart: UI/UX Improvements

**Feature**: 005-ux-improvement
**Date**: 2026-01-24

## Prerequisites

- Node.js 20+ installed
- pnpm installed (`npm install -g pnpm`)
- Backend server running on port 8000
- Valid user session (logged in)

---

## Installation

### 1. Install New Dependencies

```bash
cd frontend

# Install shadcn/ui
npx shadcn@latest init

# Add required shadcn components
npx shadcn@latest add button input textarea dialog sheet skeleton badge

# Install nuqs for query state management
pnpm add nuqs

# Note: Sonner is already installed
```

### 2. Configure shadcn/ui

During `shadcn init`, select:
- Style: Default
- Base color: Slate
- CSS variables: Yes
- Tailwind config: `tailwind.config.ts`
- Components path: `@/components`
- Utils path: `@/lib/utils`

---

## Development

### Start Development Server

```bash
cd frontend
pnpm dev
```

Visit `http://localhost:3000`

---

## Key Implementation Files

### New Files to Create

```
frontend/src/
├── components/
│   ├── ui/                    # shadcn components (added by CLI)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── sheet.tsx
│   │   ├── skeleton.tsx
│   │   └── badge.tsx
│   ├── chatbot/
│   │   ├── FloatingChat.tsx   # NEW: Floating chat button + sheet
│   │   └── ChatStore.tsx      # NEW: Chat state context
│   ├── landing/
│   │   └── LandingPage.tsx    # NEW: Landing page component
│   └── loading/
│       └── TaskSkeleton.tsx   # NEW: Task loading skeleton
├── app/
│   ├── page.tsx               # MODIFY: Landing page + auth redirect
│   └── dashboard/
│       └── page.tsx           # MODIFY: Server-side data fetching
├── lib/
│   ├── hooks.ts               # MODIFY: Add useQueryState hooks
│   └── task-api.ts            # MODIFY: Add optimistic update helpers
└── styles/
    └── notion-theme.css       # NEW: Notion-inspired theme variables
```

---

## Component Usage Examples

### Using nuqs for Filters

```typescript
// app/dashboard/page.tsx
import { useQueryStates } from 'nuqs'
import { filterParsers } from '@/lib/filters'

function Dashboard() {
  const [filters, setFilters] = useQueryStates(filterParsers)

  // Update filter
  const setStatus = (status: 'all' | 'active' | 'completed') => {
    setFilters({ status })
  }

  return <FilterBar value={filters.status} onChange={setStatus} />
}
```

### Floating Chatbot

```typescript
// components/chatbot/FloatingChat.tsx
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { MessageSquare } from 'lucide-react'

export function FloatingChat() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <button className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 rounded-full shadow-lg">
          <MessageSquare className="w-6 h-6" />
        </button>
      </SheetTrigger>
      <SheetContent side="right" className="w-full sm:max-w-md">
        <ChatInterface />
      </SheetContent>
    </Sheet>
  )
}
```

### Optimistic Updates

```typescript
// lib/task-api.ts
export function useTaskMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: TaskCreateInput) => api.createTask(data),
    onMutate: async (newTask) => {
      // Cancel ongoing queries
      await queryClient.cancelQueries({ queryKey: ['tasks'] })

      // Snapshot previous value
      const previous = queryClient.getQueryData(['tasks'])

      // Optimistically update
      queryClient.setQueryData(['tasks'], (old: TaskListResponse) => ({
        ...old,
        tasks: [...old.tasks, { ...newTask, id: 'temp', completed: false }]
      }))

      return { previous }
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      queryClient.setQueryData(['tasks'], context.previous)
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    }
  })
}
```

### Toast Notifications

```typescript
import { toast } from 'sonner'

// Success
toast.success('Task created successfully')

// Error with context
toast.error('Failed to create task', {
  description: 'Please check your connection and try again'
})

// Loading promise
toast.promise(createTask(data), {
  loading: 'Creating task...',
  success: 'Task created!',
  error: 'Failed to create task'
})
```

---

## Theme Customization

### Notion-Inspired Colors

Add to `app/globals.css`:

```css
@layer base {
  :root {
    /* Neutral */
    --background: 0 0% 100%;
    --foreground: 0 0% 15%;

    /* Muted */
    --muted: 0 0% 96%;
    --muted-foreground: 0 0% 45%;

    /* Border */
    --border: 0 0% 90%;

    /* Primary (Notion Blue) */
    --primary: 204 87% 50%;
    --primary-foreground: 0 0% 100%;

    /* Semantic */
    --success: 142 76% 36%;
    --warning: 48 96% 47%;
    --error: 0 72% 51%;

    /* Priority */
    --priority-high: 0 72% 51%;
    --priority-medium: 48 96% 47%;
    --priority-low: 204 87% 50%;
  }
}
```

---

## Testing Changes

### 1. Test Dashboard Loading

```bash
# Navigate to dashboard
curl http://localhost:3000/dashboard

# Check for fast initial load (should be < 1s)
```

### 2. Test Filters and Search

1. Open dashboard
2. Change status filter - URL should update
3. Type in search - results should update after 300ms debounce
4. Clear filters - should return to all tasks

### 3. Test Optimistic Updates

1. Create a task
2. Task should appear immediately
3. Check network tab - API call happens in background
4. If API fails, task should be removed

### 4. Test Chatbot Integration

1. Click floating chat button (bottom-right)
2. Sheet should open from right side
3. Send a message
4. WebSocket should stream response
5. Navigate to another page - chat should remain open

---

## Troubleshooting

### Issue: shadcn components not styled

**Solution**: Ensure `@import "tailwindcss"` is in `app/globals.css`

### Issue: nuqs hydration errors

**Solution**: Wrap query state usage in `Suspense` boundary

### Issue: Optimistic updates not rolling back

**Solution**: Ensure `onError` handler uses the `context.previous` snapshot

### Issue: Chatbot doesn't preserve state

**Solution**: Use a React context provider at root layout level

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks in priority order (P1 → P2 → P3)
3. Test each user story independently
4. Run `/sp.implement` to execute the full implementation
