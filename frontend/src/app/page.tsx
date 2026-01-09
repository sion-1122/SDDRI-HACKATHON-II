/* Homepage with redirect logic.

[Task]: T027
[From]: specs/003-frontend-task-manager/plan.md

Redirects unauthenticated users to /login and authenticated users to /tasks.
*/
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authClient } from '@/lib/auth-client';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data, error } = await authClient.getSession();

        if (error || !data) {
          // Not authenticated - redirect to login
          router.push('/login');
        } else {
          // Authenticated - redirect to tasks
          router.push('/tasks');
        }
      } catch (err) {
        // Error checking auth - redirect to login
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
