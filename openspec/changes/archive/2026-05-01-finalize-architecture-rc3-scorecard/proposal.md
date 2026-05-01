## Why

The two enforcement scripts (`scripts/check_claim_provenance.py` and `scripts/check_adr_cross_links.py`) now exist and pass. With evidence-backed enforcement in place, the rc2 categories at `PASS-with-tracked-gaps` (#8 audit/DR/lifecycle, #9 vault/authorization) need to be reclassified — either upgraded to strict `PASS` or explicitly `DEFERRED` with owner + milestone + acceptance criteria. rc3 must surface zero `UNAUDITED` and zero unannotated `tracked-gaps`.

This change is bookkeeping: re-run the three architecture enforcement scripts, record results, update the scorecard to rc3 (target ≥ 8.5/8.5), update the issue ledger to reflect the implemented enforcement, and write the rc3 freeze decision-log entry. No new architecture, no new specs, no new product scope.

## What Changes

- Update `architecture/review/release-candidate-scorecard.md` to rc3:
  - Documents-only score ≥ 8.5; evidence-backed score ≥ 8.5.
  - Convert PASS-with-tracked-gaps categories to strict PASS or explicitly DEFERRED with owner/milestone/acceptance.
  - Record evidence: each of the three enforcement scripts ran and passed.
- Update `architecture/review/issue-ledger.yaml`: ARCH-P2-001, ARCH-P2-002, ARCH-P3-001 stay open as `accepted (track)` with explicit DEFERRED tags. ARCH-P1-002 stays `deferred`.
- Add `TR-006` to `architecture/review/decision-log.md`: rc3 freeze entry.
- **Out of scope:** new specs; new capabilities; product implementation; changes to enforcement-script behavior; reopening triage on closed issues.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — this is governance bookkeeping, not a spec change)

## Impact

- **Documents touched:** `architecture/review/release-candidate-scorecard.md`, `architecture/review/issue-ledger.yaml`, `architecture/review/decision-log.md`.
- **Files added:** none.
- **Code:** none.
- **Linked items:** prepares the working tree for the `architecture-rc3` tag.
