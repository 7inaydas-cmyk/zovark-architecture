# ADR Cross-Link Verification — Object Architecture

The rc2 spec set introduces references to baseline ADRs that live outside this
finalization repo (in the v3.2.3.5 baseline). Without a documented post-apply
verification step, the cross-references could resolve to ADRs that no longer exist,
were superseded, or contradict patch ADRs 0038-0043.

This document specifies the verification contract. The verification script
`scripts/check_adr_cross_links.py` is an **M0 deliverable**; the binding spec is
`openspec/specs/adr-cross-link-verification/spec.md`. Direct edits to this file
without a corresponding `MODIFIED Requirements` change against the
`adr-cross-link-verification` capability SHALL be rejected at review.

## What "cross-link verification" means

For every baseline ADR ID referenced by the rc2 spec set or by patch ADRs
0038-0043, post-apply verification confirms three things:

1. **Existence** — a file exists at the post-apply baseline ADR path for the
   referenced ID.
2. **Status** — the ADR is `active`, `proposed`, or `amended`. ADRs in
   `superseded`, `rejected`, or `historical` states surface as failures so the
   referencing rc2 spec is amended to point at the superseder.
3. **Non-contradiction** — the referenced ADR's invariants (parsed by INV-ID) do
   not directly contradict the invariants asserted by patch ADRs 0038-0043 or by
   the rc2 spec set. "Direct contradiction" means same INV-ID with different
   statements.

## Enumerated baseline ADR set

The rc2 spec set + patch ADRs reference the following baseline ADRs:

| ADR ID | Reference site | Notes |
|---|---|---|
| ADR-0011 | Patch ADR-0038 (control-plane authority boundary) amends ADR-0011. |
| ADR-0024 | `invariants.md` `INV-020`, `INV-021` | audit erasure boundary, tenant usage attribution |
| ADR-0025 | `invariants.md` `INV-020` | audit erasure boundary |
| ADR-0027 | `invariants.md` `INV-018` | verdict canonicalization |
| ADR-0028 | `invariants.md` `INV-019`, rc2 `vault-authorization` spec | vault threat model |
| ADR-0030 | `invariants.md` `INV-023` | bootstrap evidence: every fitness function has both a fail-fixture and a pass-fixture |
| ADR-0031 | `invariants.md` `INV-022`, rc2 `claim-provenance` spec | claim provenance benchmark artifacts |
| ADR-0034 | DD-blocker `M3-DEPENDENCY-002`, rc2 `vault-authorization` spec | tenant DEK rotation |

Adding a new baseline ADR reference to any rc2 spec requires a
`MODIFIED Requirements` change against this capability to extend the verification
set.

## Script interface contract (M0 deliverable)

`scripts/check_adr_cross_links.py` SHALL:

### Walk

- `architecture/adr/**/*.md` (post-apply path).
- `openspec/specs/**/*.md` (rc2 spec set + future specs).
- `architecture/adr-index.md`.

### Per-baseline-ADR check

For each baseline ADR ID in the enumerated set:

1. Resolve the ADR file path. **Fail** if missing.
2. Parse status from frontmatter or body. **Fail** if `superseded`, `rejected`,
   or `historical`.
3. Parse asserted invariants (INV-NNN tokens) and their statements.
4. Compare invariants against patch ADRs 0038-0043 and rc2 specs for same-INV-ID
   conflicts. **Fail** on direct contradiction.

### Output

- **Exit 0** if all checks pass; print `ADR cross-link verification passed`.
- **Exit non-zero** with one line per failure: `<reference-site>: <reason>: <baseline-adr-id>`.
- On success, write `architecture/adr-index.draft.md` enriching the placeholder
  rows with full metadata pulled from the verified baseline ADRs.

### Implementation hints (non-binding)

- Mirror `scripts/check_mvp_scope_consistency.py` and the to-be-implemented
  `scripts/check_claim_provenance.py` — same walk pattern, same exit-code
  convention.
- Sharing helper code via a future `scripts/_arch_check_helpers.py` is encouraged
  but not required.
- The script SHALL NOT make network calls.

## M0 acceptance criteria

The deliverable is accepted when:

1. `scripts/check_adr_cross_links.py` exists, executable, matches this contract.
2. Running the script after applying v3.2.4.6 to the v3.2.3.5 baseline returns
   exit 0.
3. The script is wired into a post-apply gate (out of scope for this change;
   tracked as M0 follow-up).
4. `architecture/adr-index.md`'s "Baseline ADRs (post-apply verified)" section is
   replaced with the script-generated draft after human review.

## adr-index.md placeholder rows

Until the script runs, the eight baseline ADRs appear as placeholder rows in
`architecture/adr-index.md` under "Baseline ADRs (post-apply verified)". After the
script first passes, a human reviewer merges the script's
`architecture/adr-index.draft.md` into the live index.

## Build planning

This spec gives the build team enough to scope:

- **Verification script:** walk + parse + compare; clean exit-code surface.
- **CI gate:** post-apply step that runs the script; failure blocks promotion.
- **Audit trail:** the script's enriched draft + the human review record become
  part of the architecture-rcN tag's evidence.

## What this document does not define

- Implementing the script (M0 deliverable).
- Producing or importing the baseline ADRs.
- Auditing baseline ADR content (the script does that after apply).
- Preventing baseline-ADR drift between v3.2.3.5 and v3.2.4.6 (handled by
  version-pinning the baseline at apply time, separate concern).
- Semantic-level contradiction detection beyond same-INV-ID conflict (future
  enhancement via `MODIFIED Requirements`).
