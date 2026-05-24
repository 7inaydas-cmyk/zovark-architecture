# ADR-0052: Deterministic Replay as Primary Differentiator

**Status:** proposed  
**Date:** 2026-05-16  
**Version context:** v3.2.4.4 positioning amendment  
**Scope:** positioning and architecture guidance only; no runtime implementation

## Context

Earlier marketing framing emphasized air-gap deployment as the buying wedge.
Air-gap is one possible regulated-deployment target, but it is not the
differentiator by itself and is not made available by this architecture-only PR.

The differentiator is evidence integrity: every investigation should produce a
byte-identical-replayable record; replay should not re-inference; auditors
should be able to verify verdicts offline indefinitely, even after the original
model is retired. This ADR establishes that positioning direction and relies on
ADR-0046 and ADR-0047 as authoritative evidence-integrity architecture.

## Decision

The primary marketing, sales, and customer-facing differentiator is
deterministic replay plus evidence integrity.

Secondary differentiators are:

- planned regulated-deployment topology targets, including air-gap, pending
  runtime support, operator controls, validation, and deployment evidence;
- customer-data authority under ADR-0038; and
- supply-chain integrity under ADR-0039.

Air-gap remains a planned regulated-deployment target. It is not the headline
and is not a current supported deployment profile.

## Consequences

- Customer-facing material leads with replay and evidence integrity, not
  air-gap.
- Regulated-buyer conversations anchor on ADR-0046, ADR-0047, and INV-039 as
  the evidence-integrity architecture while continuing to avoid legal,
  compliance, benchmark, or customer-readiness claims.
- Air-gap remains in the buying-wedge story as a possible deployment target, not
  the wedge and not a current runtime capability.
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
- ADR-0046
- ADR-0047
- INV-036
- INV-039
- INV-022 quantified claim provenance

## Boundary

This ADR does not add runtime implementation, RamaLama code, benchmarks,
customer-readiness material, legal admissibility claims, compliance
certification claims, signing, anchoring, SLSA, or in-toto scope. It does not
make air-gap, local-only, or hybrid inference topology currently
customer-selectable or runtime-supported.
