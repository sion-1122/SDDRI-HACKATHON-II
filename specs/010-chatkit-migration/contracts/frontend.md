# Frontend Contracts: ChatKit Migration

**Feature**: 010-chatkit-migration
**Date**: 2026-02-06

## Overview

This document defines the frontend integration contracts for ChatKit React. The migration replaces custom chat components with the ChatKit UI component.

## Component Integration

### ChatKit Component

**Package**: `@openai/chatkit-react`

**Installation**:
```bash
npm install @openai/chatkit-react
```

**Basic Usage**:
```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

function ChatPage() {
  const { control } = useChatKit({
    api: {
      apiURL: `${API_URL}/api/chatkit`,
      fetch: customFetchWithAuth,
    },
  });

  return <ChatKit control={control} className="h-full w-full" />;
}
```

---

## useChatKit Hook

### Configuration Options

```typescript
interface UseChatKitOptions {
  api: {
    // Self-hosted API URL (no OpenAI Sessions API)
    apiURL: string;

    // Custom fetch for authentication
    fetch?: (url: string, options: RequestInit) => Promise<Response>;

    // Client secret callback (NOT USED in self-hosted mode)
    getClientSecret?: (existing?: string) => Promise<string>;
  };

  // Client-side tools (executed in browser)
  clientTools?: Record<string, (args: any) => Promise<any>>;

  // Effect handlers for widget actions
  effectHandlers?: Record<string, (action: any) => void>;

  // Custom theme
  theme?: ChatKitTheme;

  // Initial thread ID (for existing conversations)
  initialThreadID?: string;
}
```

### Return Value

```typescript
interface ChatKitControl {
  // Control object passed to ChatKit component
  control: {
    // Thread management
    createThread: () => Promise<string>;
    switchThread: (threadId: string) => void;

    // Message sending
    sendMessage: (content: string) => void;

    // State
    currentThreadId: string | null;
    isStreaming: boolean;

    // Error handling
    error: Error | null;
  };
}
```

---

## Authentication Integration

### Custom Fetch Implementation

```typescript
/**
 * Custom fetch implementation that injects JWT authentication.

[From]: frontend/src/lib/api/client.ts - API client with credentials
*/
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function customFetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // Include credentials for httpOnly cookies
  return fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
    },
  });
}
```

### ChatKit Configuration with Auth

```typescript
/**
 * ChatKit configuration with custom authentication.

[From]: specs/010-chatkit-migration/research.md - Section 6
*/
const { control } = useChatKit({
  api: {
    apiURL: `${API_URL}/api/chatkit`,
    fetch: customFetchWithAuth,
  },
});
```

---

## Component Replacement Map

| Old Component | New Component | Notes |
|--------------|---------------|-------|
| `ChatInterface.tsx` | `ChatKit` (from `@openai/chatkit-react`) | Main UI replacement |
| `MessageList.tsx` | Built into `ChatKit` | Removed |
| `MessageInput.tsx` | Built into `ChatKit` | Removed |
| `ProgressBar.tsx` | Built-in widget system | Removed |
| `ConnectionStatus.tsx` | Built-in status indicators | Removed |
| `useWebSocket.ts` | SSE handling (built into ChatKit) | Removed |

---

## State Management Changes

### Before (Custom Implementation)

```typescript
// Local state management
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [conversationId, setConversationId] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

// LocalStorage persistence
const CONVERSATION_STORAGE_KEY = (userId: string) => `chat_conversation_${userId}`;

useEffect(() => {
  const stored = localStorage.getItem(CONVERSATION_STORAGE_KEY(userId));
  if (stored) {
    const parsed = JSON.parse(stored);
    setMessages(parsed.messages);
    setConversationId(parsed.conversationId);
  }
}, [userId]);
```

### After (ChatKit)

```typescript
// ChatKit manages state internally
const { control } = useChatKit({
  api: {
    apiURL: `${API_URL}/api/chatkit`,
    fetch: customFetchWithAuth,
  },
  // ChatKit handles conversation persistence via backend
  initialThreadID: existingThreadId, // Optional: restore previous thread
});

// No local state management needed
// No localStorage needed (backend persists threads)
```

---

## Deleted Components

### Files to Delete

```
frontend/src/components/chat/
├── ChatInterface.tsx          ← DELETE
├── MessageList.tsx             ← DELETE
├── MessageInput.tsx            ← DELETE
├── ProgressBar.tsx             ← DELETE
├── ConnectionStatus.tsx        ← DELETE
├── ToolStatus.tsx              ← DELETE (if exists)
└── useWebSocket.ts             ← DELETE
```

### Total LOC Removed: ~600 lines

---

## New Component Structure

### ChatKit Wrapper Component

```typescript
/**
 * ChatKit integration wrapper component.

[From]: specs/010-chatkit-migration/plan.md - Phase 2
*/
"use client";

import { ChatKit, useChatKit } from '@openai/chatkit-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function customFetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  return fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
    },
  });
}

interface TaskChatProps {
  userId: string;
  initialThreadId?: string;
}

export function TaskChat({ userId, initialThreadId }: TaskChatProps) {
  const { control } = useChatKit({
    api: {
      apiURL: `${API_URL}/api/chatkit`,
      fetch: customFetchWithAuth,
    },
    initialThreadID: initialThreadId,
  });

  return (
    <div className="flex flex-col h-full w-full border rounded-lg shadow-sm bg-card">
      <ChatKit
        control={control}
        className="h-full w-full"
      />
    </div>
  );
}
```

