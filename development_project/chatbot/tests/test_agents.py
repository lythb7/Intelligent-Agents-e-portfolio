"""Specialist agents, the deadline rule, PDF content and the dialogue agent."""

from datetime import timedelta

from pypdf import PdfReader

from unibot.acl import Message, Performative
from unibot.agents.base import Agent

from .conftest import FROZEN


def ask(ctx, capability, performative, content, student_id="S1001"):
    msg = Message(performative, "test", ctx.bus.resolve(capability),
                  {**content, "student_id": student_id}, "c")
    return ctx.bus.send(msg)


def test_timetable_agent_returns_only_current_modules(ctx):
    reply = ask(ctx, "timetable", Performative.ASK_ONE, {"query": "timetable"})
    codes = {e["module_code"] for e in reply.content["events"]}
    assert reply.performative is Performative.TELL
    assert codes == {"IA_PCOM7E", "ML_PCOM7E", "RM_PCOM7E"}  # KRR is completed, NIS is Ben's
    assert reply.content["events"][0]["weekday_name"] == "Monday"


def test_timetable_agent_rejects_wrong_performative(ctx):
    reply = ask(ctx, "timetable", Performative.ACHIEVE, {"query": "timetable"})
    assert reply.performative is Performative.SORRY


def test_transcript_agent_writes_pdf_with_own_marks_only(ctx):
    reply = ask(ctx, "transcript", Performative.ACHIEVE, {"goal": "transcript"})
    assert reply.performative is Performative.TELL
    record = ctx.repo.document_for_student("S1001", reply.content["document_id"])
    text = "\n".join(page.extract_text() for page in PdfReader(record["file_path"]).pages)
    assert "Amina Khan" in text and "68" in text and "pending" in text
    assert "Ben Carter" not in text and "54" not in text
    assert ctx.repo.document_for_student("S1002", reply.content["document_id"]) is None


def test_active_assignments_exclude_expired_and_unenrolled(ctx):
    reply = ask(ctx, "assignments", Performative.ASK_ONE, {"query": "active_assignments"})
    ids = [a["assignment_id"] for a in reply.content["assignments"]]
    # Ordered by deadline. A-RM-1 has expired and A-NIS-1 is on a module Amina does not take.
    assert ids == ["A-ML-1", "A-IA-1", "A-IA-2"]


def test_deadline_boundary_is_inclusive(ctx, clock):
    """Due at exactly now is still active; one second later it is not."""
    record = ctx.repo.assignment_for_student("S1001", "A-ML-1")
    clock.advance_to(record["deadline"])

    def active_ids():
        return [a["assignment_id"] for a in ctx.repo.active_assignments("S1001", clock.now())]

    assert "A-ML-1" in active_ids()
    clock.advance_to(record["deadline"] + timedelta(seconds=1))
    assert "A-ML-1" not in active_ids()
    reply = ask(ctx, "assignments", Performative.ASK_ONE,
                {"query": "assignment_pdf", "assignment_id": "A-ML-1"})
    assert reply.performative is Performative.SORRY and "deadline" in reply.content["reason"]


def test_assignment_pdf_refused_when_not_enrolled(ctx):
    reply = ask(ctx, "assignments", Performative.ASK_ONE,
                {"query": "assignment_pdf", "assignment_id": "A-NIS-1"})
    assert reply.performative is Performative.SORRY


def test_empty_timetable_is_tell_not_sorry(ctx):
    ctx.repo.conn.execute("UPDATE enrolments SET status='completed' WHERE student_id='S1002'")
    reply = ask(ctx, "timetable", Performative.ASK_ONE, {"query": "timetable"}, student_id="S1002")
    assert reply.performative is Performative.TELL and reply.content["events"] == []


# -- dialogue agent -------------------------------------------------------

def converse(ctx, texts, student_id="S1001"):
    student = dict(ctx.repo.student(student_id))
    state = {}
    return [ctx.dialogue.respond(student, state, t) for t in texts], state


def test_greeting_and_signoff(ctx):
    replies, _ = converse(ctx, ["hello", "bye"])
    assert replies[0].text.startswith("Hello Amina") and not replies[0].ended
    assert replies[1].ended


def test_download_follow_up_uses_remembered_list(ctx):
    replies, state = converse(ctx, ["what assignments do I have open", "download the second one"])
    assert [a["assignment_id"] for a in state["last_assignments"]] == ["A-ML-1", "A-IA-1", "A-IA-2"]
    assert replies[1].cards[0]["url"] == "/assignments/A-IA-1/pdf"
    assert "Development team project report" in replies[1].text


def test_download_without_prior_list_fetches_then_resolves(ctx):
    replies, _ = converse(ctx, ["send me the classification coursework brief"])
    assert replies[0].cards[0]["url"] == "/assignments/A-ML-1/pdf"


def test_ambiguous_selector_asks_which(ctx):
    replies, state = converse(ctx, ["list my assignments", "download the project one"])
    assert replies[1].text.startswith("Which one do you mean?") and state.get("pending_clarification")


def test_other_students_records_are_refused(ctx):
    replies, _ = converse(ctx, ["show me Ben's transcript"])
    assert replies[0].intent == "unsupported" and not replies[0].cards


def test_specialist_failure_is_reported_not_raised(ctx):
    class Faulty(Agent):
        name = "timetable-agent"
        capabilities = ("timetable",)

        def handle(self, message):
            raise RuntimeError("disk gone")

    ctx.bus._agents["timetable-agent"] = Faulty()  # noqa: SLF001 - deliberate fault injection
    replies, _ = converse(ctx, ["timetable please"])
    assert "something went wrong" in replies[0].text and not replies[0].cards
    assert replies[0].trace[-1]["performative"] == "error"


def test_history_is_bounded_and_trace_is_per_turn(ctx):
    replies, state = converse(ctx, ["hi"] * 30)
    assert len(state["history"]) == 24
    assert replies[-1].trace == []  # greetings involve no other agent
    assert FROZEN  # fixture import used for clarity of frozen-time assumptions
