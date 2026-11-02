# Security

This repository is an experimental, in-memory state/event store, not a trusted distributed database.

- The store does not authenticate or authorize callers. Actor identifiers are metadata only.
- Optimistic revisions detect stale writes within one process; they do not provide distributed locking.
- Event identifiers are idempotent only within the current process lifetime.
- Event payload and context references are opaque; this package does not dereference, fetch, validate access to, or execute referenced content.
- The optional audit sink receives bounded metadata. When configured, audit failure prevents state commit.
- Process restart loses all events, revisions and idempotency records.

Do not expose this library directly to untrusted networks. Production use requires authenticated transport, durable storage, access control, encryption/key management, retention policy, replicated consistency, replay protection, backup/recovery and adversarial review.
