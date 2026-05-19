# ADR-0020: Tape Recorder - Replay-Grade Investigation Record

**Status:** active
**Date:** 2026-05-19
**Owner:** replay-owner
**Source:** rewritten from bootstrap ADR-0020 for the v3.2.5.0 consolidation baseline

## Context

ADR-0052 makes deterministic replay and evidence integrity the primary
positioning direction. INV-005 requires replayable investigations, INV-006
requires tamper evidence, INV-036 requires replay to avoid re-inference, and
ADR-0047 defines replay compatibility and failure modes. The predecessor
ADR-0020 captured the tape-recorder idea, but it predates the current
bounded-context and proof-package boundaries.

The tape recorder is therefore the internal investigation record, not a
customer-facing raw-data dump. It records enough canonical, hashed, and
versioned material to prove what the investigation saw and decided while
respecting the later proof-package and Context Compaction Memory boundaries.

## Decision

Every investigation produces a replay-grade investigation record. The record
captures:

- investigation identity, tenant identity, schema version, and runtime version;
- ordered step records for ingest, planning, tool use, assessment, and verdict
  derivation;
- references to lossless investigation memory objects rather than unbounded raw
  tool output in model context;
- model-visible envelopes and hashes sufficient to prove what a model actually
  saw when model contribution exists;
- deterministic verdict inputs conforming to ADR-0046 and INV-039;
- compatibility metadata required by ADR-0047; and
- audit-chain linkage needed to detect tampering under INV-006.

Replay uses the recorded material. It does not call a live model, substitute a
new model result, re-run external systems, or repair missing evidence. If a
required record, schema, or compatibility rule is absent, replay fails closed
under INV-017 and ADR-0047.

The investigation record is broader than a proof package. A proof package may
include hashes, bounded excerpts, canonical verdict inputs, and replay metadata;
it must not become an unbounded raw prompt, tool-argument, tool-output, chat, or
hidden-reasoning archive.

Retention, cold storage, export format, and customer-visible summaries are
separate policy and implementation surfaces. This ADR binds the replay-grade
record shape and integrity boundary, not a storage product claim.

## Consequences

- Replay is grounded in recorded evidence and canonical verdict inputs.
- Model nondeterminism is contained because replay never re-inferences.
- Proof-package generation can remain bounded while still referencing the
  richer internal investigation record.
- Storage and retention policy must respect tenant authority, legal holds, and
  audit-chain integrity.
- Any recorder failure is a fail-closed investigation integrity issue, not a
  condition to paper over in a customer artifact.

## Alternatives Considered

- **Re-run the investigation during replay.** Rejected because external systems,
  model outputs, and runtime conditions can change.
- **Store only a verdict summary.** Rejected because summaries cannot prove what
  evidence the verdict used.
- **Put all raw data into proof packages.** Rejected because proof packages must
  remain bounded, auditable, and safe to share.

