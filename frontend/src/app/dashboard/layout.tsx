/* Dashboard layout with NotificationManager for browser notifications.

[Task]: T056
[From]: specs/008-advanced-features/tasks.md (User Story 2)

This layout:
- Wraps dashboard page with NotificationManager
- Enables browser notifications for task reminders
- Runs on client-side for notification permission and polling
*/
import { NotificationManager } from '@/components/tasks/NotificationManager';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      {children}
      <NotificationManager enabled={true} pollInterval={60000} />
    </>
  );
}
