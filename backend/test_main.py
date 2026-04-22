import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    from backend import database
    database.init_db()
    yield
    del os.environ["DB_PATH"]


@pytest.fixture
def client(isolated_db):
    from backend.main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_get_kanban_returns_board(client):
    r = client.get("/api/kanban")
    assert r.status_code == 200
    data = r.json()
    assert "columns" in data
    assert "cards" in data


def test_get_kanban_has_five_columns(client):
    data = client.get("/api/kanban").json()
    assert len(data["columns"]) == 5


def test_get_kanban_has_eight_cards(client):
    data = client.get("/api/kanban").json()
    assert len(data["cards"]) == 8


def test_get_kanban_column_order(client):
    data = client.get("/api/kanban").json()
    ids = [c["id"] for c in data["columns"]]
    assert ids == ["col-backlog", "col-discovery", "col-progress", "col-review", "col-done"]


def test_get_kanban_card_in_correct_column(client):
    data = client.get("/api/kanban").json()
    backlog = next(c for c in data["columns"] if c["id"] == "col-backlog")
    assert "card-1" in backlog["cardIds"]
    assert "card-2" in backlog["cardIds"]


def test_put_kanban_persists_changes(client):
    original = client.get("/api/kanban").json()

    # Move card-1 from backlog to done
    updated = {
        "columns": [
            {**col, "cardIds": [cid for cid in col["cardIds"] if cid != "card-1"]}
            if col["id"] == "col-backlog"
            else ({**col, "cardIds": col["cardIds"] + ["card-1"]}
                  if col["id"] == "col-done" else col)
            for col in original["columns"]
        ],
        "cards": original["cards"],
    }

    r = client.put("/api/kanban", json=updated)
    assert r.status_code == 200

    saved = client.get("/api/kanban").json()
    done_col = next(c for c in saved["columns"] if c["id"] == "col-done")
    backlog_col = next(c for c in saved["columns"] if c["id"] == "col-backlog")
    assert "card-1" in done_col["cardIds"]
    assert "card-1" not in backlog_col["cardIds"]


def test_put_kanban_persists_renamed_column(client):
    original = client.get("/api/kanban").json()
    original["columns"][0]["title"] = "Renamed"
    client.put("/api/kanban", json=original)
    saved = client.get("/api/kanban").json()
    assert saved["columns"][0]["title"] == "Renamed"


def test_put_kanban_invalid_body_returns_422(client):
    r = client.put("/api/kanban", json={"wrong": "data"})
    assert r.status_code == 422


def test_api_test_endpoint_still_works(client):
    # /api/test was removed; kanban endpoint is the new health check
    r = client.get("/api/kanban")
    assert r.status_code == 200
