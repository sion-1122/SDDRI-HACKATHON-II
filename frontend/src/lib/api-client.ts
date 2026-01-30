/* API client for communicating with FastAPI backend.

[Task]: T014
[From]: specs/001-user-auth/plan.md, specs/001-user-auth/research.md
*/
import type {
  SignUpRequest,
  SignUpResponse,
  SignInRequest,
  SignInResponse,
  SessionResponse,
  SignOutResponse,
  ApiError,
} from "@/types/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiErrorClass extends Error {
  detail: string;

  constructor(detail: string) {
    super(detail);
    this.name = "ApiError";
    this.detail = detail;
  }
}

/**
 * API Client for FastAPI backend authentication endpoints.
 *
 * Handles all HTTP requests to the backend with proper credentials,
 * error handling, and type safety.
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make an authenticated API request with credentials (cookies).
   *
   * @param endpoint - API endpoint path (e.g., "/api/auth/session")
   * @param options - Fetch options (method, headers, body)
   * @returns Parsed JSON response
   * @throws ApiErrorClass if request fails
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultOptions: RequestInit = {
      credentials: "include", // Include httpOnly cookies
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    // Handle non-JSON responses (e.g., 204 No Content)
    if (response.status === 204) {
      return undefined as T;
    }

    const data = await response.json();

    // Handle error responses
    if (!response.ok) {
      const error = data as ApiError;
      throw new ApiErrorClass(error.detail || "Request failed");
    }

    return data as T;
  }

  /**
   * Register a new user account.
   *
   * @param credentials - User registration credentials (email, password)
   * @returns Registration response with success message and user data
   * @throws ApiErrorClass if email already exists (409) or validation fails (400)
   *
   * @example
   * ```typescript
   * const result = await apiClient.signUp({
   *   email: "user@example.com",
   *   password: "password123"
   * });
   * console.log(result.user.email); // "user@example.com"
   * ```
   */
  async signUp(credentials: SignUpRequest): Promise<SignUpResponse> {
    return this.request<SignUpResponse>("/api/auth/sign-up", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  /**
   * Authenticate user and receive JWT token.
   *
   * Backend sets httpOnly cookie with token automatically.
   *
   * @param credentials - User login credentials (email, password)
   * @returns Login response with JWT token and user data
   * @throws ApiErrorClass if credentials are invalid (401)
   *
   * @example
   * ```typescript
   * const result = await apiClient.signIn({
   *   email: "user@example.com",
   *   password: "password123"
   * });
   * console.log(result.token); // JWT token
   * console.log(result.user.email); // "user@example.com"
   * // Token is automatically stored in httpOnly cookie
   * ```
   */
  async signIn(credentials: SignInRequest): Promise<SignInResponse> {
    return this.request<SignInResponse>("/api/auth/sign-in", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  /**
   * Verify current user session.
   *
   * Checks JWT token from httpOnly cookie and returns user data if authenticated.
   *
   * @returns Session response with authentication status and user data
   * @throws ApiErrorClass if token is invalid or expired (401)
   *
   * @example
   * ```typescript
   * const session = await apiClient.getSession();
   * if (session.authenticated) {
   *   console.log("Logged in as:", session.user?.email);
   * } else {
   *   console.log("Not authenticated");
   * }
   * ```
   */
  async getSession(): Promise<SessionResponse> {
    return this.request<SessionResponse>("/api/auth/session");
  }

  /**
   * Logout current user.
   *
   * Clears httpOnly cookie on client side.
   *
   * @returns Logout response with success message
   * @throws ApiErrorClass if request fails (500)
   *
   * @example
   * ```typescript
   * await apiClient.signOut();
   * // Cookie cleared, redirect to login page
   * ```
   */
  async signOut(): Promise<SignOutResponse> {
    const response = await this.request<SignOutResponse>("/api/auth/sign-out", {
      method: "POST",
    });

    // Clear client-side cookie (httpOnly cookies can't be accessed via JS,
    // but the backend should clear the cookie by setting Set-Cookie header with expired date)
    // Note: The backend is responsible for clearing the httpOnly cookie

    return response;
  }

  /**
   * Make an authenticated API request to a protected endpoint.
   *
   * @param endpoint - API endpoint path (e.g., "/api/users/me")
   * @param options - Fetch options (method, headers, body)
   * @returns Parsed JSON response
   * @throws ApiErrorClass if request fails or user is not authenticated (401)
   *
   * @example
   * ```typescript
   * const tasks = await apiClient.authenticatedRequest("/api/tasks");
   * console.log(tasks); // Array of tasks
   * ```
   */
  async authenticatedRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    return this.request<T>(endpoint, options);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class type for testing
export type { ApiClient };
