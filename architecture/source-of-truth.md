# Architecture Source of Truth

This repository is finalized through an architecture release-candidate process.

## Source-of-truth hierarchy

1. `architecture/source-of-truth.md`
2. `architecture/review/finalization-checklist.md`
3. `architecture/adr-index.md`
4. Active ADRs
5. Invariants
6. Main architecture documents
7. Handover / milestone documents
8. Customer-facing architecture docs
9. OpenSpec change records
10. Historical / superseded ADRs

If two documents conflict, the higher source in this hierarchy governs unless a newer active ADR explicitly supersedes it.

## Current product wedge

Zovark is the tape recorder for cybersecurity investigations.

The core flow is:

EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.

## Finalization rule

The architecture is frozen only when:

- open P0 issues = 0,
- MVP contradictions = 0,
- customer-facing false claims = 0,
- active ADR index is current,
- missing evidence is labeled M0/future,
- release-candidate scorecard is complete.
