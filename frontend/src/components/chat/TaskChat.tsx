/**
 * Simple chat interface component for task management with AI.
 *
 * This is a fallback implementation that uses Server-Sent Events (SSE)
 * directly without the ChatKit React library.
 */
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, X } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface ToolCall {
  tool: string;
  status: "starting" | "complete" | "error";
  message?: string;
}

interface TaskChatProps {
  userId: string;
  initialThreadId?: string;
  className?: string;
}

export function TaskChat({ userId, initialThreadId, className = "" }: TaskChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTool, setCurrentTool] = useState<ToolCall | null>(null);
  const [threadId, setThreadId] = useState<string | undefined>(initialThreadId);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Use Next.js proxy route instead of direct backend URL
  // This ensures cookies are sent correctly in production
  const API_URL = typeof window !== 'undefined' 
    ? window.location.origin 
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessageText = input.trim();
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userMessageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);
    setCurrentTool(null);

    console.log("[TaskChat] Sending message:", userMessageText);

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      // Use Next.js proxy route to ensure cookies are sent correctly
      const response = await fetch("/api/chatkit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          event: "conversation_item_created",
          conversation_id: threadId || null,
          item: {
            type: "message",
            role: "user",
            content: [{ type: "text", text: input.trim() }],
          },
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || "Failed to connect to chat service");
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let assistantMessage = "";
      let assistantMessageId = Date.now().toString() + "_assistant";

      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          timestamp: new Date(),
          isStreaming: true,
        },
      ]);

      setIsConnected(true);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.trim() || !line.startsWith("data: ")) continue;

          const data = line.slice(6); // Remove "data: " prefix
          console.log("[TaskChat] SSE data:", data);  // Debug log
          try {
            const event = JSON.parse(data);
            console.log("[TaskChat] Parsed event:", event);  // Debug log

            if (event.type === "text" || event.event === "message_delta") {
              const textContent = event.text || "";
              assistantMessage += textContent;
              console.log("[TaskChat] Assistant response so far:", assistantMessage);  // Debug log
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: assistantMessage }
                    : msg
                )
              );
            } else if (event.event === "tool_call_created" || event.tool) {
              setCurrentTool({
                tool: event.tool || event.function?.name || "tool",
                status: "starting",
                message: event.message || "Executing...",
              });
            } else if (event.event === "tool_call_done" || event.status === "complete") {
              setCurrentTool({
                tool: currentTool?.tool || "tool",
                status: "complete",
                message: "Done",
              });
              setTimeout(() => setCurrentTool(null), 1000);
            } else if (event.event === "message_done") {
              // Message complete, save thread ID
              if (event.thread_id) {
                setThreadId(event.thread_id);
              }
            } else if (event.event === "error") {
              throw new Error(event.message || event.detail || "Unknown error");
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", e, data);
          }
        }
      }

      // Mark streaming as complete
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, isStreaming: false }
            : msg
        )
      );

    } catch (err: any) {
      if (err.name === "AbortError") {
        console.log("Request aborted");
      } else {
        console.error("Chat error:", err);
        setError(err.message || "Failed to send message");
        setMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg?.isStreaming) {
            return prev.slice(0, -1);
          }
          return prev;
        });
      }
    } finally {
      setIsLoading(false);
      setIsConnected(false);
      abortControllerRef.current = null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`flex flex-col h-full w-full bg-background ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-card">
        <div>
          <h3 className="font-semibold text-foreground">AI Task Assistant</h3>
          <p className="text-xs text-muted-foreground">
            {isConnected ? "Connected" : "Ready"} | Thread: {threadId ? threadId.slice(0, 8) + "..." : "New"}
          </p>
        </div>
        {error && (
          <div className="text-xs text-red-500 max-w-xs truncate" title={error}>
            {error}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <p className="mb-2">👋 Hello! I'm your AI task assistant.</p>
            <p className="text-sm">Try asking me to:</p>
            <ul className="text-sm text-left inline-block mt-2 space-y-1">
              <li>• "Create a task called Buy groceries"</li>
              <li>• "List all my tasks"</li>
              <li>• "Mark task #1 as complete"</li>
            </ul>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap break-words">
                  {message.content}
                  {message.isStreaming && <span className="animate-pulse">▊</span>}
                </p>
                <p className="text-xs opacity-50 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {/* Tool execution indicator */}
        {currentTool && (
          <div className="flex justify-start">
            <div className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg px-4 py-2 flex items-center gap-2">
              <div className="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full" />
              <span className="text-sm">
                <strong>{currentTool.tool}</strong>: {currentTool.message}
              </span>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && !currentTool && (
          <div className="flex justify-start">
            <div className="bg-muted text-muted-foreground rounded-lg px-4 py-2">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-card p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to create, list, or manage your tasks..."
            disabled={isLoading}
            className="flex-1 min-h-[60px] max-h-[200px] px-4 py-3 rounded-lg border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            rows={1}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

export default TaskChat;
