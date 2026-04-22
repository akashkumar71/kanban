# Kanban Studio

A single-board Kanban application with an AI chat assistant. Cards persist in SQLite, the AI can read and modify the board in natural language, and the entire stack runs in a single Docker container.

## Features

- Drag-and-drop cards across five columns (Backlog, Discovery, In Progress, Review, Done)
- Inline card creation and deletion; column titles are editable
- AI sidebar powered by Claude via OpenRouter — ask questions or issue commands that update the board in real time
- SQLite persistence — board state survives container restarts
- Fake sign-in gate (username: `user`, password: `password`) for MVP access control

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React, Tailwind CSS 4, dnd-kit |
| Backend | FastAPI, Python 3.11, SQLite |
| AI | OpenRouter API (Claude Haiku 4.5 by default) |
| Container | Docker (multi-stage build) |

## Prerequisites

- Docker
- An [OpenRouter](https://openrouter.ai) API key

## Running with Docker

**1. Create a `.env` file in the project root:**

```
OPENROUTER_API_KEY=your-key-here
```

**2. Build and start the container:**

Windows (PowerShell):
```powershell
.\scripts\start-pc.ps1
```

Mac / Linux:
```bash
bash scripts/start-mac.sh
# or
bash scripts/start-linux.sh
```

Or manually:
```bash
docker build -t pm-app .
docker run -d --name pm-container -p 8000:8000 \
  --env-file .env \
  pm-app
```

**3. Open `http://localhost:8000` in a browser.**

**4. Stop the container:**

```powershell
.\scripts\stop-pc.ps1
```
```bash
bash scripts/stop-mac.sh
```

## Running locally without Docker

**Backend** (from repo root, requires Python 3.11+ and a virtual environment):

```bash
pip install fastapi uvicorn aiofiles httpx python-dotenv
uvicorn backend.main:app --reload --port 8000
```

**Frontend dev server** (from `frontend/`):

```bash
npm install
npx next dev
```

The dev server runs on `http://localhost:3000`. For the backend to serve the built frontend at `http://localhost:8000`, build the frontend first:

```bash
cd frontend && npm run build
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/kanban` | Fetch the current board |
| PUT | `/api/kanban` | Replace the board with a new state |
| POST | `/api/chat` | Send a chat message; returns a reply and optional board update |
| GET | `/api/ai-test` | Smoke-test the OpenRouter connection |

## Running tests

All commands run from `frontend/`.

```bash
# Unit tests (Vitest)
npx vitest run

# E2E tests (Playwright — requires dev server on :3000)
npx playwright test

# All tests
npm run test:all
```

Backend tests (from repo root):

```bash
python -m pytest backend/ -q
```

## Project structure

```
.
├── backend/
│   ├── main.py          # FastAPI app and API routes
│   ├── database.py      # SQLite connection and board persistence
│   ├── ai.py            # OpenRouter client and chat logic
│   ├── test_main.py     # API route tests
│   └── test_ai.py       # AI module tests
├── frontend/
│   ├── src/
│   │   ├── app/         # Next.js App Router entry point
│   │   ├── components/  # KanbanBoard, ChatSidebar, SignInPage, etc.
│   │   └── lib/         # Board types, pure logic, API client, auth
│   └── tests/           # Playwright E2E specs
├── docs/
│   ├── PLAN.md          # Build plan and progress tracking
│   ├── DATABASE.md      # Schema design and rationale
│   └── schema.json      # SQLite schema as JSON
├── scripts/             # Docker start/stop for Mac, PC, Linux
└── Dockerfile           # Multi-stage: Node build then Python serve
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | API key from openrouter.ai |
| `DB_PATH` | No | Path to the SQLite database file (default: `kanban.db`) |
