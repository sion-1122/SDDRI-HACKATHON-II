/* Client-side hooks.

[Task]: T040, T046
[From]: specs/001-user-auth/plan.md, specs/005-ux-improvement/tasks.md

This file exports client-side React hooks for authentication and optimistic mutations.
*/
"use client";

import { useState, useEffect, useOptimistic, useTransition } from "react";
import { authClient } from "@/lib/auth-client";
import type { User, AuthState } from "@/types/auth";
import { toast } from "sonner";

/**
 * Hook to manage authentication state in Client Components.
 * Provides session data, loading state, and authentication methods.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { user, isAuthenticated, isLoading } = useSession();
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (!isAuthenticated) return <div>Please sign in</div>;
 *
 *   return <div>Welcome, {user.email}!</div>;
 * }
 * ```
 */
export function useSession() {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;

    const checkSession = async () => {
      try {
        const { data: session } = await authClient.getSession();

        if (mounted) {
          setState({
            user: session?.user || null,
            token: null, // Token is in httpOnly cookie, not accessible
            isAuthenticated: !!session?.user,
            isLoading: false,
            error: null,
          });
        }
      } catch (error) {
        if (mounted) {
          setState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error instanceof Error ? error.message : "Failed to check session",
          });
        }
      }
    };

    checkSession();

    return () => {
      mounted = false;
    };
  }, []);

  return state;
}

/**
 * Redirect to login page if not authenticated.
 * Useful in Client Components that require authentication.
 *
 * @example
 * ```tsx
 * function ProtectedComponent() {
 *   const { isAuthenticated } = useSession();
 *
 *   useEffect(() => {
 *     if (!isAuthenticated) {
 *       router.push('/login');
 *     }
 *   }, [isAuthenticated, router]);
 * }
 * ```
 */
export function requireAuth(isAuthenticated: boolean, router: any) {
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);
}

/**
 * useOptimisticMutation hook for optimistic UI updates with rollback.
 *
 * [Task]: T046
 * [From]: specs/005-ux-improvement/tasks.md
 *
 * This hook provides:
 * - Optimistic state updates that happen immediately
 * - Automatic rollback on error
 * - Loading state during mutation
 * - Error toast notifications
 *
 * @example
 * ```tsx
 * function TaskList() {
 *   const { tasks, mutate } = useOptimisticMutation<Task[]>({
 *     mutations: {
 *       create: async (newTask) => {
 *         const result = await taskApi.createTask(newTask);
 *         return (current) => [...current, result];
 *       },
 *       delete: async (taskId) => {
 *         await taskApi.deleteTask(taskId);
 *         return (current) => current.filter(t => t.id !== taskId);
 *       },
 *     },
 *   });
 * }
 * ```
 */
export interface OptimisticMutationConfig<T, M = Record<string, (arg: any) => Promise<any>>> {
  initialData: T;
  mutations: {
    [K in keyof M]: {
      mutate: M[K];
      optimisticUpdate: (currentData: T, arg: Parameters<M[K]>[0]) => T;
      successMessage?: string;
      errorMessage?: string;
    };
  };
}

export function useOptimisticMutation<T, M extends Record<string, (arg: any) => Promise<any>>>({
  initialData,
  mutations,
}: OptimisticMutationConfig<T, M>) {
  const [isPending, startTransition] = useTransition();
  const [data, setData] = useState(initialData);

  const [optimisticData, addOptimistic] = useOptimistic(
    data,
    (state, newState: T) => newState
  );

  const mutate = async <K extends keyof M>(
    mutationName: K,
    arg: Parameters<M[K]>[0]
  ): Promise<void> => {
    const config = mutations[mutationName];

    if (!config) {
      throw new Error(`Mutation "${String(mutationName)}" not found`);
    }

    // Apply optimistic update immediately
    startTransition(async () => {
      const optimisticValue = config.optimisticUpdate(data, arg);
      addOptimistic(optimisticValue);

      try {
        // Execute the actual mutation
        await config.mutate(arg);

        // Update real data on success
        // Re-fetch or update based on the mutation result
        // For now, the optimistic state becomes the real state
        setData(optimisticValue);

        if (config.successMessage) {
          toast.success(config.successMessage);
        }
      } catch (error) {
        // Rollback on error - revert to original data
        setData(data);

        const errorMsg = config.errorMessage || 'Operation failed. Please try again.';
        toast.error(error instanceof Error ? error.message : errorMsg);
      }
    });
  };

  return {
    data: optimisticData,
    isPending,
    mutate,
  };
}

/**
 * Simplified optimistic mutation hook for single operations.
 * Useful for individual task operations (toggle, delete, etc.).
 *
 * @example
 * ```tsx
 * const { isPending, executeOptimistic } = useOptimisticAction();
 *
 * const handleToggle = async () => {
 *   await executeOptimistic({
 *     optimisticUpdate: () => setLocalTask(prev => ({ ...prev, completed: !prev.completed })),
 *     action: () => taskApi.toggleComplete(task.id),
 *     onSuccess: () => toast.success('Task updated'),
 *     onError: () => setLocalTask(task), // rollback
 *   });
 * };
 * ```
 */
export function useOptimisticAction() {
  const [isPending, startTransition] = useTransition();

  const executeOptimistic = async <T,>({
    optimisticUpdate,
    action,
    onSuccess,
    onError,
    successMessage = 'Operation successful',
    errorMessage = 'Operation failed',
  }: {
    optimisticUpdate: () => void;
    action: () => Promise<T>;
    onSuccess?: (result: T) => void;
    onError?: (error: Error) => void;
    successMessage?: string;
    errorMessage?: string;
  }): Promise<T | null> => {
    // Apply optimistic update immediately
    optimisticUpdate();

    return new Promise((resolve) => {
      startTransition(async () => {
        try {
          const result = await action();
          if (onSuccess) onSuccess(result);
          toast.success(successMessage);
          resolve(result);
        } catch (error) {
          if (onError) onError(error as Error);
          toast.error(error instanceof Error ? error.message : errorMessage);
          resolve(null);
        }
      });
    });
  };

  return { isPending, executeOptimistic };
}
