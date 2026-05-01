# build-planning-artifacts Specification

## Purpose
Governs build-planning derived artifacts — the one-page architecture map (`architecture/one-page-architecture.md`) and its companion Mermaid diagram (`architecture/one-page-architecture.mmd`) — including content rules, the page-fit budget, and the requirement that the artifacts not introduce new architecture decisions.
## Requirements
### Requirement: One-page architecture map SHALL exist

The repository SHALL contain `architecture/one-page-architecture.md` — a single-page derived map of the rc3-frozen architecture intended for build planning. The file SHALL fit on one printed page (target ≤ 100 markdown lines including headings and blank lines).

#### Scenario: Missing one-pager fails review

- **WHEN** a build branch is opened without `architecture/one-page-architecture.md` present
- **THEN** review SHALL reject the branch and require the file before any product implementation begins

#### Scenario: One-pager exceeding the page-fit budget fails review

- **WHEN** `architecture/one-page-architecture.md` exceeds 100 lines
- **THEN** review SHALL flag the file for trimming or for migration of overflow content into the underlying specs

### Requirement: One-pager SHALL preserve the canonical wedge verbatim

`architecture/one-page-architecture.md` SHALL include the canonical product-wedge statement and the canonical core flow verbatim, per the `product-wedge` capability:

- **Statement:** Zovark is the tape recorder for cybersecurity investigations.
- **Core flow:** EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.

Paraphrasing or shortening the statement or flow SHALL be rejected — the `product-wedge` spec already requires verbatim use across the architecture corpus.

#### Scenario: One-pager paraphrases the wedge

- **WHEN** the one-pager substitutes a paraphrase (e.g., "Zovark records investigations") for the canonical statement
- **THEN** review SHALL reject and require verbatim wording

### Requirement: One-pager SHALL declare the first MVP build slice

The one-pager SHALL declare exactly one "first MVP build slice" path. The slice SHALL be the smallest path that exercises every governing spec under `openspec/specs/`. The current rc3 declared slice is:

```
1 EDR sample → 1 investigation tape → 1 timeline → 1 evidence ledger
            → 1 verdict → 1 EDR handoff recommendation → 1 replay report
```

The one-pager SHALL match this declaration. Changes to the slice SHALL go through a `MODIFIED Requirements` change against `build-planning-artifacts`.

#### Scenario: First MVP slice is missing from one-pager

- **WHEN** the one-pager omits the first MVP slice declaration
- **THEN** review SHALL reject

#### Scenario: One-pager declares a different MVP slice than rc3

- **WHEN** the one-pager declares an MVP slice that differs from the rc3 scorecard's "Bridge to product implementation" slice
- **THEN** review SHALL reject and require the one-pager to match (or a `MODIFIED Requirements` change to update the slice)

### Requirement: One-pager SHALL list explicit deferred scope

The one-pager SHALL list at least the rc3 scorecard's `PASS-with-explicit-DEFERRAL` items as out-of-scope for the first slice:

- M2 control-plane DR sketch (ARCH-P2-002).
- M3 vault IPC schemas + `check_vault_ipc_contract.py`.
- Post-apply baseline-ADR cross-link verification.

It MAY also list additional items that are obviously out of MVP (live EDR API, autonomous action, multi-tenancy, Sigma/SIEM publication, full UI, customer dashboards, DR drills).

#### Scenario: Deferred scope omitted

- **WHEN** the one-pager does not enumerate at least the three DEFERRED items from the rc3 scorecard
- **THEN** review SHALL reject

### Requirement: One-pager SHALL NOT introduce new architecture decisions

The one-pager SHALL be derived from the existing 8 governing specs and 5 architecture object documents. It SHALL NOT introduce new fields, new object names, new capabilities, new wedge framings, new vendor commitments, or new milestone definitions.

#### Scenario: One-pager invents a new capability

- **WHEN** the one-pager describes an architecture object or capability that has no corresponding entry under `openspec/specs/` or `architecture/objects/`
- **THEN** review SHALL reject

#### Scenario: One-pager redefines a field

- **WHEN** the one-pager describes a field or sub-field that contradicts the canonical definition in the relevant capability spec
- **THEN** review SHALL reject and require alignment

### Requirement: Mermaid diagram SHALL accompany the markdown one-pager

The repository SHALL contain `architecture/one-page-architecture.mmd` — a Mermaid flowchart representing the same data flow as the markdown one-pager. The Mermaid file SHALL include:

- An `MVP Slice` subgraph containing the 7-step slice path.
- A `Deferred` subgraph listing out-of-MVP items as nodes (no edges to or within the MVP subgraph).

#### Scenario: Mermaid file missing

- **WHEN** `architecture/one-page-architecture.md` exists but `architecture/one-page-architecture.mmd` does not
- **THEN** review SHALL reject

#### Scenario: Mermaid file contains an edge from Deferred to MVP

- **WHEN** the `.mmd` file connects a Deferred node to an MVP node
- **THEN** review SHALL reject (deferred items have no committed path into MVP; an edge would imply a roadmap claim)

### Requirement: Future updates go through this spec

Changes to the one-pager's content (wedge wording, MVP slice declaration, deferred scope list, page-fit budget) SHALL go through a `MODIFIED Requirements` OpenSpec change against `build-planning-artifacts`. Direct edits to `architecture/one-page-architecture.md` or `architecture/one-page-architecture.mmd` SHALL be rejected at review.

#### Scenario: Direct edit without spec change

- **WHEN** a PR modifies `architecture/one-page-architecture.md` without a corresponding `MODIFIED Requirements` change
- **THEN** review SHALL reject and ask for a spec proposal first

#### Scenario: Spec-driven update

- **WHEN** an OpenSpec `MODIFIED Requirements` change against `build-planning-artifacts` lands first, and a follow-up PR updates the one-pager content per the new spec
- **THEN** review SHALL accept the update

