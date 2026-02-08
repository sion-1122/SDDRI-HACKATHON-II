/* useNotifications hook for browser notification management.

[Task]: T059
[From]: specs/008-advanced-features/tasks.md (User Story 2)

This hook provides:
- Notification permission state
- Permission request function
- Check notifications function
- Subscribe to notification events
*/
import { useState, useEffect, useCallback } from 'react'
import { useNotificationPermission } from '@/components/tasks/NotificationPermissionPrompt'

interface NotificationEvent extends CustomEvent {
  detail: {
    taskIds: string[]
    message: string
  }
}

export function useNotifications() {
  const { permission, requestPermission, canShow, isDefault } = useNotificationPermission()
  const [isEnabled, setIsEnabled] = useState(false)

  useEffect(() => {
    setIsEnabled(canShow && permission === 'granted')
  }, [canShow, permission])

  /**
   * Request notification permission from user
   */
  const enableNotifications = useCallback(async () => {
    const granted = await requestPermission()
    setIsEnabled(granted)
    return granted
  }, [requestPermission])

  /**
   * Manually trigger notification check
   * Useful after creating/updating a task
   */
  const checkNow = useCallback(() => {
    window.dispatchEvent(new CustomEvent('check-notifications'))
  }, [])

  /**
   * Subscribe to notification events
   */
  const onNotification = useCallback((callback: (event: NotificationEvent) => void) => {
    const handler = (event: Event) => {
      callback(event as NotificationEvent)
    }

    window.addEventListener('notification', handler as EventListener)
    return () => {
      window.removeEventListener('notification', handler as EventListener)
    }
  }, [])

  return {
    // State
    permission,
    isEnabled,
    canShow,
    isDefault,

    // Actions
    enableNotifications,
    checkNow,
    onNotification,
  }
}

/**
 * Simplified hook for just checking if notifications are available
 */
export function useCanNotify() {
  const { canShow } = useNotificationPermission()
  return canShow
}
