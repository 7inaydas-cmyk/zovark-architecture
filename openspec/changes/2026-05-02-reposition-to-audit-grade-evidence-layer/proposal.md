## Why

YC readiness requires a product wedge that lands with a non-technical evaluator in
one sentence. "The tape recorder for cybersecurity investigations" is an accurate
internal engineering metaphor but does not communicate the customer value or the
market category to an investor or MSSP buyer.

The internal architecture is correct and remains unchanged. The investigation tape,
evidence ledger, timeline, findings, verdict, EDR handoff, replay report, and audit
chain are all valid and frozen at rc3. What changes is the external framing: what
we call the product, what we lead with in demos, and what the customer-facing
artifact looks like.

This change is documentation-only. No new runtime capabilities are introduced.
No architecture specs are modified. All existing enforcement scripts continue to
pass.

## What Changes

### MODIFIED Requirements — `product-wedge`

- The spec now distinguishes an **internal** canonical statement (engineering and
  architecture documents) from an **external** canonical statement (customer-facing,
  investor-facing, partner-facing documents).
- Internal: "Zovark is the tape recorder for cybersecurity investigations." —
  unchanged, governs all `openspec/specs/`, `architecture/`, and ADR documents.
- External: "Zovark is the audit-grade evidence layer for AI-assisted SOC response."
- Customer one-liner: "Before your SOC isolates a host or disables a user, Zovark
  shows the evidence, explains the verdict, records the approval path, and creates
  a replayable proof package."
- The product hero artifacts are the **approval-required EDR action card** and the
  **replayable proof package**. The investigation tape is the internal proof
  substrate, not the external headline.

### Documents updated

- `openspec/specs/product-wedge/spec.md` — MODIFIED Requirements (internal/external split)
- `architecture/source-of-truth.md` — updated "Current product wedge" section
- `architecture/one-page-architecture.md` — §1 and §7 updated
- `.kiro/specs/slice-001-investigation-tape/requirements.md` — overview framing updated
- `.kiro/specs/slice-001-investigation-tape/design.md` — `customer-report.md` structure updated to lead with action card

### New documents

- `docs/yc-positioning.md` — YC application positioning doc
- `docs/slice-001-demo-script.md` — Slice 001 demo script for design partners and YC
- `docs/mssp-outreach.md` — MSSP outreach one-pager

## Capabilities

### Modified Capabilities

- `product-wedge` — MODIFIED Requirements: internal/external wedge split; hero
  artifact designation; `customer-report.md` leads with action card.

### New Capabilities

(none — documentation only)

## Impact

- **Documents touched:** 5 existing files (minimal edits).
- **Documents added:** 3 new docs under this change directory.
- **Code:** none. Slice 001 implementation scope is unchanged.
- **Architecture checks:** all existing enforcement scripts continue to pass.
  `check_mvp_scope_consistency.py`, `check_claim_provenance.py`, and
  `check_adr_cross_links.py` are unaffected.
- **Out of scope:** live EDR API, autonomous response, Sigma, SIEM, full UI,
  production vault runtime, production multi-tenancy, broad architecture rewrite.
