"""Injectable clocks.

Whether an assignment is "active" depends on the current time, so the time
source is an explicit dependency rather than a hidden call to
``datetime.now()``. That makes the deadline boundary testable to the second.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")


class Clock:
    """Real clock. Always returns an aware UTC datetime."""

    def now(self) -> datetime:
        return datetime.now(tz=timezone.utc)


class FixedClock(Clock):
    """A clock frozen at a chosen instant, for tests and demonstrations."""

    def __init__(self, instant: datetime) -> None:
        if instant.tzinfo is None:
            raise ValueError("FixedClock needs an aware datetime")
        self._instant = instant.astimezone(timezone.utc)

    def now(self) -> datetime:
        return self._instant

    def advance_to(self, instant: datetime) -> None:
        self._instant = instant.astimezone(timezone.utc)


def clock_from_setting(fake_now: str | None) -> Clock:
    """Build a clock from the optional ``UNIBOT_FAKE_NOW`` ISO string."""
    if not fake_now:
        return Clock()
    parsed = datetime.fromisoformat(fake_now)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return FixedClock(parsed)


def to_london(instant: datetime) -> datetime:
    """Display helper: records are stored in UTC and shown in UK local time."""
    return instant.astimezone(LONDON)
