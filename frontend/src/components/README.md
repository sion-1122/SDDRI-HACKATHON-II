# Components Documentation

This directory contains all React components for the Todo List frontend application.

## Component Categories

- **`ui/`** - Reusable UI primitives (Button, Input, Modal, etc.)
- **`auth/`** - Authentication-related components (LoginForm, RegisterForm)
- **`tasks/`** - Task management components (TaskList, TaskItem, TaskForm, FilterBar, Pagination)

---

## UI Components (`ui/`)

### Button

**File**: `ui/Button.tsx`

Reusable button component with variants and sizes.

**Props**:
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}
```

**Usage**:
```tsx
import { Button } from '@/components/ui/Button';

// Primary button (default)
<Button onClick={handleClick}>Save</Button>

// Secondary button
<Button variant="secondary" onClick={handleCancel}>Cancel</Button>

// Danger button
<Button variant="danger" onClick={handleDelete}>Delete</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// Disabled state
<Button disabled onClick={handleClick}>Disabled</Button>
```

**Variants**:
- `primary`: Blue background (`bg-blue-600`), white text
- `secondary`: Gray background (`bg-gray-200`), dark text
- `danger`: Red background (`bg-red-600`), white text

**Sizes**:
- `sm`: Small padding (`px-3 py-1`), small text
- `md`: Medium padding (`px-4 py-2`), medium text (default)
- `lg`: Large padding (`px-6 py-3`), large text

---

### Input

**File**: `ui/Input.tsx`

Text input component with label and error display support.

**Props**:
```typescript
interface InputProps {
  label?: string;
  error?: string;
  type?: 'text' | 'email' | 'password' | 'number';
  name: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  // All standard input attributes
  [key: string]: any;
}
```

**Usage**:
```tsx
import { Input } from '@/components/ui/Input';

// Basic input
<Input
  name="email"
  type="email"
  placeholder="Enter your email"
/>

// With label and error
<Input
  label="Email Address"
  name="email"
  type="email"
  error={errors.email?.message}
  placeholder="user@example.com"
/>

// Required field
<Input
  label="Password"
  name="password"
  type="password"
  required
/>

// Disabled
<Input
  label="Read-only field"
  name="readonly"
  disabled
/>
```

**Features**:
- Automatic error message display (when `error` prop is provided)
- Required field indicator (asterisk)
- Ref forwarding for form integration
- ARIA attributes for accessibility

---

### Textarea

**File**: `ui/Textarea.tsx`

Multi-line text input component with label and error display.

**Props**:
```typescript
interface TextareaProps {
  label?: string;
  error?: string;
  name: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  rows?: number;
  className?: string;
  // All standard textarea attributes
  [key: string]: any;
}
```

**Usage**:
```tsx
import { Textarea } from '@/components/ui/Textarea';

// Basic textarea
<Textarea
  name="description"
  placeholder="Enter description"
  rows={4}
/>

// With label and error
<Textarea
  label="Task Description"
  name="description"
  error={errors.description?.message}
  placeholder="Describe your task..."
  rows={5}
/>
```

**Features**:
- Multi-line text input
- Configurable rows (default: 4)
- Label and error display
- Ref forwarding

---

### Modal

**File**: `ui/Modal.tsx`

Modal dialog component with backdrop and accessibility features.

**Props**:
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  footer?: React.ReactNode;
  children: React.ReactNode;
}
```

**Usage**:
```tsx
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Edit Task"
        footer={
          <>
            <Button variant="secondary" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save</Button>
          </>
        }
      >
        <p>Modal content goes here...</p>
      </Modal>
    </>
  );
}
```

**Features**:
- Backdrop click to close
- Escape key to close
- Focus trap (keyboard navigation)
- ARIA attributes (`role="dialog"`, `aria-modal`)
- Scrollable content area

---

### LoadingSpinner

**File**: `ui/LoadingSpinner.tsx`

Animated loading spinner component.

**Props**:
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

