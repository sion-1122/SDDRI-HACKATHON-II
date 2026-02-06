"use client"

import React, { useEffect, useState, useRef, useCallback } from "react"
import { toast } from "sonner"
import { taskApi } from "@/lib/task-api"
import type { Task } from "@/types/task"
import { useNotificationPermission } from "./NotificationPermissionPrompt"

/**
 * NotificationManager component for handling browser notifications.
 *
 * [Task]: T049-T056
 * [From]: specs/008-advanced-features/tasks.md (User Story 2)
 *
 * Manages:
 * - Notification permission requests
 * - Polling for due tasks (every minute)
 * - Sending browser notifications
 * - Grouping multiple notifications
 * - Handling notification clicks
 */
interface NotificationManagerProps {
  enabled?: boolean
  pollInterval?: number // in milliseconds
}

interface NotificationData {
  taskId: string
  taskTitle: string
  dueDate: string
}

export function NotificationManager({
  enabled = true,
  pollInterval = 60000, // 1 minute default
}: NotificationManagerProps) {
  const { permission, requestPermission, canShow } = useNotificationPermission()
  const [hasRequestedPermission, setHasRequestedPermission] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const processedTasksRef = useRef<Set<string>>(new Set())

  // [T055] Handle notification click - navigate to task
  const handleNotificationClick = useCallback((data: NotificationData) => {
    // Focus on the window/tab
    window.focus()

    // Navigate to dashboard with the task highlighted
    window.location.href = `/dashboard?task=${data.taskId}`

    // Close the notification
    if ("Notification" in window) {
      const notifications = Array.from(Notification.getNotifications?.() || [])
      notifications.forEach((notif: any) => {
        if (notif.data?.taskId === data.taskId) {
          notif.close()
        }
      })
    }
  }, [])

  // [T053] Show single notification
  const showNotification = useCallback((task: Task) => {
    if (!canShow || !("Notification" in window)) {
      return
    }

    const notificationData: NotificationData = {
      taskId: task.id,
      taskTitle: task.title,
      dueDate: task.due_date || "",
    }

    try {
      const notif = new Notification(`Task Due: ${task.title}`, {
        body: `This task is due now${task.description ? `: ${task.description.substring(0, 100)}` : ""}`,
        icon: "/favicon.ico",
        tag: `task-${task.id}`,
        data: notificationData,
        requireInteraction: true,
      })

      notif.onclick = () => handleNotificationClick(notificationData)

      // Track that we've notified for this task
      processedTasksRef.current.add(task.id)
    } catch (error) {
      console.error("Error showing notification:", error)
    }
  }, [canShow, handleNotificationClick])

  // [T054] Group multiple notifications
  const groupNotifications = useCallback((tasks: Task[]) => {
    if (!canShow || !("Notification" in window) || tasks.length === 0) {
      return
    }

    const notificationData: NotificationData = {
      taskId: "group",
      taskTitle: `${tasks.length} tasks due`,
      dueDate: new Date().toISOString(),
    }

    try {
      const taskTitles = tasks.slice(0, 3).map(t => t.title).join(", ")
      const moreCount = tasks.length - 3

      const notif = new Notification(`${tasks.length} Tasks Due`, {
        body: `You have ${tasks.length} tasks due now.\n${taskTitles}${moreCount > 0 ? ` and ${moreCount} more...` : ""}`,
        icon: "/favicon.ico",
        tag: "tasks-group",
        data: notificationData,
        requireInteraction: true,
      })

      notif.onclick = () => {
        window.focus()
        window.location.href = "/dashboard"
      }

      // Track all notified tasks
      tasks.forEach(task => processedTasksRef.current.add(task.id))
    } catch (error) {
      console.error("Error showing grouped notification:", error)
    }
  }, [canShow])

  // [T052] Check and send notifications
  const checkAndSendNotifications = useCallback(async () => {
    if (!canShow) {
      return
    }

    try {
      // Get tasks that are due now or overdue, with reminders not sent
      const now = new Date()
      const oneHourFromNow = new Date(now.getTime() + 60 * 60 * 1000)

      const response = await taskApi.listTasks({
        completed: false,
        limit: 100,
        sort_by: "due_date",
        sort_order: "asc",
      })

      // Filter tasks that need notification:
      // 1. Have a due_date set
      // 2. Have reminder_offset set
      // 3. reminder_sent is false
      // 4. Due time is within reminder window
      const tasksNeedingNotification = response.tasks.filter(task => {
        if (!task.due_date || task.reminder_offset === null || task.reminder_sent) {
          return false
        }

        // Already processed?
        if (processedTasksRef.current.has(task.id)) {
          return false
        }

        const dueDate = new Date(task.due_date)
        const reminderTime = new Date(dueDate.getTime() - task.reminder_offset * 60 * 1000)
        const nowMinusBuffer = new Date(now.getTime() - 30000) // 30 second buffer

        return reminderTime <= now && reminderTime >= nowMinusBuffer
      })

      if (tasksNeedingNotification.length === 0) {
        return
      }

      // [T054] Group notifications if multiple
      if (tasksNeedingNotification.length > 1) {
        groupNotifications(tasksNeedingNotification)
      } else {
        showNotification(tasksNeedingNotification[0])
      }

      // Mark reminders as sent via API
      for (const task of tasksNeedingNotification) {
        try {
          await fetch(`/api/tasks/${task.id}/reminder`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ reset_sent: false }),
          })
        } catch (error) {
          console.error("Error marking reminder as sent:", error)
        }
      }

      // Show toast summary
      if (tasksNeedingNotification.length > 0) {
        const taskWord = tasksNeedingNotification.length === 1 ? "task" : "tasks"
        toast.success(`${tasksNeedingNotification.length} ${taskWord} due`, {
          description: "Check your notifications for details",
        })
      }
    } catch (error) {
      console.error("Error checking notifications:", error)
    }
  }, [canShow, showNotification, groupNotifications])

  // [T050] Request permission on mount (if not already requested)
  useEffect(() => {
    if (!enabled || hasRequestedPermission) {
      return
    }

    const requestOnInteraction = async () => {
      if (permission === "default" && !hasRequestedPermission) {
        const granted = await requestPermission()
        setHasRequestedPermission(true)

        if (granted) {
          toast.success("Notifications enabled", {
            description: "You'll be reminded when tasks are due",
          })
        }
      }
    }

    // Request on first user interaction
    const handleUserInteraction = () => {
      requestOnInteraction()
      document.removeEventListener("click", handleUserInteraction)
      document.removeEventListener("keydown", handleUserInteraction)
    }

    document.addEventListener("click", handleUserInteraction)
    document.addEventListener("keydown", handleUserInteraction)

    return () => {
      document.removeEventListener("click", handleUserInteraction)
      document.removeEventListener("keydown", handleUserInteraction)
    }
  }, [enabled, hasRequestedPermission, permission, requestPermission])

  // [T051] Poll for due tasks
  useEffect(() => {
    if (!enabled || !canShow) {
      return
    }

    // Check immediately on mount
    checkAndSendNotifications()

    // Set up polling interval
    intervalRef.current = setInterval(() => {
      checkAndSendNotifications()
    }, pollInterval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [enabled, canShow, pollInterval, checkAndSendNotifications])

  // This component doesn't render anything visible
  return null
}

/**
 * Hook to programmatically check for notifications.
 * Can be called from other components like after creating a task.
 */
export function useNotificationChecker() {
  const { canShow } = useNotificationPermission()

  const checkNow = useCallback(async () => {
    if (!canShow) {
      return false
    }

    // Trigger the check by dispatching a custom event
    window.dispatchEvent(new CustomEvent("check-notifications"))
    return true
  }, [canShow])

  return { canShow, checkNow }
}
