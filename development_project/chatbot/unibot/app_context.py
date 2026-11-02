"""Wires the pieces together once, for both the web app and the CLI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .agents import AssignmentAgent, DialogueAgent, TimetableAgent, TranscriptAgent
from .auth import SessionStore
from .bus import MessageBus
from .clock import Clock, clock_from_setting
from .config import Settings
from .db import Repository, connect
from .interpreters import Interpreter, build_interpreter


@dataclass
class AppContext:
    """Everything a front end needs, built once."""

    settings: Settings
    clock: Clock
    repo: Repository
    bus: MessageBus
    dialogue: DialogueAgent
    sessions: SessionStore


def build_context(settings: Settings | None = None, clock: Clock | None = None,
                  interpreter: Interpreter | None = None) -> AppContext:
    settings = settings or Settings.from_env()
    clock = clock or clock_from_setting(settings.fake_now)
    repo = Repository(connect(settings.database_path))
    bus = MessageBus()
    bus.register(TimetableAgent(repo))
    bus.register(TranscriptAgent(repo, settings.documents_dir, clock))
    bus.register(AssignmentAgent(repo, clock))
    interpreter = interpreter or build_interpreter(settings.llm_enabled, settings.llm_model,
                                                   settings.llm_timeout_seconds)
    dialogue = DialogueAgent(bus, interpreter)
    bus.register(dialogue)
    sessions = SessionStore(clock, timedelta(minutes=settings.session_ttl_minutes))
    return AppContext(settings, clock, repo, bus, dialogue, sessions)
