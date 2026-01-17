/** MessageInput component for chat message input.

[Task]: T062
[From]: specs/004-ai-chatbot/tasks.md

This component provides a text input field and send button for submitting
chat messages to the AI assistant.
*/
"use client";

import { useState, FormEvent } from "react";

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  maxLength?: number;
  placeholder?: string;
}

export function MessageInput({
  onSendMessage,
  disabled = false,
  maxLength = 10000,
  placeholder = "Type your message...",
}: MessageInputProps) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const message = inputValue.trim();

    if (message && !disabled) {
      onSendMessage(message);
      setInputValue("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Allow sending message with Enter key (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && !disabled) {
        onSendMessage(inputValue.trim());
        setInputValue("");
      }
    }
  };

  const characterCount = inputValue.length;
  const isNearLimit = characterCount > maxLength * 0.9;
  const isAtLimit = characterCount >= maxLength;

  return (
    <div className="p-4 border-t dark:border-gray-700">
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              maxLength={maxLength}
              className={`w-full px-4 py-2 pr-16 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed ${
                isAtLimit
                  ? "border-red-500 focus:ring-red-500"
                  : isNearLimit
                    ? "border-yellow-500 focus:ring-yellow-500"
                    : ""
              }`}
              aria-label="Chat message input"
              aria-describedby={isNearLimit ? "char-count" : undefined}
            />
            {characterCount > 0 && (
              <span
                id="char-count"
                className={`absolute right-3 top-1/2 -translate-y-1/2 text-xs ${
                  isAtLimit
                    ? "text-red-500"
                    : isNearLimit
                      ? "text-yellow-500"
                      : "text-gray-400 dark:text-gray-500"
                }`}
              >
                {characterCount}/{maxLength}
              </span>
            )}
          </div>
          <button
            type="submit"
            disabled={disabled || !inputValue.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            aria-label="Send message"
          >
            {disabled ? (
              <span className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Sending...
              </span>
            ) : (
              "Send"
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Press <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-600 rounded">Enter</kbd> to send,{" "}
          <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-600 rounded">Shift+Enter</kbd> for new line
        </p>
      </form>
    </div>
  );
}
