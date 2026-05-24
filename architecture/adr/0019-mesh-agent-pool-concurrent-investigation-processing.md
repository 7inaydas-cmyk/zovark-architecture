# ADR-0019: Mesh Agent Pool - Concurrent Investigation Processing

**Status:** active
**Date:** 2026-05-19
**Owner:** architect
**Source:** rewritten from bootstrap ADR-0019 for the v3.2.5.0 consolidation baseline

## Context

Investigations cannot assume a single serialized worker. Alert bursts,
customer-specific workload isolation, and replay requirements all require a
runtime model where multiple investigation workers can process independent work
without changing verdict semantics.

The predecessor ADR included unverified capacity and latency targets. Those
numbers are intentionally not carried forward here. INV-022 requires
benchmark-backed provenance before quantified performance claims become
binding. This ADR keeps only the architecture rule: investigation workers are
stateless and interchangeable, and shared state must live in durable,
tenant-scoped records.

## Decision

Zovark's runtime architecture uses a mesh agent pool for investigation work.
The pool is a set of interchangeable workers consuming tenant-scoped
investigation work from a durable queue or equivalent scheduler. Each
investigation instance is processed against explicit inputs, versioned
configuration, recorded tool outputs, and replay metadata.

Workers must not keep authoritative investigation state in process memory.
Durable state belongs in tenant-scoped storage, replay records, audit events,
or explicitly versioned runtime metadata. If a worker fails, another worker can
continue or restart the investigation from recorded state without changing the
deterministic verdict inputs.

Within a single investigation, ordering-sensitive steps remain explicit. The
pool provides concurrency across investigations; it does not authorize
unordered fan-out inside verdict derivation, unbounded model context, or
shared mutable state between tenants.

The worker-pool implementation must preserve:

- INV-001 tenant isolation;
- INV-004 deterministic verdicts;
- INV-005 replayability;
- INV-006 tamper evidence; and
- INV-039 canonical `VerdictInput` boundaries.

Pool size, queue technology, scheduling policy, and autoscaling mechanics are
implementation choices that require measured evidence before product claims.

## Consequences

- The runtime can scale investigation work without making individual workers
  authoritative.
- Worker crashes become retry and recovery events instead of silent state loss.
- Determinism and replay are preserved because workers consume recorded,
  versioned inputs rather than ambient process state.
- Capacity planning remains evidence-gated by INV-022; this ADR does not make
  throughput, latency, or queue-depth claims.

## Alternatives Considered

- **Single serialized worker.** Rejected because it makes alert bursts and
  tenant isolation depend on one process.
- **Shared in-memory worker state.** Rejected because it breaks replay,
  recovery, and tenant isolation.
- **Unordered intra-investigation fan-out.** Rejected because it risks changing
  verdict inputs and makes replay comparison ambiguous.

