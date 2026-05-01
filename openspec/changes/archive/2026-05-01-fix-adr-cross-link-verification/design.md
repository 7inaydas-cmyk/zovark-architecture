## Context

The rc2 spec set introduces several cross-references to baseline ADRs that live outside this repo:

| Spec | References baseline ADR(s) |
|---|---|
| `claim-provenance` | ADR-0031 (per `INV-022`) |
| `investigation-tape` | (none direct) |
| `edr-handoff` | (none direct, but adopts policy snapshots from baseline ADRs) |
| `replay-and-audit` | ADR-0024, ADR-0025 (audit erasure boundary), ADR-0027 (verdict canonicalization), ADR-0030 (bootstrap evidence), implicit ADR-0042 in this tree |
| `vault-authorization` | ADR-0028 (vault threat model), ADR-0034 (tenant DEK rotation) |

`adr-index.md` lists ADR-0038…0043 with full metadata, but ADR-0001…0037 are
referenced by ID without metadata. Baseline ADR contents could have superseded the
behavior the rc2 specs assume, contradict ADR-0038 (which amends ADR-0011), or be
missing entirely from a careless apply.

The fix is not to import baseline ADRs into this repo (they live in v3.2.3.5 and
will continue to). The fix is to **specify the verification contract** so a script
checks the baseline ADRs after the patch is applied.

This is documentation-only; the script is an M0 deliverable.

## Goals / Non-Goals

**Goals:**

- Specify what cross-link verification means: existence, status, non-contradiction.
- Enumerate the baseline ADR IDs the rc2 spec set depends on.
- Specify `scripts/check_adr_cross_links.py`'s interface (CLI, walk, exit codes).
- Specify M0 acceptance criteria for the script.
- Update `architecture/adr-index.md` with a "Baseline ADRs (post-apply verified)" section listing the referenced IDs as placeholder rows.
- Move finalization-checklist criterion #3 (ADR inventory and supersession) from PASS-with-tracked-gaps to PASS for rc2.

**Non-Goals:**

