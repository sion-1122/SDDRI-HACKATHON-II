"use client"

import React, { useState, useEffect } from "react"
import { Bell, X, Check } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/Button"

/**
 * NotificationPermissionPrompt component for requesting notification permission.
 *
 * [Task]: T047
 * [From]: specs/008-advanced-features/tasks.md (User Story 2)
 *
 * Shows a non-intrusive prompt to enable browser notifications.
 * Remembers user's choice in localStorage.
 */
interface NotificationPermissionPromptProps {
  onPermissionGranted?: () => void
  onPermissionDenied?: () => void
  className?: string
}

const STORAGE_KEY = "notification-prompt-dismissed"

export function NotificationPermissionPrompt({
  onPermissionGranted,
  onPermissionDenied,
  className,
}: NotificationPermissionPromptProps) {
  const [permission, setPermission] = useState<NotificationPermission>("default")
  const [dismissed, setDismissed] = useState(false)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    // Check if running in browser with Notification API
    if (typeof window === "undefined" || !("Notification" in window)) {
      return
    }

    // Check current permission state
    setPermission(Notification.permission)

    // Check if user previously dismissed
    const wasDismissed = localStorage.getItem(STORAGE_KEY)
    if (wasDismissed) {
      setDismissed(true)
      return
    }

    // Show prompt if permission is default (not asked yet)
    if (Notification.permission === "default") {
      // Delay showing prompt for better UX (show after user interacts)
      const timer = setTimeout(() => {
        setShowPrompt(true)
      }, 3000) // Show after 3 seconds

      return () => clearTimeout(timer)
    }
  }, [])

  const handleRequestPermission = async () => {
    if (!("Notification" in window)) {
      return
    }

    try {
      const result = await Notification.requestPermission()
      setPermission(result)

      if (result === "granted") {
        setShowPrompt(false)
        onPermissionGranted?.()
      } else {
        handleDismiss()
        onPermissionDenied?.()
      }
    } catch (error) {
      console.error("Error requesting notification permission:", error)
      handleDismiss()
    }
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    setDismissed(true)
    // Remember that user dismissed
    try {
      localStorage.setItem(STORAGE_KEY, "true")
    } catch {
      // localStorage might not be available
    }
  }

  // Don't render if notifications not supported, already granted/denied, or dismissed
  if (typeof window === "undefined" || !("Notification" in window)) {
    return null
  }

  if (permission === "granted" || permission === "denied" || !showPrompt || dismissed) {
    return null
  }

  return (
    <div
      className={cn(
        "fixed bottom-4 right-4 z-50 max-w-sm animate-in slide-in-from-bottom-4",
        className
      )}
    >
      <div className="bg-background border border-input rounded-lg shadow-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Bell className="h-5 w-5 text-primary" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold">Enable Notifications</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Get reminded about upcoming tasks so you never miss a deadline.
            </p>

            <div className="flex gap-2 mt-3">
              <Button
                size="sm"
                onClick={handleRequestPermission}
                className="flex-1"
              >
                Enable
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleDismiss}
              >
                Not now
              </Button>
            </div>
          </div>

          <button
            onClick={handleDismiss}
            className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook to check and request notification permission.
 *
 * [Task]: T059 (part of useNotifications hook)
 *
 * @returns Object with permission state and request function
 */
export function useNotificationPermission() {
  const [permission, setPermission] = useState<NotificationPermission>("default")

  useEffect(() => {
    // Initialize permission state on mount
    if (typeof window !== "undefined" && "Notification" in window) {
      setPermission(Notification.permission)
    }
  }, [])

  const requestPermission = async () => {
    if (typeof window === "undefined" || !("Notification" in window)) {
      return false
    }

    try {
      const result = await Notification.requestPermission()
      setPermission(result)
      return result === "granted"
    } catch {
      return false
    }
  }

  return {
    permission,
    requestPermission,
    canShow: permission === "granted",
    isDefault: permission === "default",
    isDenied: permission === "denied",
  }
}
