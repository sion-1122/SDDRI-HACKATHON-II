/* TaskItem component - minimalistic Notion-inspired task card.

[Task]: T028-T031, T049-T052, T073
[From]: specs/005-ux-improvement/tasks.md

This client component:
- Displays task title, description, completion status, timestamps
- Includes edit, delete, and toggle complete buttons
- Shows priority badge and due date with urgency indicators
- Notion-inspired minimalistic design
- Urgency-based styling with colored border-left accent
- Optimistic UI updates with rollback on error
*/
"use client";

import { useState } from "react";
import { toast } from "sonner";
import type { Task } from "@/types/task";
import { formatRelativeDate } from "@/lib/utils";
import { taskApi } from "@/lib/task-api";
import { TaskForm } from "./TaskForm";
import { PriorityBadge } from "./PriorityBadge";
import { TagBadgeGroup } from "./TagBadge";
import { DueDateBadge } from "./DueDateBadge";
import { Button } from "@/components/ui/Button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { cn } from "@/lib/utils";
import { useOptimisticAction } from "@/lib/hooks";
import { Check } from "lucide-react";

interface TaskItemProps {
  task: Task;
  onDelete?: (taskId: string) => void;
}

// Urgency-based border accent colors - subtle Notion-style
const urgencyBorderColors = {
  overdue: "border-l-urgency-overdue",
  "due-today": "border-l-urgency-due-today",
  "due-soon": "border-l-urgency-due-soon",
  "due-later": "border-l-urgency-due-later",
  none: "",
};

export function TaskItem({ task, onDelete }: TaskItemProps) {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [localTask, setLocalTask] = useState(task);

  // Use optimistic action hook for instant UI updates with rollback
  const { isPending: isToggling, executeOptimistic } = useOptimisticAction();
  const { isPending: isDeleting, executeOptimistic: executeDelete } =
    useOptimisticAction();

  const urgencyBorderColor = urgencyBorderColors[localTask.urgency || "none"];

  // Toggle complete functionality with optimistic update [T049]
  const handleToggleComplete = async () => {
    await executeOptimistic({
      optimisticUpdate: () => {
        setLocalTask((prev) => ({ ...prev, completed: !prev.completed }));
      },
      action: () => taskApi.toggleComplete(task.id),
      onSuccess: (updated) => {
        setLocalTask(updated);
      },
      onError: () => {
        setLocalTask(task);
      },
      successMessage: localTask.completed
        ? "Task marked as active"
        : "Task completed",
      errorMessage: "Failed to update task",
    });
  };

  // Delete task functionality with optimistic update [T050]
  const handleDelete = async () => {
    await executeDelete({
      optimisticUpdate: () => {
        setShowDeleteModal(false);
      },
      action: () => taskApi.deleteTask(task.id),
      onSuccess: () => {
        onDelete?.(task.id);
        setTimeout(() => window.location.reload(), 100);
      },
      onError: () => {
        setShowDeleteModal(true);
      },
      successMessage: "Task deleted",
      errorMessage: "Failed to delete task",
    });
  };

  const handleTaskUpdated = (updated: Task) => {
    setLocalTask(updated);
  };

  return (
    <>
      <div
        className={cn(
          // Notion-inspired card with subtle styling [T073]
          "group relative bg-card border border-border rounded-xl p-4 sm:p-5",
          "transition-all duration-200",
          "hover:shadow-md hover:border-muted-foreground/20",
          // Urgency border accent
          "border-l-4",
          urgencyBorderColor,
          // Completed state
          localTask.completed && "opacity-60",
        )}
      >
        <div className="flex items-start gap-3 sm:gap-4">
          {/* Checkbox - Notion-style clean checkbox */}
          <button
            onClick={handleToggleComplete}
            disabled={isToggling}
            className={cn(
              "mt-0.5 flex-shrink-0 w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all duration-200",
              localTask.completed
                ? "bg-primary border-primary text-primary-foreground"
                : "border-muted-foreground/40 hover:border-primary hover:bg-primary/5",
              "disabled:opacity-50 disabled:cursor-not-allowed",
            )}
            aria-label={
              localTask.completed ? "Mark as incomplete" : "Mark as complete"
            }
          >
            {isToggling ? (
              <LoadingSpinner size="xs" className="border-primary-foreground" />
            ) : localTask.completed ? (
              <Check className="w-3.5 h-3.5" strokeWidth={3} />
            ) : null}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3
              className={cn(
                "text-base font-medium text-foreground leading-snug",
                "transition-colors duration-200",
                localTask.completed && "line-through text-muted-foreground",
              )}
            >
              {localTask.title}
            </h3>

            {/* Description */}
            {localTask.description && (
              <p
                className={cn(
                  "mt-1 text-sm text-muted-foreground line-clamp-2 leading-relaxed",
                  "transition-colors duration-200",
                  localTask.completed &&
                    "line-through text-muted-foreground/60",
                )}
              >
                {localTask.description}
              </p>
            )}

            {/* Meta info: badges and date - subtle row */}
            <div className="flex flex-wrap items-center gap-2 mt-3">
              <PriorityBadge priority={localTask.priority} />
              <TagBadgeGroup tags={localTask.tags || []} />
              <DueDateBadge
                dueDate={localTask.due_date}
                urgency={localTask.urgency}
              />
              <span className="text-xs text-muted-foreground/70">
                {formatRelativeDate(localTask.created_at)}
              </span>
            </div>
          </div>

          {/* Action buttons - always visible on mobile, hover on desktop */}
          <div className="flex items-center gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200">
            <button
              onClick={() => setShowEditModal(true)}
              className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Edit task"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2h3l-1-6H6l1-1z"
                />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteModal(true)}
              disabled={isDeleting}
              className="p-2 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Delete task"
            >
              {isDeleting ? (
                <LoadingSpinner size="xs" />
              ) : (
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 011-1h3a1 1 0 011 1v3a4 4 0 004 4h2a2 2 0 002-2v-4a1 1 0 011-1h4a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2V6a2 2 0 012-2h2a2 2 0 012 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2z"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Delete confirmation alert */}
      <AlertDialog
        open={showDeleteModal}
        onOpenChange={(open) => !open && setShowDeleteModal(false)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Task</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{localTask.title}&quot;?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel asChild>
              <Button variant="secondary">Cancel</Button>
            </AlertDialogCancel>
            <AlertDialogAction asChild>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </Button>
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Edit modal */}
      {showEditModal && (
        <TaskForm
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          task={localTask}
          mode="edit"
          onTaskUpdated={handleTaskUpdated}
        />
      )}
    </>
  );
}
