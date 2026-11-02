"""The message format and the bus: threading, routing and failure handling."""

from unibot.acl import Message, Performative
from unibot.agents.base import Agent
from unibot.bus import MessageBus


class Echo(Agent):
    name = "echo"
    capabilities = ("echo",)

    def handle(self, message):
        return message.reply(Performative.TELL, {"heard": message.content})


class Broken(Agent):
    name = "broken"
    capabilities = ("broken",)

    def handle(self, message):
        raise RuntimeError("database on fire")


def test_reply_threads_conversation_and_swaps_parties():
    ask = Message(Performative.ASK_ONE, "a", "b", {"q": 1}, "conv-1")
    tell = ask.reply(Performative.TELL, {"answer": 2})
    assert (tell.sender, tell.receiver) == ("b", "a")
    assert tell.in_reply_to == ask.reply_with
    assert tell.conversation_id == "conv-1"
    assert "(tell :sender b :receiver a" in tell.as_sexpr()


def test_bus_routes_by_capability_and_records_trace():
    bus = MessageBus()
    bus.register(Echo())
    assert bus.resolve("echo") == "echo"
    reply = bus.send(Message(Performative.ASK_ONE, "me", "echo", {"x": 1}, "c"))
    assert reply.performative is Performative.TELL and reply.content == {"heard": {"x": 1}}
    assert [m.performative for m in bus.drain_trace()] == [Performative.ASK_ONE, Performative.TELL]
    assert bus.trace == []


def test_unknown_receiver_gets_sorry_not_exception():
    bus = MessageBus()
    reply = bus.send(Message(Performative.ASK_ONE, "me", "nobody", {}, "c"))
    assert reply.performative is Performative.SORRY


def test_agent_exception_becomes_error_message():
    bus = MessageBus()
    bus.register(Broken())
    reply = bus.send(Message(Performative.ASK_ONE, "me", "broken", {}, "c"))
    assert reply.performative is Performative.ERROR
    assert "RuntimeError" in reply.content["reason"]


def test_duplicate_registration_is_refused():
    bus = MessageBus()
    bus.register(Echo())
    try:
        bus.register(Echo())
    except ValueError:
        return
    raise AssertionError("duplicate registration should fail")
