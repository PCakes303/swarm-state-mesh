# Agent instructions

Preserve bounded, deterministic, single-process state semantics. Treat event payload references, context references and actor identifiers as untrusted metadata. Enforce optimistic revision checks and idempotent event identifiers. Never imply that an actor identifier authenticates a writer. Add regression tests for stale revisions, duplicate event IDs, conflicting duplicate writes, capacity limits, audit failures and concurrent append behavior.

This scaffold is an in-memory reference implementation. Do not describe it as durable, replicated, eventually consistent, consensus-backed or production-ready.
