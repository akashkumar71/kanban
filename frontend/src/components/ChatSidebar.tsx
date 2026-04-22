"use client";

import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import { sendChat, type ChatMessage } from "@/lib/api";
import type { BoardData } from "@/lib/kanban";

interface Props {
  onBoardUpdate: (board: BoardData) => void;
}

export const ChatSidebar = ({ onBoardUpdate }: Props) => {
  const [open, setOpen] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages, pending]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || pending) return;

    const nextHistory: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages(nextHistory);
    setInput("");
    setPending(true);
    setError(null);

    try {
      const result = await sendChat(text, messages);
      setMessages([...nextHistory, { role: "assistant", content: result.response }]);
      if (result.board) onBoardUpdate(result.board);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Chat failed";
      setError(msg);
      setMessages(nextHistory);
    } finally {
      setPending(false);
    }
  };

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        data-testid="chat-open"
        className="fixed bottom-6 right-6 z-30 rounded-full bg-[var(--primary-blue)] px-5 py-3 text-xs font-semibold uppercase tracking-[0.25em] text-white shadow-[var(--shadow)] transition hover:bg-[var(--navy-dark)]"
      >
        Open AI Chat
      </button>
    );
  }

  return (
    <aside
      data-testid="chat-sidebar"
      className="fixed bottom-6 right-6 top-6 z-30 flex w-[360px] max-w-[90vw] flex-col rounded-3xl border border-[var(--stroke)] bg-white/95 shadow-[var(--shadow)] backdrop-blur"
    >
      <header className="flex items-center justify-between gap-3 border-b border-[var(--stroke)] px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
            AI Assistant
          </p>
          <p className="font-display text-base font-semibold text-[var(--navy-dark)]">
            Ask about the board
          </p>
        </div>
        <button
          type="button"
          onClick={() => setOpen(false)}
          aria-label="Close chat"
          className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--navy-dark)] hover:text-[var(--navy-dark)]"
        >
          Hide
        </button>
      </header>

      <div
        ref={logRef}
        data-testid="chat-log"
        className="flex-1 space-y-3 overflow-y-auto px-5 py-4"
      >
        {messages.length === 0 && !pending && (
          <p className="text-sm leading-6 text-[var(--gray-text)]">
            Try{" "}
            <span className="font-semibold text-[var(--navy-dark)]">
              &ldquo;Add a card called Plan launch to Backlog&rdquo;
            </span>{" "}
            or{" "}
            <span className="font-semibold text-[var(--navy-dark)]">
              &ldquo;What&rsquo;s in Review?&rdquo;
            </span>
          </p>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            data-testid={`chat-msg-${msg.role}`}
            className={clsx(
              "max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-6 whitespace-pre-wrap",
              msg.role === "user"
                ? "ml-auto bg-[var(--primary-blue)] text-white"
                : "bg-[var(--surface)] text-[var(--navy-dark)]"
            )}
          >
            {msg.content}
          </div>
        ))}
        {pending && (
          <div
            data-testid="chat-pending"
            className="bg-[var(--surface)] inline-block rounded-2xl px-4 py-2 text-sm text-[var(--gray-text)]"
          >
            Thinking…
          </div>
        )}
        {error && (
          <p data-testid="chat-error" className="text-xs text-red-500">
            {error}
          </p>
        )}
      </div>

      <form
        onSubmit={submit}
        className="flex items-center gap-2 border-t border-[var(--stroke)] px-4 py-3"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message the AI…"
          aria-label="Chat message"
          disabled={pending}
          className="flex-1 rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
        />
        <button
          type="submit"
          disabled={pending || !input.trim()}
          className="rounded-xl bg-[var(--primary-blue)] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[var(--navy-dark)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </aside>
  );
};
