/* Authentication utilities and session management.

[Task]: T040
[From]: specs/001-user-auth/plan.md
*/
"use client";

import { useState, useEffect } from "react";
import { apiClient } from "./api-client";
import type { User, AuthState } from "@/types/auth";

/**
 * Get current session on the server side.
 * For use in Server Components or Server Actions.
 *
 * NOTE: This won't work in Client Components during SSR.
 * Use useSession hook for client-side session management.
 */
export async function getServerSession() {
  try {
    const session = await apiClient.getSession();
    return session;
  } catch (error) {
    console.error("Failed to get server session:", error);
    return {
      authenticated: false,
      user: null,
      expires_at: null
    };
  }
}

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
        const session = await apiClient.getSession();

        if (mounted) {
          setState({
            user: session.user,
            token: null, // Token is in httpOnly cookie, not accessible
            isAuthenticated: session.authenticated,
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
