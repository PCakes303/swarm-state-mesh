# Security Policy

This repository is an experimental, bounded in-memory state/event store, not a trusted distributed database.

## Reporting

Do not publish exploitable vulnerabilities, credentials, tokens, or private operational data in public issues. Use GitHub private vulnerability reporting or a private security advisory if enabled for this repository. A dedicated private reporting address is not published here; if private reporting is unavailable, the owner must configure an owner-approved private channel before production use.

## Trust and resource boundaries

- The store does not authenticate or authorize callers. Actor identifiers are metadata only.
- Optimistic revisions detect stale writes within one process; they do not provide distributed locking or writer identity.
- Event identifiers are idempotent only within the current process lifetime.
- Task, per-task event, aggregate event, context-reference and field-length limits are enforced locally; they do not replace network request limits or rate controls.
- Event payload and context references are opaque; this package does not dereference, fetch, validate access to, or execute referenced content.
- The optional audit sink receives bounded metadata. When configured, audit failure prevents state commit; it is not a production audit service.
- Process restart loses all events, revisions and idempotency records.

Do not expose this library directly to untrusted networks. Production use requires authenticated transport, durable storage, access control, encryption/key management, retention policy, replicated consistency, replay protection, backup/recovery and adversarial review.
