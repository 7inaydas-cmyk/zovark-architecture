## 1. Land the architecture object document

- [ ] 1.1 Write `architecture/objects/adr-cross-link-verification.md` with: introduction (link to rc2 spec set + patch ADRs + invariants), what cross-link verification means (existence + status + non-contradiction), enumerated baseline ADR set with reference sites, script interface contract, M0 acceptance criteria.
- [ ] 1.2 Verify the doc enumerates all 8 baseline ADR IDs (0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034) with their reference sites.

## 2. Update the ADR index

- [ ] 2.1 Add a "Baseline ADRs (post-apply verified)" section to `architecture/adr-index.md` listing the 8 baseline ADRs as placeholder rows.

## 3. Capture the spec

- [ ] 3.1 Run `openspec validate fix-adr-cross-link-verification`.
- [ ] 3.2 Run `openspec archive fix-adr-cross-link-verification --yes`.

## 4. Commit and push

- [ ] 4.1 Stage `architecture/objects/adr-cross-link-verification.md`, the ADR-index update, the change archive, and the new spec.
- [ ] 4.2 Commit: "Define ADR cross-link verification spec".
- [ ] 4.3 Push.
