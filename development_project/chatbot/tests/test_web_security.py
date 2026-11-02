"""Access control and input handling at the HTTP boundary.

These are the tests I would want a reviewer to read first: they encode the
claims the report makes about who can download what.
"""

from datetime import timedelta

from .conftest import PASSWORDS, chat, login


def test_unauthenticated_requests_are_refused(client):
    assert client.get("/", follow_redirects=False).status_code == 303
    headers = {"X-Requested-With": "UniBot"}
    assert client.post("/api/chat", json={"message": "hi"}, headers=headers).status_code == 401
    assert client.get("/documents/anything").status_code == 401
    assert client.get("/assignments/A-IA-1/pdf").status_code == 401


def test_wrong_password_and_sql_injection_attempts_fail(client):
    bad = client.post("/login", data={"username": "amina", "password": "nope"}, follow_redirects=False)
    assert bad.status_code == 303 and "error" in bad.headers["location"]
    inj = client.post("/login", data={"username": "amina' OR '1'='1", "password": "x"},
                      follow_redirects=False)
    assert inj.status_code == 303 and "error" in inj.headers["location"]
    assert "unibot_session" not in inj.cookies


def test_chat_requires_custom_header_and_strict_body(client):
    login(client, "amina")
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 403
    assert client.post("/api/chat", json={"message": "hi", "student_id": "S1002"},
                       headers={"X-Requested-With": "UniBot"}).status_code == 422
    assert client.post("/api/chat", json={"message": "x" * 1001},
                       headers={"X-Requested-With": "UniBot"}).status_code == 422


def test_security_headers_present(client):
    response = client.get("/login")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_transcript_download_is_owner_only(app, client):
    login(client, "amina")
    reply = chat(client, "my transcript please")
    url = reply["cards"][0]["url"]
    ok = client.get(url)
    assert ok.status_code == 200 and ok.headers["content-type"] == "application/pdf"
    assert ok.content.startswith(b"%PDF")
    # Another signed-in student with the copied link
    from fastapi.testclient import TestClient
    other = TestClient(app)
    login(other, "ben")
    assert other.get(url).status_code == 404
    # An invented identifier
    assert client.get("/documents/not-a-real-id").status_code == 404
    # After logout the owner cannot fetch it either
    client.post("/logout", follow_redirects=False)
    assert client.get(url).status_code == 401


def test_assignment_download_checks_enrolment_deadline_and_path(client, clock):
    login(client, "amina")
    assert client.get("/assignments/A-IA-1/pdf").status_code == 200
    assert client.get("/assignments/A-NIS-1/pdf").status_code == 404      # not enrolled
    assert client.get("/assignments/A-RM-1/pdf").status_code == 404       # deadline passed
    assert client.get("/assignments/..%2F..%2Fetc%2Fpasswd/pdf").status_code == 404
    assert client.get("/assignments/A-IA-1'; DROP TABLE assignments;--/pdf").status_code == 404
    clock.advance_to(clock.now() + timedelta(days=13))
    login(client, "amina")  # the old session has expired too, which is correct
    assert client.get("/assignments/A-IA-1/pdf").status_code == 404       # expired since listing


def test_session_expiry_logs_student_out(client, clock):
    login(client, "amina")
    assert chat(client, "hello")["intent"] == "greeting"
    clock.advance_to(clock.now() + timedelta(minutes=31))
    headers = {"X-Requested-With": "UniBot"}
    assert client.post("/api/chat", json={"message": "hi"}, headers=headers).status_code == 401


def test_full_conversation_over_http(client):
    login(client, "amina")
    assert chat(client, "hi")["intent"] == "greeting"
    timetable = chat(client, "when are my classes?")
    assert timetable["cards"][0]["type"] == "timetable" and len(timetable["cards"][0]["events"]) == 4
    assert timetable["trace"][0]["performative"] == "ask-one"
    listing = chat(client, "which assignments are still open")
    assert len(listing["cards"][0]["items"]) == 3
    pick = chat(client, "the first one please")
    assert pick["cards"][0]["url"] == "/assignments/A-ML-1/pdf"
    assert client.get(pick["cards"][0]["url"]).status_code == 200
    assert chat(client, "cheers, bye")["ended"] is True


def test_trace_never_exposes_server_paths(app, client):
    """The agent-message panel shows every reply; none may contain a filesystem path."""
    login(client, "amina")
    documents_dir = str(app.state.ctx.settings.documents_dir)
    for text in ("timetable", "transcript please", "list my assignments", "download the first one"):
        reply = chat(client, text)
        assert documents_dir not in str(reply) and "/Users/" not in str(reply) and "\\" not in str(reply)


def test_passwords_are_hashed_not_stored(app):
    row = app.state.ctx.repo.student_by_username("amina")
    assert PASSWORDS["amina"] not in row["password_hash"] and "$" in row["password_hash"]