**Usage**:
```tsx
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

// Sizes
<LoadingSpinner size="sm" />
<LoadingSpinner size="md" /> // Default
<LoadingSpinner size="lg" />

// With custom class
<LoadingSpinner className="border-white" />
```

**Sizes**:
- `sm`: Small spinner (16px)
- `md`: Medium spinner (24px)
- `lg`: Large spinner (32px)

**Styling**:
- Animated border rotation
- Configurable border color via `className`

---

## Auth Components (`auth/`)

### LoginForm

**File**: `auth/LoginForm.tsx`

Login form component with email/password fields and Zod validation.

**Props**:
```typescript
interface LoginFormProps {
  // No props - uses authClient internally
}
```

**Usage**:
```tsx
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return <LoginForm />;
}
```

**Features**:
- Email and password fields
- Zod schema validation (`loginFormSchema`)
- Integrates with `authClient.signIn.email()`
- Redirects to `/tasks` on success
- Error toast notifications
- Loading state during submission

**Validation Rules**:
- Email: Valid email format
- Password: Minimum 8 characters

---

### RegisterForm

**File**: `auth/RegisterForm.tsx`

Registration form with email/password/confirm password and Zod validation.

**Props**:
```typescript
interface RegisterFormProps {
  // No props - uses authClient internally
}
```

**Usage**:
```tsx
import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  return <RegisterForm />;
}
```

**Features**:
- Email, password, and confirm password fields
- Zod schema validation (`registerFormSchema`)
- Passwords must match validation
- Integrates with `authClient.signUp.email()`
- Auto-login after successful registration
- Redirects to `/tasks` on success
- Error toast notifications

**Validation Rules**:
- Email: Valid email format
- Password: Minimum 8 characters
- Confirm Password: Must match password

---

## Task Components (`tasks/`)

### TaskList

**File**: `tasks/TaskList.tsx`

Server component that renders a list of tasks.

**Props**:
```typescript
interface TaskListProps {
  tasks: Task[];
}
```

**Usage**:
```tsx
import { TaskList } from '@/components/tasks/TaskList';
import { taskApi } from '@/lib/task-api';

export default async function TasksPage() {
  const response = await taskApi.listTasks();
  return <TaskList tasks={response.tasks} />;
}
```

**Features**:
- Displays list of `TaskItem` components
- Empty state when no tasks
- Special empty state for filtered results
- Responsive layout (1 column mobile, 2 columns tablet, 3 columns desktop)

**Empty States**:
- No tasks: "Get started by creating a new task"
- No filtered results: "No tasks match your filters"

---

### TaskItem

**File**: `tasks/TaskItem.tsx`

Client component that displays a single task with action buttons.

**Props**:
```typescript
interface TaskItemProps {
  task: Task;
}
```

**Usage**:
```tsx
import { TaskItem } from '@/components/tasks/TaskItem';

function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <div>
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
```

**Features**:
- Displays task title, description, completion status
- Shows relative time created
- Checkbox to toggle completion
- Edit button (opens TaskForm modal)
- Delete button (with confirmation modal)
- Strikethrough style for completed tasks
- Loading spinner during API calls
- Optimistic UI updates

**Task Display**:
- Title: Bold text, strikethrough if completed
- Description: Gray text, strikethrough if completed
- Timestamp: Relative time (e.g., "2 hours ago")
- Checkbox: Green checkmark when completed

---

### TaskForm

**File**: `tasks/TaskForm.tsx`

Modal form component for creating and editing tasks.

**Props**:
```typescript
interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task; // If provided, form is in edit mode
  mode?: 'create' | 'edit';
}
```

**Usage**:
```tsx
import { TaskForm } from '@/components/tasks/TaskForm';

function CreateTaskButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Create Task</Button>
      <TaskForm
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        mode="create"
      />
    </>
  );
}

function EditTaskButton({ task }: { task: Task }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Edit</Button>
      <TaskForm
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        task={task}
        mode="edit"
      />
    </>
  );
}
```

