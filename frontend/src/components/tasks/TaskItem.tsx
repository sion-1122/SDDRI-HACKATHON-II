/* TaskItem component - displays individual task.

[Task]: T037
[From]: specs/003-frontend-task-manager/plan.md

This client component:
- Displays task title, description, completion status, timestamps
- Includes edit, delete, and toggle complete buttons
- Shows strikethrough for completed tasks
*/
'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import type { Task } from '@/types/task';
import { formatRelativeTime } from '@/lib/utils';
import { taskApi } from '@/lib/task-api';
import { TaskForm } from './TaskForm';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [localTask, setLocalTask] = useState(task);

  // Toggle complete functionality (T039)
  const handleToggleComplete = async () => {
    setIsToggling(true);
    try {
      // Optimistic UI update
      setLocalTask(prev => ({ ...prev, completed: !prev.completed }));

      const updated = await taskApi.toggleComplete(task.id);
      setLocalTask(updated);
      toast.success('Task updated');
    } catch (error: any) {
      // Rollback on error
      setLocalTask(task);
      toast.error(error.message || 'Failed to update task');
    } finally {
      setIsToggling(false);
    }
  };

  // Delete task functionality (T040)
  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await taskApi.deleteTask(task.id);
      toast.success('Task deleted');
      setShowDeleteModal(false);
      // Note: The parent component will need to refresh the task list
      window.location.reload();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete task');
    } finally {
      setIsDeleting(false);
    }
  };

  // Edit functionality (T042)
  const handleEdit = () => {
    setShowEditModal(true);
  };

  return (
    <>
      <div className={`bg-white shadow rounded-lg p-6 transition-all ${
        localTask.completed ? 'opacity-60' : ''
      }`}>
        <div className="flex items-start space-x-4">
          {/* Checkbox */}
          <button
            onClick={handleToggleComplete}
            disabled={isToggling}
            className={`
              mt-1 flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center transition-colors
              ${localTask.completed
                ? 'bg-green-500 border-green-500 text-white'
                : 'border-gray-300 hover:border-green-500'
              }
              disabled:opacity-50
            `}
            aria-label={localTask.completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {isToggling ? (
              <LoadingSpinner size="sm" className="border-white" />
            ) : localTask.completed ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : null}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-medium ${
              localTask.completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}>
              {localTask.title}
            </h3>
            {localTask.description && (
              <p className={`mt-1 text-sm ${
                localTask.completed ? 'line-through text-gray-400' : 'text-gray-600'
              }`}>
                {localTask.description}
              </p>
            )}
            <p className="mt-2 text-xs text-gray-500">
              Created {formatRelativeTime(localTask.created_at)}
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleEdit}
              className="text-sm"
            >
              Edit
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowDeleteModal(true)}
              disabled={isDeleting}
              className="text-sm"
            >
              {isDeleting ? <LoadingSpinner size="sm" /> : 'Delete'}
            </Button>
          </div>
        </div>
      </div>

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Task"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </>
        }
      >
        <p className="text-gray-600">
          Are you sure you want to delete this task? This action cannot be undone.
        </p>
      </Modal>

      {/* Edit modal */}
      {showEditModal && (
        <TaskForm
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          task={localTask}
          mode="edit"
        />
      )}
    </>
  );
}
