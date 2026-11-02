"""Specialist agents for timetable, transcript and assignment requests.

These are simple reactive agents in Wooldridge's (2009) sense: no internal
deliberation, a direct mapping from the incoming request to a database read
or a document write. Their value is in the boundary they enforce. Each one
takes the student id only from the message its coordinating agent built from
the authenticated session, and each answers with facts (TELL) or a reason it
could not (SORRY), never with free text addressed to the user. Presentation
is the dialogue agent's job.
"""

from __future__ import annotations

import secrets
from pathlib import Path

from ..acl import Message, Performative
from ..clock import Clock, to_london
from ..db import Repository
from ..documents import write_transcript
from .base import Agent

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class TimetableAgent(Agent):
    """Answers ASK_ONE timetable queries from the enrolment and events tables."""

    name = "timetable-agent"
    capabilities = ("timetable",)

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def handle(self, message: Message) -> Message:
        if message.performative is not Performative.ASK_ONE or message.content.get("query") != "timetable":
            return self.unsupported(message)
        events = self.repo.timetable(message.content["student_id"])
        for event in events:
            event["weekday_name"] = WEEKDAYS[event["weekday"]]
        # An empty timetable is a true answer, so it is a TELL with an empty
        # list, not a SORRY. The distinction is tested.
        return message.reply(Performative.TELL, {"events": events})


class TranscriptAgent(Agent):
    """Achieves the goal of a fresh transcript PDF and registers it to its owner."""

    name = "transcript-agent"
    capabilities = ("transcript",)

    def __init__(self, repo: Repository, documents_dir: Path, clock: Clock) -> None:
        self.repo = repo
        self.documents_dir = documents_dir
        self.clock = clock

    def handle(self, message: Message) -> Message:
        if message.performative is not Performative.ACHIEVE or message.content.get("goal") != "transcript":
            return self.unsupported(message)
        student_id = message.content["student_id"]
        student = self.repo.student(student_id)
        if student is None:
            return message.reply(Performative.SORRY, {"reason": "unknown student"})
        marks = self.repo.marks(student_id)
        now = self.clock.now()
        out_dir = self.documents_dir / "transcripts"
        out_dir.mkdir(parents=True, exist_ok=True)
        # The file is written first and only then recorded, so a document id
        # never points at a file that failed to generate.
        path = out_dir / f"transcript-{student_id}-{secrets.token_hex(6)}.pdf"
        write_transcript(path, dict(student), marks)
        document_id = self.repo.record_document(student_id, "transcript", path, now)
        released = [m for m in marks if m["status"] == "released"]
        return message.reply(
            Performative.TELL,
            {
                "document_id": document_id,
                "released_count": len(released),
                "pending_count": len(marks) - len(released),
            },
        )


class AssignmentAgent(Agent):
    """Lists active assignments and releases a brief only while it is active."""

    name = "assignment-agent"
    capabilities = ("assignments",)

    def __init__(self, repo: Repository, clock: Clock) -> None:
        self.repo = repo
        self.clock = clock

    def handle(self, message: Message) -> Message:
        if message.performative is not Performative.ASK_ONE:
            return self.unsupported(message)
        query = message.content.get("query")
        student_id = message.content["student_id"]
        now = self.clock.now()
        if query == "active_assignments":
            items = self.repo.active_assignments(student_id, now)
            return message.reply(Performative.TELL, {"assignments": [self._public(a) for a in items]})
        if query == "assignment_pdf":
            record = self.repo.assignment_for_student(student_id, message.content.get("assignment_id", ""))
            if record is None:
                return message.reply(Performative.SORRY, {"reason": "not enrolled or unknown assignment"})
            if record["deadline"] < now:
                # Re-checked at download time, not just when the list was shown:
                # the deadline may have passed between the two requests.
                return message.reply(Performative.SORRY, {"reason": "deadline has passed"})
            # The brief's filesystem path is deliberately *not* included: the
            # trace is shown in the browser, and the download route resolves the
            # path from the database itself. (Found and fixed during testing.)
            return message.reply(Performative.TELL, {"assignment": self._public(record)})
        return self.unsupported(message)

    @staticmethod
    def _public(record: dict) -> dict:
        deadline = record["deadline"]
        return {
            "assignment_id": record["assignment_id"],
            "module_code": record["module_code"],
            "module_title": record["module_title"],
            "title": record["title"],
            "deadline_display": to_london(deadline).strftime("%a %d %b %Y, %H:%M"),
            "deadline_iso": deadline.isoformat(),
        }
