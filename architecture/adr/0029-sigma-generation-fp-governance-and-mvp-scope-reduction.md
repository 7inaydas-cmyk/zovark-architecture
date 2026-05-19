# ADR-0029: Sigma Generation Scope Reduction and Manual Export Boundary

**Status:** active
**Date:** 2026-05-19
**Owner:** detection-owner
**Source:** rewritten from bootstrap ADR-0029 for the v3.2.5.0 consolidation baseline

## Context

The predecessor ADR-0029 tried to reduce Sigma-generation scope while retaining
too much rejected publication and false-positive governance language. The
current baseline separates the concerns:

- ADR-0023 defines the Sigma rule draft-generation pipeline.
- INV-015 requires analyst approval before a Sigma rule is published.
- ADR-0049 defines alert-budget governance for publication paths.

This ADR preserves the scope-reduction decision that remains coherent after
that separation.

## Decision

The initial Sigma-generation scope is draft generation and analyst review, not
system-side SIEM delivery. Zovark stores rule drafts with source linkage,
validation results, review status, and audit events. Analysts may approve a
draft for manual export or reject it with a reason.

System-side publication adapters, corpus-wide production validation, and
automated customer-environment delivery are not part of this decision. They may
only be added through a later ADR or implementation PR that satisfies INV-015,
ADR-0049, tenant policy, audit recording, and benchmark-backed claim rules.

Allowed review statuses for this scope are:

- `pending_review`;
- `approved_for_manual_export`;
- `rejected`; and
- `superseded`.

The approved-for-manual-export status records analyst intent. It does not mean
Zovark pushed a rule into a customer SIEM. Manual export keeps the customer in
their own change-management path until a later publication surface is approved.

ADR-0049 supersedes the historical false-positive governance model with
alert-budget governance. This ADR does not define alert thresholds, corpus
drift policy, or publication eligibility.

## Consequences

- Sigma generation remains useful while avoiding premature delivery surfaces.
- Analysts can evaluate and export rule drafts without the product claiming
  automated customer-environment deployment.
- Later publication work has a narrow contract to satisfy: INV-015, ADR-0049,
  tenant policy, and auditability.
- Rejected rule drafts and review outcomes can still feed research work through
  ADR-0040, but cannot mutate customer runtime directly.

## Alternatives Considered

- **Keep generation and delivery in one scope.** Rejected because delivery has a
  higher governance bar than draft generation.
- **Remove Sigma generation entirely.** Rejected because review-gated drafts are
  still valuable detection material.
- **Let review status imply customer deployment.** Rejected because manual
  export and system-side publication are separate operational acts.

