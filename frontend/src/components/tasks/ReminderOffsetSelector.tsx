"use client"

import React from "react"
import { Bell, BellOff } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/Button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

/**
 * ReminderOffsetSelector component for setting task reminder times.
 *
 * [Task]: T046
 * [From]: specs/008-advanced-features/tasks.md (User Story 2)
 *
 * Allows users to select when they want to be reminded before a task is due.
 * Offset is in minutes: 0 = at due time, 15 = 15 min before, etc.
 */
interface ReminderOffsetSelectorProps {
  value: number | null
  onChange: (offset: number | null) => void
  disabled?: boolean
  className?: string
}

// Common reminder offsets in minutes
const REMINDER_OPTIONS = [
  { value: 0, label: "At due time" },
  { value: 5, label: "5 minutes before" },
  { value: 15, label: "15 minutes before" },
  { value: 30, label: "30 minutes before" },
  { value: 60, label: "1 hour before" },
  { value: 120, label: "2 hours before" },
  { value: 360, label: "6 hours before" },
  { value: 1440, label: "1 day before" },
  { value: 2880, label: "2 days before" },
]

export function ReminderOffsetSelector({
  value,
  onChange,
  disabled = false,
  className,
}: ReminderOffsetSelectorProps) {
  const handleToggle = () => {
    if (value !== null) {
      onChange(null) // Turn off reminder
    } else {
      onChange(15) // Turn on with default 15 minutes
    }
  }

  const selectedOption = REMINDER_OPTIONS.find(opt => opt.value === value)

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium flex items-center gap-2">
          {value !== null ? (
            <Bell className="h-4 w-4 text-primary" />
          ) : (
            <BellOff className="h-4 w-4 text-muted-foreground" />
          )}
          Reminder
        </label>

        <Button
          type="button"
          variant={value !== null ? "default" : "secondary"}
          size="sm"
          onClick={handleToggle}
          disabled={disabled}
          className="h-7 px-2 text-xs"
        >
          {value !== null ? "On" : "Off"}
        </Button>
      </div>

      {value !== null && (
        <Select
          value={value.toString()}
          onValueChange={(val) => onChange(parseInt(val, 10))}
          disabled={disabled}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select reminder time">
              {selectedOption?.label}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {REMINDER_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value.toString()}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {value !== null && (
        <p className="text-xs text-muted-foreground">
          You'll receive a browser notification{" "}
          {value === 0
            ? "when the task is due"
            : `${Math.floor(value / 60)} hour${value >= 120 ? "s" : ""} before`}.
        </p>
      )}
    </div>
  )
}
