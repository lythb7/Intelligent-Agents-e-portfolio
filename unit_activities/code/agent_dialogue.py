"""Unit 6 activity: an agent dialogue in KQML with KIF-style content.

Alice is a procurement agent for a retailer; Bob is the stock-management
agent for a warehouse. Alice wants to know how many 50-inch televisions are in
stock and how many HDMI ports each model has. The exchange is written out as
KQML performatives (Finin et al., 1994) and then enacted by two small Python
classes so that the conversation can be run and inspected rather than only
read. The exact wording of the original activity page was not available to me
when I wrote this, so the scenario follows the commonly set version of the
task; the protocol itself is what the exercise is about.

Run:  python agent_dialogue.py
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

_ids = itertools.count(1)


@dataclass
class KQMLMessage:
    performative: str
    sender: str
    receiver: str
    content: str
    language: str = "KIF"
    ontology: str = "warehouse-stock"
    reply_with: str = field(default_factory=lambda: f"id{next(_ids)}")
    in_reply_to: str | None = None

    def __str__(self) -> str:
        lines = [f"({self.performative}",
                 f"  :sender {self.sender}",
                 f"  :receiver {self.receiver}",
                 f"  :language {self.language}",
                 f"  :ontology {self.ontology}",
                 f"  :reply-with {self.reply_with}"]
        if self.in_reply_to:
            lines.append(f"  :in-reply-to {self.in_reply_to}")
        lines.append(f"  :content {self.content})")
        return "\n".join(lines)


class Bob:
    """Warehouse stock agent. Knows the stock and answers questions about it."""

    name = "Bob"
    # (product id, description, screen size in inches, HDMI ports, units in stock)
    STOCK = [
        ("TV-5001", "Vizia 50 inch 4K", 50, 3, 42),
        ("TV-5002", "Samsonic 50 inch QLED", 50, 4, 17),
        ("TV-5503", "Vizia 55 inch 4K", 55, 3, 9),
    ]

    def handle(self, msg: KQMLMessage) -> KQMLMessage:
        if msg.performative == "ask-all" and "screen-size" in msg.content and "50" in msg.content:
            facts = " ".join(f"(in-stock {pid} {units})" for pid, _, size, _, units in self.STOCK if size == 50)
            return KQMLMessage("tell", self.name, msg.sender, f"({facts})", in_reply_to=msg.reply_with)
        if msg.performative == "ask-one" and "hdmi-ports" in msg.content:
            pid = msg.content.split()[1]
            for product, _, _, ports, _ in self.STOCK:
                if product == pid:
                    return KQMLMessage("tell", self.name, msg.sender, f"(hdmi-ports {pid} {ports})",
                                       in_reply_to=msg.reply_with)
            return KQMLMessage("sorry", self.name, msg.sender, f"(unknown-product {pid})",
                               in_reply_to=msg.reply_with)
        return KQMLMessage("error", self.name, msg.sender, "(unrecognised-performative)",
                           in_reply_to=msg.reply_with)


class Alice:
    """Procurement agent. Drives the conversation and collects the answers."""

    name = "Alice"

    def run(self, bob: Bob) -> list[KQMLMessage]:
        transcript: list[KQMLMessage] = []

        def send(msg: KQMLMessage) -> KQMLMessage:
            transcript.append(msg)
            reply = bob.handle(msg)
            transcript.append(reply)
            return reply

        stock = send(KQMLMessage("ask-all", self.name, bob.name, "(in-stock ?product ?units) (screen-size ?product 50)"))
        products = [token for token in stock.content.replace("(", " ").replace(")", " ").split()
                    if token.startswith("TV-")]
        for product in products:
            send(KQMLMessage("ask-one", self.name, bob.name, f"(hdmi-ports {product} ?n)"))
        # A deliberately unknown product shows the sorry performative in use.
        send(KQMLMessage("ask-one", self.name, bob.name, "(hdmi-ports TV-9999 ?n)"))
        return transcript


if __name__ == "__main__":
    for message in Alice().run(Bob()):
        print(message)
        print()
