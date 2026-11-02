# Swarm State Mesh

Experimental bounded event and state reference for versioned task state, synchronization contracts and shared context references in the hybrid agent ecosystem.

## Initial vertical slice

This scaffold is a deterministic, single-process in-memory reference store—not a distributed database or network mesh.

- Appends bounded task-scoped events with monotonic per-task revisions.
- Uses optimistic revision checks to reject stale writes.
- Makes event IDs idempotent within the current process lifetime and rejects conflicting reuse.
- Returns deterministic event histories and unique context-reference lists.
- Enforces bounded task, per-task event, aggregate event (100,000 by default) and context-reference capacity.
- Supports an optional audit callback; configured audit failure prevents event commit.
- Keeps payload and context references opaque; it never fetches or executes content.

## Quick start

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```



```python
from swarm_state_mesh import StateEvent, StateStore

store = StateStore()
first = StateEvent(
    event_id="event.001",
    task_id="task.001",
    actor_id="principal.coordinator",
    event_type="task.assigned",
    payload_ref="artifact://events/001",
    expected_revision=0,
    context_refs=("artifact://context/plan",),
)
snapshot = store.append(first)
assert snapshot.revision == 1

second = StateEvent(
    event_id="event.002",
    task_id="task.001",
    actor_id="principal.worker",
    event_type="task.acknowledged",
    payload_ref="artifact://events/002",
    expected_revision=1,
)
snapshot = store.append(second)
assert snapshot.revision == 2
```

## Integration boundary

The store's task IDs and lifecycle references can be mapped by external adapters to Swarm Coordination and Swarm Runtime contracts. An audit adapter can forward event metadata to Audit & Provenance. These are declared integration boundaries, not tested compatibility claims.

## Security and reliability limits

State is volatile and local to one process. Restart loses events and idempotency records. There is no authentication, authorization, encryption, replication, peer protocol, distributed locking, consensus or CRDT merge. Actor identifiers are metadata only. Opaque references are not fetched or access-controlled.

See [state contract](docs/STATE-CONTRACT.md) and [threat model](docs/THREAT-MODEL.md). Python 3.10–3.12 are covered by CI. No release is published and the repository-specific license decision is pending review.
