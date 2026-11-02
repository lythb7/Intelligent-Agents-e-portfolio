"""Shared agent contract.

Wooldridge (2009) characterises an agent by autonomy, reactivity,
pro-activeness and social ability. The agents here are modest on the first
three and strongest on the last: each owns one competence, decides for itself
how to answer, and interacts with the others only through messages. That is
the property I wanted, because it is what makes the system decomposable and
testable, and it is what lets the dialogue agent stay ignorant of how records
are stored.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..acl import Message, Performative


class Agent(ABC):
    """An agent has a name, advertises capabilities and handles messages."""

    name: str = "agent"
    capabilities: tuple[str, ...] = ()

    @abstractmethod
    def handle(self, message: Message) -> Message:
        """Process one incoming message and return the reply."""

    def unsupported(self, message: Message) -> Message:
        """Standard SORRY for a performative or query this agent does not do."""
        return message.reply(
            Performative.SORRY,
            {"reason": f"{self.name} cannot handle {message.performative.value} "
                       f"with content keys {sorted(message.content)}"},
        )
