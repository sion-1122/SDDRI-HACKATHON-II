/* Task API client for task CRUD operations.

[Task]: T019
[From]: specs/003-frontend-task-manager/contracts/api-client.ts

This client uses the new apiClient wrapper that automatically adds JWT tokens.
*/
import type {
  Task,
  TaskCreate,
  TaskUpdate,
} from '@/types/task';

import type {
  TaskListResponse,
} from '@/types/api';

import { apiClient } from '@/lib/api/client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Task API Client Interface
 */
export interface TaskApi {
  listTasks(params?: TaskListParams): Promise<TaskListResponse>;
  createTask(data: TaskCreate): Promise<Task>;
  getTask(taskId: string): Promise<Task>;
  updateTask(taskId: string, data: TaskUpdate): Promise<Task>;
  deleteTask(taskId: string): Promise<{ ok: boolean }>;
  toggleComplete(taskId: string): Promise<Task>;
}

export interface TaskListParams {
  offset?: number;
  limit?: number;
  completed?: boolean;
  search?: string;
}

/**
 * Task API Client Implementation
 */
export class TaskApiClient implements TaskApi {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Use the new apiClient which handles JWT tokens automatically
    return apiClient({
      url: endpoint,
      method: (options.method as any) || 'GET',
      data: options.body ? JSON.parse(options.body as string) : undefined,
    });
  }

  /**
   * List all tasks for authenticated user
   */
  async listTasks(params?: TaskListParams): Promise<TaskListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.offset !== undefined) queryParams.append('offset', params.offset.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.completed !== undefined) queryParams.append('completed', params.completed.toString());
    if (params?.search !== undefined) queryParams.append('search', params.search);

    const queryString = queryParams.toString();
    const endpoint = `/api/tasks${queryString ? `?${queryString}` : ''}`;

    return this.request<TaskListResponse>(endpoint);
  }

  /**
   * Create a new task
   */
  async createTask(data: TaskCreate): Promise<Task> {
    return this.request<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get a specific task
   */
  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`/api/tasks/${taskId}`);
  }

  /**
   * Update a task
   */
  async updateTask(taskId: string, data: TaskUpdate): Promise<Task> {
    return this.request<Task>(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: string): Promise<{ ok: boolean }> {
    return this.request<{ ok: boolean }>(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Toggle task completion status
   */
  async toggleComplete(taskId: string): Promise<Task> {
    return this.request<Task>(
      `/api/tasks/${taskId}/complete`,
      {
        method: 'PATCH',
      }
    );
  }
}

// Export singleton instance
export const taskApi = new TaskApiClient();
