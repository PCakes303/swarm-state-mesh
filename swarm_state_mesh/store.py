"""Bounded, deterministic, process-local event store."""
import threading
from typing import Callable

from .models import StateConflict, StateEvent, StateSnapshot


AuditSink = Callable[[dict], None]


class StateStore:
    """Single-process in-memory event store; no durability or replication is implied."""

    def __init__(
        self,
        *,
        max_tasks: int = 256,
        max_events_per_task: int = 512,
        max_context_refs: int = 64,
        max_total_events: int = 100_000,
        audit_sink: AuditSink | None = None,
    ):
        for name, value, upper in (
            ("max_tasks", max_tasks, 10000),
            ("max_events_per_task", max_events_per_task, 100000),
            ("max_context_refs", max_context_refs, 64),
            ("max_total_events", max_total_events, 1_000_000),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= upper:
                raise ValueError(f"{name} must be an integer in [1, {upper}]")
        self.max_tasks = max_tasks
        self.max_events_per_task = max_events_per_task
        self.max_context_refs = max_context_refs
        self.max_total_events = max_total_events
        self._total_events = 0
        self.audit_sink = audit_sink
        self._events: dict[str, list[StateEvent]] = {}
        self._event_ids: dict[str, StateEvent] = {}
        self._lock = threading.RLock()

    def _snapshot(self, task_id: str) -> StateSnapshot:
        events = tuple(self._events[task_id])
        refs = []
        seen = set()
        for event in events:
            for ref in event.context_refs:
                if ref not in seen:
                    seen.add(ref)
                    refs.append(ref)
        return StateSnapshot(task_id, len(events), events, tuple(refs))

    def append(self, event: StateEvent) -> StateSnapshot:
        event.validate(max_context_refs=self.max_context_refs)
        with self._lock:
            previous = self._event_ids.get(event.event_id)
            if previous is not None:
                if previous != event:
                    raise StateConflict("event_id already belongs to different event content")
                return self._snapshot(event.task_id)

            current = self._events.get(event.task_id)
            revision = len(current) if current is not None else 0
            if event.expected_revision != revision:
                raise StateConflict(
                    f"stale revision: expected {event.expected_revision}, current revision is {revision}"
                )
            if current is None and len(self._events) >= self.max_tasks:
                raise StateConflict("state store task capacity reached")
            if current is not None and len(current) >= self.max_events_per_task:
                raise StateConflict("per-task event capacity reached")
            if self._total_events >= self.max_total_events:
                raise StateConflict("state store total event capacity reached")

            audit_record = {
                "event_id": event.event_id,
                "task_id": event.task_id,
                "actor_id": event.actor_id,
                "event_type": event.event_type,
                "expected_revision": event.expected_revision,
                "new_revision": revision + 1,
                "payload_ref": event.payload_ref,
                "context_refs": list(event.context_refs),
            }
            if self.audit_sink is not None:
                self.audit_sink(audit_record)

            if current is None:
                current = []
                self._events[event.task_id] = current
            current.append(event)
            self._event_ids[event.event_id] = event
            self._total_events += 1
            return self._snapshot(event.task_id)

    def get(self, task_id: str) -> StateSnapshot:
        with self._lock:
            if task_id not in self._events:
                raise KeyError(task_id)
            return self._snapshot(task_id)
