"""FastAPI front end.

The web layer does three jobs and nothing else: authenticate the browser,
pass the student's text to the dialogue agent, and serve files only after
re-checking that the session's student owns them. Every download route goes
back to the database; the chat reply's link is a convenience, not a
capability, so a copied URL in another student's browser returns 404.
"""

from __future__ import annotations

import logging
import os
import socket
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from . import __version__, auth
from .app_context import build_context
from .clock import Clock
from .config import PACKAGE_DIR, Settings
from .interpreters import Interpreter

log = logging.getLogger(__name__)
COOKIE = "unibot_session"


class ChatRequest(BaseModel):
    """Only one field, bounded; anything else in the body is rejected."""

    message: str = Field(min_length=1, max_length=1000)

    model_config = {"extra": "forbid"}


def create_app(  # pylint: disable=too-many-locals
    settings: Settings | None = None, clock: Clock | None = None, interpreter: Interpreter | None = None,
) -> FastAPI:
    """Application factory. Routes are closures so tests can inject a clock and interpreter."""
    ctx = build_context(settings, clock, interpreter)
    app = FastAPI(title="UniBot", version=__version__, docs_url=None, redoc_url=None)
    app.state.ctx = ctx
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")

    def current_session(request: Request):
        session = ctx.sessions.get(request.cookies.get(COOKIE))
        if session is None:
            raise HTTPException(status_code=401, detail="Please sign in.")
        return session

    def current_student(session=Depends(current_session)) -> dict:
        row = ctx.repo.student(session.student_id)
        if row is None:  # pragma: no cover - would need a deleted student
            raise HTTPException(status_code=401, detail="Please sign in.")
        return dict(row)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        session = ctx.sessions.get(request.cookies.get(COOKIE))
        if session is None:
            return RedirectResponse("/login", status_code=303)
        student = dict(ctx.repo.student(session.student_id))
        return templates.TemplateResponse(request, "chat.html", {
            "student": student,
            "interpreter": type(ctx.dialogue.interpreter).__name__,
        })

    @app.get("/login", response_class=HTMLResponse)
    def login_form(request: Request, error: str | None = None):
        return templates.TemplateResponse(request, "login.html", {"error": error})

    @app.post("/login")
    def login(username: str = Form(...), password: str = Form(...)):
        row = ctx.repo.student_by_username(username.strip().lower())
        # The same failure message for unknown user and wrong password avoids
        # confirming which usernames exist.
        if row is None or not auth.verify_password(password, row["password_hash"]):
            log.info("failed login for %r", username)
            return RedirectResponse("/login?error=Invalid+username+or+password", status_code=303)
        token = ctx.sessions.create(row["student_id"])
        response = RedirectResponse("/", status_code=303)
        # HttpOnly keeps the token away from page scripts; SameSite=Strict
        # means cross-site pages cannot ride on the session. ``secure`` is
        # deliberately off because the prototype runs on plain localhost.
        response.set_cookie(COOKIE, token, httponly=True, samesite="strict",
                            max_age=ctx.settings.session_ttl_minutes * 60)
        return response

    @app.post("/logout")
    def logout(request: Request):
        ctx.sessions.revoke(request.cookies.get(COOKIE))
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(COOKIE)
        return response

    @app.post("/api/chat")
    def chat(body: ChatRequest, request: Request, session=Depends(current_session),
             student=Depends(current_student)):
        # Defence against cross-site form posts: browsers cannot add custom
        # headers cross-origin without a CORS pre-flight, which this app
        # never grants.
        if request.headers.get("x-requested-with") != "UniBot":
            raise HTTPException(status_code=403, detail="Bad request origin.")
        reply = ctx.dialogue.respond(student, session.state, body.message)
        return JSONResponse({
            "text": reply.text, "cards": reply.cards, "intent": reply.intent,
            "intent_source": reply.intent_source, "trace": reply.trace, "ended": reply.ended,
        })

    @app.get("/documents/{document_id}")
    def download_document(document_id: str, session=Depends(current_session)):
        record = ctx.repo.document_for_student(session.student_id, document_id)
        path = Path(record["file_path"]) if record else None
        # Unauthorised and missing look identical from outside, on purpose.
        if path is None or not path.is_file():
            raise HTTPException(status_code=404, detail="Document not found.")
        return FileResponse(path, media_type="application/pdf", filename=path.name)

    @app.get("/assignments/{assignment_id}/pdf")
    def download_assignment(assignment_id: str, session=Depends(current_session)):
        record = ctx.repo.assignment_for_student(session.student_id, assignment_id)
        if record is None or record["deadline"] < ctx.clock.now():
            raise HTTPException(status_code=404, detail="Document not found.")
        # The path comes from the database row, never from the URL, so there
        # is no way to traverse to another file.
        path = Path(record["brief_path"])
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Document not found.")
        return FileResponse(path, media_type="application/pdf", filename=f"{assignment_id}.pdf")

    return app


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def choose_port(requested: str | None, first: int = 8000, last: int = 8020) -> tuple[int, str]:
    """Pick the port to serve on.

    An explicit ``UNIBOT_PORT`` is honoured or refused with a clear message;
    otherwise the first free port from ``first`` upwards is used, with a note
    when it is not the default, so the user knows which address to open.
    """
    if requested:
        port = int(requested)
        if not _port_is_free(port):
            raise SystemExit(f"UniBot: port {port} (UNIBOT_PORT) is already in use.")
        return port, ""
    for port in range(first, last + 1):
        if _port_is_free(port):
            note = "" if port == first else f"Port {first} is in use, so UniBot is using {port} instead."
            return port, note
    raise SystemExit(f"UniBot: no free port between {first} and {last}; set UNIBOT_PORT.")


def run() -> None:  # pragma: no cover - convenience entry point
    # Only needed when serving, so it is not a hard dependency of the tests.
    import uvicorn  # pylint: disable=import-outside-toplevel

    settings = Settings.from_env()
    if not Path(settings.database_path).is_file():
        raise SystemExit(
            f"UniBot: no database at {settings.database_path}. "
            "Run 'python -m unibot.seed --reset' first, then start the server again."
        )
    port, note = choose_port(os.environ.get("UNIBOT_PORT"))
    if note:
        print(note, flush=True)
    print(f"UniBot is running at http://127.0.0.1:{port}  (press Ctrl+C to stop)", flush=True)
    uvicorn.run(create_app(settings), host="127.0.0.1", port=port)


if __name__ == "__main__":  # pragma: no cover
    run()
