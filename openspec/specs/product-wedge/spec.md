# product-wedge Specification

## Purpose
Defines Zovark's canonical product positioning, the canonical core-flow phrasing, and
the rules that govern how these framings must appear across architecture and
customer-facing documentation.

This spec was modified by the `reposition-to-audit-grade-evidence-layer` OpenSpec
change (2026-05-02). The internal architecture metaphor ("tape recorder") is
preserved for engineering use. The external product wedge and customer-facing
language now lead with the audit-grade evidence layer framing.

## Requirements

### Requirement: External canonical product-wedge statement

Customer-facing documents, investor materials, and external positioning SHALL use
the following canonical external wedge statement:

> **Zovark is the audit-grade evidence layer for AI-assisted SOC response.**

The customer-facing one-sentence description is:

> **Before your SOC isolates a host or disables a user, Zovark shows the evidence, explains the verdict, records the approval path, and creates a replayable proof package.**

These statements MUST appear verbatim in external-facing documents. Alternative
framings (e.g., "AI SOC platform", "agent framework", "investigation engine",
"tape recorder") MUST NOT be used as the primary external positioning.

#### Scenario: External document leads with the audit-grade evidence layer statement

- **WHEN** a customer-facing, investor-facing, or partner-facing document states
  Zovark's product positioning
- **THEN** the external canonical statement appears verbatim
- **AND** no alternative primary positioning statement contradicts it

#### Scenario: "tape recorder" framing is not used externally as the headline

- **WHEN** any external document refers to Zovark's product positioning
- **THEN** "tape recorder" does not appear as the primary description
- **AND** if used at all, it is explicitly subordinated as an internal engineering
  metaphor (e.g., "Internally, Zovark uses an investigation tape as its proof
  substrate.")

### Requirement: Internal canonical product-wedge statement

Internal architecture documents, engineering specs, and ADRs SHALL use the
following canonical internal wedge statement:

> **Zovark is the tape recorder for cybersecurity investigations.**

This statement governs internal architecture documents. It MUST NOT appear as the
primary positioning in customer-facing or investor-facing documents.

#### Scenario: Internal architecture document uses the tape recorder statement

- **WHEN** `architecture/source-of-truth.md`, `architecture/one-page-architecture.md`,
  or any `openspec/specs/` document states Zovark's product positioning
- **THEN** the internal canonical statement appears verbatim
- **AND** no other internal positioning statement contradicts it

### Requirement: Canonical core-flow phrasing

The architecture and customer-facing documentation set SHALL describe Zovark's core
flow using a single canonical phrasing. The canonical core flow is:

> **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

The arrow sequence MUST appear verbatim in internal architecture documents wherever
the core flow is described. External documents MAY describe the same flow in
customer-facing language (see the `reposition-to-audit-grade-evidence-layer` change
docs) but MUST NOT contradict the internal flow sequence.

#### Scenario: Internal architecture documents use the canonical core-flow sequence

- **WHEN** an internal architecture document describes how Zovark processes alerts
  end-to-end
- **THEN** the canonical core-flow arrow sequence appears verbatim
- **AND** no alternative end-to-end pipeline is presented as the primary flow

#### Scenario: Architecture overviews name the investigation tape and EDR handoff

- **WHEN** a top-level architecture document includes a product-wedge or core-flow
  section
- **THEN** the section names the **investigation tape** as the central proof substrate
- **AND** the section names the **EDR handoff** as the approval-required action card
  that is evidence-linked, replayable, and reversible

### Requirement: Hero artifact in external materials

External documents SHALL lead with the **approval-required EDR action card** and the
**replayable proof package** as the product hero artifacts. The investigation tape is
the internal proof substrate that produces these artifacts; it is not the external
headline.

#### Scenario: External demo and outreach materials lead with the action card

- **WHEN** a demo script, outreach document, or investor deck describes what Zovark
  produces
- **THEN** the first artifact named is the EDR action card (recommended action,
  evidence basis, approval status, reversibility class)
- **AND** the second artifact named is the replayable proof package
- **AND** the investigation tape is described as the substrate, not the headline

### Requirement: Wedge changes go through this spec

The architecture review process SHALL treat any future change to Zovark's product
wedge or core flow as a modification of this spec, not as ad-hoc edits to individual
documents.

#### Scenario: Future wedge revisions require a spec change

- **WHEN** anyone proposes a change to either canonical wedge statement or the
  canonical core flow
- **THEN** the proposal is filed as an OpenSpec change with a `MODIFIED Requirements`
  block against `product-wedge`
- **AND** the change updates every document that contains the previous canonical
  statement, in the same change

#### Scenario: Wedge consistency is verifiable

- **WHEN** a finalization-checklist verification pass runs
- **THEN** internal architecture documents contain the internal canonical statement
- **AND** external documents contain the external canonical statement
- **AND** no document uses the internal statement as external positioning or vice versa

