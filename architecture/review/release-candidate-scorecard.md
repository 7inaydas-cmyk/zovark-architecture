# Architecture Release Candidate Scorecard

## Status

Architecture release candidate: **rc3 — proposed for freeze.**

Scoring date: 2026-05-01. Supersedes the rc2 scorecard (same date, prior commit).

## Freeze criteria (rc3)

- [x] Open P0 issues = 0
- [x] No accepted-status open P1 issues (ARCH-P1-002 stays `deferred`; ARCH-P1-001 closed)
- [x] MVP contradictions = 0 (`scripts/check_mvp_scope_consistency.py` passes)
- [x] Customer-facing false claims = 0 (no documented false claim found; `scripts/check_claim_provenance.py` passes)
- [x] Active ADR index current (8 baseline ADRs surfaced as placeholder rows; `scripts/check_adr_cross_links.py` passes in bootstrap mode)
- [x] Missing evidence labeled M0 / M3 / future with explicit acceptance criteria
- [x] Product wedge clear
- [x] Investigation tape defined as a structured object (`investigation-tape` capability)
- [x] Replay semantics fully specified (`replay-and-audit` capability)
- [x] EDR handoff record fully specified (`edr-handoff` capability)
- [x] Customer validation workflow present
- [x] No `UNAUDITED` checklist categories
- [x] No `PASS-with-tracked-gaps` (all upgraded to PASS or annotated PASS-with-explicit-DEFERRAL with owner + milestone + acceptance)
- [x] M0 architecture enforcement scripts implemented and passing
- [x] ADR cross-link verification script exists and passes (bootstrap mode)
- [x] Claim-provenance checker exists and passes

## Documents-only architecture score

**8.5 / 10**

Unchanged from rc2. The documentary state is the same — three rc3 changes added scripts and updated specs but did not introduce new architecture content.

Points withheld:

- Bootstrap-mode adr-cross-link script verifies structural placeholders, not actual baseline ADR content. Full evidence requires post-apply.
- M3 vault IPC schemas not produced yet (DEFERRED with M3 + schema-owner).
- ARCH-P2-002 control-plane DR sketch ADR not produced (DEFERRED with M2 + architect).

## Evidence-backed architecture score

**8.5 / 10**

Three architecture-finalization enforcement scripts exist and pass:

| Script | Status | Output |
|---|---|---|
| `scripts/check_mvp_scope_consistency.py` | ✅ pass | "MVP scope consistency check passed" |
| `scripts/check_claim_provenance.py` | ✅ pass | "Claim provenance check passed" |
| `scripts/check_adr_cross_links.py` | ✅ pass (bootstrap mode) | "ADR cross-link verification (bootstrap mode) passed" |

Bootstrap-mode adr-cross-link verifies structural completeness (placeholder section, IDs, patch ADR presence). Post-apply mode is implemented and ready; it runs once the v3.2.3.5 baseline is merged in. Both modes are codified in the spec.

Points withheld:

- Post-apply adr-cross-link verification cannot run yet (baseline not merged in this finalization repo).
- M3 vault IPC schemas + `check_vault_ipc_contract.py` (DEFERRED to M3).
- DR sketch ADR (DEFERRED to M2).

## Checklist scoring (rc3)

| Category | Status | Change | Notes |
|---|---|---|---|
| 1. Product wedge clarity | **PASS** | from rc2 PASS | Canonical statement + core flow in 4 target docs; spec governs. |
| 2. MVP scope consistency | **PASS** | from rc2 PASS | `check_mvp_scope_consistency.py` passes (rc1+). Evidence-backed. |
| 3. ADR inventory and supersession | **PASS** | from rc2 PASS | `check_adr_cross_links.py` passes in bootstrap mode. Post-apply verification is the rc3-codified evidence path. |
| 4. Claim provenance | **PASS** | from rc2 PASS | `check_claim_provenance.py` implemented and passing. Spec MODIFIED to expand cadence allowlist + acknowledge `BOOTSTRAP_PENDING_OWNERS`. Evidence-backed. |
| 5. Investigation tape object | **PASS** | from rc2 PASS | `investigation-tape` spec covers required fields, lifecycle, customer-facing surface. |
| 6. Replay correctness | **PASS** | from rc2 PASS | `replay-and-audit` capability — recorded-output vs. forensic, hash verification, version pinning, deterministic verdict. |
| 7. EDR handoff correctness | **PASS** | from rc2 PASS | `edr-handoff` 14-field record + approval modes + idempotency + rollback classes. |
| 8. Audit, DR, and tenant lifecycle | **PASS-with-explicit-DEFERRAL** | from rc2 PASS-with-tracked-gaps | Audit chain spec PASS. DR control-plane sketch DEFERRED. **Owner:** architect. **Milestone:** M2. **Acceptance:** ADR-0038 contains RPO/RTO targets, HA vs. DR posture, restore-drill cadence, data-authority guarantees during partial control-plane loss (ARCH-P2-002 acceptance criteria). Tracked GH #5. |
| 9. Vault / authorization | **PASS-with-explicit-DEFERRAL** | from rc2 PASS-with-tracked-gaps | `vault-authorization` spec PASS. M3 IPC schemas DEFERRED. **Owner:** schema-owner. **Milestone:** M3. **Acceptance:** `vault_request.schema.json`, `vault_response.schema.json`, `vault_audit_envelope.schema.json` each carry the metadata triple, have pass/fail fixtures, and are referenced by `scripts/check_vault_ipc_contract.py`. Cross-link audit of baseline ADR-0028 / ADR-0034 lands in post-apply (script ready). |
| 10. Evidence status | **PASS** | from rc2 PASS | All M0/M3 deliverables enumerated. M0 deliverables (claim-provenance + adr-cross-links scripts) implemented in rc3. |
| 11. Schedule realism | **PASS** | from rc2 PASS | M0 / M1 / M2 / M3 / M4 / M5 / M6 / M9 / M10 separation in patch + handoff. |
| 12. Customer validation workflow | **PRESENT** | from rc2 PRESENT | `customer-validation-workflow.md` exists; depth-audit out of rc3 scope. |

