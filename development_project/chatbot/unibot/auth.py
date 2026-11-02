"""Password hashing and server-side sessions.

A typed student number is an *identifier*, not a credential, so the prototype
requires a password and binds the browser to a server-side session. The
session token is random, stored only as a hash, and expires. This is the
minimum needed to make the ownership checks on downloads meaningful; a real
deployment would sit behind the university's single sign-on instead.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .clock import Clock

_PBKDF2_ROUNDS = 200_000


def hash_password(password: str, salt: bytes | None = None) -> str:
    """PBKDF2-HMAC-SHA256; the standard library is enough for a prototype."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), _PBKDF2_ROUNDS
    )
    # Constant-time comparison so timing does not leak how many bytes matched.
    return hmac.compare_digest(candidate.hex(), digest_hex)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass
class Session:
    """An authenticated browser, bound to one student until it expires."""

    student_id: str
    expires_at: datetime
    # Dialogue state lives here so that it is cleared with the session and
    # never leaks between students (see DialogueAgent).
    state: dict[str, Any]


class SessionStore:
    """In-memory sessions keyed by the hash of the browser token."""

    def __init__(self, clock: Clock, ttl: timedelta) -> None:
        self._clock = clock
        self._ttl = ttl
        self._sessions: dict[str, Session] = {}

    def create(self, student_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[_token_hash(token)] = Session(
            student_id=student_id,
            expires_at=self._clock.now() + self._ttl,
            state={},
        )
        return token

    def get(self, token: str | None) -> Session | None:
        if not token:
            return None
        session = self._sessions.get(_token_hash(token))
        if session is None:
            return None
        if session.expires_at <= self._clock.now():
            # Expired sessions are removed on first touch rather than by a
            # background sweeper, which keeps the prototype single-threaded.
            del self._sessions[_token_hash(token)]
            return None
        return session

    def revoke(self, token: str | None) -> None:
        if token:
            self._sessions.pop(_token_hash(token), None)
