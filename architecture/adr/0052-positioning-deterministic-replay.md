# ADR-0052: Deterministic Replay as Primary Differentiator

**Status:** proposed  
**Date:** 2026-05-16  
**Version context:** v3.2.4.4 positioning amendment  
**Scope:** positioning and architecture guidance only; no runtime implementation

## Context

Earlier marketing framing emphasized air-gap deployment as the buying wedge.
Air-gap is one of three deployment topologies under ADR-0038. It is necessary
for some regulated buyers, but it is not the differentiator by itself.

The differentiator is evidence integrity: every investigation should produce a
byte-identical-replayable record; replay should not re-inference; auditors
should be able to verify verdicts offline indefinitely, even after the original
model is retired. This PR establishes that positioning direction without making
recovered ADR-0046 or ADR-0047 active current source before reconciliation.

## Decision

The primary marketing, sales, and customer-facing differentiator is
deterministic replay plus evidence integrity.

Secondary differentiators are:

- air-gap capability under ADR-0038 and ADR-0041;
- customer-data authority under ADR-0038; and
- supply-chain integrity under ADR-0039.

Air-gap remains a supported topology. It is not the headline.

## Consequences

- Customer-facing material leads with replay and evidence integrity, not
  air-gap.
- Regulated-buyer conversations must not cite recovered ADR-0046, ADR-0047, or
  INV-039 as active commitments until those materials are reconciled into the
  current baseline. Until then, they remain candidate/future evidence-integrity
  work that informs the positioning direction.
- Air-gap remains in the buying-wedge story as a deployment option, not the
  wedge.
- Local inference through RamaLama, per the ADR-0009 amendment, is an approved
  topology choice pending runtime implementation for customers who require
  sovereignty, cost, or latency properties. The architecture does not require
  local inference for deterministic replay.
- Quantified claims remain forbidden unless backed by benchmark artifacts per
  INV-022.

## Alternatives Considered

- **Lead with air-gap.** Rejected because air-gap is a topology capability, not
  the proof that Zovark's investigations remain audit-verifiable.
- **Lead with autonomous response.** Rejected because response claims are not
  trustworthy without replay-grade evidence and approval/reversal records.
- **Lead with local inference.** Rejected because local inference is an
  inference topology choice, not the invariant that makes verdicts auditable.
- **Lead with generic AI SOC automation.** Rejected because it obscures the
  replay/evidence-integrity trust boundary.

## Related

- ADR-0009, as amended by v3.2.4.4
- ADR-0038
- ADR-0041
- ADR-0046 as recovered candidate material pending reconciliation
- ADR-0047 as recovered candidate material pending reconciliation
- INV-036
- INV-039 as recovered candidate material pending reconciliation
- INV-022 quantified claim provenance

## Boundary

This ADR does not add runtime implementation, RamaLama code, benchmarks,
customer-readiness material, legal admissibility claims, compliance
certification claims, signing, anchoring, SLSA, or in-toto scope. It does not
make recovered ADR-0046, ADR-0047, or INV-039 active current source before a
separate reconciliation PR.