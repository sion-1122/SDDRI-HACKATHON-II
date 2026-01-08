"""BetterAuth API route handler for Next.js 16.

[Task]: T019
[From]: specs/001-user-auth/quickstart.md

This route handles all BetterAuth authentication endpoints:
- POST /api/auth/sign-up - User registration
- POST /api/auth/sign-in - User login
- POST /api/auth/sign-out - User logout
- GET /api/auth/session - Get current session
*/
import { auth } from "@/lib/auth";

export const { GET, POST } = auth.handler;
