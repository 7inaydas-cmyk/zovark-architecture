## 1. Verify governance docs match the canonical block

- [ ] 1.1 Confirm `architecture/source-of-truth.md` contains the canonical product-wedge statement verbatim under `## Current product wedge`. If not, edit to match.
- [ ] 1.2 Confirm `architecture/source-of-truth.md` contains the canonical core-flow arrow sequence verbatim. If not, edit to match.
- [ ] 1.3 Confirm `architecture/review/finalization-checklist.md` §1 matches the wedge statement exactly. If not, edit.

## 2. Update MVP scope document

- [ ] 2.1 Open `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/mvp-scope.md`.
- [ ] 2.2 Replace the first paragraph of `## Product Wedge` with the canonical block (statement + core flow), preserving the existing first-user / design-partner sentence as the immediately following paragraph.
- [ ] 2.3 Add a one-paragraph signpost after the canonical block that names the **investigation tape** as the central recorded object and the **EDR handoff** as replayable, evidence-linked, and reversible. Do not redefine either; mark schema definitions as out of scope for this change.
- [ ] 2.4 Verify with `grep -F "Zovark is the tape recorder for cybersecurity investigations." zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/mvp-scope.md`.

## 3. Update top-level package documents

- [ ] 3.1 Open `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ZOVARK-v3.2.4.6-FINAL.md`.
- [ ] 3.2 Insert a `## Product wedge` section immediately after `## Summary` containing the canonical block (statement + core flow) followed by the tape/EDR signpost paragraph.
- [ ] 3.3 Open `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ENGINEERING-READY-HANDOFF.md`.
- [ ] 3.4 Insert a `## Product wedge` section immediately after `## Purpose` containing the canonical block (statement + core flow) followed by the tape/EDR signpost paragraph.
- [ ] 3.5 Verify both files contain the canonical statement verbatim with `grep -F "Zovark is the tape recorder for cybersecurity investigations."`.

## 4. Subordinate any drift framing

- [ ] 4.1 Run `grep -rni "AI SOC platform\|generic SOC\|agent framework" zovark-v3.2.4.6-engineering-ready/ architecture/ --include="*.md"` to surface any drift framing in scope.
- [ ] 4.2 If hits found: edit each occurrence so it does not function as the primary product positioning. If "AI SOC" describes mechanism rather than product, leave it but ensure the surrounding paragraph cites the canonical wedge.
- [ ] 4.3 If no hits found, record the empty result in the change's commit message.

## 5. Verification

- [ ] 5.1 Run `grep -rF "Zovark is the tape recorder for cybersecurity investigations." architecture/ zovark-v3.2.4.6-engineering-ready/` and confirm hits in: `architecture/source-of-truth.md`, `mvp-scope.md`, `ZOVARK-v3.2.4.6-FINAL.md`, `ENGINEERING-READY-HANDOFF.md`.
- [ ] 5.2 Run `grep -rF "EDR alerts → investigation tape → replayable evidence" architecture/ zovark-v3.2.4.6-engineering-ready/` and confirm the same hit set.
- [ ] 5.3 Re-read finalization-checklist criterion #1 acceptance bullets and confirm each is now satisfied.

## 6. Close the issue and archive the change

- [ ] 6.1 Update `architecture/review/issue-ledger.yaml` entry `ARCH-P0-001`: set `status: fixed`, add `fixed_by_openspec_change: fix-product-wedge`, add a `verification:` line citing the grep results from §5.
- [ ] 6.2 Add a triage entry to `architecture/review/decision-log.md` recording the fix and verification.
- [ ] 6.3 Close GitHub issue #1 with a comment linking to the merge commit and the change archive path.
- [ ] 6.4 Re-label GitHub issue #1: remove `status:accepted`, add `status:fixed`.
- [ ] 6.5 Run `openspec archive fix-product-wedge` to move the change into `openspec/changes/archive/`.
- [ ] 6.6 Commit and push: "Fix product wedge consistency".
