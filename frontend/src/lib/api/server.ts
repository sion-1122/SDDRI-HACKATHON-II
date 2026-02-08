/* Server-side API client for data fetching in Server Components.

[Task]: T021-T023
[From]: specs/005-ux-improvement/tasks.md

This client:
- Works in Server Components (no window/document)
- Forwards cookies from the incoming request to backend
- Provides type-safe data fetching for initial page load
*/
import { cookies } from 'next/headers';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface ServerFetchRequestConfig {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: any;
}

/**
 * Fetch from API in Server Component with cookie forwarding
 * Next.js automatically forwards cookies when using fetch()
 */
export async function serverFetch<T>({
  url,
  method = 'GET',
  data,
}: ServerFetchRequestConfig): Promise<T> {
  const cookieStore = await cookies();

  // Build headers with forwarded cookies
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Forward cookies from the incoming request
  const allCookies = cookieStore.getAll();
  if (allCookies.length > 0) {
    headers['Cookie'] = allCookies
      .map((c: { name: string; value: string }) => `${c.name}=${c.value}`)
      .join('; ');
  }

  const response = await fetch(`${API_URL}${url}`, {
    method,
    headers,
    ...(data && { body: JSON.stringify(data) }),
    // Cache revalidation for fresh data
    cache: 'no-store',
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Return null for unauthorized - let client handle redirect
      return null as T;
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Task-specific server fetchers
export async function fetchTasks(params?: {
  offset?: number;
  limit?: number;
  completed?: boolean;
  search?: string;
}) {
  const queryParams = new URLSearchParams();
  if (params?.offset !== undefined) queryParams.append('offset', params.offset.toString());
  if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
  if (params?.completed !== undefined) queryParams.append('completed', params.completed.toString());
  if (params?.search) queryParams.append('search', params.search);

  const queryString = queryParams.toString();
  const endpoint = `/api/tasks${queryString ? `?${queryString}` : ''}`;

  return serverFetch<{
    tasks: Array<{
      id: string;
      user_id: string;
      title: string;
      description: string | null;
      due_date: string | null;
      priority: 'LOW' | 'MEDIUM' | 'HIGH';
      completed: boolean;
      created_at: string;
      updated_at: string;
    }>;
    total: number;
  }>({ url: endpoint });
}
