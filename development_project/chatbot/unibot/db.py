"""SQLite storage: schema, synthetic seed data and a repository of queries.

Two decisions shape this module. Every query is parameterised and every
record-returning query takes the student id as a parameter, so the database
layer itself cannot return another student's rows however the request was
phrased; this is the standard defence against injection described by OWASP
(2021). And all instants are stored as ISO-8601 UTC strings and compared as
aware ``datetime`` objects, because the British clock change falls inside a
typical term and naive comparisons silently go wrong across it.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from . import auth
from .clock import Clock, to_london

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    programme TEXT NOT NULL,
    password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS modules (
    module_code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS enrolments (
    student_id TEXT NOT NULL REFERENCES students(student_id),
    module_code TEXT NOT NULL REFERENCES modules(module_code),
    status TEXT NOT NULL CHECK (status IN ('current', 'completed')),
    PRIMARY KEY (student_id, module_code)
);
CREATE TABLE IF NOT EXISTS timetable_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_code TEXT NOT NULL REFERENCES modules(module_code),
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    kind TEXT NOT NULL,
    location TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    module_code TEXT NOT NULL REFERENCES modules(module_code),
    assessment TEXT NOT NULL,
    weight INTEGER NOT NULL,
    mark INTEGER,
    status TEXT NOT NULL CHECK (status IN ('released', 'pending'))
);
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id TEXT PRIMARY KEY,
    module_code TEXT NOT NULL REFERENCES modules(module_code),
    title TEXT NOT NULL,
    deadline_utc TEXT NOT NULL,
    brief_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS generated_documents (
    document_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    kind TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_utc TEXT NOT NULL
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def parse_utc(text: str) -> datetime:
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_utc(instant: datetime) -> str:
    return instant.astimezone(timezone.utc).isoformat(timespec="seconds")


class Repository:
    """All reads and writes the agents are allowed to perform."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # -- students and authentication --------------------------------------
    def student_by_username(self, username: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM students WHERE username = ?", (username,)
        ).fetchone()

    def student(self, student_id: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    # -- timetable ---------------------------------------------------------
    def timetable(self, student_id: str) -> list[dict[str, Any]]:
        """Weekly events for the modules the student is *currently* taking."""
        rows = self.conn.execute(
            """
            SELECT m.module_code, m.title, t.weekday, t.start_time, t.end_time,
                   t.kind, t.location
            FROM enrolments e
            JOIN modules m ON m.module_code = e.module_code
            JOIN timetable_events t ON t.module_code = m.module_code
            WHERE e.student_id = ? AND e.status = 'current'
            ORDER BY t.weekday, t.start_time
            """,
            (student_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    # -- marks -------------------------------------------------------------
    def marks(self, student_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT m.module_code, m.title, m.credits, k.assessment, k.weight,
                   k.mark, k.status
            FROM marks k JOIN modules m ON m.module_code = k.module_code
            WHERE k.student_id = ?
            ORDER BY m.module_code, k.mark_id
            """,
            (student_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    # -- assignments -------------------------------------------------------
    def active_assignments(self, student_id: str, now: datetime) -> list[dict[str, Any]]:
        """Assignments on current modules whose deadline has not passed.

        The brief defines "active" as the deadline not having passed, so an
        assignment due at exactly ``now`` is still active. The comparison is
        done in Python on aware datetimes rather than as string comparison in
        SQL, which keeps the rule in one visible place and timezone-safe.
        """
        rows = self.conn.execute(
            """
            SELECT a.assignment_id, a.module_code, m.title AS module_title,
                   a.title, a.deadline_utc, a.brief_path
            FROM assignments a
            JOIN enrolments e ON e.module_code = a.module_code
            JOIN modules m ON m.module_code = a.module_code
            WHERE e.student_id = ? AND e.status = 'current'
            ORDER BY a.deadline_utc
            """,
            (student_id,),
        ).fetchall()
        result = []
        for row in rows:
            record = dict(row)
            record["deadline"] = parse_utc(record.pop("deadline_utc"))
            if record["deadline"] >= now:
                result.append(record)
        return result

    def assignment_for_student(self, student_id: str, assignment_id: str) -> dict[str, Any] | None:
        """One assignment, but only if this student is enrolled on its module."""
        row = self.conn.execute(
            """
            SELECT a.assignment_id, a.module_code, m.title AS module_title,
                   a.title, a.deadline_utc, a.brief_path
            FROM assignments a
            JOIN enrolments e ON e.module_code = a.module_code
            JOIN modules m ON m.module_code = a.module_code
            WHERE e.student_id = ? AND e.status = 'current' AND a.assignment_id = ?
            """,
            (student_id, assignment_id),
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["deadline"] = parse_utc(record.pop("deadline_utc"))
        return record

    # -- generated documents ----------------------------------------------
    def record_document(self, student_id: str, kind: str, file_path: Path, now: datetime) -> str:
        document_id = secrets.token_urlsafe(16)
        self.conn.execute(
            "INSERT INTO generated_documents VALUES (?, ?, ?, ?, ?)",
            (document_id, student_id, kind, str(file_path), format_utc(now)),
        )
        self.conn.commit()
        return document_id

    def document_for_student(self, student_id: str, document_id: str) -> dict[str, Any] | None:
        """Ownership check and lookup in one query: no row, no file."""
        row = self.conn.execute(
            "SELECT * FROM generated_documents WHERE document_id = ? AND student_id = ?",
            (document_id, student_id),
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Synthetic seed data
# ---------------------------------------------------------------------------

MODULES = [
    ("IA_PCOM7E", "Intelligent Agents", 20),
    ("KRR_PCOM7E", "Knowledge Representation and Reasoning", 20),
    ("ML_PCOM7E", "Machine Learning", 20),
    ("RM_PCOM7E", "Research Methods and Professional Practice", 20),
    ("NIS_PCOM7E", "Network and Information Security", 20),
]

TIMETABLE = [
    # module, weekday (0 = Monday), start, end, kind, location
    ("IA_PCOM7E", 0, "10:00", "12:00", "Seminar", "Online room A"),
    ("IA_PCOM7E", 3, "18:00", "19:00", "Tutor drop-in", "Online room A"),
    ("ML_PCOM7E", 1, "14:00", "16:00", "Lab", "Online lab 2"),
    ("RM_PCOM7E", 2, "09:00", "10:30", "Lecture", "Online room C"),
    ("NIS_PCOM7E", 4, "13:00", "15:00", "Seminar", "Online room B"),
]

STUDENTS = [
    # student_id, username, full name, programme
    ("S1001", "amina", "Amina Khan", "MSc Artificial Intelligence"),
    ("S1002", "ben", "Ben Carter", "MSc Computer Science"),
]

ENROLMENTS = {
    "S1001": [("IA_PCOM7E", "current"), ("ML_PCOM7E", "current"),
              ("RM_PCOM7E", "current"), ("KRR_PCOM7E", "completed")],
    "S1002": [("IA_PCOM7E", "current"), ("NIS_PCOM7E", "current"),
              ("KRR_PCOM7E", "completed")],
}

MARKS = {
    "S1001": [
        ("KRR_PCOM7E", "Ontology development project", 60, 68, "released"),
        ("KRR_PCOM7E", "Critical analysis essay", 40, 72, "released"),
        ("ML_PCOM7E", "Coursework 1: regression", 30, 65, "released"),
        ("IA_PCOM7E", "Team project report", 20, None, "pending"),
    ],
    "S1002": [
        ("KRR_PCOM7E", "Ontology development project", 60, 54, "released"),
        ("KRR_PCOM7E", "Critical analysis essay", 40, 58, "released"),
        ("NIS_PCOM7E", "Threat model report", 50, None, "pending"),
    ],
}


def _end_of_day(instant: datetime) -> datetime:
    """23:59 UK time on the given day, returned in UTC."""
    local = to_london(instant).replace(hour=23, minute=59, second=0, microsecond=0)
    return local.astimezone(timezone.utc)


def assignment_fixtures(now: datetime) -> list[tuple[str, str, str, datetime]]:
    """Assignments relative to ``now`` so the demo stays meaningful on any date.

    One is already past its deadline (and must therefore never be offered),
    one is due soon, one is further off, and one belongs to a module neither
    demo student currently takes.
    """
    def due(days: int) -> datetime:
        return _end_of_day(now + timedelta(days=days))

    return [
        ("A-IA-1", "IA_PCOM7E", "Development team project report", due(12)),
        ("A-IA-2", "IA_PCOM7E", "Individual development project", due(33)),
        ("A-ML-1", "ML_PCOM7E", "Coursework 2: classification", due(5)),
        ("A-RM-1", "RM_PCOM7E", "Literature review", due(-4)),
        ("A-NIS-1", "NIS_PCOM7E", "Penetration test plan", due(20)),
        ("A-KRR-1", "KRR_PCOM7E", "Ontology development project", due(-90)),
    ]


def _seed_students(conn: sqlite3.Connection, passwords: dict[str, str]) -> None:
    for sid, username, name, programme in STUDENTS:
        conn.execute(
            "INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?)",
            (sid, username, name, programme, auth.hash_password(passwords[username])),
        )
        for module_code, status in ENROLMENTS[sid]:
            conn.execute("INSERT OR REPLACE INTO enrolments VALUES (?, ?, ?)", (sid, module_code, status))
        for module_code, assessment, weight, mark, status in MARKS[sid]:
            conn.execute(
                "INSERT INTO marks (student_id, module_code, assessment, weight, mark, status)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (sid, module_code, assessment, weight, mark, status),
            )


def _seed_timetable(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM timetable_events")
    for module_code, weekday, start, end, kind, location in TIMETABLE:
        conn.execute(
            "INSERT INTO timetable_events (module_code, weekday, start_time, end_time, kind, location)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (module_code, weekday, start, end, kind, location),
        )


def _seed_assignments(conn: sqlite3.Connection, documents_dir: Path, now: datetime) -> None:
    # Imported here rather than at module level because documents.py imports
    # the clock helpers and db.py is imported by nearly everything; a top-level
    # import would create a cycle.
    from .documents import write_assignment_brief  # pylint: disable=import-outside-toplevel

    briefs_dir = documents_dir / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    for assignment_id, module_code, title, deadline in assignment_fixtures(now):
        path = briefs_dir / f"{assignment_id}.pdf"
        module_title = next(t for c, t, _ in MODULES if c == module_code)
        write_assignment_brief(path, assignment_id, module_code, module_title, title, deadline)
        conn.execute(
            "INSERT OR REPLACE INTO assignments VALUES (?, ?, ?, ?, ?)",
            (assignment_id, module_code, title, format_utc(deadline), str(path)),
        )


def seed(conn: sqlite3.Connection, documents_dir: Path, clock: Clock,
         passwords: dict[str, str] | None = None) -> dict[str, str]:
    """Create the schema and fill it with synthetic data.

    Returns the plaintext demo passwords so the caller can show them once.
    They are generated randomly unless supplied, which avoids a hard-coded
    secret in source while still giving a marker working credentials.
    """
    conn.executescript(SCHEMA)
    passwords = passwords or {username: secrets.token_urlsafe(8) for _, username, _, _ in STUDENTS}
    with conn:
        for code, title, credit_value in MODULES:
            conn.execute("INSERT OR REPLACE INTO modules VALUES (?, ?, ?)", (code, title, credit_value))
        _seed_students(conn, passwords)
        _seed_timetable(conn)
        _seed_assignments(conn, documents_dir, clock.now())
    return passwords


def write_credentials_file(path: Path, passwords: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(passwords, indent=2), encoding="utf-8")
