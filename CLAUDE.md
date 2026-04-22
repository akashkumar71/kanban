# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A Project Management MVP — a Kanban board web app with AI chat. A signed-in user sees one board with draggable, editable cards. An AI sidebar can create/edit/move cards. Runs locally in Docker.

Read `AGENTS.md` for business requirements and technical decisions. Read `docs/PLAN.md` before doing any work — it defines the 10-part build plan and tracks progress.

## Running locally (without Docker)

**Backend** (from repo root):
```
.venv/Scripts/uvicorn backend.main:app --reload --port 8000
```

**Frontend dev server** (from `frontend/`):
```
npx next dev
```

The backend serves the built frontend at `/`. For the backend to serve the Kanban board, the frontend must be built first (see below).

## Key commands

All frontend commands run from `frontend/`.

**Build frontend static export:**
```
npx next build
# outputs to frontend/out/
```

**Unit tests (Vitest):**
```
npx vitest run                    # all unit tests
npx vitest run src/lib/kanban     # single test file
```

**E2E tests (Playwright — requires dev server on :3000):**
```
npx playwright test               # all E2E tests
npx playwright test kanban        # single spec file
```

**Run all tests:**
```
npm run test:all
```

## Architecture

```
repo root
├── backend/main.py          # FastAPI app — serves frontend/out/ at / and API at /api/
├── backend/pyproject.toml   # Python deps (fastapi, uvicorn, aiofiles)
├── frontend/                # Next.js 16 app (static export via output: "export")
│   ├── src/app/             # Next.js App Router — single page at /
│   ├── src/components/      # KanbanBoard, KanbanColumn, KanbanCard, etc.
│   ├── src/lib/kanban.ts    # All board data types and pure logic (moveCard, etc.)
│   └── tests/               # Playwright E2E specs
├── Dockerfile               # Multi-stage: node build → python serve
└── scripts/                 # start/stop scripts for Mac, PC, Linux
```

**Data flow:** `kanban.ts` owns the `BoardData` type (`columns[]` + `cards{}` record). `KanbanBoard` holds the state; all mutations go through handlers passed down as props.

**Static serving:** `next.config.ts` sets `output: "export"`. `npm run build` writes to `frontend/out/`. `backend/main.py` has a catch-all `/{full_path:path}` route that serves files from `frontend/out/` (falls back to `index.html`). API routes (`/api/...`) are defined before the catch-all.

**Docker:** Multi-stage Dockerfile — stage 1 runs `npm ci && next build`, stage 2 is `python:3.11-slim` with FastAPI, copies `frontend/out` from stage 1.

## Python environment

The `.venv` at repo root is the dev venv. In Docker, `uv` is used as the package manager.

## Styling

Tailwind CSS 4 with PostCSS. Color tokens defined in `src/app/globals.css` as CSS variables: `--accent-yellow`, `--primary-blue`, `--purple-secondary`, `--navy-dark`, `--gray-text`.
