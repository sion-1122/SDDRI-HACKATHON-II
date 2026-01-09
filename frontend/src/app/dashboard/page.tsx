/* Dashboard page (protected page example).

[Task]: T035
[From]: specs/001-user-auth/plan.md
*/
import { apiClient } from "@/lib/api-client";

export const metadata = {
  title: "Dashboard - Todo List",
  description: "Your personal Todo List dashboard",
};

async function DashboardPage() {
  try {
    // Verify session by calling FastAPI backend
    const session = await apiClient.getSession();

    if (!session.authenticated || !session.user) {
      // Redirect to login if not authenticated
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Not authenticated
            </h2>
            <p className="text-gray-600 mb-4">
              Please sign in to access this page
            </p>
            <a
              href="/login"
              className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Go to Login
            </a>
          </div>
        </div>
      );
    }

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
                    Signed in as: {session.user.email}
                  </p>
                </div>
                <a
                  href="/api/auth/sign-out"
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Logout
                </a>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Your Todo List
                </h2>
                <p className="text-gray-600">
                  This is a protected page. You can only see this if you're authenticated.
                </p>
                <p className="mt-4 text-sm text-gray-500">
                  Token expires at: {new Date(session.expires_at || "").toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  } catch (error) {
    // If session check fails, redirect to login
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Session expired
          </h2>
          <p className="text-gray-600 mb-4">
            Please sign in again to access this page
          </p>
          <a
            href="/login"
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }
}

export default DashboardPage;
