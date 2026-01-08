"""Protected dashboard page.

[Task]: T060
[From]: specs/001-user-auth/tasks.md (User Story 3)

This is a protected page that:
- Checks if user is authenticated
- Displays user information (email, user ID)
- Redirects to /login if not authenticated
- Provides logout functionality
- Shows JWT token for testing purposes
"""
"use client";

import { useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Get current session
        const { data, error } = await authClient.getSession();

        if (error || !data) {
          router.push("/login");
          return;
        }

        setUser(data.user as User);
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = async () => {
    // Logout functionality (T070 - User Story 4)
    await authClient.signOut();
    router.push("/login");
  };

  const handleGetToken = async () => {
    try {
      const { data } = await authClient.token();
      if (data?.token) {
        setToken(data.token);
      }
    } catch (err) {
      console.error("Failed to get token", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-6 bg-white">
            <h2 className="text-2xl font-semibold mb-4">Welcome!</h2>

            {user && (
              <div className="space-y-4">
                <div>
                  <p className="text-gray-600">Email:</p>
                  <p className="text-lg font-medium">{user.email}</p>
                </div>

                <div>
                  <p className="text-gray-600">User ID:</p>
                  <p className="text-sm font-mono bg-gray-100 p-2 rounded">
                    {user.id}
                  </p>
                </div>

                <div>
                  <p className="text-gray-600">Account Created:</p>
                  <p className="text-sm">
                    {new Date(user.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            )}

            {/* JWT Token Display (for testing) */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <button
                onClick={handleGetToken}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4"
              >
                Get JWT Token
              </button>

              {token && (
                <div>
                  <p className="text-gray-600 mb-2">Your JWT Token:</p>
                  <p className="text-xs font-mono bg-gray-100 p-3 rounded break-all">
                    {token}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    Use this token in API requests with Authorization: Bearer
                    {token}
                  </p>
                </div>
              )}
            </div>

            {/* Tasks placeholder */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-semibold mb-2">Your Tasks</h3>
              <p className="text-gray-600">
                Task management functionality will be implemented in the next
                phase.
              </p>
              <p className="text-sm text-gray-500 mt-2">
                API endpoints are protected and require JWT authentication.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
