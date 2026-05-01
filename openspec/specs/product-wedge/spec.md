# product-wedge Specification

## Purpose
TBD - created by archiving change fix-product-wedge. Update Purpose after archive.
## Requirements
### Requirement: Canonical product-wedge statement

The architecture and customer-facing documentation set SHALL use a single canonical product-wedge statement to describe Zovark. The canonical statement is:

> **Zovark is the tape recorder for cybersecurity investigations.**

The statement MUST appear verbatim (case- and punctuation-preserving) wherever Zovark's product positioning is stated in top-level architecture and customer-facing documents. Paraphrases, near-paraphrases, or alternative wedge framings (e.g., "AI SOC platform", "agent framework", "investigation engine") MUST NOT be used as the primary positioning statement.

#### Scenario: Source-of-truth contains the canonical statement

- **WHEN** `architecture/source-of-truth.md` is read
- **THEN** the canonical statement appears verbatim in the document
- **AND** no other product-positioning statement contradicts it

#### Scenario: MVP scope document contains the canonical statement

- **WHEN** `mvp-scope.md` (the active MVP scope document) is read
- **THEN** the canonical statement appears verbatim
- **AND** any first-paragraph product-wedge prose follows the canonical statement, not replaces it

#### Scenario: Top-level architecture-package documents contain the canonical statement

- **WHEN** `ZOVARK-v3.2.4.6-FINAL.md` and `ENGINEERING-READY-HANDOFF.md` are read (or their successors in later patch versions)
- **THEN** the canonical statement appears verbatim under a clearly named section near the top of the document

#### Scenario: Generic platform framing is not used as positioning

- **WHEN** any architecture or customer-facing document refers to Zovark's product positioning
- **THEN** the canonical statement is used
- **AND** generic framings such as "AI SOC platform" do not appear as the primary description; if used at all, they are explicitly subordinated (e.g., "Zovark uses AI SOC techniques internally, but the product is the tape recorder.")

### Requirement: Canonical core-flow phrasing

The architecture and customer-facing documentation set SHALL describe Zovark's core flow using a single canonical phrasing. The canonical core flow is:

> **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

The arrow sequence MUST appear verbatim wherever the core flow is described. Documents MAY elaborate on individual steps after the sequence, but MUST NOT introduce alternative bookings (e.g., flows that omit EDR as the entry, omit replayable evidence as the bridge, or omit rollback as the final state).

#### Scenario: Core flow appears alongside the wedge statement

- **WHEN** the canonical product-wedge statement appears in a document
- **THEN** the canonical core-flow arrow sequence appears immediately after, in the same section, verbatim

#### Scenario: No alternative core-flow framings are introduced

- **WHEN** any document describes how Zovark processes alerts, evidence, or response actions end-to-end
- **THEN** the canonical core-flow sequence is used
- **AND** no alternative end-to-end pipeline is presented as the primary flow

#### Scenario: Architecture overviews mention investigation tape and EDR handoff

- **WHEN** a top-level architecture or customer-facing document includes a product-wedge or core-flow section
- **THEN** the section names the **investigation tape** as the central recorded object
- **AND** the section names the **EDR handoff** as replayable, evidence-linked, and reversible
- **AND** the section does not redefine these objects (full schemas are out of scope; signposting is sufficient)

### Requirement: Wedge changes go through this spec

The architecture review process SHALL treat any future change to Zovark's product wedge or core flow as a modification of this spec, not as ad-hoc edits to individual documents.

#### Scenario: Future wedge revisions require a spec change

- **WHEN** anyone proposes a change to the canonical product-wedge statement or canonical core flow
- **THEN** the proposal is filed as an OpenSpec change with a `MODIFIED Requirements` block against `product-wedge`
- **AND** the change updates every document that contains the previous canonical statement, in the same change

#### Scenario: Wedge consistency is verifiable

- **WHEN** a finalization-checklist verification pass runs
- **THEN** every document listed in `architecture/source-of-truth.md` source hierarchy that mentions product positioning contains the canonical statement and core flow
- **AND** any deviation is filed as a new `area:tape` / `severity:P0` issue against this spec

