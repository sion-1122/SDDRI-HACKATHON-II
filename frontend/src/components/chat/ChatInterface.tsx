/** ChatInterface component for AI-powered task management.

[Task]: T019, T032, T061, T062, T078
[From]: specs/004-ai-chatbot/tasks.md

This component provides a conversational interface for task management
with persistent conversation state across page refreshes.

Enhanced with real-time WebSocket progress streaming for AI tool execution.
*/
"use client";

import { useState, useEffect } from "react";
import { MessageList, type ChatMessage } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { useWebSocket, type ToolProgressEvent } from "./useWebSocket";
import { ProgressBar } from "./ProgressBar";
import { ConnectionStatus } from "./ConnectionStatus";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Storage key for conversation persistence
const CONVERSATION_STORAGE_KEY = (userId: string) => `chat_conversation_${userId}`;

interface ChatInterfaceProps {
  userId: string;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  tasks: Array<{
    id: string;
    title: string;
    description?: string;
    due_date?: string;
    priority?: string;
    completed: boolean;
  }>;
}

interface StoredConversation {
  conversationId: string | null;
  messages: ChatMessage[];
}

export function ChatInterface({ userId }: ChatInterfaceProps) {
  // Load conversation state from localStorage on mount
  // [From]: T032 - Store conversation_id in frontend chat state
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const stored = localStorage.getItem(CONVERSATION_STORAGE_KEY(userId));
      if (stored) {
        const parsed: StoredConversation = JSON.parse(stored);
        return parsed.messages || [];
      }
    } catch {
      // Ignore storage errors
    }
    return [];
  });

  const [conversationId, setConversationId] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const stored = localStorage.getItem(CONVERSATION_STORAGE_KEY(userId));
      if (stored) {
        const parsed: StoredConversation = JSON.parse(stored);
        return parsed.conversationId || null;
      }
    } catch {
      // Ignore storage errors
    }
    return null;
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection state
  // [From]: T078 - Integrate WebSocket and progress components
  const [progressEvents, setProgressEvents] = useState<ToolProgressEvent[]>([]);

  /**
   * Handle WebSocket events.
   * [From]: specs/004-ai-chatbot/research.md - Section 5
   */
  const handleWebSocketEvent = (event: ToolProgressEvent) => {
    setProgressEvents((prev) => {
      // Filter out previous agent_thinking when a new event comes in
      const filtered = prev.filter(
        (e) => e.event_type !== "agent_thinking" && e.event_type !== "agent_done"
      );
      return [...filtered, event];
    });

    // Clear progress events when agent is done
    if (event.event_type === "agent_done") {
      setTimeout(() => {
        setProgressEvents([]);
      }, 3000);
    }
  };

  // Initialize WebSocket connection
  // [From]: T078 - Integrate useWebSocket hook
  const { isConnected, isConnecting } = useWebSocket(userId, {
    onEvent: handleWebSocketEvent,
    onConnectionChange: (connected) => {
      console.log("WebSocket connection changed:", connected);
    },
    onError: (error) => {
      console.warn("WebSocket error:", error);
    },
  });

  // Persist conversation state to localStorage whenever it changes
  // [From]: T032 - Store conversation_id in frontend chat state
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const stored: StoredConversation = {
        conversationId,
        messages,
      };
      localStorage.setItem(CONVERSATION_STORAGE_KEY(userId), JSON.stringify(stored));
    } catch {
      // Ignore storage errors (e.g., quota exceeded, private browsing)
    }
  }, [conversationId, messages, userId]);

  /**
   * Send a message to the AI chatbot.
   * [From]: specs/004-ai-chatbot/plan.md - Chat API Contract
   */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: "user",
      content: content.trim(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Clear previous progress events
    setProgressEvents([]);

    try {
      // Call backend chat API
      // [From]: T015 - POST /api/{user_id}/chat
      const response = await fetch(`${API_URL}/api/${userId}/chat`, {
        method: "POST",
        credentials: "include", // Include httpOnly cookies for JWT
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Unknown error occurred",
        }));

        // Handle specific error types
        // [From]: T021 - Rate limiting (429)
        if (response.status === 429) {
          throw new Error(
            `Daily message limit reached. Resets at ${errorData.resets_at || "midnight UTC"}`
          );
        }

        // [From]: T022 - AI service errors (503, 504)
        if (response.status === 503 || response.status === 504) {
          throw new Error(
            errorData.detail?.message ||
            errorData.detail ||
            "AI service temporarily unavailable"
          );
        }

        throw new Error(errorData.detail || "Failed to send message");
      }

      const data: ChatResponse = await response.json();

      // Add AI response to messages
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Update conversation ID for next request
      // [From]: T016 - Conversation persistence
      setConversationId(data.conversation_id);

      // TODO: Handle task references (data.tasks)
      // This will be used in future enhancements to show task creation confirmations
      if (data.tasks && data.tasks.length > 0) {
        console.log("Tasks created/modified:", data.tasks);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);

      // Remove the user message if the request failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear conversation history.
   * [From]: specs/004-ai-chatbot/spec.md - US6 (Persistent Conversations)
   * [From]: T032 - Store conversation_id in frontend chat state
   */
  const handleClearConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setProgressEvents([]);
    // Clear persisted state
    if (typeof window !== "undefined") {
      try {
        localStorage.removeItem(CONVERSATION_STORAGE_KEY(userId));
      } catch {
        // Ignore storage errors
      }
    }
  };

  return (
    <div className="flex flex-col h-full w-full border rounded-lg shadow-sm bg-card">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b shrink-0">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Chat
          </h2>
          <p className="text-sm text-muted-foreground">
            Ask me to create, list, or manage your tasks
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearConversation}
            className="px-3 py-1 text-sm text-muted-foreground hover:text-foreground border rounded hover:bg-muted transition-colors"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Connection Status */}
      {/* [From]: T078 - Integrate ConnectionStatus component */}
      <ConnectionStatus isConnected={isConnected} isConnecting={isConnecting} />

      {/* Progress Bar for Real-Time Tool Updates */}
      {/* [From]: T078 - Integrate ProgressBar component */}
      <ProgressBar events={progressEvents} />

      {/* Message List Component */}
      {/* [From]: T061 - Add MessageList React component */}
      <MessageList messages={messages} isLoading={isLoading} error={error} />

      {/* Message Input Component */}
      {/* [From]: T062 - Add MessageInput React component */}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        maxLength={10000}
        placeholder="Type your message..."
      />
    </div>
  );
}
