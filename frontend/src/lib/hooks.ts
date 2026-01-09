/* Client-side authentication hooks.

[Task]: T040
[From]: specs/001-user-auth/plan.md

This file exports client-side React hooks for authentication.
*/
"use client";

import { useState, useEffect } from "react";
import { authClient } from "@/lib/auth-client";
import type { User, AuthState } from "@/types/auth";

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
