# Database Design

## Overview

SQLite, stored at `backend/kanban.db`. Created automatically on first startup. The full schema is in `docs/schema.json`.

## Tables

### users
One row per user. For the MVP this is a single seeded row (`username = "user"`).

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | auto-increment |
| username | TEXT UNIQUE | |
| created_at | TEXT | ISO-8601 via `datetime('now')` |

### boards
One board per user.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | auto-increment |
| user_id | INTEGER FK | → users(id) |
| title | TEXT | default "My Board" |
| created_at | TEXT | |

### columns
Ordered columns within a board.

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | slug e.g. `col-backlog` |
| board_id | INTEGER FK | → boards(id) |
| title | TEXT | editable display name |
| position | INTEGER | 0-based sort order |
| created_at | TEXT | |

### cards
Ordered cards within a column.

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT PK | slug e.g. `card-1` |
| column_id | TEXT FK | → columns(id) |
| title | TEXT | |
| details | TEXT | free-form notes |
| position | INTEGER | 0-based sort order within column |
| created_at | TEXT | |

## Relationships

```
users (1) ──── (many) boards
boards (1) ──── (many) columns
columns (1) ──── (many) cards
```

## Seed data

On first startup, if the user row does not exist, the backend seeds:
- 1 user: `username = "user"`
- 1 board: `title = "My Board"`
- 5 columns: Backlog, Discovery, In Progress, Review, Done
- 8 cards matching the frontend `initialData`

## Migration strategy

For this MVP there is only one schema version. Tables are created with `CREATE TABLE IF NOT EXISTS` on every startup — no destructive migrations needed. Future schema changes would be handled by numbered migration scripts run at startup.

## API shape

The backend API returns and accepts `BoardData` (matching the frontend type):

```json
{
  "columns": [
    { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"] }
  ],
  "cards": {
    "card-1": { "id": "card-1", "title": "Align roadmap themes", "details": "..." }
  }
}
```

The `position` column in the DB is the source of truth for ordering; `cardIds` arrays are derived from it when reading.
