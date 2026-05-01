## 1. Re-run enforcement scripts

- [ ] 1.1 Run `python3 scripts/check_mvp_scope_consistency.py`. Record output.
- [ ] 1.2 Run `python3 scripts/check_claim_provenance.py`. Record output.
- [ ] 1.3 Run `python3 scripts/check_adr_cross_links.py`. Record output.

## 2. Update governance documents

- [ ] 2.1 Update `architecture/review/release-candidate-scorecard.md` to rc3:
  - Status: rc3 — proposed for freeze.
  - Documents-only score: 8.5/10.
  - Evidence-backed score: 8.5/10.
  - 12 categories at PASS or PASS-with-explicit-DEFERRAL.
  - Evidence section names the three scripts and their pass status.
- [ ] 2.2 Update `architecture/review/issue-ledger.yaml`:
  - ARCH-P1-001: already `fixed`. No change.
  - ARCH-P1-002: stays `deferred` (founder).
  - ARCH-P2-001, ARCH-P2-002, ARCH-P3-001: stay `accepted`; scorecard adds DEFERRED annotation.
- [ ] 2.3 Append `TR-006` to `architecture/review/decision-log.md`: rc3 freeze.

## 3. Capture the change

- [ ] 3.1 Run `openspec validate finalize-architecture-rc3-scorecard`.
- [ ] 3.2 Run `openspec archive finalize-architecture-rc3-scorecard --yes`.

## 4. Commit and push

- [ ] 4.1 Stage governance docs and the change archive.
- [ ] 4.2 Commit: "Finalize architecture-rc3 scorecard".
- [ ] 4.3 Push.

## 5. Tag

- [ ] 5.1 Confirm 0 open severity:P0 issues and 0 open accepted-status severity:P1 issues.
- [ ] 5.2 `git tag -a architecture-rc3 -m "Architecture release candidate 3 — evidence-backed freeze"`.
- [ ] 5.3 `git push origin architecture-rc3`.
