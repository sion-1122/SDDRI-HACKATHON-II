"use client";

import React, { useEffect, useState } from "react";
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
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

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
        priority: task?.priority || ("MEDIUM" as TaskPriority),
        tags: task?.tags || [],
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    const { isPending, executeOptimistic } = useOptimisticAction();

    useEffect(() => {
        if (isOpen && mode === "create" && !task) {
            setFormData({
                title: "",
                description: "",
                due_date: null,
                priority: "MEDIUM",
                tags: [],
            });
            setErrors({});
        } else if (isOpen && task) {
            setFormData({
                title: task.title,
                description: task.description || "",
                due_date: task.due_date || null,
                priority: task.priority as TaskPriority,
                tags: task.tags || [],
            });
            setErrors({});
        }
        // we only want to react to opening or the given task changing
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isOpen, task, mode]);

    const handleChange = (
        e: React.ChangeEvent<
            HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
        >,
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors((prev) => {
                const copy = { ...prev };
                delete copy[name];
                return copy;
            });
        }
    };

    const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const tags = value
            .split(",")
            .map((t) => t.trim())
            .filter((t) => t.length > 0);
        setFormData((prev) => ({ ...prev, tags }));
        if (errors.tags) {
            setErrors((prev) => {
                const copy = { ...prev };
                delete copy.tags;
                return copy;
            });
        }
    };

    const getTagsDisplayValue = () => formData.tags.join(", ");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});

        try {
            taskFormSchema.parse(formData);
        } catch (err: any) {
            if (err?.errors) {
                const newErrors: Record<string, string> = {};
                err.errors.forEach((zErr: any) => {
                    if (zErr.path && zErr.path.length > 0) {
                        newErrors[zErr.path[0]] = zErr.message;
                    }
                });
                setErrors(newErrors);
                return;
            }
        }

        if (mode === "create") {
            await executeOptimistic({
                optimisticUpdate: () => {
                    // parent may add placeholder task if desired
                },
                action: async () => {
                    const result = await taskApi.createTask(formData);
                    return result;
                },
                onSuccess: (newTask: Task) => {
                    toast.success("Task created successfully");
                    onTaskCreated?.(newTask);
                    handleClose();
                    setTimeout(() => router.refresh(), 150);
                },
                onError: (error: any) => {
                    toast.error(error?.message || "Failed to create task");
                },
                successMessage: "Task created successfully",
                errorMessage: "Failed to create task",
            });
        } else {
            try {
                const updated = await taskApi.updateTask(task!.id, formData);
                toast.success("Task updated successfully");
                onTaskUpdated?.(updated);
                handleClose();
                router.refresh();
            } catch (error: any) {
                toast.error(error?.message || "Failed to update task");
            }
        }
    };

    const handleClose = () => {
        setFormData({
            title: "",
            description: "",
            due_date: null,
            priority: "MEDIUM",
            tags: [],
        });
        setErrors({});
        onClose();
    };

    return (
        <Dialog
            open={isOpen}
            onOpenChange={(open) => {
                if (!open) handleClose();
            }}
        >
            <DialogContent className="w-full max-w-[95vw] sm:max-w-lg md:max-w-2xl lg:max-w-3xl xl:max-w-4xl mx-auto p-6 overflow-auto max-h-[90vh]">
                <DialogHeader>
                    <DialogTitle>
                        {mode === "create" ? "Create New Task df" : "Edit Task"}
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
                        <Label htmlFor="title">
                            Title <span className="text-destructive">*</span>
                        </Label>
                        <Input
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            required
                            placeholder="Enter task title"
                            className={cn(
                                errors.title &&
                                    "border-destructive focus:ring-destructive",
                            )}
                        />
                        {errors.title && (
                            <p className="mt-1 text-xs text-destructive">
                                {errors.title}
                            </p>
                        )}
                    </div>

                    {/* Description */}
                    <div>
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows={3}
                            placeholder="Enter task description (optional)"
                            className={cn(
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

                    {/* Tags */}
                    <div>
                        <Label htmlFor="tags">Tags</Label>
                        <Input
                            id="tags"
                            name="tags"
                            type="text"
                            value={getTagsDisplayValue()}
                            onChange={handleTagsChange}
                            placeholder="Enter tags separated by commas (e.g., work, urgent)"
                            className={cn(
                                errors.tags &&
                                    "border-destructive focus:ring-destructive",
                            )}
                        />
                        {errors.tags && (
                            <p className="mt-1 text-xs text-destructive">
                                {errors.tags}
                            </p>
                        )}
                    </div>

                    {/* Priority and Due Date - responsive */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="priority">Priority</Label>
                            <Select
                                value={formData.priority}
                                onValueChange={(value) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        priority: value as TaskPriority,
                                    }))
                                }
                            >
                                <SelectTrigger id="priority" className="w-full">
                                    <SelectValue placeholder="Select priority" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="LOW">Low</SelectItem>
                                    <SelectItem value="MEDIUM">
                                        Medium
                                    </SelectItem>
                                    <SelectItem value="HIGH">High</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <Label htmlFor="due_date">Due Date</Label>
                            <Input
                                id="due_date"
                                name="due_date"
                                type="date"
                                value={
                                    formData.due_date
                                        ? formData.due_date.split("T")[0]
                                        : ""
                                }
                                onChange={(e) => {
                                    const value = e.target.value;
                                    setFormData((prev) => ({
                                        ...prev,
                                        due_date: value
                                            ? new Date(value).toISOString()
                                            : null,
                                    }));
                                }}
                                className={cn(
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

                    <DialogFooter className="px-0">
                        <div className="w-full flex justify-end gap-2">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={handleClose}
                                disabled={isPending}
                            >
                                Cancel
                            </Button>

                            <Button type="submit" disabled={isPending}>
                                {isPending ? (
                                    <div className="flex items-center gap-2">
                                        <LoadingSpinner
                                            size="sm"
                                            className="border-primary-foreground"
                                        />
                                        <span>Saving...</span>
                                    </div>
                                ) : mode === "create" ? (
                                    "Create Task"
                                ) : (
                                    "Save Changes"
                                )}
                            </Button>
                        </div>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
