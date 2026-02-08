/* Custom authentication client for FastAPI backend.

[Task]: T020
[From]: specs/001-user-auth/quickstart.md

This client provides methods for user authentication:
- signIn.email() - Login with email and password
- signUp.email() - Register with email and password
- signOut() - Logout current user
- getSession() - Get current user session

Note: Uses Next.js API proxy route to ensure cookies are set correctly
on the frontend domain, especially in production environments.
*/
"use client";

// Use Next.js proxy route instead of direct backend URL
// This ensures cookies are set on the frontend domain
const API_URL = typeof window !== 'undefined' 
  ? window.location.origin 
  : process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

interface SessionResponse {
  authenticated: boolean;
  user?: User;
  expires_at?: string;
}

interface AuthResponse {
  message: string;
  user?: User;
  token?: string;
}

interface SignInCredentials {
  email: string;
  password: string;
}

interface SignUpCredentials {
  email: string;
  password: string;
}

/**
 * Custom auth client that works with FastAPI backend
 * Replaces BetterAuth client to match our FastAPI endpoints
 */
export const authClient = {
  /**
   * Sign in with email and password
   */
  signIn: {
    email: async (credentials: SignInCredentials) => {
      const response = await fetch("/api/auth/sign-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Sign in failed");
      }

      const data: AuthResponse = await response.json();

      return {
        data: {
          user: data.user,
          token: data.token,
        },
        error: null,
      };
    },
  },

  /**
   * Sign up with email and password
   */
  signUp: {
    email: async (credentials: SignUpCredentials) => {
      const response = await fetch("/api/auth/sign-up", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Sign up failed");
      }

      const data: AuthResponse = await response.json();

      return {
        data: {
          user: data.user,
          token: data.token,
        },
        error: null,
      };
    },
  },

  /**
   * Sign out current user
   */
  signOut: async () => {
    const response = await fetch("/api/auth/sign-out", {
      method: "POST",
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Sign out failed");
    }

    return { data: null, error: null };
  },

  /**
   * Get current session
   */
  getSession: async () => {
    const response = await fetch("/api/auth/session", {
      credentials: "include",
    });

    if (!response.ok) {
      return {
        data: null,
        error: new Error("Not authenticated"),
      };
    }

    const session: SessionResponse = await response.json();

    if (!session.authenticated || !session.user) {
      return {
        data: null,
        error: new Error("Not authenticated"),
      };
    }

    return {
      data: {
        user: session.user,
        session: {
          expiresAt: session.expires_at,
        },
      },
      error: null,
    };
  },

  /**
   * Get JWT token (from cookie or localStorage)
   */
  token: async () => {
    // Try to get token from localStorage first
    if (typeof window !== "undefined") {
      const localToken = localStorage.getItem("auth_token");
      if (localToken) {
        return {
          data: { token: localToken },
          error: null,
        };
      }
    }

    // If no token in localStorage, return null
    // (token is in httpOnly cookie managed by backend)
    return {
      data: { token: null },
      error: null,
    };
  },
};