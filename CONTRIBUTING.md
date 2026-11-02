# Contributing

Run `python -m unittest discover -s tests -v`. Add tests for every state transition, revision conflict, idempotency edge, retention/capacity limit and audit failure. Keep event and context payloads as opaque references; do not add implicit fetching or execution. Keep storage and replication behind explicit adapters. Do not mark dependencies `tested` without reproducible cross-repository evidence.
