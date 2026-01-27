# Implementation Plan: UI/UX Improvements

**Branch**: `005-ux-improvement` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ux-improvement/spec.md`

## Summary

This feature improves the user experience of the todo list application by addressing critical usability issues: slow dashboard loading, broken filters, missing search, incomplete data display, generic design, and isolated chatbot. The implementation focuses on frontend enhancements using modern React patterns, shadcn/ui components, and Next.js 16 App Router features. No backend changes are required—all necessary data already exists in the database.

**Technical Approach**:
- **Server-side data fetching** for fast initial page load
- **shadcn/ui** components for Notion-inspired minimalistic design
- **nuqs** for type-safe, URL-based filter and search state
- **Sonner** for toast notifications (already installed)
- **Optimistic UI updates** for perceived performance
- **Integrated chatbot** as a floating dialog

## Technical Context

**Language/Version**: TypeScript 5+, React 19.2.3, Next.js 16.1.1
**Primary Dependencies**: shadcn/ui, nuqs, Sonner, Tailwind CSS 4
**Storage**: Neon Serverless PostgreSQL (existing, no changes)
**Testing**: React Testing Library (optional), Playwright (E2E)
**Target Platform**: Web browser (desktop + mobile responsive)
**Project Type**: Web application (frontend enhancement)
**Performance Goals**: Dashboard loads in <1s, search returns in <500ms
**Constraints**: Must preserve existing API contracts, no backend changes
**Scale/Scope**: 100+ tasks per user, 1000+ concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle III: Responsive Web UI
✅ **PASS** - Feature enhances responsive UI with improved components and layout

### Principle VI: Monorepo Structure Standard
✅ **PASS** - All changes within `frontend/` directory, following established structure

### Principle VIII: Frontend Architecture (Next.js)
✅ **PASS** - Uses Next.js App Router with Server Components where appropriate

### Principle IX: Data Ownership & Isolation
✅ **PASS** - All API calls include JWT (via httpOnly cookie), data scoped to authenticated user

### Principle X: API Response Consistency
✅ **PASS** - No API changes; frontend consumes existing consistent responses

**Result**: All gates passed. No constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/005-ux-improvement/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology research & decisions
├── data-model.md        # Entity definitions (frontend types)
├── quickstart.md        # Development quickstart guide
├── contracts/           # API contracts
│   └── api-contracts.md # Existing API documentation
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (modifications)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                 # MODIFY: Landing page + auth redirect
│   │   ├── layout.tsx               # MODIFY: Add Toaster (already has)
│   │   ├── globals.css              # MODIFY: Add Notion theme variables
│   │   └── dashboard/
│   │       └── page.tsx             # MODIFY: Server-side data fetching
│   ├── components/
│   │   ├── ui/                      # ADD: shadcn components
│   │   │   ├── button.tsx           # shadcn Button
│   │   │   ├── input.tsx            # shadcn Input
│   │   │   ├── textarea.tsx         # shadcn Textarea
│   │   │   ├── dialog.tsx           # shadcn Dialog
│   │   │   ├── sheet.tsx            # shadcn Sheet (for chatbot)
│   │   │   ├── skeleton.tsx         # shadcn Skeleton
│   │   │   └── badge.tsx            # shadcn Badge
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx         # MODIFY: Add due date, priority display
│   │   │   ├── TaskItem.tsx         # MODIFY: Show urgency, add badges
│   │   │   ├── FilterBar.tsx        # MODIFY: Use nuqs, add filters
│   │   │   └── TaskSkeleton.tsx     # ADD: Loading skeleton
│   │   ├── chatbot/
│   │   │   ├── FloatingChat.tsx     # ADD: Floating chat button + sheet
│   │   │   └── ChatProvider.tsx     # ADD: Chat state context
│   │   └── landing/
│   │       └── LandingPage.tsx      # ADD: Marketing landing page
│   ├── lib/
│   │   ├── hooks.ts                 # MODIFY: Add useQueryState hooks
│   │   ├── task-api.ts              # MODIFY: Optimistic update helpers
│   │   └── utils.ts                 # MODIFY: Add date formatting utils
│   └── types/
│       ├── task.ts                  # MODIFY: Add due_date, priority types
│       └── filters.ts               # MODIFY: Enhanced filter types
└── package.json                     # MODIFY: Add nuqs dependency
```

**Structure Decision**: Full monorepo structure (Option 3). This feature modifies existing `frontend/` directory to add UX improvements while maintaining compatibility with `backend/` and `cli/` directories. All additions are within the established frontend structure.

## Phase 0: Research Complete

Technology decisions documented in `research.md`:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Library | shadcn/ui | Copy-paste components, Tailwind native, Notion-like aesthetic |
| Query State | nuqs | Type-safe, App Router compatible, debounced search |
| Toast | Sonner | Already installed, beautiful defaults |
| Color Palette | Custom Notion-inspired | Neutral tones, blue accent, semantic colors |
| Data Fetching | Server Components | Fast initial load, streaming support |
| Chatbot | shadcn Sheet | Floating dialog, state preservation via context |