---

## Theme Customization

### Default Theme Variables

```css
/* ChatKit uses CSS variables for theming */

:root {
  --chatkit-primary: #3b82f6;
  --chatkit-primary-hover: #2563eb;
  --chatkit-bg: #ffffff;
  --chatkit-bg-secondary: #f9fafb;
  --chatkit-text: #111827;
  --chatkit-text-secondary: #6b7280;
  --chatkit-border: #e5e7eb;
  --chatkit-message-user-bg: #3b82f6;
  --chatkit-message-user-text: #ffffff;
  --chatkit-message-assistant-bg: #f3f4f6;
  --chatkit-message-assistant-text: #111827;
}
```

### Dark Mode Support

```css
[data-theme="dark"] {
  --chatkit-bg: #1f2937;
  --chatkit-bg-secondary: #374151;
  --chatkit-text: #f9fafb;
  --chatkit-text-secondary: #9ca3af;
  --chatkit-border: #4b5563;
  --chatkit-message-assistant-bg: #374151;
}
```

---

## Error Handling

### Error Display

```typescript
const { control, error } = useChatKit({
  api: {
    apiURL: `${API_URL}/api/chatkit`,
    fetch: customFetchWithAuth,
  },
});

// Display error if needed
if (error) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded">
      <p className="text-red-600">
        Chat error: {error.message}
      </p>
      <button onClick={() => window.location.reload()}>
        Reload
      </button>
    </div>
  );
}
```

---

## Migration Steps

### Step 1: Install Dependencies

```bash
npm install @openai/chatkit-react
```

### Step 2: Create ChatKit Wrapper

Create `frontend/src/components/chat/TaskChat.tsx` with the wrapper component shown above.

### Step 3: Replace ChatInterface Import

**Before**:
```typescript
import { ChatInterface } from '@/components/chat/ChatInterface';
```

**After**:
```typescript
import { TaskChat } from '@/components/chat/TaskChat';
```

### Step 4: Update Component Usage

**Before**:
```typescript
<ChatInterface userId={userId} />
```

**After**:
```typescript
<TaskChat userId={userId} initialThreadId={threadId} />
```

### Step 5: Delete Old Components

```bash
rm frontend/src/components/chat/ChatInterface.tsx
rm frontend/src/components/chat/MessageList.tsx
rm frontend/src/components/chat/MessageInput.tsx
rm frontend/src/components/chat/ProgressBar.tsx
rm frontend/src/components/chat/ConnectionStatus.tsx
rm frontend/src/components/chat/useWebSocket.ts
```

### Step 6: Clean Up Imports

Remove any unused imports from other files that referenced deleted components.

### Step 7: Test

1. Start the development server
2. Open the chat interface
3. Send a test message
4. Verify streaming works
5. Verify tool execution displays
6. Verify authentication works
7. Test cross-tab synchronization

---

## TypeScript Types

### Exported Types

```typescript
/**
 * ChatKit control object type.
*/
export interface ChatKitControl {
  createThread: () => Promise<string>;
  switchThread: (threadId: string) => void;
  sendMessage: (content: string) => void;
  currentThreadId: string | null;
  isStreaming: boolean;
  error: Error | null;
}

/**
 * ChatKit configuration options.
*/
export interface UseChatKitOptions {
  api: {
    apiURL: string;
    fetch?: (url: string, options: RequestInit) => Promise<Response>;
  };
  clientTools?: Record<string, (args: any) => Promise<any>>;
  effectHandlers?: Record<string, (action: any) => void>;
  theme?: ChatKitTheme;
  initialThreadID?: string;
}
```

---

## Browser Compatibility

### Required Browser Features

- Server-Sent Events (SSE)
- Fetch API
- ES2020+ JavaScript features
- CSS Custom Properties (variables)

### Browser Support

| Browser | Minimum Version |
|---------|-----------------|
| Chrome/Edge | 90+ |
| Firefox | 88+ |
| Safari | 14+ |

---

## Performance Considerations

1. **Bundle Size**: ChatKit React adds ~50KB gzipped to bundle
2. **SSE Connection**: Single persistent connection vs WebSocket
3. **State Management**: No React state overhead (managed by ChatKit)
4. **LocalStorage**: No longer needed (backend persistence)

---

## Accessibility

### Built-in Accessibility

- Keyboard navigation (Tab, Enter, Arrow keys)
- Screen reader support (ARIA labels)
- Focus management
- High contrast mode support

### Customization

If custom ARIA labels are needed, use the theme configuration:

```typescript
const { control } = useChatKit({
  api: { apiURL: `${API_URL}/api/chatkit`, fetch: customFetchWithAuth },
  ariaLabels: {
    chatInput: "Type your message",
    sendButton: "Send message",
    // ... more labels
  },
});
```

---

## References

- [ChatKit React Documentation](https://platform.openai.com/docs/api-reference/chatkit-react)
- [ChatKit Sessions Guide](https://platform.openai.com/docs/guides/chatkit/sessions)
