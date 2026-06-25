"use client";

import { AppHeader } from "@/components/app-header";
import { SignalStrip } from "@/components/signal-strip";
import { MessageList } from "@/components/message-list";
import { ChatInput } from "@/components/chat-input";
import { EmptyState } from "@/components/empty-state";
import { useAgroChat } from "@/hooks/use-agro-chat";

export default function Home() {
  const { messages, isLoading, sendMessage } = useAgroChat();

  return (
    <div className="texture-field flex h-screen flex-col">
      <AppHeader />
      <SignalStrip />

      {messages.length === 0 ? (
        <EmptyState onPick={sendMessage} />
      ) : (
        <MessageList messages={messages} isLoading={isLoading} />
      )}

      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
