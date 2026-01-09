// """API client for making authenticated requests to backend.

// [Task]: T064
// [From]: specs/001-user-auth/tasks.md (User Story 3)

// This client provides a wrapper around fetch that automatically:
// - Adds JWT tokens to requests
// - Handles authentication errors
// - Provides typed response handling

// Usage:
// ```typescript
// import { apiClient } from '@/lib/api/client';

// // Get tasks for authenticated user
// const tasks = await apiClient({ url: '/api/tasks' });

// // Create a new task
// const newTask = await apiClient({
//   url: '/api/tasks',
//   method: 'POST',
//   data: { title: 'My Task', description: 'Task description' }
// });
// ```
// */
import { authClient } from "@/lib/auth-client";

export interface ApiRequestConfig {
  url: string;
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  data?: any;
  requiresAuth?: boolean;
}

export const apiClient = async ({
  url,
  method = "GET",
  data,
  requiresAuth = true,
}: ApiRequestConfig) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Add JWT token if authentication is required
  if (requiresAuth) {
    try {
      const { data: tokenData } = await authClient.token();
      if (tokenData?.token) {
        headers["Authorization"] = `Bearer ${tokenData.token}`;
      }
    } catch (error) {
      console.error("Failed to get JWT token:", error);
      throw new Error("Authentication failed");
    }
  }

  const response = await fetch(`http://localhost:8000${url}`, {
    method,
    headers,
    ...(data && { body: JSON.stringify(data) }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
};

// Task service with typed methods
export const taskService = {
  getTasks: () => apiClient({ url: "/api/tasks" }),

  getTask: (id: string) =>
    apiClient({ url: `/api/tasks/${id}` }),

  createTask: (task: { title: string; description?: string }) =>
    apiClient({
      url: "/api/tasks",
      method: "POST",
      data: task,
    }),

  updateTask: (id: string, updates: any) =>
    apiClient({
      url: `/api/tasks/${id}`,
      method: "PUT",
      data: updates,
    }),

  deleteTask: (id: string) =>
    apiClient({
      url: `/api/tasks/${id}`,
      method: "DELETE",
    }),

  toggleComplete: (id: string) =>
    apiClient({
      url: `/api/tasks/${id}/complete`,
      method: "PATCH",
    }),
};
