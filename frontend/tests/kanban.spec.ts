import { expect, test, type Page } from "@playwright/test";

const INITIAL_BOARD = {
  columns: [
    { id: "col-backlog", title: "Backlog", cardIds: ["card-1", "card-2"] },
    { id: "col-discovery", title: "Discovery", cardIds: ["card-3"] },
    { id: "col-progress", title: "In Progress", cardIds: ["card-4", "card-5"] },
    { id: "col-review", title: "Review", cardIds: ["card-6"] },
    { id: "col-done", title: "Done", cardIds: ["card-7", "card-8"] },
  ],
  cards: {
    "card-1": { id: "card-1", title: "Align roadmap themes", details: "Draft quarterly themes with impact statements and metrics." },
    "card-2": { id: "card-2", title: "Gather customer signals", details: "Review support tags, sales notes, and churn feedback." },
    "card-3": { id: "card-3", title: "Prototype analytics view", details: "Sketch initial dashboard layout and key drill-downs." },
    "card-4": { id: "card-4", title: "Refine status language", details: "Standardize column labels and tone across the board." },
    "card-5": { id: "card-5", title: "Design card layout", details: "Add hierarchy and spacing for scanning dense lists." },
    "card-6": { id: "card-6", title: "QA micro-interactions", details: "Verify hover, focus, and loading states." },
    "card-7": { id: "card-7", title: "Ship marketing page", details: "Final copy approved and asset pack delivered." },
    "card-8": { id: "card-8", title: "Close onboarding sprint", details: "Document release notes and share internally." },
  },
};

test.beforeEach(async ({ request }) => {
  await request.put("/api/kanban", { data: INITIAL_BOARD });
});

async function login(page: Page) {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
}

// Sign-in tests

test("shows sign-in page at /", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  await expect(page.getByLabel("Username")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
});

test("rejects invalid credentials", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("wrong");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText("Invalid username or password.")).toBeVisible();
  await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
});

test("valid credentials show the kanban board", async ({ page }) => {
  await login(page);
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("sign out returns to sign-in page", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
});

// Kanban board tests

test("loads the kanban board", async ({ page }) => {
  await login(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("added card persists after page reload", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persisted card");
  await firstColumn.getByPlaceholder("Details").fill("Should survive reload.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persisted card")).toBeVisible();

  await page.reload();
  await expect(page.locator('[data-testid^="column-"]').first().getByText("Persisted card")).toBeVisible();
});

// AI chat tests

test("AI chat replies in the sidebar without changing the board", async ({ page }) => {
  await page.route("**/api/chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ response: "There are 8 cards.", board: null }),
    });
  });

  await login(page);
  await page.getByLabel("Chat message").fill("How many cards?");
  await page.getByRole("button", { name: /send/i }).click();
  await expect(page.getByTestId("chat-msg-assistant")).toHaveText("There are 8 cards.");
});

test("AI chat updates the board when the response includes one", async ({ page }) => {
  await page.route("**/api/chat", async (route) => {
    const updated = {
      ...INITIAL_BOARD,
      columns: INITIAL_BOARD.columns.map((col) =>
        col.id === "col-backlog"
          ? { ...col, cardIds: [...col.cardIds, "card-ai"] }
          : col
      ),
      cards: {
        ...INITIAL_BOARD.cards,
        "card-ai": { id: "card-ai", title: "AI generated card", details: "Done by AI." },
      },
    };
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ response: "Added it.", board: updated }),
    });
  });

  await login(page);
  await page.getByLabel("Chat message").fill("Add a card called AI generated card to Backlog");
  await page.getByRole("button", { name: /send/i }).click();

  await expect(page.getByTestId("chat-msg-assistant")).toHaveText("Added it.");
  await expect(
    page.getByTestId("column-col-backlog").getByText("AI generated card")
  ).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) throw new Error("Unable to resolve drag coordinates.");

  await page.mouse.move(cardBox.x + cardBox.width / 2, cardBox.y + cardBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(columnBox.x + columnBox.width / 2, columnBox.y + 120, { steps: 12 });
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});
