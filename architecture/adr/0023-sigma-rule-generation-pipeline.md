# ADR-0023: Sigma Rule Generation Pipeline

**Status:** active
**Date:** 2026-05-19
**Owner:** detection-owner
**Source:** rewritten from bootstrap ADR-0023 for the v3.2.5.0 consolidation baseline

## Context

Sigma rule generation remains a useful downstream detection workflow, but the
historical source mixed that workflow with rejected publication paths and
unsupported marketing claims. INV-015 is now the binding safety rule: no Sigma
rule reaches a customer SIEM without an analyst approval record. ADR-0049
governs alert-budget evaluation for approved publication paths.

This ADR covers the generation pipeline only. It does not authorize direct SIEM
publication, customer outreach claims, benchmark claims, or any bypass around
analyst review.

## Decision

Zovark may generate Sigma rule drafts from completed investigations as a
post-investigation detection workflow. The pipeline is:

1. **Extract:** collect approved structured evidence, verdict facts, IOCs, and
   technique references from replay-grade investigation records.
2. **Synthesize:** produce a Sigma rule draft from those structured inputs.
3. **Validate syntax:** reject drafts that fail Sigma syntax or required-field
   checks.
4. **Validate against source evidence:** confirm that the draft matches the
   source investigation evidence that motivated it.
5. **Score and explain:** attach confidence, source linkage, and rule-quality
   explanation for analyst review.
6. **Store for review:** persist the draft with provenance, source
   investigation reference, validation results, and audit linkage.

The pipeline output is review material. It is not a published detection, a
customer-ready claim, or a runtime update. A rule can move beyond review only
through an analyst approval event under INV-015 and the governance checks in
ADR-0049.

The generation system must record enough provenance for replay and audit:
source investigation reference, evidence hashes, rule version, validation
results, reviewer decisions, and rejection reasons. Rejections remain useful
feedback but do not silently mutate production behavior.

ADR-0049 owns alert-budget governance. This ADR owns the pipeline architecture
that prepares rule drafts for that governance path.

## Consequences

- Detection-generation work has a clear architecture boundary and audit trail.
- Analysts remain the approval gate for customer-facing detection changes.
- Rule drafts can improve over time without becoming silent runtime mutations.
- The pipeline depends on replay-grade records and verdict canonicalization, so
  it inherits the integrity constraints of ADR-0020, ADR-0046, and ADR-0047.
- SIEM-specific delivery remains outside this ADR unless separately approved.

## Alternatives Considered

- **Generate no Sigma drafts.** Rejected because confirmed investigations can
  produce useful detection material when review-gated.
- **Treat generated rules as deployable output.** Rejected because INV-015
  requires analyst approval.
- **Make alert-budget checks part of the generation pipeline.** Rejected
  because ADR-0049 owns publication governance and should remain separable from
  draft generation.

