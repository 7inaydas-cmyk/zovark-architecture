## Why

Closes ARCH-P1-001 / GitHub #2. The patch tree's `architecture/claims/claim-provenance.md` defines four allowed provenance tags and prose rules, but the root `architecture/claims/claim-provenance.md` in this finalization repo is empty, and `scripts/check_claim_provenance.py` is named in `invariants.md` INV-022 and `ENGINEERING-READY-HANDOFF.md` as an M0 deliverable without acceptance criteria. Without authoritative rules and a specified checker, the rc2 finalization-checklist criterion #4 (Claim provenance) stays at FAIL.

This change does not implement the script — that remains an M0 deliverable per the locked rc2 plan. It captures the rules, the script's interface contract, and the M0 acceptance criteria so the deliverable is unambiguous.

## What Changes

- Promote the patch tree's claim-provenance rules to the root finalization repo at `architecture/claims/claim-provenance.md`. The root copy becomes the source of truth.
- Specify `scripts/check_claim_provenance.py`'s interface (CLI surface, exit codes, doc set scanned, tag grammar) without implementing it.
- Define explicit acceptance criteria for the M0 deliverable: which docs are in scope, which tag grammar must parse, which categories of claims are required to carry tags, and what the customer-facing exclusion list is.
- Capture the rules and the interface contract as `openspec/specs/claim-provenance/spec.md` so future changes go through a spec modification.
- **Out of scope:** implementing the checker; adding new tag formats; expanding which docs are customer-facing; touching invariants or ADRs.

## Capabilities

### New Capabilities

- `claim-provenance`: Source-of-truth rules for tagging quantified claims across architecture and customer-facing documentation, plus the interface contract for the M0 verification script `scripts/check_claim_provenance.py`. Defines what tags exist, where they must appear, what counts as a violation, and how the M0 deliverable will be verified.

### Modified Capabilities

(none)

## Impact

- **Documents touched:** `architecture/claims/claim-provenance.md` (currently empty — populated). No patch-tree edits.
- **Documents added:** `openspec/specs/claim-provenance/spec.md` (after archive).
- **Code:** none. `scripts/check_claim_provenance.py` is specified but not implemented (M0 deliverable).
- **Linked issue:** ARCH-P1-001 / GitHub #2. Marks the issue as `fixed` for **rules + spec**; the script implementation remains the M0 deliverable.
