// """BetterAuth client for frontend authentication.

// [Task]: T020
// [From]: specs/001-user-auth/quickstart.md

// This client provides methods for user authentication:
// - signIn.email() - Login with email and password
// - signUp.email() - Register with email and password
// - signOut() - Logout current user
// - getSession() - Get current user session
// - token() - Get JWT token for API requests
// */
"use client";

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL
    ? `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth`
    : "http://localhost:3000/api/auth",
});
