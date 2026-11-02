"""Runtime configuration.

Settings are read from environment variables, optionally pre-loaded from a
local ``.env`` file. I deliberately avoided adding ``python-dotenv`` as a
dependency: the parser needed here is a dozen lines, and a smaller dependency
surface makes the security story simpler to explain.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent


def load_dotenv(path: Path | None = None) -> None:
    """Load ``KEY=value`` lines from ``.env`` into ``os.environ``.

    Existing variables win, so a shell export always overrides the file. The
    file is never committed (see ``.gitignore``); it is the only place the
    API key is expected to live when the LLM interpreter is enabled.
    """
    env_path = path or PROJECT_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:  # pylint: disable=too-many-instance-attributes
    """Immutable snapshot of the settings the application uses."""

    data_dir: Path
    database_path: Path
    documents_dir: Path
    llm_enabled: bool
    llm_model: str
    llm_timeout_seconds: float
    session_ttl_minutes: int
    fake_now: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        data_dir = Path(os.environ.get("UNIBOT_DATA_DIR", PROJECT_DIR / "data"))
        return cls(
            data_dir=data_dir,
            database_path=data_dir / "unibot.sqlite3",
            documents_dir=data_dir / "documents",
            # The LLM is off by default so that a marker can run the whole
            # system, including the test-suite, without an API key.
            llm_enabled=_flag("UNIBOT_LLM_ENABLED", False),
            llm_model=os.environ.get("UNIBOT_LLM_MODEL", "claude-haiku-5-5"),
            llm_timeout_seconds=float(os.environ.get("UNIBOT_LLM_TIMEOUT", "10")),
            session_ttl_minutes=int(os.environ.get("UNIBOT_SESSION_TTL_MINUTES", "60")),
            # Lets a demonstration or test pin "now", which matters because the
            # active-assignment rule depends on the current instant.
            fake_now=os.environ.get("UNIBOT_FAKE_NOW"),
        )
