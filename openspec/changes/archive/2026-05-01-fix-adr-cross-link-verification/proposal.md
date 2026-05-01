## Why

The patch tree's `adr-index.md` notes "VERSION_METADATA.json records the expected post-apply baseline count as 43 ADRs. This patch ships ADR-0038 through ADR-0043; ADR-0001 through ADR-0037 remain in the predecessor baseline and must be verified after apply." Several capabilities in this rc2 push (`vault-authorization`, `replay-and-audit`, `claim-provenance`) reference baseline ADRs (0028, 0034, 0024, 0025, 0027, 0030, 0031) by ID. None of those baseline ADR files are in this repo. Without a documented post-apply verification step, the cross-references could resolve to ADRs that no longer exist, were superseded, or contradict patch ADRs 0038-0043.

This change defines a spec-level verification: what exists must be checked, how, by what script, with what acceptance criteria. The verification script is an M0 deliverable, mirroring the pattern used by `fix-claim-provenance` and `fix-vault-authorization-audit`.

## What Changes

- Land `architecture/objects/adr-cross-link-verification.md` defining: which ADR IDs are referenced from the rc2 specs, what cross-link verification means (existence + non-contradiction), the script's interface contract, and the acceptance criteria.
- Capture as `openspec/specs/adr-cross-link-verification/spec.md`.
- Update `architecture/adr-index.md` to add a "Baseline ADRs (post-apply verified)" section listing the referenced baseline ADR IDs as placeholder rows pending verification.
- Document `scripts/check_adr_cross_links.py` as an M0 deliverable with acceptance criteria.
- **Out of scope:** implementing the script; producing the baseline ADRs; auditing baseline ADR content (that's the verification's job at M0).

## Capabilities

### New Capabilities

- `adr-cross-link-verification`: Spec for the post-apply verification that confirms baseline ADRs referenced by patch and rc2 specs (a) exist, (b) are not in `superseded` or `rejected` state, and (c) do not contradict the active patch ADRs 0038-0043 or the rc2 spec set. Defines the script interface contract and the M0 acceptance criteria.

### Modified Capabilities

(none)

## Impact

- **Documents added:** `architecture/objects/adr-cross-link-verification.md`, `openspec/specs/adr-cross-link-verification/spec.md`.
- **Documents touched:** `architecture/adr-index.md` — adds the baseline-ADR placeholder section.
- **Code:** none. `scripts/check_adr_cross_links.py` is specified, not implemented (M0 deliverable).
- **Linked items:** drives the rc2 freeze-criterion "no UNAUDITED checklist categories" by giving criterion #9 (vault) and #3 (ADR inventory) a documented post-apply audit path. Closes the cross-link gap left by `fix-vault-authorization-audit`.
