/* TaskForm modal component - create or edit task with optimistic updates.

[Task]: T038, T047-T048
[From]: specs/003-frontend-task-manager/plan.md, specs/005-ux-improvement/tasks.md

This client component:
- Modal with form fields for title, description, due date, and priority
- Submit and cancel buttons
- Zod validation with taskFormSchema
- Calls taskApi.createTask for new tasks or taskApi.updateTask for edits
- Optimistic UI updates with rollback on error
- Shows success/error toasts
- Closes on success
*/
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import type { Task, TaskFormData, TaskPriority } from "@/types/task";
import { taskFormSchema } from "@/lib/schemas/forms";
import { taskApi } from "@/lib/task-api";
import { useOptimisticAction } from "@/lib/hooks";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/Button";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task;
  mode: "create" | "edit";
  onTaskCreated?: (newTask: Task) => void;
  onTaskUpdated?: (updatedTask: Task) => void;
}

export function TaskForm({
  isOpen,
  onClose,
  task,
  mode,
  onTaskCreated,
  onTaskUpdated,
}: TaskFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<TaskFormData>({
    title: task?.title || "",
    description: task?.description || "",
    due_date: task?.due_date || null,
    priority: task?.priority || "medium",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Optimistic action hook
  const { isPending, executeOptimistic } = useOptimisticAction();

  // Reset form when opening for create mode
  useEffect(() => {
    if (isOpen && mode === "create" && !task) {
      setFormData({
        title: "",
        description: "",
        due_date: null,
        priority: "medium",
      });
      setErrors({});
    } else if (isOpen && task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        due_date: task.due_date,
        priority: task.priority,
      });
      setErrors({});
    }
  }, [isOpen, mode, task]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Validate with Zod
    try {
      taskFormSchema.parse(formData);
    } catch (error: any) {
      if (error.errors) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err: any) => {
          if (err.path.length > 0) {
            newErrors[err.path[0]] = err.message;
          }
        });
        setErrors(newErrors);
        return;
      }
    }

    if (mode === "create") {
      // Optimistic create [T048]
      await executeOptimistic({
        optimisticUpdate: () => {
          // Optimistically close modal
          // The parent will add a placeholder task
        },
        action: async () => {
          const result = await taskApi.createTask(formData);
          return result;
        },
        onSuccess: (newTask) => {
          toast.success("Task created successfully");
          onTaskCreated?.(newTask);
          handleClose();
          // Refresh to get updated list from server
          setTimeout(() => router.refresh(), 100);
        },
        onError: (error) => {
          // Rollback - keep modal open
          toast.error(error.message || "Failed to create task");
        },
        successMessage: "Task created successfully",
        errorMessage: "Failed to create task",
      });
    } else {
      // Edit mode - not optimistic, just update
      try {
        const updated = await taskApi.updateTask(task!.id, formData);
        toast.success("Task updated successfully");
        onTaskUpdated?.(updated);
        handleClose();
        router.refresh();
      } catch (error: any) {
        toast.error(error.message || "Failed to update task");
      }
    }
  };

  const handleClose = () => {
    setFormData({
      title: "",
      description: "",
      due_date: null,
      priority: "medium",
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "Create New Task" : "Edit Task"}
          </DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Add a new task to your list."
              : "Update the task details."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label
              htmlFor="title"
              className="block text-sm font-medium text-foreground mb-1.5"
            >
              Title <span className="text-destructive">*</span>
            </label>
            <input
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="Enter task title"
              className={cn(
                "w-full px-3 py-2 bg-background border border-input rounded-lg",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                "text-sm placeholder:text-muted-foreground",
                errors.title && "border-destructive focus:ring-destructive",
              )}
            />
            {errors.title && (
              <p className="mt-1 text-xs text-destructive">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-foreground mb-1.5"
            >
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              placeholder="Enter task description (optional)"
              className={cn(
                "w-full px-3 py-2 bg-background border border-input rounded-lg",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                "text-sm placeholder:text-muted-foreground resize-none",
                errors.description &&
                  "border-destructive focus:ring-destructive",
              )}
            />
            {errors.description && (
              <p className="mt-1 text-xs text-destructive">
                {errors.description}
              </p>
            )}
          </div>

          {/* Priority and Due Date - inline */}
          <div className="grid grid-cols-2 gap-4">
            {/* Priority */}
            <div>
              <label
                htmlFor="priority"
                className="block text-sm font-medium text-foreground mb-1.5"
              >
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className={cn(
                  "w-full px-3 py-2 bg-background border border-input rounded-lg",
                  "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                  "text-sm cursor-pointer hover:bg-muted/50 transition-colors appearance-none",
                  "pr-8",
                )}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            {/* Due Date */}
            <div>
              <label
                htmlFor="due_date"
                className="block text-sm font-medium text-foreground mb-1.5"
              >
                Due Date
              </label>
              <input
                id="due_date"
                name="due_date"
                type="date"
                value={formData.due_date ? formData.due_date.split("T")[0] : ""}
                onChange={(e) => {
                  const value = e.target.value;
                  setFormData((prev) => ({
                    ...prev,
                    due_date: value ? new Date(value).toISOString() : null,
                  }));
                }}
                className={cn(
                  "w-full px-3 py-2 bg-background border border-input rounded-lg",
                  "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                  "text-sm",
                  errors.due_date &&
                    "border-destructive focus:ring-destructive",
                )}
              />
              {errors.due_date && (
                <p className="mt-1 text-xs text-destructive">
                  {errors.due_date}
                </p>
              )}
            </div>
          </div>
        </form>
        <DialogFooter>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isPending}
          >
            Cancel
          </Button>
          <Button type="button" onClick={handleSubmit} disabled={isPending}>
            {isPending ? (
              <LoadingSpinner size="sm" className="border-primary-foreground" />
            ) : null}
            {isPending
              ? "Saving..."
              : mode === "create"
                ? "Create Task"
                : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
