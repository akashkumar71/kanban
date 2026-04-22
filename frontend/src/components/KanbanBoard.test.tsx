import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, beforeEach, afterEach } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

function mockFetch(data = initialData) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => data,
    })
  );
}

beforeEach(() => mockFetch());
afterEach(() => vi.unstubAllGlobals());

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  it("renders five columns", async () => {
    render(<KanbanBoard />);
    await waitFor(() =>
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5)
    );
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await waitFor(() => screen.getAllByTestId(/column-/i));
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await waitFor(() => screen.getAllByTestId(/column-/i));
    const column = getFirstColumn();

    await userEvent.click(
      within(column).getByRole("button", { name: /add a card/i })
    );
    await userEvent.type(
      within(column).getByPlaceholderText(/card title/i),
      "New card"
    );
    await userEvent.type(
      within(column).getByPlaceholderText(/details/i),
      "Notes"
    );
    await userEvent.click(
      within(column).getByRole("button", { name: /add card/i })
    );

    expect(within(column).getByText("New card")).toBeInTheDocument();

    await userEvent.click(
      within(column).getByRole("button", { name: /delete new card/i })
    );
    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
