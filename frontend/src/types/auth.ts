/* Authentication types for FastAPI backend integration.

[Task]: T013
[From]: specs/001-user-auth/data-model.md
*/

// User types
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

// Auth requests
export interface SignUpRequest {
  email: string;
  password: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

// Auth responses
export interface SignUpResponse {
  success: boolean;
  message: string;
  user: User;
}

export interface SignInResponse {
  success: boolean;
  token: string;
  user: User;
  expires_at: string;
}

export interface SessionResponse {
  authenticated: boolean;
  user: User | null;
  expires_at: string | null;
}

export interface SignOutResponse {
  success: boolean;
  message: string;
}

// Error types
export interface ApiError {
  detail: string;
}

// Auth state (for React Context or state management)
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}