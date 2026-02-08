/** Chat page for AI-powered task management.

[Task]: T020, T024
[From]: specs/004-ai-chatbot/tasks.md
[From]: specs/010-chatkit-migration/tasks.md - T024

This page provides the main chat interface where users can interact
with the AI assistant to create and manage tasks through natural language.

MIGRATION (Phase 010-chatkit-migration):
- Replaced ChatInterface with ChatKit-powered TaskChat component
- SSE streaming replaces WebSocket for real-time updates
- Custom authentication via httpOnly cookies
- Tool execution visualization built into ChatKit UI
*/
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth";
import { TaskChat } from "@/components/chat/TaskChat";

export default function ChatPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useSession();
  const [currentThreadId, setCurrentThreadId] = useState<string>();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Show nothing while redirecting
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header with title */}
      <header className="flex items-center justify-between px-6 py-4 border-b bg-card">
        <div>
          <h1 className="text-xl font-semibold text-foreground">
            AI Task Assistant
          </h1>
          <p className="text-sm text-muted-foreground">
            Create and manage tasks using natural language
          </p>
        </div>
      </header>

      {/* ChatKit TaskChat component */}
      {/* [From]: T024 - Update dashboard to use TaskChat instead of ChatInterface */}
      <main className="flex-1 overflow-hidden p-4">
        <TaskChat
          userId={user?.id || ""}
          initialThreadId={currentThreadId}
          className="h-full w-full max-w-5xl mx-auto"
        />
      </main>
    </div>
  );
}
