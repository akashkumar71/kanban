import type { BoardData } from "./kanban";

export type ChatRole = "user" | "assistant";
export type ChatMessage = { role: ChatRole; content: string };
export type ChatResponse = { response: string; board: BoardData | null };

export async function fetchBoard(): Promise<BoardData> {
  const res = await fetch("/api/kanban");
  if (!res.ok) throw new Error(`Failed to load board (${res.status})`);
  return res.json();
}

export async function saveBoard(board: BoardData): Promise<void> {
  const res = await fetch("/api/kanban", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(board),
  });
  if (!res.ok) throw new Error(`Failed to save board (${res.status})`);
}

export async function sendChat(
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) throw new Error(`Chat failed (${res.status})`);
  return res.json();
}
