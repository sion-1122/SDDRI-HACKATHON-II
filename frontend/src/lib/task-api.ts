/* Task API client for task CRUD operations.

[Task]: T019, T037, T038
[From]: specs/003-frontend-task-manager/contracts/api-client.ts, specs/007-intermediate-todo-features/tasks.md

This client uses the new apiClient wrapper that automatically adds JWT tokens.
*/
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskTagName,
} from '@/types/task';

import type {
  TaskListResponse,
} from '@/types/api';

import { apiClientFn } from '@/lib/api/client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Task API Client Interface
 */
export interface TaskApi {
  listTasks(params?: TaskListParams): Promise<TaskListResponse>;
  searchTasks(params: TaskSearchParams): Promise<TaskSearchResponse>;
  createTask(data: TaskCreate): Promise<Task>;
  getTask(taskId: string): Promise<Task>;
  updateTask(taskId: string, data: TaskUpdate): Promise<Task>;
  deleteTask(taskId: string): Promise<{ ok: boolean }>;
  toggleComplete(taskId: string): Promise<Task>;
  getAllTags(): Promise<TagsListResponse>; // [T038]
  updateReminder(taskId: string, reminder_offset: number | null, resetSent?: boolean): Promise<Task>; // [T058]
}

export interface TaskListParams {
  offset?: number;
  limit?: number;
  completed?: boolean;
  search?: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH';
  tags?: TaskTagName[]; // [T037]
  due_date?: 'overdue' | 'today' | 'week' | 'month'; // [T047]
  due_before?: string; // [T028] ISO 8601 datetime string
  due_after?: string; // [T028] ISO 8601 datetime string
  timezone?: string; // [T047]
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'title'; // [T056]
  sort_order?: 'asc' | 'desc'; // [T056]
}

export interface TagsListResponse {
  tags: TagInfo[];
  total: number;
}

export interface TagInfo {
  tag: string;
  count: number;
}

export interface TaskSearchParams {
  q: string;
  page?: number;
  limit?: number;
}

export interface TaskSearchResponse {
  tasks: Task[];
  total: number;
  page: number;
  limit: number;
  query: string;
}

export interface TaskListParams {
  offset?: number;
  limit?: number;
  completed?: boolean;
  search?: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH';
}

/**
 * Task API Client Implementation
 */
export class TaskApiClient implements TaskApi {
  private baseUrl: string;
  // Search result cache [T024] - up to 10 recent queries
  private searchCache: Map<string, { data: TaskSearchResponse; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_CACHE_SIZE = 10;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private getCacheKey(query: string, page: number): string {
    return `${query}:${page}`;
  }

  private cleanExpiredCache(): void {
    const now = Date.now();
    for (const [key, value] of this.searchCache.entries()) {
      if (now - value.timestamp > this.CACHE_TTL) {
        this.searchCache.delete(key);
      }
    }
  }

  private enforceCacheSizeLimit(): void {
    if (this.searchCache.size >= this.MAX_CACHE_SIZE) {
      // Remove oldest entry (first item in map iterator)
      const firstKey = this.searchCache.keys().next().value;
      if (firstKey) {
        this.searchCache.delete(firstKey);
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Use the new apiClientFn which handles JWT tokens automatically
    return apiClientFn({
      url: endpoint,
      method: (options.method as any) || 'GET',
      data: options.body ? JSON.parse(options.body as string) : undefined,
    });
  }

  /**
   * List all tasks for authenticated user
   * [Task]: T018 - Add priority parameter to list request
   * [Task]: T037 - Add tags parameter to list request
   * [Task]: T047 - Add due_date and timezone parameters to list request
   * [Task]: T056 - Add sort_by and sort_order parameters to list request
   */
  async listTasks(params?: TaskListParams): Promise<TaskListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.offset !== undefined) queryParams.append('offset', params.offset.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.completed !== undefined) queryParams.append('completed', params.completed.toString());
    if (params?.search !== undefined) queryParams.append('search', params.search);
    if (params?.priority !== undefined) queryParams.append('priority', params.priority);
    // [T037] Add tags to query parameters (repeat for multiple tags)
    if (params?.tags && params.tags.length > 0) {
      params.tags.forEach(tag => queryParams.append('tags', tag));
    }
    // [T047] Add due_date and timezone to query parameters
    if (params?.due_date) queryParams.append('due_date', params.due_date);
    // [T028] Add due_before and due_after for date range filtering
    if (params?.due_before) queryParams.append('due_before', params.due_before);
    if (params?.due_after) queryParams.append('due_after', params.due_after);
    // Get user's timezone from browser (or use provided timezone)
    const timezone = params?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    queryParams.append('timezone', timezone);
    // [T056] Add sort_by and sort_order to query parameters
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);

    const queryString = queryParams.toString();
    const endpoint = `/api/tasks${queryString ? `?${queryString}` : ''}`;

    return this.request<TaskListResponse>(endpoint);
  }

  /**
   * Search tasks by keyword [T022, T024, T028]
   * Performs full-text search with caching for recent queries
   */
  async searchTasks(params: TaskSearchParams): Promise<TaskSearchResponse> {
    const { q, page = 1, limit = 20 } = params;
    const cacheKey = this.getCacheKey(q, page);

    // Check cache first
    const cached = this.searchCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }

    // Build query parameters
    const queryParams = new URLSearchParams();
    queryParams.append('q', q);
    queryParams.append('page', page.toString());
    queryParams.append('limit', limit.toString());

    const queryString = queryParams.toString();
    const endpoint = `/api/tasks/search?${queryString}`;

    const result = this.request<TaskSearchResponse>(endpoint);

    // Cache the result
    this.cleanExpiredCache();
    this.enforceCacheSizeLimit();
    this.searchCache.set(cacheKey, {
      data: await result,
      timestamp: Date.now()
    });

    return result;
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

  /**
   * Get all tags with usage counts [T038]
   * Returns tags sorted by usage frequency
   */
  async getAllTags(): Promise<TagsListResponse> {
    return this.request<TagsListResponse>('/api/tasks/tags');
  }

  /**
   * Update reminder settings for a task [T058]
   * Updates reminder_offset and optionally resets reminder_sent flag
   */
  async updateReminder(
    taskId: string,
    reminder_offset: number | null,
    resetSent: boolean = false
  ): Promise<Task> {
    const params = new URLSearchParams()
    if (reminder_offset !== null) {
      params.append('reminder_offset', reminder_offset.toString())
    }
    if (resetSent) {
      params.append('reset_sent', 'true')
    }

    const queryString = params.toString()
    const endpoint = `/api/tasks/${taskId}/reminder${queryString ? `?${queryString}` : ''}`

    return this.request<Task>(endpoint, {
      method: 'PATCH',
    })
  }
}

// Export singleton instance
export const taskApi = new TaskApiClient();
