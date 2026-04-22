import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, beforeEach, afterEach, describe, it, expect } from "vitest";
import { ChatSidebar } from "@/components/ChatSidebar";
import { initialData } from "@/lib/kanban";

function mockChatFetch(impl: () => Promise<unknown>) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async () => ({
      ok: true,
      json: impl,
    }))
  );
}

beforeEach(() => {
  vi.unstubAllGlobals();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ChatSidebar", () => {
  it("sends a message and renders the assistant reply", async () => {
    mockChatFetch(async () => ({
      response: "There are 8 cards.",
      board: null,
    }));
    const onBoardUpdate = vi.fn();
    render(<ChatSidebar onBoardUpdate={onBoardUpdate} />);

    await userEvent.type(
      screen.getByLabelText("Chat message"),
      "How many cards?"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() =>
      expect(screen.getByTestId("chat-msg-assistant")).toHaveTextContent(
        "There are 8 cards."
      )
    );
    expect(screen.getByTestId("chat-msg-user")).toHaveTextContent(
      "How many cards?"
    );
    expect(onBoardUpdate).not.toHaveBeenCalled();
  });

  it("calls onBoardUpdate when the AI returns a new board", async () => {
    mockChatFetch(async () => ({
      response: "Added.",
      board: initialData,
    }));
    const onBoardUpdate = vi.fn();
    render(<ChatSidebar onBoardUpdate={onBoardUpdate} />);

    await userEvent.type(
      screen.getByLabelText("Chat message"),
      "Add a card"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(onBoardUpdate).toHaveBeenCalledWith(initialData));
  });

  it("shows an error message when the request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 502, json: async () => ({}) })
    );

    render(<ChatSidebar onBoardUpdate={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Chat message"), "hi");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => expect(screen.getByTestId("chat-error")).toBeVisible());
  });

  it("hides and reopens the sidebar", async () => {
    render(<ChatSidebar onBoardUpdate={vi.fn()} />);
    expect(screen.getByTestId("chat-sidebar")).toBeVisible();

    await userEvent.click(screen.getByRole("button", { name: /close chat/i }));
    expect(screen.queryByTestId("chat-sidebar")).not.toBeInTheDocument();

    await userEvent.click(screen.getByTestId("chat-open"));
    expect(screen.getByTestId("chat-sidebar")).toBeVisible();
  });
});