## Phase 1: Design Complete

### Data Model
- **No new database entities** required
- Frontend TypeScript types enhanced for `due_date`, `priority`, `urgency`
- Filter state types defined for nuqs serialization
- See `data-model.md` for complete type definitions

### API Contracts
- **No new API endpoints** required
- Existing endpoints already support all needed data
- See `contracts/api-contracts.md` for complete API documentation

### Components to Create/Modify

#### New Components (shadcn)
- `Button`, `Input`, `Textarea`, `Dialog`, `Sheet`, `Skeleton`, `Badge`

#### New Feature Components
- `FloatingChat.tsx` - Floating chatbot button with Sheet panel
- `ChatProvider.tsx` - React context for chat state preservation
- `TaskSkeleton.tsx` - Skeleton loading component for task list
- `LandingPage.tsx` - Marketing landing page

#### Modified Components
- `TaskItem.tsx` - Add due date display, priority badge, urgency styling
- `TaskList.tsx` - Add empty state, skeleton loading
- `FilterBar.tsx` - Replace with nuqs-based implementation
- `dashboard/page.tsx` - Convert to Server Component with initial data fetch

## Implementation Phases

### Phase 1: Critical UX Issues (P1)

1. **Server-Side Data Fetching**
   - Convert dashboard to Server Component
   - Fetch initial tasks server-side
   - Implement skeleton loading states
   - Target: <1s initial page load

2. **Display Missing Task Data**
   - Add due date display to TaskItem
   - Add priority badge
   - Implement urgency color coding (overdue, today, soon)
   - Format dates relative to now

3. **Fix Filter Functionality**
   - Replace current filter implementation with nuqs
   - Add priority filter
   - Add due date range filter
   - Ensure filter + search work together (AND logic)

4. **Task Search**
   - Implement real-time search with debouncing
   - Search in title and description
   - Update URL with search query
   - Show "no results" state

### Phase 2: Enhanced Interactions (P2)

1. **Optimistic UI Updates**
   - Implement optimistic create (task appears immediately)
   - Implement optimistic toggle (checkbox updates immediately)
   - Implement optimistic delete (task removed immediately)
   - Add rollback on error

2. **Integrated Chatbot**
   - Create floating button in bottom-right
   - Use shadcn Sheet for slide-over panel
   - Implement chat state context (preserves across navigation)
   - Reuse existing WebSocket connection

3. **Enhanced Toast Notifications**
   - Add success toasts for all actions
   - Add error toasts with helpful messages
   - Implement promise toasts for async operations
   - Use appropriate color coding

### Phase 3: Visual Polish (P3)

1. **Notion-Inspired Theme**
   - Implement custom color palette (CSS variables)
   - Update typography (Inter font, proper hierarchy)
   - Add generous whitespace
   - Ensure consistent design across all pages

2. **Engaging Loading Animations**
   - Replace generic spinners with skeleton screens
   - Add typing indicator for chatbot
   - Implement smooth transitions

3. **Landing Page**
   - Create marketing-focused homepage
   - Add value proposition hero section
   - Add feature highlights
   - Implement auth redirect for logged-in users

4. **Dark Mode Support**
   - Add theme toggle
   - Ensure all components work in both modes

## Complexity Tracking

> No constitution violations. This section not required.

## Dependencies

### External Dependencies (New)

```json
{
  "nuqs": "^2.0.0"
}
```

### shadcn/ui Components

```bash
npx shadcn@latest add button input textarea dialog sheet skeleton badge
```

### Feature Dependencies

- **Feature 001 (User Authentication)**: Required for session check on landing page
- **Feature 003 (Frontend Task Manager)**: This feature enhances existing frontend
- **Feature 004 (AI Chatbot)**: Reuses WebSocket, chat components for integrated dialog

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing filter functionality | Comprehensive testing, gradual rollout with feature flags |
| Optimistic update desync | Implement rollback on error, periodic revalidation |
| Chatbot state loss across navigation | Use React context with proper provider placement |
| Performance regression with shadcn | Tree-shake unused components, monitor bundle size |
| Browser compatibility (nuqs) | Test across browsers, provide fallback to useSearchParams |

## Success Criteria

From feature spec, measured post-implementation:

- **SC-001**: Dashboard loads in <1s for 100 tasks
- **SC-002**: 95% user satisfaction with design
- **SC-003**: Search returns results in <500ms
- **SC-004**: Task completion rate increases 30%
- **SC-005**: 90% users successfully use filters first session
- **SC-006**: Time to find task decreases 50%
- **SC-007**: Perceived wait time decreases 80% (optimistic updates)
- **SC-008**: Chatbot usage increases 200% (integrated access)
- **SC-009**: Landing page conversion rate reaches 15%

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks in priority order (P1 → P2 → P3)
3. Run `/sp.implement` to execute full implementation
