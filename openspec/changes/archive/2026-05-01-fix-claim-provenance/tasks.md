## 1. Populate the source-of-truth rules document

- [ ] 1.1 Write `architecture/claims/claim-provenance.md` with the four allowed tag formats, the quantified-claim category list, the customer-facing classification rules, and the M0 script-interface contract. Mirror the patch-tree rules verbatim where they overlap; add the script interface and customer-facing classification, which the patch-tree version does not contain.
- [ ] 1.2 Verify the file contains all four tag format strings (`[hypothesis:`, `[measured:`, `[vendor-cited:`, `[policy-commitment:`).

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-claim-provenance` and confirm pass.
- [ ] 2.2 Run `openspec archive fix-claim-provenance --yes` to promote to `openspec/specs/claim-provenance/spec.md`.

## 3. Close the issue

- [ ] 3.1 Update `architecture/review/issue-ledger.yaml` entry `ARCH-P1-001`: `status: fixed`, `fixed_by_openspec_change: fix-claim-provenance`, `verification:` line citing both the rules doc and the M0 deliverable note.
- [ ] 3.2 Add a `TR-003` entry to `architecture/review/decision-log.md` summarizing the fix and explicitly calling out that the M0 script implementation remains pending.
- [ ] 3.3 Comment on GitHub issue #2 referencing the change archive and the M0 deliverable.
- [ ] 3.4 Re-label GitHub issue #2: remove `status:accepted`, add `status:fixed`. Close the issue.

## 4. Commit and push

- [ ] 4.1 Stage `architecture/claims/claim-provenance.md`, the change archive, the new spec, the ledger update, and the decision-log update.
- [ ] 4.2 Commit: "Fix claim provenance rules and M0 script contract".
- [ ] 4.3 Push.