**Features**:
- Title input (required, max 255 characters)
- Description textarea (optional, max 2000 characters)
- Zod schema validation
- Create mode: Calls `taskApi.createTask()`
- Edit mode: Pre-fills with task data, calls `taskApi.updateTask()`
- Success/error toast notifications
- Closes modal on success
- Cancel button

**Validation Rules**:
- Title: Required, 1-255 characters
- Description: Optional, max 2000 characters

---

### FilterBar

**File**: `tasks/FilterBar.tsx`

Client component for filtering and searching tasks.

**Props**:
```typescript
interface FilterBarProps {
  // No props - reads/writes URL params
}
```

**Usage**:
```tsx
import { FilterBar } from '@/components/tasks/FilterBar';

export default function TasksPage() {
  return (
    <div>
      <FilterBar />
      <TaskList tasks={tasks} />
    </div>
  );
}
```

**Features**:
- Status dropdown: All, Active, Completed
- Search input with 300ms debounce
- Clear filters button
- URL param synchronization (`?status=active&search=query`)
- Responsive layout (stacked on mobile, inline on tablet+)

**URL Params**:
- `?status=all` - Show all tasks
- `?status=active` - Show incomplete tasks
- `?status=completed` - Show completed tasks
- `?search=query` - Search by keyword
- `?status=active&search=query` - Combined filters

---

### Pagination

**File**: `tasks/Pagination.tsx`

Client component for paginated task list navigation.

**Props**:
```typescript
interface PaginationProps {
  total: number;       // Total number of tasks
  limit: number;       // Items per page (default: 50)
  currentPage: number; // Current page (1-based)
}
```

**Usage**:
```tsx
import { Pagination } from '@/components/tasks/Pagination';
import { useSearchParams } from 'next/navigation';

export default function TasksPage() {
  const searchParams = useSearchParams();
  const page = parseInt(searchParams.get('page') || '1', 10);

  return (
    <>
      <TaskList tasks={tasks} />
      <Pagination
        total={response.total}
        limit={50}
        currentPage={page}
      />
    </>
  );
}
```

**Features**:
- Previous/Next buttons
- Page indicator ("Page X of Y")
- Jump to page input
- URL param synchronization (`?page=2`)
- Disabled Previous on page 1
- Disabled Next on last page
- Preserves filters across page changes
- Responsive layout (stacked on mobile, inline on tablet+)

**Calculations**:
- Total pages: `Math.ceil(total / limit)`
- Offset: `(page - 1) * limit`
- Has prev page: `currentPage > 1`
- Has next page: `currentPage < totalPages`

---

## Component Composition Patterns

### Form + Modal Pattern

```tsx
function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Form</Button>
      <TaskForm isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
```

### List + Item Pattern

```tsx
function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
```

### Filter + List + Pagination Pattern

```tsx
function TasksPage() {
  return (
    <>
      <FilterBar />
      <TaskList tasks={tasks} />
      <Pagination total={total} limit={limit} currentPage={page} />
    </>
  );
}
```

## Styling Conventions

All components use Tailwind CSS utility classes:

- **Spacing**: `space-y-4`, `gap-2`, `p-4`, `m-2`
- **Flexbox**: `flex`, `flex-row`, `flex-col`, `justify-between`, `items-center`
- **Grid**: `grid`, `grid-cols-1`, `md:grid-cols-2`, `lg:grid-cols-3`
- **Colors**: `bg-blue-600`, `text-gray-900`, `border-gray-300`
- **Typography**: `text-sm`, `font-semibold`, `text-gray-500`
- **States**: `hover:bg-blue-700`, `disabled:opacity-50`, `focus:ring-2`

## Accessibility

All components include ARIA attributes:

- **Button**: `aria-label` for icon-only buttons
- **Input**: `aria-describedby` for error messages
- **Modal**: `role="dialog"`, `aria-modal`, focus trap
- **Forms**: Proper label associations

## Type Safety

All components are fully typed with TypeScript:

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  // ...
}

export function Button({ variant, size, children }: ButtonProps) {
  // ...
}
```

Import types from `@/types/`:

```typescript
import type { Task } from '@/types/task';

interface TaskItemProps {
  task: Task;
}
```
