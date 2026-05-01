## Context

Closing rc3. The two enforcement scripts implemented in `fix-claim-provenance-enforcement` and `fix-adr-cross-link-enforcement` now exist and pass. The third script (`check_mvp_scope_consistency.py`) has been passing since rc1. rc3's target says all 12 finalization-checklist categories should be PASS or explicitly DEFERRED, with no UNAUDITED and no unannotated PASS-with-tracked-gaps.

This change updates the governance documents (scorecard, ledger, decision log) to reflect the new evidence-backed posture, and prepares the tree for the `architecture-rc3` tag. It is intentionally narrow — no spec changes, no architecture changes, no product implementation.

## Goals / Non-Goals

**Goals:**

- rc3 scorecard shows documents-only score ≥ 8.5, evidence-backed score ≥ 8.5.
- All 12 categories at PASS or explicitly DEFERRED (with owner / milestone / acceptance).
- Issue ledger reflects current state.
- Decision log records the rc3 freeze with evidence pointers.
- Architecture-rc3 tag is ready to push.

**Non-Goals:**

- New OpenSpec specs.
- Modifying enforcement-script behavior.
- Reopening triage on previously triaged issues.
- Sketch ADR for ARCH-P2-002 — explicitly remains DEFERRED in rc3.
- Product implementation, runtime code, vendor support.

## Decisions

### Reclassifying PASS-with-tracked-gaps

Two categories were `PASS-with-tracked-gaps` at rc2:

- **#8 Audit, DR, and tenant lifecycle** — gap: ARCH-P2-002 control-plane DR plan sketch. Reclassify as `PASS-with-explicit-DEFERRAL` for ARCH-P2-002 (owner: architect; milestone: M2; acceptance: RPO/RTO targets, HA vs DR posture, restore-drill cadence).
- **#9 Vault / authorization** — gap: M3 IPC schemas + cross-link audit of baseline ADR-0028 / ADR-0034. Reclassify as `PASS-with-explicit-DEFERRAL` for the M3 schema deliverables (owner: schema-owner; milestone: M3) and for baseline-ADR cross-link verification (owner: architect; milestone: M0 — script implemented, runs in bootstrap mode passing).

Both categories meet the rc3 target ("PASS or explicitly DEFERRED with owner + milestone + acceptance criteria"). The DEFERRED annotations make the gap auditable.

**Rationale.** rc2's `PASS-with-tracked-gaps` was a soft state — implicit deferral. rc3 makes the deferral explicit by naming owner/milestone/acceptance. The category still passes; the gap is just visible.

### Evidence-backed score

The score moves from rc2's "TBD until M0 closes" to a real value. Three scripts now exist:

- `check_mvp_scope_consistency.py` (existed since rc1; passing).
- `check_claim_provenance.py` (rc3; passing in bootstrap state).
- `check_adr_cross_links.py` (rc3; passing in bootstrap mode; post-apply mode awaits baseline merge).

Score: **8.5/10**. Points withheld:

- Bootstrap-mode adr-cross-link script verifies structural placeholders, not actual baseline ADR content. Full evidence requires post-apply.
- M3 vault IPC schemas not produced yet (deferred per spec).
- ARCH-P2-002 sketch ADR not produced (deferred).

These three points are explicit DEFERRALs; they don't reduce the score below the rc3 target of 8.5.

**Rationale.** Strict 9 or 10 would require post-apply verification + M3 schemas + DR sketch. rc3 target is 8.5; we're at 8.5 evidence-backed.

### Documents-only score

Stays at rc2's 8.5. No new documents added in rc3 (only scripts + spec MODIFIED blocks). Documents-only score reflects the documentation state, which is unchanged since rc2 — three new spec MODIFIED blocks but no new architecture content.

**Rationale.** rc3 hardens evidence; rc2 set the documentary ceiling. Both at 8.5 satisfies the rc3 target.

### Issue ledger updates

ARCH-P1-001 already moved to `fixed` in `fix-claim-provenance-enforcement`. ARCH-P1-002 stays `deferred` (founder decision). ARCH-P2-001/002 + ARCH-P3-001 stay `accepted` with `track` annotation in the scorecard's "Remaining issues" section.

No new issues created — that would breach the "do not perform broad architecture review" rule.

### Decision log

A single TR-006 entry records:

- The rc3 freeze with evidence-script results.
- The explicit DEFERRAL annotations on categories #8 and #9.
- Pointers to the three archived rc3 changes (`fix-claim-provenance-enforcement`, `fix-adr-cross-link-enforcement`, this change).

## Risks / Trade-offs

- **Risk:** reclassifying PASS-with-tracked-gaps as PASS-with-explicit-DEFERRAL is cosmetic — the gap is still real. → **Mitigation:** the DEFERRAL annotation includes owner + milestone + acceptance criteria, which the rc3 target explicitly requires. The annotation forces accountability that PASS-with-tracked-gaps did not.
- **Trade-off:** keeping P2/P3 issues open means rc3 ships with debt. Accepted: rc3 target says "no open P0, no accepted open P1." P2/P3 are out of scope for the freeze gate.

## Migration Plan

1. Re-run all three enforcement scripts; record output.
2. Update `release-candidate-scorecard.md` to rc3.
3. Update `issue-ledger.yaml` ledger entries.
4. Append TR-006 to `decision-log.md`.
5. Archive this change.
6. Commit.
7. Tag `architecture-rc3`.

**Rollback:** revert. rc3 governance state goes back to rc2.

## Open Questions

(none — scope is governance-only)
