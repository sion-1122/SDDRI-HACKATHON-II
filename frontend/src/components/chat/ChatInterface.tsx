/** ChatInterface component for AI-powered task management.

[Task]: T019, T032
[From]: specs/004-ai-chatbot/tasks.md

This component provides a conversational interface for task management
with persistent conversation state across page refreshes.
*/
"use client";

import { useState, useRef, useEffect } from "react";
import { ChatInterface as OpenAIChatInterface } from "@openai/chatkit-react";
import type { Message } from "@openai/chatkit-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Storage key for conversation persistence
const CONVERSATION_STORAGE_KEY = (userId: string) => `chat_conversation_${userId}`;

interface ChatInterfaceProps {
  userId: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
    <div className="flex flex-col h-[600px] border rounded-lg shadow-sm bg-white dark:bg-gray-800 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Chat
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Ask me to create, list, or manage your tasks
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearConversation}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white border rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Start a conversation to manage your tasks
              </p>
              <div className="space-y-2 text-sm text-gray-400 dark:text-gray-500">
                <p>Try: "Create a task to buy groceries"</p>
                <p>Try: "Show me my tasks"</p>
                <p>Try: "Mark the first task as complete"</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.currentTarget);
          const input = formData.get("message") as string;
          if (input) {
            handleSendMessage(input);
            e.currentTarget.reset();
          }
        }}
        className="p-4 border-t dark:border-gray-700"
      >
        <div className="flex space-x-2">
          <input
            type="text"
            name="message"
            placeholder="Type your message..."
            disabled={isLoading}
            maxLength={10000}
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
