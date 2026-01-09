/* Registration form component (client component).

[Task]: T023
[From]: specs/001-user-auth/plan.md
*/
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import type { SignUpRequest } from "@/types/auth";

export function RegisterForm() {
  const router = useRouter();
  const [formData, setFormData] = useState<SignUpRequest>({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Client-side validation
  /* [Task]: T024 */
  const validateEmail = (email: string): boolean => {
    // Basic email validation: must contain @ and domain
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
  };

  const validatePassword = (password: string): boolean => {
    // Minimum 8 characters
    return password.length >= 8;
  };

  const validateForm = (): boolean => {
    // Reset error
    setError(null);

    // Validate email
    if (!formData.email) {
      setError("Email is required");
      return false;
    }

    if (!validateEmail(formData.email)) {
      setError("Invalid email format");
      return false;
    }

    // Validate password
    if (!formData.password) {
      setError("Password is required");
      return false;
    }

    if (!validatePassword(formData.password)) {
      setError("Password must be at least 8 characters");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Call FastAPI backend to register user
      /* [Task]: T025 */
      const result = await apiClient.signUp(formData);

      // Show success message
      setSuccess(true);

      // Redirect to login page after 2 seconds
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: unknown) {
      // Handle error responses
      if (err instanceof Error) {
        // Check for specific error types
        if (err.message.includes("already registered")) {
          setError("Email already registered");
        } else if (err.message.includes("Invalid email format")) {
          setError("Invalid email format");
        } else if (err.message.includes("Password must be at least")) {
          setError(err.message);
        } else {
          setError("Failed to create account. Please try again.");
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  };

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
      <div className="rounded-md shadow-sm -space-y-px">
        <div>
          <label htmlFor="email" className="sr-only">
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="Email address"
            value={formData.email}
            onChange={handleChange}
            disabled={isLoading || success}
          />
        </div>
        <div>
          <label htmlFor="password" className="sr-only">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="Password (min 8 characters)"
            value={formData.password}
            onChange={handleChange}
            disabled={isLoading || success}
          />
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Success message */}
      {success && (
        <div className="rounded-md bg-green-50 p-4">
          <p className="text-sm text-green-800">
            Account created successfully! Redirecting to login...
          </p>
        </div>
      )}

      <div>
        <button
          type="submit"
          disabled={isLoading || success}
          className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed"
        >
          {isLoading ? "Creating account..." : success ? "Account created!" : "Sign Up"}
        </button>
      </div>
    </form>
  );
}
