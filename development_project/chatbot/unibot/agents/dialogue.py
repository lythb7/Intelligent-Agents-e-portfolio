"""The dialogue agent: the student's single point of contact.

This is the one agent with any deliberation in it, and its control loop is
the practical-reasoning shape described by Bratman, Israel and Pollack
(1988) and in Wooldridge (2009): perceive the new message, update beliefs
about the conversation, decide what the student is trying to achieve, commit
to a plan for it, execute the plan by asking the specialist agents, and then
respond. I describe it as a *deliberative control loop* rather than a BDI
agent, because the "plans" are short fixed sequences and there is no
reconsideration of intentions mid-plan. Beliefs are the per-session state:
what was last listed, whether a clarification is pending, and the recent
turns. Those beliefs matter for follow-ups like "download the second one",
which make no sense without them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..acl import Message, Performative
from ..bus import MessageBus
from ..interpreters import (ASSIGNMENTS, CLARIFY, DOWNLOAD, FAREWELL, GREETING, HELP,
                            THANKS, TIMETABLE, TRANSCRIPT, UNSUPPORTED, Intent,
                            Interpreter)
from .base import Agent

HELP_TEXT = (
    "I can do four things for you: show your weekly timetable, create a PDF transcript "
    "of your marks so far, list the assignments you still have open, and send you the "
    "PDF brief for any of them. Just ask in your own words."
)

MAX_HISTORY_TURNS = 12
MAX_MESSAGE_CHARS = 1000


@dataclass
class Reply:
    """What the interface renders for one turn."""

    text: str
    cards: list[dict[str, Any]] = field(default_factory=list)
    intent: str = ""
    intent_source: str = ""
    trace: list[dict[str, Any]] = field(default_factory=list)
    ended: bool = False


class DialogueAgent(Agent):
    """Coordinates the conversation and delegates record work over the bus."""

    name = "dialogue-agent"
    capabilities = ("conversation",)

    def __init__(self, bus: MessageBus, interpreter: Interpreter) -> None:
        self.bus = bus
        self.interpreter = interpreter
        self._conversation_counter = 0

    # The dialogue agent is also addressable on the bus, which keeps the
    # design uniform, but the web and CLI layers call ``respond`` directly.
    def handle(self, message: Message) -> Message:
        return self.unsupported(message)

    # -- the control loop ---------------------------------------------------
    def respond(self, student: dict[str, Any], state: dict[str, Any], text: str) -> Reply:
        text = text.strip()[:MAX_MESSAGE_CHARS]
        history: list[dict[str, str]] = state.setdefault("history", [])
        conversation_id = state.setdefault("conversation_id", self._new_conversation_id(student))

        # 1. Perceive: turn the utterance into an intent.
        intent = self.interpreter.interpret(text, history)

        # 2. Deliberate and 3. act: each intent has a short plan.
        reply = self._execute(intent, student, state, conversation_id)
        reply.intent = intent.name
        reply.intent_source = intent.source

        # 4. Update beliefs for the next turn.
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply.text})
        del history[:-2 * MAX_HISTORY_TURNS]
        reply.trace = [m.as_dict() for m in self.bus.drain_trace()]
        return reply

    def _new_conversation_id(self, student: dict[str, Any]) -> str:
        self._conversation_counter += 1
        return f"conv-{student['student_id']}-{self._conversation_counter}"

    # -- plans --------------------------------------------------------------
    def _execute(self, intent: Intent, student: dict[str, Any], state: dict[str, Any],
                 conversation_id: str) -> Reply:
        first_name = student["full_name"].split()[0]
        if intent.name == GREETING:
            greeting = intent.arguments.get("reply") or f"Hello {first_name}, good to see you."
            return Reply(f"{greeting} {HELP_TEXT}")
        if intent.name == FAREWELL:
            farewell = intent.arguments.get("reply") or f"Goodbye {first_name}, good luck with your studies."
            return Reply(farewell, ended=True)
        if intent.name == THANKS:
            return Reply(intent.arguments.get("reply") or "You're welcome. Anything else?")
        if intent.name == HELP:
            return Reply(HELP_TEXT)
        if intent.name == CLARIFY:
            state["pending_clarification"] = True
            return Reply(intent.arguments.get("question") or "Could you say more about what you need?")
        if intent.name == UNSUPPORTED:
            reason = intent.arguments.get("reason") or (
                "I can only help with your own timetable, transcript and assignments.")
            return Reply(f"{reason} {HELP_TEXT}")
        if intent.name == TIMETABLE:
            return self._plan_timetable(student, conversation_id)
        if intent.name == TRANSCRIPT:
            return self._plan_transcript(student, conversation_id)
        if intent.name == ASSIGNMENTS:
            return self._plan_assignments(student, state, conversation_id)
        if intent.name == DOWNLOAD:
            return self._plan_download(intent, student, state, conversation_id)
        return Reply("I'm not sure how to help with that. " + HELP_TEXT)

    def _ask(self, capability: str, performative: Performative, content: dict[str, Any],
             student: dict[str, Any], conversation_id: str) -> Message:
        receiver = self.bus.resolve(capability) or capability
        # The student id comes from the authenticated session, never from the
        # text of the request. This is the line the interpreter cannot cross.
        content = {**content, "student_id": student["student_id"]}
        return self.bus.send(Message(performative, self.name, receiver, content, conversation_id))

    def _plan_timetable(self, student: dict[str, Any], conversation_id: str) -> Reply:
        answer = self._ask("timetable", Performative.ASK_ONE, {"query": "timetable"},
                           student, conversation_id)
        if answer.performative is not Performative.TELL:
            return self._failure("fetch your timetable", answer)
        events = answer.content["events"]
        if not events:
            return Reply("You are not enrolled on any modules with scheduled sessions at the moment.")
        modules = sorted({e["module_code"] for e in events})
        return Reply(
            f"Here is your weekly timetable for {len(modules)} current module"
            f"{'s' if len(modules) != 1 else ''}: {', '.join(modules)}.",
            cards=[{"type": "timetable", "events": events}],
        )

    def _plan_transcript(self, student: dict[str, Any], conversation_id: str) -> Reply:
        answer = self._ask("transcript", Performative.ACHIEVE, {"goal": "transcript"},
                           student, conversation_id)
        if answer.performative is not Performative.TELL:
            return self._failure("create your transcript", answer)
        c = answer.content
        pending = ""
        if c["pending_count"]:
            pending = f" {c['pending_count']} mark{'s' if c['pending_count'] != 1 else ''} still pending."
        return Reply(
            f"Your transcript is ready. It lists {c['released_count']} released mark"
            f"{'s' if c['released_count'] != 1 else ''}.{pending}",
            cards=[{"type": "document", "label": "Download transcript (PDF)",
                    "url": f"/documents/{c['document_id']}"}],
        )

    def _plan_assignments(self, student: dict[str, Any], state: dict[str, Any],
                          conversation_id: str) -> Reply:
        answer = self._ask("assignments", Performative.ASK_ONE, {"query": "active_assignments"},
                           student, conversation_id)
        if answer.performative is not Performative.TELL:
            return self._failure("look up your assignments", answer)
        items = answer.content["assignments"]
        state["last_assignments"] = items  # belief used by "download the second one"
        if not items:
            return Reply("You have no assignments with open deadlines right now.")
        return Reply(
            f"You have {len(items)} active assignment{'s' if len(items) != 1 else ''}. "
            "Each brief can be downloaded below, or just tell me which one you want.",
            cards=[{"type": "assignments", "items": [
                {**item, "url": f"/assignments/{item['assignment_id']}/pdf"} for item in items
            ]}],
        )

    def _plan_download(self, intent: Intent, student: dict[str, Any], state: dict[str, Any],
                       conversation_id: str) -> Reply:
        items = state.get("last_assignments")
        if items is None:
            # No list in the beliefs yet: fetch it first, then resolve.
            listed = self._plan_assignments(student, state, conversation_id)
            items = state.get("last_assignments") or []
            if not items:
                return listed
        chosen = _resolve_selector(intent.arguments.get("selector", ""), items)
        if chosen is None:
            titles = "; ".join(f"{i + 1}. {a['title']} ({a['module_code']})" for i, a in enumerate(items))
            state["pending_clarification"] = True
            return Reply(f"Which one do you mean? {titles}")
        answer = self._ask("assignments", Performative.ASK_ONE,
                           {"query": "assignment_pdf", "assignment_id": chosen["assignment_id"]},
                           student, conversation_id)
        if answer.performative is not Performative.TELL:
            return self._failure("fetch that brief", answer)
        a = answer.content["assignment"]
        return Reply(
            f"Here is the brief for {a['title']} ({a['module_code']}), due {a['deadline_display']}.",
            cards=[{"type": "document", "label": f"Download brief: {a['title']} (PDF)",
                    "url": f"/assignments/{a['assignment_id']}/pdf"}],
        )

    @staticmethod
    def _failure(action: str, answer: Message) -> Reply:
        reason = answer.content.get("reason", "unknown reason")
        if answer.performative is Performative.ERROR:
            # Internal detail stays in the trace; the student sees a plain message.
            return Reply(f"Sorry, something went wrong while trying to {action}. Please try again shortly.")
        return Reply(f"Sorry, I could not {action}: {reason}.")


def _resolve_selector(selector: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Map '2', 'A-IA-1' or title words on to exactly one listed assignment."""
    selector = (selector or "").strip().lower()
    if not selector:
        return items[0] if len(items) == 1 else None
    if selector.lstrip("-").isdigit():
        index = int(selector)
        if index == -1:
            return items[-1]
        return items[index - 1] if 1 <= index <= len(items) else None
    by_ref = [a for a in items if a["assignment_id"].lower() == selector]
    if len(by_ref) == 1:
        return by_ref[0]
    stop = {"download", "that", "this", "the", "one", "brief", "please", "send", "give", "open",
            "fetch", "want", "assignment", "pdf", "file", "copy"}
    words = {w for w in re.findall(r"[a-z0-9]+", selector) if len(w) > 2 and w not in stop}
    scored = []
    for item in items:
        haystack = f"{item['title']} {item['module_code']} {item['module_title']}".lower()
        score = sum(1 for w in words if w in haystack)
        if score:
            scored.append((score, item))
    if not scored:
        return None
    scored.sort(key=lambda pair: pair[0], reverse=True)
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None  # a tie is ambiguous; ask rather than guess
    return scored[0][1]
