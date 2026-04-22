import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-haiku-4.5"

CHAT_SYSTEM_PROMPT = """You are an assistant inside a Kanban board project management tool.
The user sees one board with five fixed columns and a set of cards. You can answer questions
about the board or apply changes to it.

You MUST reply with a single JSON object matching this schema:
{
  "response": "<a short plain-language reply for the user>",
  "board_update": <null OR a complete updated board object>
}

The board has the shape:
{
  "columns": [{"id": "<col-id>", "title": "<title>", "cardIds": ["<card-id>", ...]}, ...],
  "cards":   {"<card-id>": {"id": "<card-id>", "title": "<title>", "details": "<details>"}, ...}
}

Rules:
- If the user is only asking a question, set "board_update" to null.
- If the user wants to add, edit, move, rename, or delete cards/columns, return a fully updated
  board in "board_update" reflecting the change. The shape and existing column ids must be
  preserved; cards may be added/removed.
- New card ids must start with "card-" and be unique. Reuse existing ids when editing.
- Every cardIds entry must reference a card present in the "cards" map, and vice versa.
- Reply with ONLY the JSON object. No markdown fences, no commentary."""


class AIConfigError(RuntimeError):
    pass


class AIRequestError(RuntimeError):
    pass


def _api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise AIConfigError("OPENROUTER_API_KEY is not set")
    return key


async def _post(payload: dict, timeout: float = 30.0) -> dict:
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(OPENROUTER_URL, json=payload, headers=headers)
    if r.status_code != 200:
        raise AIRequestError(f"OpenRouter returned {r.status_code}: {r.text}")
    return r.json()


def _extract_content(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIRequestError(f"Unexpected response shape: {data}") from e


async def ask(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 1024) -> str:
    data = await _post({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    })
    return _extract_content(data)


def _parse_chat_json(content: str) -> dict:
    text = content.strip()
    # Strip ```json ... ``` fences if the model wrapped its reply.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise AIRequestError(f"AI response was not valid JSON: {content}") from e
    if not isinstance(parsed, dict) or "response" not in parsed:
        raise AIRequestError(f"AI response missing 'response' field: {content}")
    return {
        "response": str(parsed["response"]),
        "board_update": parsed.get("board_update"),
    }


async def chat(
    user_message: str,
    board: dict,
    history: list[dict] | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> dict:
    """Returns {"response": str, "board_update": dict | None}."""
    messages: list[dict] = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Current board JSON:\n{json.dumps(board)}"},
    ]
    for entry in history or []:
        role = entry.get("role")
        content = entry.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    data = await _post(
        {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
        },
        timeout=60.0,
    )
    return _parse_chat_json(_extract_content(data))
