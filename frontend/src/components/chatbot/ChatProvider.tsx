/* ChatProvider context - manages chat state across navigation.

[Task]: T054
[From]: specs/005-ux-improvement/tasks.md

This context:
- Manages chat open/close state
- Preserves chat state across page navigation
- Provides chat controls to all child components
- Uses localStorage for persistence
*/
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ChatContextType {
  isOpen: boolean;
  openChat: () => void;
  closeChat: () => void;
  toggleChat: () => void;
  unreadCount: number;
  setUnreadCount: (count: number) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const CHAT_STATE_KEY = 'chat_state';
const CHAT_UNREAD_KEY = 'chat_unread';

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  // Initialize state from localStorage
  const [isOpen, setIsOpen] = useState(() => {
    if (typeof window === 'undefined') return false;
    try {
      const stored = localStorage.getItem(CHAT_STATE_KEY);
      return stored === 'true';
    } catch {
      return false;
    }
  });

  const [unreadCount, setUnreadCountState] = useState(() => {
    if (typeof window === 'undefined') return 0;
    try {
      const stored = localStorage.getItem(CHAT_UNREAD_KEY);
      return stored ? parseInt(stored, 10) : 0;
    } catch {
      return 0;
    }
  });

  // Persist chat state to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(CHAT_STATE_KEY, isOpen.toString());
    } catch {
      // Ignore storage errors
    }
  }, [isOpen]);

  // Persist unread count to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(CHAT_UNREAD_KEY, unreadCount.toString());
    } catch {
      // Ignore storage errors
    }
  }, [unreadCount]);

  // Reset unread count when chat is opened
  useEffect(() => {
    if (isOpen) {
      setUnreadCountState(0);
    }
  }, [isOpen]);

  const openChat = () => setIsOpen(true);
  const closeChat = () => setIsOpen(false);
  const toggleChat = () => setIsOpen(prev => !prev);

  const setUnreadCount = (count: number) => {
    // Only increment when chat is closed
    if (!isOpen) {
      setUnreadCountState(count);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        isOpen,
        openChat,
        closeChat,
        toggleChat,
        unreadCount,
        setUnreadCount,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}
