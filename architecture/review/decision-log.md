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
