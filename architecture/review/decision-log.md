# Architecture Decision Log

This log records triage decisions and material architectural calls made during the
architecture release-candidate process. ADR-level decisions live in their respective
ADR files; this log captures the lighter-weight calls (issue triage, scope changes,
override decisions, deferred items) that don't merit a full ADR.

Each entry: date, ID, decision, rationale, links.

---

## 2026-05-01

### TR-001 — Triage of inventory pass (ARCH-P0-001 … ARCH-P3-001)

**Decision.** Six issues filed from the first inventory pass. Triage outcomes:

| ID | GH issue | Severity | Decision | Rationale |
|---|---|---|---|---|
| ARCH-P0-001 | #1 | P0 | **accept** | Wedge clarity is finalization checklist criterion #1; cannot freeze without reconciling. Drives `fix-product-wedge` OpenSpec change. |
| ARCH-P1-001 | #2 | P1 | **accept** | `scripts/check_claim_provenance.py` is referenced as an M0 deliverable in invariants and handoff docs but missing. Architecture-blocker for customer-facing review. Drives `fix-claim-provenance` change (deferred from current execution per locked plan; revisit if customer review timing moves up). |
| ARCH-P1-002 | #3 | P1 | **defer** | ADR-0043 founder sign-off (M1-DECISION-001). Not architecture-mechanical; outside the architecture-review loop. Architecture review can proceed in parallel; only the bootstrap baseline tag is blocked. |
| ARCH-P2-001 | #4 | P2 | **accept (track)** | ADR-0042 drill ambiguity. Track but defer; not freeze-blocking. |
| ARCH-P2-002 | #5 | P2 | **accept (track)** | ADR-0038 DR plan deferred. Track but defer; becomes load-bearing at M2. |
| ARCH-P3-001 | #6 | P3 | **accept (track)** | ADR-0040 corpora polish. Nice-to-have; not freeze-blocking. |

**Rationale.** Only one P0 (ARCH-P0-001 wedge) is freeze-blocking under the current
finalization checklist. The P1 architecture-blocker (claim-provenance) is held for a
future iteration because customer-facing review is not imminent and the current locked
scope per the plan is wedge-only. The yc-blocker P1 (ADR-0043) is deferred because it
is a founder/legal decision, not architecture-mechanical.

**Implication for freeze.** Only ARCH-P0-001 must be closed before
`architecture-rc1` can be tagged. P2 and P3 entries remain open as tracked debt and
do not block freeze; they are listed under "Remaining non-blocking issues" on the
release-candidate scorecard.

**Links.** GitHub issues #1–#6; `architecture/review/issue-ledger.yaml`.
