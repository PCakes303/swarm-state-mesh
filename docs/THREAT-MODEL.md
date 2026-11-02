# Threat model

## Assets and threats

The store handles task identifiers, event identifiers, actor identifiers, event types, opaque payload references, context references and per-task revisions. Threats include malformed or oversized metadata, stale writes, duplicate event replay, conflicting event-ID reuse, untrusted references, audit failure, resource exhaustion and process loss.

## Controls in this scaffold

- Strict bounded identifiers, event types and references.
- Bounded task count, per-task event count, aggregate event count, references per event and event-type length.
- Per-task optimistic revision checks.
- Event-ID idempotency and conflicting duplicate detection.
- Deterministic ordered event history and context-reference snapshots.
- Process-local serialization with a lock.
- Optional audit callback; configured audit failure prevents commit.

## Not implemented

No authentication, authorization, cryptographic signatures, encryption, durable persistence, replicated storage, distributed consensus, CRDT merge, cross-process replay protection, backup, compaction, retention enforcement, or peer-to-peer synchronization exists.

Actor IDs are claims supplied by the caller. A revision check is not authorization. Opaque references are not access-controlled or dereferenced. Production deployment requires a trusted identity/policy boundary, durable storage, authenticated peers, cryptographic integrity, explicit consistency and partition semantics, and recovery testing.
