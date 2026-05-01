## 1. Implement the script

- [ ] 1.1 Add `scripts/check_claim_provenance.py` matching the interface in `openspec/specs/claim-provenance/spec.md` (as MODIFIED by this change).
- [ ] 1.2 Make it executable: `chmod +x scripts/check_claim_provenance.py`.
- [ ] 1.3 Run it: `python3 scripts/check_claim_provenance.py`. Verify exit 0 and output "Claim provenance check passed".

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-claim-provenance-enforcement`.
- [ ] 2.2 Run `openspec archive fix-claim-provenance-enforcement --yes`.

## 3. Update issue ledger

- [ ] 3.1 Append to `architecture/review/issue-ledger.yaml` `ARCH-P1-001` `verification:` field a note that the script now exists and passes; status remains `fixed`.

## 4. Commit and push

- [ ] 4.1 Stage `scripts/check_claim_provenance.py`, the change archive, the updated spec, and the ledger update.
- [ ] 4.2 Commit: "Implement claim-provenance enforcement script".
- [ ] 4.3 Push.
