"""Terminal client: ``python -m unibot.cli --user amina``.

Shares every agent with the web app; only the rendering differs. Useful for
quick demonstrations and for capturing plain-text transcripts as evidence.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

from . import auth
from .app_context import build_context
from .config import Settings


def render(reply) -> str:
    lines = [f"UniBot: {reply.text}"]
    for card in reply.cards:
        if card["type"] == "timetable":
            for e in card["events"]:
                lines.append(f"   {e['weekday_name']:<9} {e['start_time']}-{e['end_time']}  "
                             f"{e['module_code']} {e['kind']} ({e['location']})")
        elif card["type"] == "assignments":
            for i, a in enumerate(card["items"], 1):
                lines.append(f"   {i}. {a['title']} [{a['module_code']}] due {a['deadline_display']}"
                             f"  -> {a['url']}")
        elif card["type"] == "document":
            lines.append(f"   [{card['label']}] -> {card['url']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chat with UniBot in the terminal.")
    parser.add_argument("--user", required=True, help="demo username, e.g. amina")
    parser.add_argument("--trace", action="store_true", help="print inter-agent messages")
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    if not Path(settings.database_path).is_file():
        print(f"UniBot: no database at {settings.database_path}. "
              "Run 'python -m unibot.seed --reset' first.")
        return 1
    ctx = build_context(settings)
    row = ctx.repo.student_by_username(args.user)
    if sys.stdin.isatty():
        password = getpass.getpass("Password: ")
    else:  # piped input: the first line is the password, the rest are messages
        password = sys.stdin.readline().rstrip("\n")
    if row is None or not auth.verify_password(password, row["password_hash"]):
        print("Invalid username or password.")
        return 1
    student = dict(row)
    state: dict = {}
    print(f"Signed in as {student['full_name']}. Type 'bye' to finish.")
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        reply = ctx.dialogue.respond(student, state, text)
        print(render(reply))
        if args.trace:
            for m in reply.trace:
                print(f"   trace: ({m['performative']} {m['sender']} -> {m['receiver']}) {m['content']}")
        if reply.ended:
            break
        print("You: ", end="", flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
