"""A small agent communication language (ACL).

The message format borrows the three-layer idea from KQML (Finin et al.,
1994): a *performative* says what kind of speech act the message is, a
*content* field carries the proposition in a content language (here plain
JSON-compatible dictionaries), and a handful of *context* fields name the
sender, receiver and conversation. Separating the illocutionary force of a
message from its content is the point of the design, following Searle's
(1969) account of speech acts: ``ask`` and ``tell`` are different acts even
when they mention the same facts.

This is a deliberately small, KQML-*inspired* vocabulary, not an
implementation of the KQML specification. The agents in this project live in
one process, so no transport or facilitator discovery protocol is needed;
what I wanted was an explicit, inspectable record of who asked whom for what.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_counter = itertools.count(1)


class Performative(str, Enum):
    """The speech acts the agents understand.

    ASK_ONE and TELL map on to KQML's query/reply pair; ACHIEVE asks another
    agent to bring something about (here, generate a document); SORRY says
    the receiver understood but cannot help; ERROR says the message itself
    was malformed. Keeping SORRY distinct from an empty TELL matters: "you
    have no active assignments" is a fact, "I could not read the database"
    is a failure, and the user should never see one dressed up as the other.
    """

    ASK_ONE = "ask-one"
    ACHIEVE = "achieve"
    TELL = "tell"
    SORRY = "sorry"
    ERROR = "error"


@dataclass
class Message:
    """One utterance between agents."""

    performative: Performative
    sender: str
    receiver: str
    content: dict[str, Any]
    conversation_id: str
    reply_with: str = field(default_factory=lambda: f"m{next(_counter)}")
    in_reply_to: str | None = None

    def reply(self, performative: Performative, content: dict[str, Any]) -> "Message":
        """Build the reply, swapping sender/receiver and threading the ids."""
        return Message(
            performative=performative,
            sender=self.receiver,
            receiver=self.sender,
            content=content,
            conversation_id=self.conversation_id,
            in_reply_to=self.reply_with,
        )

    def as_dict(self) -> dict[str, Any]:
        """Serialisable form, used for the trace shown in the web interface."""
        return {
            "performative": self.performative.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "conversation_id": self.conversation_id,
            "reply_with": self.reply_with,
            "in_reply_to": self.in_reply_to,
        }

    def as_sexpr(self) -> str:
        """KQML-style textual rendering, for logs and the portfolio write-up."""
        content = " ".join(f":{k} {v!r}" for k, v in self.content.items())
        return (
            f"({self.performative.value} :sender {self.sender} :receiver {self.receiver} "
            f":conversation {self.conversation_id} :reply-with {self.reply_with}"
            + (f" :in-reply-to {self.in_reply_to}" if self.in_reply_to else "")
            + f" :content ({content}))"
        )
