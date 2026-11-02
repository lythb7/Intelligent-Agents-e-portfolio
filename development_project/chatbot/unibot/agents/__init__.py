"""The agents. See ``base`` for the shared contract."""

from .base import Agent
from .dialogue import DialogueAgent
from .records import AssignmentAgent, TimetableAgent, TranscriptAgent

__all__ = ["Agent", "DialogueAgent", "AssignmentAgent", "TimetableAgent", "TranscriptAgent"]
