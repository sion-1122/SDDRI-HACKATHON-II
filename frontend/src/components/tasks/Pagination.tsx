/* Pagination component - navigate pages of tasks.

[Task]: T052, T053, T054, T056
[From]: specs/003-frontend-task-manager/plan.md

This client component:
- Displays Previous/Next buttons
- Shows page indicator ("Page X of Y")
- Provides jump to page input
- Syncs page state with URL params (?page=2)
- Calculates offset from page number: offset = (page - 1) * limit
- Disables Previous on page 1, Next on last page
*/
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface PaginationProps {
  total: number;           // Total number of tasks
  limit: number;           // Items per page (default: 50)
  currentPage: number;     // Current page (1-based)
}

export function Pagination({ total, limit, currentPage }: PaginationProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Calculate total pages
  const totalPages = Math.ceil(total / limit);

  // Determine if navigation buttons should be disabled (T056)
  const hasPrevPage = currentPage > 1;
  const hasNextPage = currentPage < totalPages;

  // Update URL params when page changes (T053)
  const updatePage = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString());

    if (newPage === 1) {
      // Remove page param if on page 1 (cleaner URL)
      params.delete('page');
    } else {
      params.set('page', newPage.toString());
    }

    const queryString = params.toString();
    router.push(`${queryString ? `?${queryString}` : ''}`);
  };

  const handlePrevPage = () => {
    if (hasPrevPage) {
      updatePage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (hasNextPage) {
      updatePage(currentPage + 1);
    }
  };

  const handleJumpToPage = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const pageInput = formData.get('pageJump') as string;
    const newPage = parseInt(pageInput, 10);

    if (!isNaN(newPage) && newPage >= 1 && newPage <= totalPages) {
      updatePage(newPage);
    }
  };

  // Don't render if there's only one page
  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className="bg-white shadow rounded-lg p-4 mt-6">
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        {/* Page indicator */}
        <div className="text-sm text-gray-700">
          Page <span className="font-semibold">{currentPage}</span> of{' '}
          <span className="font-semibold">{totalPages}</span>
          <span className="text-gray-500 ml-2">({total} total tasks)</span>
        </div>

        {/* Navigation buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevPage}
            disabled={!hasPrevPage}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              hasPrevPage
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
            aria-label="Previous page"
          >
            Previous
          </button>

          <button
            onClick={handleNextPage}
            disabled={!hasNextPage}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              hasNextPage
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
            aria-label="Next page"
          >
            Next
          </button>
        </div>

        {/* Jump to page input */}
        <form onSubmit={handleJumpToPage} className="flex items-center gap-2">
          <label htmlFor="pageJump" className="text-sm text-gray-700">
            Jump to:
          </label>
          <input
            id="pageJump"
            name="pageJump"
            type="number"
            min="1"
            max={totalPages}
            placeholder="Page"
            className="w-20 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Jump to page"
          />
          <button
            type="submit"
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm font-medium"
          >
            Go
          </button>
        </form>
      </div>
    </div>
  );
}
