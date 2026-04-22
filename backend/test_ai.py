import os
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    yield


def _mock_response(status_code=200, json_data=None, text=""):
    resp = AsyncMock()
    resp.status_code = status_code
    resp.json = lambda: json_data
    resp.text = text
    return resp


@pytest.mark.asyncio
async def test_ask_returns_content():
    from backend import ai

    mock_resp = _mock_response(200, {"choices": [{"message": {"content": "4"}}]})
    with patch("backend.ai.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        result = await ai.ask("What is 2+2?")
    assert result == "4"


@pytest.mark.asyncio
async def test_ask_raises_on_non_200():
    from backend import ai

    mock_resp = _mock_response(401, {}, text="Unauthorized")
    with patch("backend.ai.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        with pytest.raises(ai.AIRequestError):
            await ai.ask("hi")


@pytest.mark.asyncio
async def test_ask_raises_on_bad_shape():
    from backend import ai

    mock_resp = _mock_response(200, {"unexpected": "shape"})
    with patch("backend.ai.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        with pytest.raises(ai.AIRequestError):
            await ai.ask("hi")


@pytest.mark.asyncio
async def test_ask_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from backend import ai

    with pytest.raises(ai.AIConfigError):
        await ai.ask("hi")


def test_ai_test_endpoint_returns_response(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    from backend import database, ai
    from backend.main import app
    from fastapi.testclient import TestClient

    database.init_db()

    async def fake_ask(prompt, model=ai.DEFAULT_MODEL):
        assert "2+2" in prompt
        return "4"

    with patch("backend.ai.ask", side_effect=fake_ask):
        with TestClient(app) as client:
            r = client.get("/api/ai-test")

    assert r.status_code == 200
    assert r.json() == {"response": "4"}


def test_ai_test_endpoint_returns_502_on_request_error(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    from backend import database, ai
    from backend.main import app
    from fastapi.testclient import TestClient

    database.init_db()

    async def failing_ask(prompt, model=ai.DEFAULT_MODEL):
        raise ai.AIRequestError("boom")

    with patch("backend.ai.ask", side_effect=failing_ask):
        with TestClient(app) as client:
            r = client.get("/api/ai-test")

    assert r.status_code == 502


# Chat helper tests

def test_parse_chat_json_plain():
    from backend import ai

    parsed = ai._parse_chat_json('{"response": "hi", "board_update": null}')
    assert parsed == {"response": "hi", "board_update": None}


def test_parse_chat_json_with_fence():
    from backend import ai

    parsed = ai._parse_chat_json('```json\n{"response": "ok", "board_update": null}\n```')
    assert parsed["response"] == "ok"


def test_parse_chat_json_missing_response_field():
    from backend import ai

    with pytest.raises(ai.AIRequestError):
        ai._parse_chat_json('{"only": "stuff"}')


def test_parse_chat_json_invalid_json():
    from backend import ai

    with pytest.raises(ai.AIRequestError):
        ai._parse_chat_json("not json at all")


@pytest.mark.asyncio
async def test_chat_sends_board_and_history():
    from backend import ai

    captured = {}

    async def fake_post(payload, timeout=30.0):
        captured["payload"] = payload
        return {
            "choices": [
                {"message": {"content": '{"response": "ack", "board_update": null}'}}
            ]
        }

    with patch("backend.ai._post", side_effect=fake_post):
        result = await ai.chat(
            "hello",
            {"columns": [], "cards": {}},
            history=[{"role": "user", "content": "earlier"},
                     {"role": "assistant", "content": "earlier reply"}],
        )

    assert result == {"response": "ack", "board_update": None}
    msgs = captured["payload"]["messages"]
    assert msgs[0]["role"] == "system"
    assert "Current board JSON" in msgs[1]["content"]
    assert msgs[2] == {"role": "user", "content": "earlier"}
    assert msgs[3] == {"role": "assistant", "content": "earlier reply"}
    assert msgs[-1] == {"role": "user", "content": "hello"}
    assert captured["payload"]["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_chat_filters_invalid_history_entries():
    from backend import ai

    captured = {}

    async def fake_post(payload, timeout=30.0):
        captured["payload"] = payload
        return {
            "choices": [
                {"message": {"content": '{"response": "ok", "board_update": null}'}}
            ]
        }

    with patch("backend.ai._post", side_effect=fake_post):
        await ai.chat(
            "hi",
            {"columns": [], "cards": {}},
            history=[
                {"role": "system", "content": "no"},
                {"role": "user", "content": 123},
                {"role": "user", "content": "yes"},
            ],
        )

    msgs = captured["payload"]["messages"]
    user_assistant_msgs = [m for m in msgs[2:-1]]
    assert user_assistant_msgs == [{"role": "user", "content": "yes"}]


# /api/chat endpoint tests

EMPTY_BOARD = {"columns": [], "cards": {}}


def _setup_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    from backend import database
    from backend.main import app
    from fastapi.testclient import TestClient

    database.init_db()
    return TestClient(app)


def test_chat_endpoint_returns_response_only(tmp_path, monkeypatch):
    from backend import ai

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        assert message == "How many cards are there?"
        return {"response": "There are 8.", "board_update": None}

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post("/api/chat", json={"message": "How many cards are there?"})

    assert r.status_code == 200
    body = r.json()
    assert body == {"response": "There are 8.", "board": None}


def test_chat_endpoint_applies_board_update(tmp_path, monkeypatch):
    from backend import ai

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        new = {
            "columns": [
                {"id": col["id"], "title": col["title"], "cardIds": col["cardIds"]}
                for col in board["columns"]
            ],
            "cards": dict(board["cards"]),
        }
        # Add a new card to first column
        new_id = "card-new"
        new["cards"][new_id] = {"id": new_id, "title": "AI added", "details": "from AI"}
        new["columns"][0]["cardIds"] = list(new["columns"][0]["cardIds"]) + [new_id]
        return {"response": "Added.", "board_update": new}

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post("/api/chat", json={"message": "Add a card called AI added."})

    assert r.status_code == 200
    body = r.json()
    assert body["response"] == "Added."
    assert body["board"] is not None
    assert "card-new" in body["board"]["cards"]
    assert body["board"]["cards"]["card-new"]["title"] == "AI added"

    # Confirm persistence
    follow = client.get("/api/kanban").json()
    assert "card-new" in follow["cards"]


def test_chat_endpoint_rejects_malformed_board_update(tmp_path, monkeypatch):
    from backend import ai

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        return {"response": "oops", "board_update": {"columns": "nope"}}

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post("/api/chat", json={"message": "break things"})

    assert r.status_code == 502


def test_chat_endpoint_502_on_ai_error(tmp_path, monkeypatch):
    from backend import ai

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        raise ai.AIRequestError("upstream failed")

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post("/api/chat", json={"message": "hi"})

    assert r.status_code == 502


def test_chat_endpoint_500_on_missing_api_key(tmp_path, monkeypatch):
    from backend import ai

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        raise ai.AIConfigError("OPENROUTER_API_KEY is not set")

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post("/api/chat", json={"message": "hi"})

    assert r.status_code == 500


def test_chat_endpoint_passes_history(tmp_path, monkeypatch):
    from backend import ai

    captured = {}

    async def fake_chat(message, board, history, model=ai.DEFAULT_MODEL):
        captured["history"] = history
        return {"response": "ok", "board_update": None}

    with patch("backend.ai.chat", side_effect=fake_chat):
        client = _setup_app(tmp_path, monkeypatch)
        r = client.post(
            "/api/chat",
            json={
                "message": "and now?",
                "history": [
                    {"role": "user", "content": "first"},
                    {"role": "assistant", "content": "reply"},
                ],
            },
        )

    assert r.status_code == 200
    assert captured["history"] == [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "reply"},
    ]
