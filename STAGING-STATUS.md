# Repository 18 deployment and audit status

**Repository:** [PCakes303/swarm-state-mesh](https://github.com/PCakes303/swarm-state-mesh)  
**Audited baseline:** `dc686ed5939119fa827077e0760ca84b0edae3da`  
**Baseline CI:** [Run 41420117940](https://github.com/PCakes303/swarm-state-mesh/actions/runs/41420117940) — success  
**Staging source:** `provisioning/staged/swarm-state-mesh/` in the master repository.

## Current deployment record

The public remote exists and is authoritative for current implementation. The historical 18-file staging parity and CI records are provenance only; refresh path/blob-SHA parity against current `main` before portfolio sign-off.

## Remediation in progress

The store now enforces an aggregate event limit (100,000 by default, configurable up to 1,000,000), in addition to per-task event and task limits. Context-reference configuration is capped at the schema limit of 64; event type is limited to 64 characters. Added tests for aggregate capacity and schema-aligned bounds.

## Remaining verification

- Bind StateEvent model validation to the normative Draft 2020-12 schema in CI and add model/schema parity tests.
- Integrate authenticated writer identity and authorization; actor IDs remain caller-supplied metadata.
- Integrate authenticated durable audit provenance; current audit sink is a callback seam.
- Define durable storage, retention/compaction, backup/recovery and replication/partition semantics before claiming mesh behavior.
- Verify GitHub private vulnerability reporting/security advisory configuration; SECURITY.md records that no dedicated private reporting address is published.
- Apply and verify GitHub About homepage/topics (description exists); verify branch rulesets/protection, Actions permissions, secret scanning, push protection and dependency alerts.
- Refresh staging-to-remote path/blob-SHA parity and retain pending license status until an explicit repository/artifact decision is approved.

## Maturity and limitations

This remains a bounded single-process in-memory event store. It does not provide authentication, authorization, encryption, durable persistence, replication, distributed consensus, CRDT merge, cross-process replay protection, backup, compaction, retention enforcement or peer-to-peer synchronization. Actor IDs are metadata only; revision checks are not authorization.
