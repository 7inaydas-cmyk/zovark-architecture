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

---

### TR-002 — ARCH-P0-001 fixed by `fix-product-wedge`

**Decision.** ARCH-P0-001 (GitHub #1, wedge framing mismatch) is closed by the OpenSpec change `fix-product-wedge`. Status: `fixed`.

**What landed.** Canonical product-wedge statement and core-flow phrasing applied verbatim to:

- `architecture/source-of-truth.md` (already aligned; no change needed)
- `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/mvp-scope.md` — replaced `## Product Wedge` opening
- `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ZOVARK-v3.2.4.6-FINAL.md` — added `## Product wedge` after `## Summary`
- `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ENGINEERING-READY-HANDOFF.md` — added `## Product wedge` after `## Purpose`

The change also lands `openspec/specs/product-wedge/spec.md` (after archive) as the governing spec for any future wedge revision.

**Verification.** `grep -rlF "Zovark is the tape recorder for cybersecurity investigations."` returns 4 expected hits across the four documents. Drift-framing scan returned only an exclusionary guardrail in `architecture/review/finalization-checklist.md:10` (acceptable).

**Implication for freeze.** Open `severity:P0` count drops to 0. The remaining open issues (P1 deferred + P2 + P3 accepted-track) do not block freeze.

**Links.** OpenSpec change `openspec/changes/archive/fix-product-wedge/`. GitHub issue #1 (closed).

---

### TR-003 — ARCH-P1-001 fixed (rules + spec) by `fix-claim-provenance`

**Decision.** ARCH-P1-001 (GitHub #2, claim-provenance enforcement missing) is closed by the OpenSpec change `fix-claim-provenance`. Status: `fixed`.

**What landed.** `architecture/claims/claim-provenance.md` (previously empty) now contains the source-of-truth rules: four allowed tag formats, quantified-claim category list, customer-facing classification rules, and the M0 verification script's interface contract. The spec is captured as `openspec/specs/claim-provenance/spec.md` and governs future changes.

**What is explicitly held as M0 deliverable.** `scripts/check_claim_provenance.py` is **not** implemented as part of this change. The interface contract is locked. The four-point M0 acceptance criteria are documented. The implementation lands when M0 work begins.

**Implication for rc2.** Finalization-checklist criterion #4 (Claim provenance) moves from FAIL to PASS — rules are authoritative, spec governs, M0 deliverable has explicit acceptance criteria. The category passes under the rc2 rule "claim provenance either fixed or explicitly marked as M0 deliverable with acceptance criteria."

**Links.** OpenSpec change `openspec/changes/archive/2026-05-01-fix-claim-provenance/`. GitHub issue #2 (closed).

---

### TR-004 — Vault authorization spec lands; one event-type follow-up

**Decision.** `fix-vault-authorization-audit` lands the authorization record spec, verification rules, replay protection, compromise response, and M3 IPC-schema deliverable acceptance criteria. Finalization-checklist criterion #9 (Vault / authorization) moves from UNAUDITED to PASS-with-tracked-gaps for rc2.

**Tracked rc2-V follow-up.** The `vault-authorization` spec introduces a new audit event type `vault_authorization_use_rejected` that is referenced from `replay-and-audit`'s event-type enum. The enum addition is a `MODIFIED Requirements` change against `replay-and-audit` and is intentionally deferred to the rc2 verification block (RC2-V) so the cross-capability linkage lands as a single batched cleanup rather than as a per-capability ripple. Until that lands, the event type exists in the `vault-authorization` spec but not in the `replay-and-audit` enum — implementations SHOULD treat the type as accepted and reviewers SHALL NOT flag it as undefined.

**M3 deliverables tracked.** Three IPC schemas (`vault_request`, `vault_response`, `vault_audit_envelope`) plus `scripts/check_vault_ipc_contract.py` are recorded as M3 deliverables with explicit acceptance criteria, mirroring the M0 hand-off used by `fix-claim-provenance`. The architecture release-candidate freeze is not blocked on these.

**Cross-link gap.** Baseline ADR-0028 (vault threat model) and ADR-0034 (tenant DEK rotation) are referenced but not in this tree. The next rc2 change (`fix-adr-cross-link-verification`) defines the post-apply audit that confirms they exist and don't contradict patch ADRs 0038-0043.

**Links.** OpenSpec change `openspec/changes/archive/2026-05-01-fix-vault-authorization-audit/`. No GitHub issue (driven directly by rc2 target).

---

### TR-005 — Architecture rc2 freeze

**Decision.** Tag `architecture-rc2` against commit on 2026-05-01. Documents-only score 8.5/10. Twelve checklist categories at PASS, PASS-with-tracked-gaps, or PRESENT; zero at FAIL or UNAUDITED.

**rc2 changes archived (8 total).** All applied + archived in this rc2 cycle:

1. `fix-claim-provenance` — rules + spec; M0 script explicit. (Closed GH #2.)
2. `fix-investigation-tape-schema` — full tape object spec.
3. `fix-edr-handoff-schema` — 14-field handoff record spec.
4. `fix-replay-and-audit-semantics` — replay state + audit chain spec.
5. `fix-vault-authorization-audit` — vault auth record spec; M3 IPC deliverables tracked. (Drove criterion #9 from UNAUDITED to PASS-with-tracked-gaps.)
6. `fix-adr-cross-link-verification` — post-apply baseline-ADR verification spec; 8 baseline ADRs surfaced as placeholder rows.
7. `fix-replay-and-audit-event-type-extension` — closes the deferred follow-up from TR-004 (adds `vault_authorization_use_rejected` to the closed event-type enum).
8. (rc1's `fix-product-wedge` predates rc2 but ships in the same release-candidate lineage.)

**rc2 spec set.** 7 capabilities now under `openspec/specs/`: `product-wedge`, `claim-provenance`, `investigation-tape`, `edr-handoff`, `replay-and-audit`, `vault-authorization`, `adr-cross-link`.

**Tracked M0/M3 deliverables.** Four scripts and three schemas with explicit acceptance criteria, drawn directly from the rc2 spec set. Implementation begins when M0/M3 work starts; rc2 freeze is not blocked on them.

**Open issues at rc2 freeze.** ARCH-P1-002 (deferred, founder), ARCH-P2-001 (track), ARCH-P2-002 (track), ARCH-P3-001 (track). All explicitly non-blocking per rc2 target.

**Links.** Release-candidate scorecard at `architecture/review/release-candidate-scorecard.md` (rc2 entry). All 8 archived changes under `openspec/changes/archive/2026-05-01-*`.

---

### TR-006 — Architecture rc3 freeze (evidence-backed)

**Decision.** Tag `architecture-rc3` against commit on 2026-05-01. Both documents-only and evidence-backed scores 8.5/10. All 12 finalization-checklist categories at PASS or PASS-with-explicit-DEFERRAL; zero UNAUDITED, zero PASS-with-tracked-gaps.

**rc3 changes archived (3 total).** Narrow hardening pass per the rc3 plan; no broad architecture review:

1. `fix-claim-provenance-enforcement` — implements `scripts/check_claim_provenance.py`. Spec MODIFIED to extend cadence allowlist (adds `quarterly-review`, `release-review`, `milestone-review`, plus per-event cadences) and acknowledge `BOOTSTRAP_PENDING_OWNERS` for roles awaiting M2 OWNERS.yaml registration (`product-owner`, `support-owner`, `release-engineering`, `research-owner`).
2. `fix-adr-cross-link-enforcement` — implements `scripts/check_adr_cross_links.py` with auto-detected bootstrap mode (current state) and post-apply mode (after v3.2.3.5 baseline merge). Spec MODIFIED to codify both modes. (Renamed from the user's suggested `fix-adr-cross-link-verification` to avoid name collision with the rc2 archive of the same name.)
3. `finalize-architecture-rc3-scorecard` — governance bookkeeping. Adds `release-candidate-process` capability codifying the rc-N tag rules, score thresholds per stage, and the requirement that `PASS-with-explicit-DEFERRAL` annotations name owner + milestone + acceptance.

**Evidence-script results at freeze.** All three architecture enforcement scripts pass:

- `scripts/check_mvp_scope_consistency.py` → "MVP scope consistency check passed".
- `scripts/check_claim_provenance.py` → "Claim provenance check passed".
- `scripts/check_adr_cross_links.py` → "ADR cross-link verification (bootstrap mode) passed" with banner listing the 8 baseline ADRs awaiting post-apply verification.

**Categories reclassified at rc3.** The two rc2 `PASS-with-tracked-gaps` categories were upgraded to `PASS-with-explicit-DEFERRAL` with owner/milestone/acceptance:

- **#8 Audit, DR, lifecycle** — DEFERRED for control-plane DR sketch (ARCH-P2-002). Owner: architect. Milestone: M2. Acceptance: ADR-0038 contains RPO/RTO targets, HA vs. DR posture, restore-drill cadence, data-authority guarantees during partial control-plane loss.
- **#9 Vault / authorization** — DEFERRED for M3 IPC schemas. Owner: schema-owner. Milestone: M3. Acceptance: three vault IPC schemas with pass/fail fixtures + `check_vault_ipc_contract.py`.

**Open issues at rc3 freeze.** ARCH-P1-002 (deferred, founder), ARCH-P2-001 (track), ARCH-P2-002 (track, DEFERRED in scorecard), ARCH-P3-001 (track). Zero P0; zero accepted-open P1.

**Bridge to product.** rc3 enables the smallest meaningful build slice: 1 EDR sample → 1 tape → 1 timeline → 1 evidence ledger → 1 verdict → 1 handoff recommendation → 1 replay report. That slice exercises every governing spec and every M0 enforcement script.

**Links.** Release-candidate scorecard at `architecture/review/release-candidate-scorecard.md` (rc3 entry). Three rc3 archived changes under `openspec/changes/archive/2026-05-01-fix-claim-provenance-enforcement`, `2026-05-01-fix-adr-cross-link-enforcement`, `2026-05-01-finalize-architecture-rc3-scorecard`.
