/* TaskForm modal component - create or edit task.

[Task]: T038
[From]: specs/003-frontend-task-manager/plan.md

This client component:
- Modal with Input and Textarea
- Submit and cancel buttons
- Zod validation with taskFormSchema
- Calls taskApi.createTask for new tasks or taskApi.updateTask for edits
- Shows success/error toasts
- Closes on success
*/
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import type { Task, TaskFormData } from '@/types/task';
import { taskFormSchema } from '@/lib/schemas/forms';
import { taskApi } from '@/lib/task-api';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task;
  mode: 'create' | 'edit';
}

export function TaskForm({ isOpen, onClose, task, mode }: TaskFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<TaskFormData>({
    title: task?.title || '',
    description: task?.description || '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
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
        setIsSubmitting(false);
        return;
      }
    }

    try {
      if (mode === 'create') {
        await taskApi.createTask(formData);
        toast.success('Task created successfully');
      } else {
        await taskApi.updateTask(task!.id, formData);
        toast.success('Task updated successfully');
      }

      // Refresh the page to show updated tasks
      router.refresh();
      onClose();
    } catch (error: any) {
      toast.error(error.message || `Failed to ${mode} task`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setFormData({ title: '', description: '' });
    setErrors({});
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={mode === 'create' ? 'Create New Task' : 'Edit Task'}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? <LoadingSpinner size="sm" className="border-white" /> : null}
            {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create Task' : 'Save Changes'}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          error={errors.title}
          required
          placeholder="Enter task title"
        />

        <Textarea
          label="Description"
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          error={errors.description}
          rows={4}
          placeholder="Enter task description (optional)"
        />
      </form>
    </Modal>
  );
}
