# State and event contract v1

## Purpose and boundary

The reference store appends task-scoped state events, applies optimistic revision checks, enforces event-ID idempotency, and returns deterministic snapshots. It is a single-process, in-memory library.

## Event envelope

Each event includes a bounded `event_id`, `task_id`, `actor_id`, `event_type`, `payload_ref`, expected current revision and zero or more opaque context references. Payload and context references are identifiers only; this library does not fetch or execute their content.

## Revision semantics

A task begins at revision zero. An accepted event must specify the exact current revision. On append, the task revision increments by one. A stale expected revision is rejected with a conflict error. The operation is serialized within one process.

## Idempotency

An identical event ID and identical event body returns the current task snapshot without appending a second event. Reusing an event ID with different content is rejected. The idempotency index is process-local and volatile.

## Snapshots and bounds

Snapshots expose task ID, current revision, ordered event metadata and a deterministic unique list of context references. Store capacity, per-task event count, context-reference count and identifier sizes are bounded by constructor limits.

## Audit integration

An optional audit sink receives the event metadata before commit. If the sink raises, the event is not committed. The sink is an integration seam, not a production audit implementation.

## Distributed semantics

There is no replication, peer protocol, consensus, CRDT merge, distributed locking, durable write-ahead log or exactly-once guarantee. A future mesh must specify partition behavior, conflict resolution, membership, authentication, encryption, retention, recovery and provenance before interoperability can be claimed.
