import sqlite3
import os

INITIAL_DATA: dict = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
        "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
        "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
        "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
        "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
        "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
        "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
        "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."},
    },
}


def _connect() -> sqlite3.Connection:
    path = os.environ.get("DB_PATH", "kanban.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL DEFAULT 'My Board',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS columns (
                id TEXT PRIMARY KEY,
                board_id INTEGER NOT NULL REFERENCES boards(id),
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                column_id TEXT NOT NULL REFERENCES columns(id),
                title TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        if conn.execute("SELECT id FROM users WHERE username = 'user'").fetchone() is None:
            conn.execute("INSERT INTO users (username) VALUES ('user')")
            conn.execute("INSERT INTO boards (user_id, title) VALUES (1, 'My Board')")
            _insert_board_data(conn, board_id=1, data=INITIAL_DATA)
        conn.commit()
    finally:
        conn.close()


def _insert_board_data(conn: sqlite3.Connection, board_id: int, data: dict) -> None:
    for pos, col in enumerate(data["columns"]):
        conn.execute(
            "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
            (col["id"], board_id, col["title"], pos),
        )
        for card_pos, card_id in enumerate(col["cardIds"]):
            card = data["cards"][card_id]
            conn.execute(
                "INSERT INTO cards (id, column_id, title, details, position) VALUES (?, ?, ?, ?, ?)",
                (card["id"], col["id"], card["title"], card["details"], card_pos),
            )


def get_board(username: str = "user") -> dict:
    conn = _connect()
    try:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        board = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user["id"],)).fetchone()
        cols = conn.execute(
            "SELECT id, title FROM columns WHERE board_id = ? ORDER BY position",
            (board["id"],),
        ).fetchall()

        result_columns = []
        cards_dict: dict = {}
        for col in cols:
            cards = conn.execute(
                "SELECT id, title, details FROM cards WHERE column_id = ? ORDER BY position",
                (col["id"],),
            ).fetchall()
            card_ids = []
            for card in cards:
                cards_dict[card["id"]] = {
                    "id": card["id"],
                    "title": card["title"],
                    "details": card["details"],
                }
                card_ids.append(card["id"])
            result_columns.append({"id": col["id"], "title": col["title"], "cardIds": card_ids})

        return {"columns": result_columns, "cards": cards_dict}
    finally:
        conn.close()


def save_board(board_data: dict, username: str = "user") -> None:
    conn = _connect()
    try:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        board = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user["id"],)).fetchone()
        board_id = board["id"]

        conn.execute(
            "DELETE FROM cards WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?)",
            (board_id,),
        )
        conn.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))
        _insert_board_data(conn, board_id, board_data)
        conn.commit()
    finally:
        conn.close()
