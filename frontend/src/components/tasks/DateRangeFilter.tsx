"use client"

import React, { useState } from "react"
import { Calendar, X, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/Button"
import { DatePicker } from "./DatePicker"
import { Input } from "@/components/ui/Input"

/**
 * DateRangeFilter component for filtering tasks by date range.
 *
 * [Task]: T036
 * [From]: specs/008-advanced-features/tasks.md (User Story 1)
 *
 * Provides a dropdown to select due_before and due_after date ranges.
 * Works with the existing preset date filters (overdue, today, week, month).
 */
interface DateRangeFilterProps {
  dueBefore: string | null
  dueAfter: string | null
  onChange: (dueBefore: string | null, dueAfter: string | null) => void
  className?: string
}

export function DateRangeFilter({
  dueBefore,
  dueAfter,
  onChange,
  className,
}: DateRangeFilterProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleDueBeforeChange = (date: Date | null) => {
    onChange(date ? date.toISOString() : null, dueAfter)
  }

  const handleDueAfterChange = (date: Date | null) => {
    onChange(dueBefore, date ? date.toISOString() : null)
  }

  const handleClear = () => {
    onChange(null, null)
    setIsOpen(false)
  }

  const hasActiveFilters = dueBefore !== null || dueAfter !== null

  return (
    <div className={cn("relative", className)}>
      <Button
        type="button"
        variant={hasActiveFilters ? "default" : "secondary"}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        <Calendar className="h-4 w-4" />
        <span>Date Range</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </Button>

      {/* Date range dropdown */}
      {isOpen && (
        <div className="absolute top-full mt-1 right-0 z-50 w-80 bg-background border border-input rounded-lg shadow-lg p-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">Filter by Date Range</h3>
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
                >
                  <X className="h-3 w-3" />
                  Clear
                </button>
              )}
            </div>

            {/* Due After (start date) */}
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">
                From (after)
              </label>
              <DatePicker
                value={dueAfter ? new Date(dueAfter) : null}
                onChange={handleDueAfterChange}
                placeholder="Select start date"
                disabledDates="before-today"
              />
            </div>

            {/* Due Before (end date) */}
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">
                To (before)
              </label>
              <DatePicker
                value={dueBefore ? new Date(dueBefore) : null}
                onChange={handleDueBeforeChange}
                placeholder="Select end date"
                disabledDates="before-today"
              />
            </div>

            {/* Helper text */}
            <p className="text-xs text-muted-foreground">
              Show tasks due between the selected dates
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
