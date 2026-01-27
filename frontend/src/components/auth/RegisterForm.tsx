/* Registration form component (client component).

[Task]: T023, T075
[From]: specs/001-user-auth/plan.md, specs/005-ux-improvement/tasks.md

Updated with Notion-inspired minimalistic design using theme variables.
*/
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import type { SignUpRequest } from "@/types/auth";
import { cn } from "@/lib/utils";

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
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
  };

  const validatePassword = (password: string): boolean => {
    return password.length >= 8;
  };

  const validateForm = (): boolean => {
    setError(null);

    if (!formData.email) {
      setError("Email is required");
      return false;
    }

    if (!validateEmail(formData.email)) {
      setError("Invalid email format");
      return false;
    }

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

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiClient.signUp(formData);
      setSuccess(true);

      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err: unknown) {
      if (err instanceof Error) {
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
    if (error) {
      setError(null);
    }
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {/* Notion-inspired form fields - clean and minimal */}
      <div className="space-y-3">
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-foreground mb-1.5"
          >
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className={cn(
              "w-full px-3 py-2",
              "bg-background border border-input rounded-lg",
              "text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "transition-shadow",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            disabled={isLoading || success}
          />
        </div>
        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-foreground mb-1.5"
          >
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            className={cn(
              "w-full px-3 py-2",
              "bg-background border border-input rounded-lg",
              "text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "transition-shadow",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
            placeholder="Min 8 characters"
            value={formData.password}
            onChange={handleChange}
            disabled={isLoading || success}
          />
        </div>
      </div>

      {/* Error message - Notion-style subtle alert */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Success message - Notion-style subtle success */}
      {success && (
        <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
          <p className="text-sm text-green-600 dark:text-green-400">
            Account created successfully! Redirecting to login...
          </p>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading || success}
        className={cn(
          "w-full py-2.5 px-4",
          "bg-primary text-primary-foreground",
          "rounded-lg font-medium text-sm",
          "hover:bg-primary/90",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "transition-colors"
        )}
      >
        {isLoading ? "Creating account..." : success ? "Account created!" : "Create Account"}
      </button>
    </form>
  );
}
