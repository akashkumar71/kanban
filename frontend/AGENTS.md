# Frontend Code Description

This directory contains the Next.js 16 frontend for the Project Management MVP. It is built as a static export (`output: "export"`) and served by the FastAPI backend at `/`. All Kanban data and AI chat traffic flow through `/api/...` on the same origin.

## Project Structure

- **package.json**: Next.js, React, TypeScript, dnd-kit, Tailwind CSS 4, Vitest, Playwright, Testing Library.
- **next.config.ts**: Sets `output: "export"` so `next build` writes a static bundle to `out/`. Includes a dev-only rewrite of `/api/*` to `http://localhost:8000` for `next dev`.
- **playwright.config.ts**: Boots `uvicorn backend.main:app --port 8765` against `test-kanban.db` and runs specs in `tests/` against it.
- **vitest.config.ts**: jsdom environment, alias `@/` → `src/`, loads `src/test/setup.ts`.
- **tsconfig.json / eslint.config.mjs / postcss.config.mjs**: Standard config.

### src/ Directory

- **app/**: Next.js App Router.
  - **page.tsx**: Renders `<App />`.
  - **layout.tsx**: Root layout with global fonts and styles.
  - **globals.css**: Tailwind import plus the project color tokens (`--accent-yellow`, `--primary-blue`, `--secondary-purple`, `--navy-dark`, `--gray-text`, `--surface`, `--stroke`, `--shadow`).

- **components/**:
  - **App.tsx**: Top-level switch between sign-in and the board, driven by `isAuthenticated()`.
  - **SignInPage.tsx**: Username/password form. Validates against the dummy `"user"` / `"password"` credentials.
  - **KanbanBoard.tsx**: Owns board state. Loads from `GET /api/kanban` on mount, persists every mutation via `PUT /api/kanban`, renders the column grid, and mounts the `ChatSidebar`.
  - **KanbanColumn.tsx**: Single column with rename, drop target, and `NewCardForm`.
  - **KanbanCard.tsx**: Draggable card with title, details, and delete affordance.
  - **KanbanCardPreview.tsx**: Static visual used inside `DragOverlay` while a card is being dragged.
  - **NewCardForm.tsx**: Inline "add a card" form per column.
  - **ChatSidebar.tsx**: Collapsible right-side AI chat panel. Posts to `/api/chat` with the running history; if the response includes a `board`, calls `onBoardUpdate` to refresh the Kanban state in place.
  - **KanbanBoard.test.tsx / ChatSidebar.test.tsx**: Vitest + Testing Library suites with `fetch` stubbed.

- **lib/**:
  - **kanban.ts**: `BoardData` / `Column` / `Card` types, the seeded `initialData`, the pure `moveCard()` reorder logic, and `createId()`.
  - **api.ts**: `fetchBoard()`, `saveBoard()`, and `sendChat()` — the only place that talks to the backend.
  - **auth.ts**: localStorage-backed dummy auth (`signIn`, `signOut`, `isAuthenticated`).
  - **kanban.test.ts / auth.test.ts**: Unit tests for the pure logic.

- **test/**:
  - **setup.ts**: Imports `@testing-library/jest-dom`.
  - **vitest.d.ts**: Vitest matcher type declarations.

### tests/ Directory

- **kanban.spec.ts**: Playwright E2E covering sign-in, board load, add/persist, drag-drop, and the AI chat flow (mocking `/api/chat` so tests do not call OpenRouter).

## Key Features Implemented

- Dummy sign-in / sign-out gating the board.
- Kanban board with five columns, rename, drag-drop reorder across columns, add/delete cards.
- Persistence through the FastAPI backend's SQLite store.
- AI chat sidebar that can answer questions about the board and apply structured board updates that auto-refresh the UI.
- Tailwind 4 styling using the shared color tokens.
- Vitest unit tests and Playwright E2E tests against the real backend.

## Current State

The frontend is fully integrated with the backend. `npm run build` produces `out/`, which `backend/main.py` serves as the static site at `/`. AI features require `OPENROUTER_API_KEY` in the environment for the backend; the Playwright suite mocks the chat endpoint so it runs without a key.
