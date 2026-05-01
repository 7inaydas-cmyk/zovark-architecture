# adr-cross-link Specification

## Purpose
Defines the post-apply verification contract for baseline ADRs (0001–0037) referenced by patch ADRs (0038–0043) and the rc2/rc3 spec set, including the bootstrap-mode (no baseline present) and post-apply-mode behaviors of `scripts/check_adr_cross_links.py`.
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

The verification script SHALL run in one of two auto-detected modes.

**Bootstrap mode** — when `architecture/adr/` does not exist at the repo root or contains no ADR with a numeric prefix less than 38 (i.e., the v3.2.3.5 baseline has not been merged in). Bootstrap mode SHALL:

- Verify `architecture/adr-index.md` exists.
- Verify the section titled "Baseline ADRs (post-apply verified)" is present in the index.
- Verify every enumerated baseline ADR ID (per the requirement "Verification scope SHALL include the enumerated baseline ADR set") appears in the index.
- Verify each patch ADR in the range ADR-0038 through ADR-0043 has a file under `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/adr/`.
- Exit 0 with a banner that explicitly lists the baseline ADRs awaiting post-apply verification.

**Post-apply mode** — when `architecture/adr/` exists at the repo root with at least one ADR file with a numeric prefix less than 38. Post-apply mode SHALL:

- Walk `architecture/adr/**/*.md`, `openspec/specs/**/*.md`, and `architecture/adr-index.md`.
- For each enumerated baseline ADR ID: resolve the file (fail if missing), parse status (fail if `superseded`, `rejected`, or `historical`), parse asserted INV-IDs and their statements.
- Compare INV-ID statements against patch ADRs 0038-0043 + rc2 specs for same-INV-ID conflicts (logged for human review; auto-failure on direct contradiction is a future enhancement).
- Write `architecture/adr-index.draft.md` enriching the placeholder rows with status pulled from each verified baseline ADR.
- Exit 0 if every check passes; exit non-zero with one line per failure (`<reference-site>: <reason>: <baseline-adr-id>`) otherwise.

The script SHALL use only the Python standard library (no third-party dependencies).

The script implementation lands in the rc3 change `fix-adr-cross-link-enforcement`. Subsequent changes to mode-detection logic, the enumerated baseline set, or the draft-output format SHALL go through a `MODIFIED Requirements` change against this spec.

#### Scenario: Bootstrap mode passes when index has placeholder section + IDs and patch ADRs are present

- **WHEN** the repo is in bootstrap state (no baseline ADRs at repo root) and `architecture/adr-index.md` contains the "Baseline ADRs (post-apply verified)" section with all 8 enumerated IDs, and patch ADRs ADR-0038 through ADR-0043 are present in the patch tree
- **THEN** the script SHALL exit 0 and print a banner listing the baseline ADRs awaiting post-apply verification

#### Scenario: Bootstrap mode fails when placeholder section is missing

- **WHEN** the repo is in bootstrap state and `architecture/adr-index.md` does not contain the "Baseline ADRs (post-apply verified)" section
- **THEN** the script SHALL exit non-zero with a clear "missing 'Baseline ADRs (post-apply verified)' section" failure

#### Scenario: Post-apply mode runs full verification

- **WHEN** the repo has been merged with the v3.2.3.5 baseline (numeric-prefix-less-than-38 ADR files exist at repo root)
- **THEN** the script SHALL run the full per-ADR existence + status + INV gathering walk
- **AND** SHALL write `architecture/adr-index.draft.md` with enriched baseline rows

#### Scenario: Post-apply mode fails on missing baseline ADR

- **WHEN** an enumerated baseline ADR ID has no matching file under `architecture/adr/`
- **THEN** the script SHALL exit non-zero with `adr_missing` failure for that ID

#### Scenario: Post-apply mode fails on superseded baseline ADR

- **WHEN** an enumerated baseline ADR's parsed status is `superseded`
- **THEN** the script SHALL exit non-zero with `superseded_reference` failure

#### Scenario: Failure run

- **WHEN** at least one verification check fails (in either mode)
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

