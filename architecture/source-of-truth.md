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

### Internal (engineering and architecture documents)

Zovark is the tape recorder for cybersecurity investigations.

The core flow is:

EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.

### External (customer-facing, investor-facing, partner-facing)

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

Customer description: Before your SOC isolates a host or disables a user, Zovark shows the evidence, explains the verdict, records the approval path, and creates a replayable proof package.

The product hero artifacts are the approval-required EDR action card and the replayable proof package. The investigation tape is the internal proof substrate that produces them.

### Primary differentiator

ADR-0052 clarifies the buying-wedge emphasis: deterministic replay and evidence
integrity are the primary customer-facing differentiator.

The current architecture direction is hybrid inference with RamaLama as the
planned local-SLM runtime paired with approved cloud inference where tenant
policy allows it. This PR names that direction for architecture planning only;
it does not add RamaLama runtime implementation, tenant controls, deployment
automation, benchmarks, or customer-ready topology selection.

Air-gap is an older deployment philosophy and a possible regulated-deployment
target, not the headline wedge and not a current runtime capability claimed by
this architecture-only PR. Any air-gap profile must remain pending until runtime
support, operator controls, validation, and deployment evidence exist.

The topology choice does not change the replay/evidence-integrity direction:
reconciled replay work should not re-inference and should rely on recorded
model-visible inputs, outputs, provenance, hashes, and verdict inputs.

## Finalization rule

The architecture is frozen only when:

- open P0 issues = 0,
- MVP contradictions = 0,
- customer-facing false claims = 0,
- active ADR index is current,
- missing evidence is labeled M0/future,
- release-candidate scorecard is complete.