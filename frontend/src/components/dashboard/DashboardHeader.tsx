/* DashboardHeader component - header with user info and actions.

[Task]: T072
[From]: specs/005-ux-improvement/tasks.md

This client component:
- Displays page title and user info
- Create task and logout buttons
- Notion-inspired clean, minimalistic design
- Generous whitespace
*/
"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { TaskForm } from "@/components/tasks/TaskForm";
import { Button } from "@/components/ui/Button";
import { useSession } from "@/lib/hooks";
import { useRouter } from "next/navigation";

export function DashboardHeader() {
  const { user } = useSession();
  const router = useRouter();
  const [showCreateModal, setShowCreateModal] = useState(false);

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/sign-out", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout failed:", err);
    }
    router.push("/login");
  };

  // Extract email/username for display
  const displayName = user?.email || "User";

  return (
    <>
      {/* Notion-inspired header with clean spacing */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* Left: Title and greeting */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3">
              <h1 className="text-xl sm:text-2xl font-semibold text-foreground tracking-tight">
                Tasks
              </h1>
              <div className="h-4 w-px bg-border hidden sm:block" />
              <p className="text-sm text-muted-foreground">{displayName}</p>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2 sm:gap-3">
              <Button
                onClick={() => setShowCreateModal(true)}
                className="gap-2"
                size="sm"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">New Task</span>
                <span className="sm:hidden">New</span>
              </Button>
              <button
                onClick={handleLogout}
                className="text-sm text-muted-foreground hover:text-foreground px-3 py-2 rounded-md hover:bg-muted transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Create Task Modal */}
      {showCreateModal && (
        <TaskForm
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          mode="create"
        />
      )}
    </>
  );
}
