"""Bounded event and snapshot data contracts."""
from dataclasses import dataclass
import re

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_EVENT_TYPE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+){0,7}$")


class StateValidationError(ValueError):
    """Raised when an event violates the state contract."""


class StateConflict(RuntimeError):
    """Raised when a revision or event identifier conflicts with stored state."""


@dataclass(frozen=True)
class StateEvent:
    event_id: str
    task_id: str
    actor_id: str
    event_type: str
    payload_ref: str
    expected_revision: int
    context_refs: tuple[str, ...] = ()

    def validate(self, *, max_context_refs: int = 64) -> None:
        if not isinstance(max_context_refs, int) or isinstance(max_context_refs, bool) or not 0 <= max_context_refs <= 64:
            raise ValueError("max_context_refs must be an integer in [0, 64]")
        for name, value in (
            ("event_id", self.event_id),
            ("task_id", self.task_id),
            ("actor_id", self.actor_id),
        ):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise StateValidationError(f"{name} must be a bounded identifier")
        if not isinstance(self.event_type, str) or len(self.event_type) > 64 or not _EVENT_TYPE.fullmatch(self.event_type):
            raise StateValidationError("event_type must be a bounded lowercase event name")
        if not isinstance(self.payload_ref, str) or not self.payload_ref.strip() or len(self.payload_ref) > 512:
            raise StateValidationError("payload_ref must contain 1..512 characters")
        if not isinstance(self.expected_revision, int) or isinstance(self.expected_revision, bool) or self.expected_revision < 0:
            raise StateValidationError("expected_revision must be a non-negative integer")
        if not isinstance(self.context_refs, tuple) or len(self.context_refs) > max_context_refs:
            raise StateValidationError(f"context_refs must be a tuple of at most {max_context_refs} entries")
        for ref in self.context_refs:
            if not isinstance(ref, str) or not ref.strip() or len(ref) > 512:
                raise StateValidationError("each context reference must contain 1..512 characters")


@dataclass(frozen=True)
class StateSnapshot:
    task_id: str
    revision: int
    events: tuple[StateEvent, ...]
    context_refs: tuple[str, ...]
