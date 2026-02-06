"use client"

import React from "react"
import { Clock } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * TimePicker component for time selection.
 *
 * [Task]: T031
 * [From]: specs/008-advanced-features/tasks.md (User Story 1)
 *
 * Uses native HTML time input for platform-consistent time selection.
 * Supports 12/24 hour format based on browser locale.
 */
interface TimePickerProps {
  value?: Date | null
  onChange: (time: Date | null) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export function TimePicker({
  value,
  onChange,
  placeholder = "Pick a time",
  disabled = false,
  className,
}: TimePickerProps) {
  // Convert Date to HH:MM format for input
  const timeToString = (date: Date): string => {
    const hours = date.getHours().toString().padStart(2, "0")
    const minutes = date.getMinutes().toString().padStart(2, "0")
    return `${hours}:${minutes}`
  }

  // Convert HH:MM string to Date
  const stringToTime = (timeString: string): Date => {
    const [hours, minutes] = timeString.split(":").map(Number)
    const date = value || new Date()
    date.setHours(hours, minutes, 0, 0)
    return date
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (!value) {
      onChange(null)
      return
    }
    onChange(stringToTime(value))
  }

  const handleClear = () => {
    onChange(null)
  }

  const timeValue = value ? timeToString(value) : ""

  return (
    <div className={cn("relative", className)}>
      <div className="relative flex items-center">
        <div className="absolute left-3 z-10 flex items-center pointer-events-none">
          <Clock className="h-4 w-4 text-muted-foreground" />
        </div>
        <input
          type="time"
          value={timeValue}
          onChange={handleChange}
          disabled={disabled}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-9 text-sm ring-offset-background",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
        />
        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Clear time"
          >
            ×
          </button>
        )}
      </div>
    </div>
  )
}
