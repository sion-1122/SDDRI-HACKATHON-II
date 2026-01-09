/* Dashboard page (protected page example).

[Task]: T035, T042
[From]: specs/001-user-auth/plan.md
*/
"use client";

import { useSession } from "@/lib/auth";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

function DashboardContent() {
  const { user } = useSession();

  const handleLogout = async () => {
    try {
      const { apiClient } = await import("@/lib/api-client");
      await apiClient.signOut();
      window.location.href = "/login";
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Welcome back!
                </h1>
                <p className="mt-1 text-sm text-gray-600">
                  Signed in as: {user?.email}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Your Todo List
              </h2>
              <p className="text-gray-600">
                This is a protected page. You can only see this if you're authenticated.
              </p>
              <p className="mt-4 text-sm text-gray-500">
                User ID: {user?.id}
              </p>
              <p className="mt-2 text-sm text-gray-500">
                Account created: {user?.created_at ? new Date(user.created_at).toLocaleString() : "N/A"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}