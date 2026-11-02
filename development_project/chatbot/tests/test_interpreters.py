"""Rule interpreter behaviour and the LLM adapter's validation and fallback."""

from types import SimpleNamespace

import pytest

from unibot import interpreters as it


@pytest.fixture
def rules():
    return it.RuleInterpreter()


@pytest.mark.parametrize("text,expected", [
    ("hello", it.GREETING),
    ("Good morning!", it.GREETING),
    ("hi, when are my classes this week?", it.TIMETABLE),
    ("what's my timetable", it.TIMETABLE),
    ("Could I get my results so far as a PDF?", it.TRANSCRIPT),
    ("transcript please", it.TRANSCRIPT),
    ("which assignments are still open?", it.ASSIGNMENTS),
    ("any deadlines coming up", it.ASSIGNMENTS),
    ("download the second one", it.DOWNLOAD),
    ("can I have the brief for A-IA-1", it.DOWNLOAD),
    ("show me Ben's marks", it.UNSUPPORTED),
    ("change my mark to 90", it.UNSUPPORTED),
    ("what can you do", it.HELP),
    ("thanks!", it.THANKS),
    ("ok bye", it.FAREWELL),
    ("", it.CLARIFY),
    ("what's the meaning of life", it.CLARIFY),
])
def test_rule_interpreter(rules, text, expected):
    assert rules.interpret(text, []).name == expected


def test_rule_interpreter_extracts_selector(rules):
    assert rules.interpret("download the second one", []).arguments == {"selector": "2"}
    assert rules.interpret("get me brief A-IA-1", []).arguments == {"selector": "A-IA-1"}


def test_validate_rejects_unknown_tool_and_smuggled_student_id():
    assert it.validate_tool_call("delete_everything", {}).name == it.CLARIFY
    assert it.validate_tool_call(it.TIMETABLE, {"student_id": "S1002"}).name == it.CLARIFY
    assert it.validate_tool_call(it.DOWNLOAD, {"selector": 2}).name == it.CLARIFY
    ok = it.validate_tool_call(it.DOWNLOAD, {"selector": " 2 "})
    assert ok.name == it.DOWNLOAD and ok.arguments == {"selector": "2"} and ok.source == "llm"


def test_validate_caps_free_text_length():
    intent = it.validate_tool_call(it.GREETING, {"reply": "x" * 1000})
    assert len(intent.arguments["reply"]) == 300


class FakeMessages:
    def __init__(self, blocks=None, error=None):
        self.blocks, self.error, self.calls = blocks, error, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(content=self.blocks, usage=SimpleNamespace(input_tokens=10, output_tokens=5))


def fake_client(blocks=None, error=None):
    return SimpleNamespace(messages=FakeMessages(blocks, error))


def test_llm_interpreter_uses_single_tool_call():
    block = SimpleNamespace(type="tool_use", name=it.TRANSCRIPT, input={})
    llm = it.LLMInterpreter("test-model", client=fake_client([block]))
    intent = llm.interpret("results pls", [])
    assert intent.name == it.TRANSCRIPT and intent.source == "llm"
    call = llm.client.messages.calls[0]
    assert call["tool_choice"] == {"type": "auto", "disable_parallel_tool_use": True}
    assert all(tool["strict"] for tool in call["tools"])
    assert llm.last_usage == {"input_tokens": 10, "output_tokens": 5}


def test_llm_interpreter_falls_back_on_api_error():
    llm = it.LLMInterpreter("test-model", client=fake_client(error=ConnectionError("offline")))
    intent = llm.interpret("when are my classes", [])
    assert intent.name == it.TIMETABLE and intent.source == "llm-fallback-rules"


def test_llm_interpreter_falls_back_when_no_or_many_tool_calls():
    text_only = [SimpleNamespace(type="text", text="Sure!")]
    llm = it.LLMInterpreter("test-model", client=fake_client(text_only))
    assert llm.interpret("transcript", []).source == "llm-fallback-rules"
    two = [SimpleNamespace(type="tool_use", name=it.TIMETABLE, input={}),
           SimpleNamespace(type="tool_use", name=it.TRANSCRIPT, input={})]
    llm = it.LLMInterpreter("test-model", client=fake_client(two))
    assert llm.interpret("transcript", []).source == "llm-fallback-rules"


def test_llm_interpreter_sends_bounded_history():
    block = SimpleNamespace(type="tool_use", name=it.HELP, input={})
    llm = it.LLMInterpreter("test-model", client=fake_client([block]))
    history = [{"role": "user", "content": f"u{i}"} for i in range(20)]
    llm.interpret("help", history)
    sent = llm.client.messages.calls[0]["messages"]
    assert len(sent) == 7 and sent[-1] == {"role": "user", "content": "help"}


def test_build_interpreter_without_key_degrades_to_rules(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(it.build_interpreter(False, "m", 1.0), it.RuleInterpreter)
    # Enabled but no credentials: the constructor may fail or succeed lazily;
    # either way interpreting must still work through the rules.
    interp = it.build_interpreter(True, "claude-haiku-5-5", 1.0)
    assert interp.interpret("timetable", []).name == it.TIMETABLE