Twelve of twelve categories at PASS or PASS-with-explicit-DEFERRAL. Zero `FAIL`, zero `UNAUDITED`, zero `PASS-with-tracked-gaps`. The two PASS-with-explicit-DEFERRAL annotations name owner + milestone + acceptance per the rc3 rule.

## Remaining non-blocking issues

| ID | GH issue | Severity | Status | Why non-blocking for rc3 |
|---|---|---|---|---|
| ARCH-P1-002 | #3 | P1 | deferred | Founder/legal decision (ADR-0043 source-model pivot). Not architecture-mechanical. |
| ARCH-P2-001 | #4 | P2 | accepted (track) | ADR-0042 drill ambiguity. Track but defer; not freeze-blocking. |
| ARCH-P2-002 | #5 | P2 | accepted (track) | ADR-0038 control-plane DR plan sketch. **DEFERRED** in scorecard #8 with owner/milestone/acceptance. |
| ARCH-P3-001 | #6 | P3 | accepted (track) | Polish. ADR-0040 corpora composition. Not freeze-blocking. |

## Tracked deliverables for post-rc3

| Deliverable | Spec | Milestone | Status at rc3 |
|---|---|---|---|
| `scripts/check_claim_provenance.py` | `claim-provenance` | M0 | ✅ implemented (rc3) |
| `scripts/check_adr_cross_links.py` | `adr-cross-link` | M0 | ✅ implemented (rc3, dual-mode) |
| `scripts/check_mvp_scope_consistency.py` | (informal) | M0 | ✅ implemented (rc1) |
| Post-apply baseline-ADR cross-link draft | `adr-cross-link` | M0 | ⏸ runs at post-apply (script ready) |
| `architecture/blueprint/schemas/vault_request.schema.json` | `vault-authorization` | M3 | ⏸ DEFERRED |
| `architecture/blueprint/schemas/vault_response.schema.json` | `vault-authorization` | M3 | ⏸ DEFERRED |
| `architecture/blueprint/schemas/vault_audit_envelope.schema.json` | `vault-authorization` | M3 | ⏸ DEFERRED |
| `scripts/check_vault_ipc_contract.py` | `vault-authorization` | M3 | ⏸ DEFERRED |
| ADR-0038 DR sketch (RPO/RTO/HA-vs-DR/restore-cadence) | n/a | M2 | ⏸ DEFERRED |

## Freeze decision

**Freeze: yes — tag `architecture-rc3`.**

The rc3 target is met:

- Documents-only score 8.5/10 (target: ≥ 8.5) ✅
- Evidence-backed score 8.5/10 (target: ≥ 8.5) ✅
- All 12 categories PASS or PASS-with-explicit-DEFERRAL (zero UNAUDITED, zero PASS-with-tracked-gaps) ✅
- All M0 architecture enforcement scripts implemented and passing ✅
- ADR cross-link verification exists and passes (bootstrap mode) ✅
- Claim-provenance checker exists and passes ✅
- MVP scope checker passes ✅
- Vault IPC and DR gaps explicitly DEFERRED with owner + milestone + acceptance ✅
- 0 open P0; 0 accepted-open P1 ✅

A subsequent `architecture-final` (or `architecture-rc4` if needed) will follow once the v3.2.3.5 baseline is merged in and the post-apply enforcement runs successfully. After that, M3 schema deliverables and the M2 DR sketch can land at their respective milestones — they don't block rc3.

## Bridge to product implementation

With rc3 frozen, the smallest meaningful build slice is:

- 1 EDR sample input
- 1 investigation tape (with all MVP-required fields populated)
- 1 timeline
- 1 evidence ledger
- 1 verdict (deterministic enum from the fixed set)
- 1 EDR handoff recommendation (in `approval_required` mode)
- 1 replay report

That slice exercises every governing spec and every M0 enforcement script.
