"use client"

import React, { useState, useEffect } from "react"
import { Calendar, Clock } from "lucide-react"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/Button"
import { DatePicker } from "./DatePicker"
import { TimePicker } from "./TimePicker"
import { formatDueDate, isOverdue } from "@/lib/utils/dateFormatters"
import type { Task } from "@/types/task"

/**
 * DueDateField component for combined date and time selection.
 *
 * [Task]: T032
 * [From]: specs/008-advanced-features/tasks.md (User Story 1)
 *
 * Combines DatePicker and TimePicker for full datetime selection.
 * Displays formatted due date with overdue status indicator.
 */
interface DueDateFieldProps {
  value?: string | null // ISO datetime string
  onChange: (dateTime: string | null) => void
  disabled?: boolean
  error?: string
  showPreview?: boolean // Show formatted preview below inputs
  className?: string
}

export function DueDateField({
  value,
  onChange,
  disabled = false,
  error,
  showPreview = true,
  className,
}: DueDateFieldProps) {
  // Parse ISO string to Date for components
  const parseDate = (isoString: string | null | undefined): Date | null => {
    if (!isoString) return null
    try {
      return new Date(isoString)
    } catch {
      return null
    }
  }

  // Format Date to ISO string for output
  const formatToISO = (date: Date | null): string | null => {
    if (!date) return null
    return date.toISOString()
  }

  const [date, setDate] = useState<Date | null>(parseDate(value))
  const [time, setTime] = useState<Date | null>(parseDate(value))

  // Sync with value prop changes
  useEffect(() => {
    const parsed = parseDate(value)
    setDate(parsed)
    setTime(parsed)
  }, [value])

  // Combine date and time when either changes
  const updateDateTime = (newDate: Date | null, newTime: Date | null) => {
    let combined: Date | null = null

    if (newDate && newTime) {
      // Combine date from newDate and time from newTime
      combined = new Date(newDate)
      combined.setHours(
        newTime.getHours(),
        newTime.getMinutes(),
        newTime.getSeconds(),
        0
      )
    } else if (newDate) {
      // Only date set, use midnight UTC
      combined = new Date(newDate)
      combined.setHours(0, 0, 0, 0)
    } else if (newTime) {
      // Only time set, use today's date
      combined = new Date()
      combined.setHours(
        newTime.getHours(),
        newTime.getMinutes(),
        newTime.getSeconds(),
        0
      )
    }

    const isoString = formatToISO(combined)
    onChange(isoString)

    // Update local state
    setDate(newDate)
    setTime(newTime)
  }

  const handleDateChange = (newDate: Date | null) => {
    updateDateTime(newDate, time)
  }

  const handleTimeChange = (newTime: Date | null) => {
    updateDateTime(date, newTime)
  }

  // Create a mock task for preview formatting
  const mockTask: Task = {
    id: "preview",
    user_id: "preview",
    title: "Preview",
    description: null,
    priority: "MEDIUM",
    tags: [],
    due_date: value ?? null,
    completed: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    // Advanced features
    reminder_offset: null,
    reminder_sent: false,
    recurrence: null,
    parent_task_id: null,
  }

  const isTaskOverdue = isOverdue(mockTask)

  return (
    <div className={cn("space-y-2", className)}>
      <Label
        htmlFor="due-date"
        className={cn(
          "flex items-center gap-2",
          isTaskOverdue && !disabled && "text-destructive"
        )}
      >
        <Calendar className="h-4 w-4" />
        Due Date
      </Label>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <DatePicker
          value={date}
          onChange={handleDateChange}
          placeholder="Select date"
          disabled={disabled}
        />
        <TimePicker
          value={time}
          onChange={handleTimeChange}
          placeholder="Select time"
          disabled={disabled}
        />
      </div>

      {error && (
        <p className="text-xs text-destructive flex items-center gap-1">
          {error}
        </p>
      )}

      {showPreview && value && (
        <div className="flex items-center gap-2 text-xs">
          <Clock className="h-3 w-3 text-muted-foreground" />
          <span
            className={cn(
              isTaskOverdue ? "text-destructive" : "text-muted-foreground"
            )}
          >
            {formatDueDate(mockTask)}
          </span>
        </div>
      )}
    </div>
  )
}
