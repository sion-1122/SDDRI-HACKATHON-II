"use client"

import React, { useState } from "react"
import { Calendar, Repeat, X, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/Button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/label"
import { DatePicker } from "./DatePicker"
import type { RecurrenceRule, RecurrenceFrequency } from "@/types/recurrence"

/**
 * RecurrencePicker component for configuring recurring tasks.
 *
 * [Task]: T066-T069
 * [From]: specs/008-advanced-features/tasks.md (User Story 3)
 *
 * Allows users to set up recurring tasks with:
 * - Frequency (daily, weekly, monthly)
 * - Interval (how often)
 * - End condition (never, after N times, on specific date)
 */
interface RecurrencePickerProps {
  value: RecurrenceRule | null
  onChange: (recurrence: RecurrenceRule | null) => void
  disabled?: boolean
  className?: string
}

const FREQUENCY_OPTIONS = [
  { value: "daily" as const, label: "Daily" },
  { value: "weekly" as const, label: "Weekly" },
  { value: "monthly" as const, label: "Monthly" },
]

const END_CONDITIONS = ["never", "count", "date"] as const
type EndCondition = typeof END_CONDITIONS[number]

export function RecurrencePicker({
  value,
  onChange,
  disabled = false,
  className,
}: RecurrencePickerProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [endCondition, setEndCondition] = useState<EndCondition>(
    !value ? "never" : value.count ? "count" : value.end_date ? "date" : "never"
  )

  const isEnabled = value !== null

  const handleToggle = () => {
    if (isEnabled) {
      onChange(null)
      setEndCondition("never")
    } else {
      onChange({
        frequency: "daily",
        interval: 1,
      })
      setEndCondition("never")
    }
  }

  const handleFrequencyChange = (frequency: RecurrenceFrequency) => {
    if (isEnabled) {
      onChange({ ...value, frequency })
    }
  }

  const handleIntervalChange = (interval: number) => {
    if (isEnabled && interval > 0) {
      onChange({ ...value, interval })
    }
  }

  const handleEndConditionChange = (condition: EndCondition) => {
    setEndCondition(condition)

    if (!isEnabled) return

    // Clear existing end conditions when switching
    if (condition === "never") {
      const { count, end_date, ...rest } = value
      onChange(rest)
    }
  }

  const handleCountChange = (count: number) => {
    if (isEnabled && count > 0) {
      onChange({ ...value, count })
    }
  }

  const handleEndDateChange = (date: Date | null) => {
    if (isEnabled) {
      if (date) {
        onChange({ ...value, end_date: date.toISOString() })
      } else {
        const { end_date, ...rest } = value
        onChange(rest)
      }
    }
  }

  const getLabel = () => {
    if (!isEnabled) return "Repeats: Never"

    const freqLabel = FREQUENCY_OPTIONS.find(f => f.value === value.frequency)?.label || value.frequency
    const intervalLabel = value.interval && value.interval > 1 ? ` every ${value.interval}` : ""
    const endLabel = value.count
      ? ` (${value.count}x)`
      : value.end_date
        ? ` (until ${new Date(value.end_date).toLocaleDateString()})`
        : ""

    return `Repeats: ${freqLabel}${intervalLabel}${endLabel}`
  }

  return (
    <div className={cn("space-y-2", className)}>
      {/* Toggle button */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium flex items-center gap-2">
          <Repeat className={cn("h-4 w-4", isEnabled ? "text-primary" : "text-muted-foreground")} />
          Recurrence
        </label>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant={isEnabled ? "default" : "secondary"}
            size="sm"
            onClick={handleToggle}
            disabled={disabled}
            className="h-7 px-2 text-xs"
          >
            {isEnabled ? "On" : "Off"}
          </Button>

          {isEnabled && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-7 px-2"
            >
              <ChevronDown className={cn(
                "h-4 w-4 transition-transform",
                isExpanded && "rotate-180"
              )} />
            </Button>
          )}
        </div>
      </div>

      {/* Expanded settings */}
      {isEnabled && isExpanded && (
        <div className="space-y-4 pl-6 border-l-2 border-muted">
          {/* [T067] Frequency selector */}
          <div>
            <Label className="text-xs text-muted-foreground">Frequency</Label>
            <Select
              value={value.frequency}
              onValueChange={(val) => handleFrequencyChange(val as RecurrenceFrequency)}
              disabled={disabled}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FREQUENCY_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* [T068] Interval input */}
          <div>
            <Label className="text-xs text-muted-foreground">
              Every {value.frequency === "daily" ? "day(s)" : value.frequency === "weekly" ? "week(s)" : "month(s)"}
            </Label>
            <Input
              type="number"
              min={1}
              max={365}
              value={value.interval || 1}
              onChange={(e) => handleIntervalChange(parseInt(e.target.value) || 1)}
              disabled={disabled}
              className="w-full"
            />
          </div>

          {/* [T069] End condition */}
          <div>
            <Label className="text-xs text-muted-foreground mb-2 block">Ends</Label>
            <Select
              value={endCondition}
              onValueChange={(val) => handleEndConditionChange(val as EndCondition)}
              disabled={disabled}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never">Never</SelectItem>
                <SelectItem value="count">After</SelectItem>
                <SelectItem value="date">On date</SelectItem>
              </SelectContent>
            </Select>

            {endCondition === "count" && (
              <div className="mt-2 flex items-center gap-2">
                <Input
                  type="number"
                  min={1}
                  max={100}
                  value={value.count || 1}
                  onChange={(e) => handleCountChange(parseInt(e.target.value) || 1)}
                  disabled={disabled}
                  placeholder="1"
                  className="w-24"
                />
                <span className="text-sm text-muted-foreground">times</span>
              </div>
            )}

            {endCondition === "date" && (
              <div className="mt-2">
                <DatePicker
                  value={value.end_date ? new Date(value.end_date) : null}
                  onChange={handleEndDateChange}
                  placeholder="Select end date"
                  disabled={disabled}
                  disabledDates="before-today"
                />
              </div>
            )}
          </div>

          {/* Summary preview */}
          <div className="text-xs text-muted-foreground bg-muted/50 rounded px-2 py-1.5">
            {getLabel()}
          </div>
        </div>
      )}
    </div>
  )
}
