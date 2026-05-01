## MODIFIED Requirements

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
