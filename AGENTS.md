# Agent instructions

- Preserve bounded, deterministic, single-process state semantics. Treat event payload references, context references and actor identifiers as untrusted metadata.
- Enforce optimistic revision checks and event-ID idempotency; never imply an actor identifier authenticates a writer.
- Enforce task, per-task event, aggregate event and context-reference limits. Keep event type and reference bounds aligned with the normative schema.
- Keep audit callback before-commit semantics: if configured audit delivery fails, do not commit the event.
- Do not fetch or execute opaque payload/context references.
- Add regression tests for stale revisions, duplicate event IDs, conflicting duplicate writes, aggregate/per-task capacity limits, schema bounds, audit failures and concurrent append behavior.
- This scaffold is an in-memory reference implementation. Do not describe it as durable, replicated, eventually consistent, consensus-backed or production-ready.
- License remains pending review; do not add a license file or infer one.
- Run `python -m unittest discover -s tests -v` before proposing changes.
