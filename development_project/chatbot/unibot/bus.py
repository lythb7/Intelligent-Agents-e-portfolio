"""In-process message bus.

The bus plays the role KQML gives to a *facilitator*: agents register the
capabilities they offer, and a sender addresses a capability rather than a
hard-wired object reference. The indirection is cheap and it buys two things.
First, the dialogue agent does not need to know which agent answers
``timetable`` questions, so a specialist can be replaced in a test with a
stub. Second, every exchange passes through one place, so the bus can keep a
trace that the interface shows to the user and that I used as evidence in the
reports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .acl import Message, Performative

if TYPE_CHECKING:  # pragma: no cover - import only for type checkers
    from .agents.base import Agent


class MessageBus:
    """Routes messages between registered agents and records a trace."""

    def __init__(self) -> None:
        self._agents: dict[str, "Agent"] = {}
        self._capabilities: dict[str, str] = {}
        self.trace: list[Message] = []

    def register(self, agent: "Agent") -> None:
        if agent.name in self._agents:
            raise ValueError(f"agent {agent.name!r} already registered")
        self._agents[agent.name] = agent
        for capability in agent.capabilities:
            self._capabilities[capability] = agent.name

    def resolve(self, capability: str) -> str | None:
        """Name of the agent advertising ``capability``, if any."""
        return self._capabilities.get(capability)

    def send(self, message: Message) -> Message:
        """Deliver ``message`` synchronously and return the reply.

        Delivery is synchronous because the user is waiting for an answer;
        the asynchronous, subscribe-style interaction KQML supports would add
        machinery this prototype does not need. The bus never raises on a
        missing receiver: it answers with a SORRY so the dialogue agent can
        explain the failure instead of crashing the turn.
        """
        self.trace.append(message)
        receiver = self._agents.get(message.receiver)
        if receiver is None:
            reply = message.reply(
                Performative.SORRY,
                {"reason": f"no agent named {message.receiver!r} is registered"},
            )
        else:
            try:
                reply = receiver.handle(message)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # Turning an unexpected exception into an ERROR message keeps the
                # failure inside the protocol, where it can be shown and tested.
                reply = message.reply(
                    Performative.ERROR,
                    {"reason": f"{type(exc).__name__}: {exc}"},
                )
        self.trace.append(reply)
        return reply

    def drain_trace(self) -> list[Message]:
        """Return and clear the trace (one web turn = one drained slice)."""
        trace, self.trace = self.trace, []
        return trace