- Implementing the script.
- Producing or importing the baseline ADRs.
- Auditing baseline ADR content (the script's job after apply).
- Preventing baseline-ADR drift between v3.2.3.5 and v3.2.4.6 (that's a different concern, addressed by version-pinning the baseline at apply time).

## Decisions

### What "cross-link verification" means

For each baseline ADR ID referenced by an rc2 spec, after applying the patch to the v3.2.3.5 baseline, the verifier SHALL confirm:

1. **Existence** — a file at `architecture/adr/<NNNN>-*.md` (or post-apply equivalent path) exists for the referenced ID.
2. **Status** — the ADR is in `active`, `proposed`, or `amended` status. ADRs in `superseded`, `rejected`, or `historical` SHALL NOT be silently relied on; if a referenced ADR is in those states, the verifier SHALL surface the issue with the reference site (rc2 spec) so the rc2 spec can be amended to point at the superseding ADR.
3. **Non-contradiction with patch ADRs** — the referenced ADR's invariants (parsed from the ADR's metadata or text) SHALL NOT directly contradict invariants asserted by patch ADRs 0038-0043 or by the rc2 spec set. (Direct contradiction is conservative — same invariant ID, different statement; not "two ADRs that touch the same area.")

**Rationale.** Existence + status is the easy check; non-contradiction is the harder one. Conservative non-contradiction (same INV-ID, different text) catches the failure modes the rc2 push actually risks (e.g., baseline ADR-0028 was superseded post-rc1 and the new vault model conflicts with `INV-019`'s wording). Alternative considered: full semantic comparison. Rejected — semantic comparison is open-ended; the conservative same-INV-ID check is auditable.

### Baseline ADR IDs the rc2 spec set depends on

| ADR ID | Source | Used by |
|---|---|---|
| ADR-0011 | `adr-index.md` patch | Amended by ADR-0038 (control-plane authority boundary) |
| ADR-0024 | `invariants.md` INV-021, INV-020 | tenant usage attribution; audit erasure boundary |
| ADR-0025 | `invariants.md` INV-020 | audit erasure boundary |
| ADR-0027 | `invariants.md` INV-018 | verdict canonicalization |
| ADR-0028 | `invariants.md` INV-019 | vault threat model |
| ADR-0030 | `invariants.md` INV-023 | bootstrap evidence (fail/pass fixtures) |
| ADR-0031 | `invariants.md` INV-022 | claim provenance benchmark artifacts |
| ADR-0034 | DD-blocker `M3-DEPENDENCY-002` | tenant DEK rotation |

Adding a new baseline ADR reference requires a `MODIFIED Requirements` change against `adr-cross-link-verification` to include it in the verification set.

**Rationale.** Enumeration is auditable. Alternative considered: scan all baseline ADR refs at runtime. Acceptable as an enhancement, but the explicit enumeration is the spec; runtime scan can be a `MODIFIED Requirements` later.

### Script interface

`scripts/check_adr_cross_links.py` SHALL:

- Walk: `architecture/adr/**/*.md` (post-apply path), `openspec/specs/**/*.md` (rc2 spec set), `architecture/adr-index.md`.
- For each referenced baseline ADR ID:
  - Resolve the ADR file path.
  - Parse status from frontmatter or body.
  - Parse asserted invariants (INV-NNN tokens).
  - Compare invariants to patch ADRs 0038-0043 + rc2 specs for same-INV-ID conflicts.
- Exit 0 if all checks pass; exit non-zero with a per-check failure list otherwise.

The script SHOULD share helpers with `scripts/check_mvp_scope_consistency.py` and `scripts/check_claim_provenance.py` (when implemented) — same walk pattern, same exit-code convention.

**Rationale.** Mirrors the existing M0/M3 fitness-function pattern.

### Updates to `architecture/adr-index.md`

Add a section after the existing 13-column ADR table titled "Baseline ADRs (post-apply verified)". The section lists the eight referenced IDs (0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034) as placeholder rows: `ADR-NNNN | <name> | post-apply-verified | <reference site>`. After the M0 verification script runs, the rows are updated with full metadata pulled from the baseline.

**Rationale.** Surfaces the dependency in the same document a reviewer reads to understand ADR status. Alternative considered: a separate "Baseline ADRs" doc. Rejected — splits the source of truth on ADR inventory.

### M0 acceptance criteria

The deliverable is accepted when:

1. `scripts/check_adr_cross_links.py` exists, executable, matching the interface in this spec.
2. Running the script after applying v3.2.4.6 to the v3.2.3.5 baseline returns exit 0.
3. The script is wired into a post-apply gate (out of scope for this change; tracked as M0 follow-up).
4. `architecture/adr-index.md` "Baseline ADRs (post-apply verified)" section is populated with full metadata pulled from the verified baseline ADRs at the same time the script first passes.

## Risks / Trade-offs

- **Risk:** baseline ADRs may be in mid-flight changes themselves (e.g., ADR-0028 superseded by something between v3.2.3.5 and v3.2.4.6). → **Mitigation:** the verifier surfaces status changes and forces an rc2-spec amendment when a referenced ADR is superseded.
- **Risk:** the conservative non-contradiction check misses semantic contradictions where two ADRs use different INV-IDs but contradict in spirit. → **Mitigation:** acceptable for M0; semantic checks land later as a `MODIFIED Requirements`.
- **Trade-off:** the placeholder rows in `adr-index.md` show "post-apply-verified" until the script runs. Accepted: the placeholder is honest about state and gives reviewers a clear signal.

## Migration Plan

1. Land `architecture/objects/adr-cross-link-verification.md` with the verification meaning, the eight baseline ADR IDs, the script interface, the M0 acceptance criteria.
2. Add the "Baseline ADRs (post-apply verified)" section to `architecture/adr-index.md` listing the eight IDs as placeholder rows.
3. Capture as `openspec/specs/adr-cross-link-verification/spec.md` via archive.

**Rollback:** revert. The cross-link gap goes back to UNAUDITED.

## Open Questions

- Should the verifier walk the baseline patches (v3.2.3.5 + earlier) themselves to confirm ADRs aren't accidentally removed by an apply? Defer — the v3.2.3.5 baseline is currently treated as an immutable predecessor; if that changes, this spec needs a `MODIFIED Requirements` to add baseline-immutability checks.
- Should the placeholder rows be updated automatically by the script or require human review? Decision: script writes a draft `architecture/adr-index.draft.md`; human review merges into `adr-index.md`. Keeps human in the loop on baseline ADR state.
