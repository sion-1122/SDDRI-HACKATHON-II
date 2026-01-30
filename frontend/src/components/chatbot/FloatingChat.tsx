"use client";

import { useEffect } from "react";
import { MessageCircle, X } from "lucide-react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { useChatContext } from "./ChatProvider";
import { useSession } from "@/lib/hooks";
import { cn } from "@/lib/utils";

export function FloatingChat() {
    const { isOpen, closeChat, toggleChat, unreadCount } = useChatContext();
    const { user, isAuthenticated } = useSession();

    if (!isAuthenticated || !user) return null;

    return (
        <>
            {/* Floating chat button - positioned bottom-right */}
            <button
                onClick={toggleChat}
                className={cn(
                    "fixed bottom-6 right-6 z-40",
                    "relative", // ensure absolutely positioned badge anchors to this button
                    "flex items-center justify-center",
                    "w-14 h-14 rounded-full",
                    "bg-primary text-primary-foreground",
                    "shadow-lg hover:shadow-xl",
                    "transition-all duration-200 ease-in-out",
                    "hover:scale-110 active:scale-95",
                    "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                )}
                aria-label={isOpen ? "Close chat" : "Open chat"}
            >
                {isOpen ? (
                    <X className="w-6 h-6" />
                ) : (
                    <>
                        <MessageCircle className="w-6 h-6" />
                        {/* Unread count badge */}
                        {unreadCount > 0 && (
                            <span
                                className={cn(
                                    "absolute -top-1 -right-1",
                                    "flex items-center justify-center",
                                    "min-w-[20px] h-5 px-1",
                                    "bg-destructive text-destructive-foreground",
                                    "text-xs font-bold",
                                    "rounded-full",
                                    "animate-bounce",
                                )}
                            >
                                {unreadCount > 9 ? "9+" : unreadCount}
                            </span>
                        )}
                    </>
                )}
            </button>

            {/* Sheet panel for chat interface */}
            <Sheet open={isOpen} onOpenChange={(open) => !open && closeChat()}>
                <SheetContent
                    side="right"
                    // Progressive responsive width across screen sizes:
                    // - mobile: nearly full width (100vw)
                    // - sm (640px): comfortable width (500px)
                    // - md (768px): expanded width (600px)
                    // - lg (1024px): generous width (700px)
                    className="max-w-[100vw] sm:max-w-[500px] md:max-w-[600px] lg:max-w-[700px] p-0"
                    showCloseButton={false}
                >
                    <div className="flex flex-col h-full overflow-hidden">
                        {/* Custom header */}
                        <div className="flex items-center justify-between p-4 border-b border-border shrink-0">
                            <div>
                                <h2 className="text-lg font-semibold text-foreground">
                                    AI Assistant
                                </h2>
                                <p className="text-sm text-muted-foreground">
                                    Ask me to create, list, or manage your tasks
                                </p>
                            </div>
                            <button
                                onClick={closeChat}
                                className="p-2 rounded-md hover:bg-muted transition-colors"
                                aria-label="Close chat"
                            >
                                <X className="w-5 h-5 text-muted-foreground" />
                            </button>
                        </div>

                        {/* Chat interface - fill the remaining space */}
                        <div className="flex-1 min-h-0 h-full">
                            <ChatInterface userId={user.id} />
                        </div>
                    </div>
                </SheetContent>
            </Sheet>
        </>
    );
}
