/** Chat page for AI-powered task management.

[Task]: T020
[From]: specs/004-ai-chatbot/tasks.md

This page provides the main chat interface where users can interact
with the AI assistant to create and manage tasks through natural language.
*/
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/auth";
import { ChatInterface } from "@/components/chat/ChatInterface";

export default function ChatPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useSession();

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
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            AI Task Assistant
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Create and manage tasks using natural language
          </p>
        </header>

        {/* [From]: T019 - ChatInterface React component */}
        <ChatInterface userId={user?.id || ""} />
      </div>
    </div>
  );
}
