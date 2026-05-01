## Why

The rc2 change `fix-adr-cross-link-verification` landed the spec contract for `scripts/check_adr_cross_links.py` and held the implementation as an M0 deliverable. rc3 closes the M0 gap. The script now exists, runs in two modes (bootstrap vs. post-apply), and passes in the current bootstrap state.

(Renamed from the user's suggested `fix-adr-cross-link-verification` to avoid name collision with the rc2 archive entry of the same name.)

## What Changes

- Implement `scripts/check_adr_cross_links.py` with automatic mode detection:
  - **Bootstrap mode** (current state): no `architecture/adr/` directory at the repo root with baseline ADRs. Verify the placeholder rows + section in `adr-index.md`, plus presence of patch ADRs 0038-0043. Exit 0.
  - **Post-apply mode**: full baseline ADR set present at the repo root. Walk and verify each enumerated baseline ADR's existence, status, and emit a `architecture/adr-index.draft.md` enriched with metadata. Exit 0 on clean run.
- Update the spec via `MODIFIED Requirements` to record the bootstrap-mode contract — the spec previously only described post-apply verification. Bootstrap-mode is a legitimate execution path during the architecture-finalization phase before the patch is applied to the v3.2.3.5 baseline.
- **Out of scope:** wiring the script into CI; producing baseline ADR files; semantic contradiction detection (the script flags multi-ADR INV references for human review but does not auto-fail on them).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `adr-cross-link-verification`: codify the bootstrap-mode behavior.

## Impact

- **Files added:** `scripts/check_adr_cross_links.py`.
- **Spec updated:** `openspec/specs/adr-cross-link/spec.md` (via archive of this change).
- **Linked items:** closes the M0 deliverable hand-off from `fix-adr-cross-link-verification`; finalization-checklist #3 stays at evidence-backed PASS in rc3.
