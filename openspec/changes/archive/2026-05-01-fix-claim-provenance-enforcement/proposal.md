## Why

The rc2 change `fix-claim-provenance` landed the rules + spec contract for `scripts/check_claim_provenance.py` and explicitly held the implementation as the M0 deliverable. rc3's hardening pass closes the M0 gap: the script now exists, runs, and passes against the current repo. Closing this also moves finalization-checklist criterion #4 (Claim provenance) from "PASS (rules + spec, M0 deliverable explicit)" to evidence-backed PASS.

Implementation surfaced two minor spec gaps in the patch tree's existing tag usage that need codifying:

1. The patch tree uses cadence values beyond the spec's original six (`release-review`, `milestone-review`, `quarterly-review`, plus per-event cadences `per-release-review`, `per-promotion-review`, `per-advisory-review`, `per-change-review`, `incident-review`).
2. The patch tree references owner roles that are not yet declared in `OWNERS.yaml`'s `roles:` section (`product-owner`, `support-owner`, `release-engineering`, `research-owner`).

This change updates the spec to acknowledge both via a `MODIFIED Requirements` block — the cadence allowlist expands, and the owner rule explicitly accepts a `BOOTSTRAP_PENDING_OWNERS` allowlist for roles awaiting M2 OWNERS.yaml registration.

## What Changes

- Implement `scripts/check_claim_provenance.py` per the existing interface contract. Runs in two passes: (1) validate every tag in scope, (2) confirm every quantified claim has a tag.
- Update the spec via `MODIFIED Requirements`:
  - Expand the cadence allowlist to include `quarterly-review`, `release-review`, `milestone-review`, `per-release-review`, `per-promotion-review`, `per-advisory-review`, `per-change-review`, `incident-review`.
  - Permit `BOOTSTRAP_PENDING_OWNERS` (declared in the script) for owner names not yet in `OWNERS.yaml` roles. The list is finite, documented in the design, and collapses to empty post-M2 OWNERS.yaml registration.
  - Acknowledge that `architecture/claims/`, license files, and the patch-tree review docs are excluded from the walk because they document rules / contain legal text rather than architecture claims.
- **Out of scope:** wiring the script into CI; new tag formats; new claim categories; re-tagging existing claims (the script passes on existing tags after the spec update).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `claim-provenance`: extend the cadence allowlist; recognize `BOOTSTRAP_PENDING_OWNERS`; codify the walk exclusions.

## Impact

- **Documents touched:** none in patch tree.
- **Files added:** `scripts/check_claim_provenance.py`.
- **Spec updated:** `openspec/specs/claim-provenance/spec.md` (via archive of this change).
- **Linked items:** closes the M0 deliverable hand-off from `fix-claim-provenance`; finalization-checklist #4 now evidence-backed.
