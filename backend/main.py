import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from backend.database import init_db, get_board, save_board
from backend import ai

STATIC_DIR = "frontend/out"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/kanban")
def read_kanban():
    return get_board()


@app.put("/api/kanban")
def write_kanban(board: dict):
    if "columns" not in board or "cards" not in board:
        raise HTTPException(status_code=422, detail="Missing columns or cards")
    save_board(board)
    return get_board()


@app.get("/api/ai-test")
async def ai_test():
    try:
        response = await ai.ask("What is 2+2? Reply with just the number.")
    except ai.AIConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ai.AIRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"response": response}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


def _is_valid_board(payload) -> bool:
    if not isinstance(payload, dict):
        return False
    cols = payload.get("columns")
    cards = payload.get("cards")
    if not isinstance(cols, list) or not isinstance(cards, dict):
        return False
    referenced: set[str] = set()
    for col in cols:
        if not isinstance(col, dict):
            return False
        if not all(k in col for k in ("id", "title", "cardIds")):
            return False
        if not isinstance(col["cardIds"], list):
            return False
        referenced.update(col["cardIds"])
    for card_id, card in cards.items():
        if not isinstance(card, dict):
            return False
        if not all(k in card for k in ("id", "title", "details")):
            return False
        if card["id"] != card_id:
            return False
    return referenced.issubset(cards.keys())


@app.post("/api/chat")
async def chat(req: ChatRequest):
    board = get_board()
    history = [m.model_dump() for m in req.history]
    try:
        result = await ai.chat(req.message, board, history)
    except ai.AIConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ai.AIRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))

    update = result.get("board_update")
    if update is None:
        return {"response": result["response"], "board": None}

    if not _is_valid_board(update):
        raise HTTPException(status_code=502, detail="AI returned malformed board update")

    save_board(update)
    return {"response": result["response"], "board": get_board()}


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    target = os.path.join(STATIC_DIR, full_path) if full_path else f"{STATIC_DIR}/index.html"
    if os.path.isfile(target):
        return FileResponse(target)
    return FileResponse(f"{STATIC_DIR}/index.html")
