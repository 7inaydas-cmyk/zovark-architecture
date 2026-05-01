# adr-cross-link Specification

## Purpose
TBD - created by archiving change fix-adr-cross-link-verification. Update Purpose after archive.
## Requirements
### Requirement: Cross-link verification SHALL check existence, status, and non-contradiction

For every baseline ADR ID referenced by the rc2 spec set or by patch ADRs 0038-0043, post-apply verification SHALL confirm:

1. **Existence** — a file exists at the post-apply baseline ADR path for the referenced ID.
2. **Status** — the ADR is in `active`, `proposed`, or `amended` status. ADRs in `superseded`, `rejected`, or `historical` SHALL surface as a verification failure that requires an rc2-spec amendment to point at the superseding ADR.
3. **Non-contradiction** — the referenced ADR's asserted invariants (parsed by INV-ID) SHALL NOT directly contradict invariants asserted by patch ADRs 0038-0043 or by the rc2 spec set. Direct contradiction means: same INV-ID, different statement.

#### Scenario: Missing baseline ADR file fails verification

- **WHEN** a referenced ADR ID has no corresponding file post-apply
- **THEN** verification SHALL fail with reason `adr_missing` and identify the reference site

#### Scenario: Referenced ADR in `superseded` status surfaces as failure

- **WHEN** a referenced ADR exists but is `superseded`
- **THEN** verification SHALL fail with reason `superseded_reference` and identify both the referenced ADR and its superseder (when discoverable)

#### Scenario: Same-INV-ID contradiction surfaces as failure

- **WHEN** baseline ADR-X asserts INV-Y with statement "all evidence must be replicated cross-region" and patch ADR-0038 asserts INV-Y with statement "all evidence is local-only by default"
- **THEN** verification SHALL fail with reason `inv_contradiction` and identify both ADRs

### Requirement: Verification scope SHALL include the enumerated baseline ADR set

The cross-link verification SHALL cover, at minimum, the following baseline ADR IDs:

- `ADR-0011` — amended by ADR-0038 (control-plane authority boundary).
- `ADR-0024` — referenced by `INV-020`, `INV-021` (audit erasure, tenant usage).
- `ADR-0025` — referenced by `INV-020` (audit erasure boundary).
- `ADR-0027` — referenced by `INV-018` (verdict canonicalization).
- `ADR-0028` — referenced by `INV-019` (vault threat model).
- `ADR-0030` — referenced by `INV-023` (bootstrap evidence).
- `ADR-0031` — referenced by `INV-022` (claim provenance benchmark artifacts).
- `ADR-0034` — referenced by DD-blocker `M3-DEPENDENCY-002` (tenant DEK rotation).

Adding a new baseline ADR reference to any rc2 spec SHALL require a `MODIFIED Requirements` change against this spec to include the new ADR in the verification set.

#### Scenario: Adding a baseline ADR reference without spec change is invalid

- **WHEN** an rc2 spec is modified to reference a baseline ADR not in the enumerated set
- **THEN** the rc2 spec change SHALL fail review until accompanied by a `MODIFIED Requirements` against `adr-cross-link-verification` extending the verification set

### Requirement: scripts/check_adr_cross_links.py SHALL implement the verification interface

The verification script SHALL:

- Walk: `architecture/adr/**/*.md` (post-apply path), `openspec/specs/**/*.md`, `architecture/adr-index.md`.
- For each baseline ADR ID in the enumerated set: resolve the file, parse status, parse asserted INV-IDs and their statements, compare against patch ADRs 0038-0043 + rc2 specs for same-INV-ID conflicts.
- Exit 0 if every check passes; exit non-zero with one line per failure (`<reference-site>: <reason>: <baseline-adr-id>`) otherwise.
- Write a draft `architecture/adr-index.draft.md` enriching the placeholder rows with metadata pulled from the verified baseline ADRs (status, scope, affected invariants, supersession links).

The script implementation is an M0 deliverable; this spec defines its contract. The script SHALL NOT be implemented as part of this change.

#### Scenario: Clean run on a properly-applied repo

- **WHEN** every referenced baseline ADR exists, has a non-superseded status, and contains no INV-ID contradictions with patch + rc2 specs
- **THEN** the script SHALL exit 0 with output "ADR cross-link verification passed"
- **AND** SHALL write `architecture/adr-index.draft.md` with enriched baseline rows

#### Scenario: Failure run

- **WHEN** at least one verification check fails
- **THEN** the script SHALL print one failure line per check and exit non-zero

### Requirement: adr-index.md SHALL list referenced baseline ADRs as placeholder rows until verified

The repository's `architecture/adr-index.md` SHALL include a section titled "Baseline ADRs (post-apply verified)" listing the enumerated baseline ADR IDs. Until the M0 verification script runs and writes the enriched draft, the rows SHALL display:

```
| ADR-NNNN | <short name> | post-apply-verified | <reference site> |
```

After the script first passes, a human reviewer merges the script-generated draft (which adds full metadata) into `adr-index.md`.

#### Scenario: Baseline section absent from adr-index.md fails review

- **WHEN** `architecture/adr-index.md` does not include the "Baseline ADRs (post-apply verified)" section
- **THEN** review SHALL reject the rc2 freeze tag

### Requirement: Future cross-link verification changes go through this spec

Adding, removing, or modifying the enumerated baseline ADR set, the verification rules, or the script interface SHALL go through a `MODIFIED Requirements` OpenSpec change against `adr-cross-link-verification`. Direct edits to `architecture/objects/adr-cross-link-verification.md` SHALL be rejected at review.

#### Scenario: Removing a baseline ADR from the verification set requires a spec change

- **WHEN** someone proposes that ADR-0030 no longer needs verification
- **THEN** they SHALL file a `MODIFIED Requirements` change against `adr-cross-link-verification` first

