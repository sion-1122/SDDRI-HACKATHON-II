/* Dashboard page - main task management interface with Notion-inspired design.

[Task]: T021-T024, T072
[From]: specs/005-ux-improvement/tasks.md

This Server Component:
- Fetches initial tasks server-side for fast page load
- Passes data to TaskListClient for client-side interactions
- Notion-inspired design with generous whitespace
- Clean, minimalistic layout
*/
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { TaskListClient } from '@/components/tasks/TaskListClient';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { fetchTasks } from '@/lib/api/server';
import { getTaskUrgency } from '@/lib/utils';
import type { Task } from '@/types/task';

const ITEMS_PER_PAGE = 50;

async function DashboardContent() {
  const cookieStore = await cookies();
  const authToken = cookieStore.get('auth_token');

  // Redirect to login if not authenticated
  if (!authToken) {
    redirect('/login');
  }

  // Fetch initial tasks server-side
  let initialTasks: Task[] = [];
  let initialTotal = 0;

  try {
    const response = await fetchTasks({
      limit: ITEMS_PER_PAGE,
      offset: 0,
    });

    if (response) {
      // Add computed urgency to each task
      initialTasks = response.tasks.map(task => ({
        ...task,
        urgency: getTaskUrgency(task.due_date),
      })) as Task[];
      initialTotal = response.total;
    }
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header with generous spacing [T072] */}
      <DashboardHeader />

      {/* Main content with Notion-style spacing */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <TaskListClient
          initialTasks={initialTasks}
          initialTotal={initialTotal}
        />
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return <DashboardContent />;
}
