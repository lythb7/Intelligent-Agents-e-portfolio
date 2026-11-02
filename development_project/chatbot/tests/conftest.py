"""Shared fixtures: a seeded database in a temporary directory, a frozen clock
and a web client. Nothing here touches the network or the real data folder."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from unibot.app_context import build_context
from unibot.clock import FixedClock
from unibot.config import Settings
from unibot.db import connect, seed
from unibot.web import create_app

FROZEN = datetime(2026, 3, 2, 12, 0, 0, tzinfo=timezone.utc)
PASSWORDS = {"amina": "amina-test-pass", "ben": "ben-test-pass"}


@pytest.fixture
def settings(tmp_path) -> Settings:
    data_dir = tmp_path / "data"
    return Settings(
        data_dir=data_dir, database_path=data_dir / "test.sqlite3",
        documents_dir=data_dir / "documents", llm_enabled=False,
        llm_model="unused", llm_timeout_seconds=1.0, session_ttl_minutes=30,
        fake_now=FROZEN.isoformat(),
    )


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(FROZEN)


@pytest.fixture
def seeded(settings, clock):
    conn = connect(settings.database_path)
    seed(conn, settings.documents_dir, clock, PASSWORDS)
    conn.close()
    return settings


@pytest.fixture
def ctx(seeded, clock):
    return build_context(seeded, clock)


@pytest.fixture
def app(seeded, clock):
    return create_app(seeded, clock)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def login(client: TestClient, username: str) -> None:
    response = client.post("/login", data={"username": username, "password": PASSWORDS[username]},
                           follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/"


def chat(client: TestClient, text: str) -> dict:
    response = client.post("/api/chat", json={"message": text}, headers={"X-Requested-With": "UniBot"})
    assert response.status_code == 200, response.text
    return response.json()
