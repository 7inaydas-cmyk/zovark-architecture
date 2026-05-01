# Architecture Release Candidate Scorecard

## Status

Architecture release candidate: **rc2 — proposed for freeze.**

Scoring date: 2026-05-01. Supersedes the rc1 scorecard (same date, prior commit).

## Freeze criteria (rc2)

- [x] Open P0 issues = 0
- [x] MVP contradictions = 0 (`scripts/check_mvp_scope_consistency.py` passes)
- [x] Customer-facing false claims = 0 (no documented false claim found)
- [x] Active ADR index current (8 baseline ADRs surfaced as placeholder rows pending M0 cross-link verification)
- [x] Missing evidence labeled M0 / M3 / future with explicit acceptance criteria
- [x] Product wedge clear (canonical statement + core flow verified across the 4 target docs; governing spec at `openspec/specs/product-wedge/spec.md`)
- [x] Investigation tape defined as a structured object (`investigation-tape` capability — required fields, lifecycle, customer-facing surface)
- [x] Replay semantics fully specified (`replay-and-audit` capability — recorded-output vs. forensic, hash verification, schema/tool/catalog version pinning, deterministic verdict recompute)
- [x] EDR handoff record fully specified (`edr-handoff` capability — 14-field record, approval modes, idempotency, rollback classes)
- [x] Customer validation workflow present (patch-tree `customer-validation-workflow.md`)
- [x] No `UNAUDITED` checklist categories (vault-authorization moved from UNAUDITED to PASS-with-tracked-gaps via `fix-vault-authorization-audit`)

## Documents-only architecture score

**8.5 / 10**

Rationale. The wedge is coherent. All five rc2 architecture objects (investigation tape, EDR handoff, replay-and-audit, vault authorization, ADR cross-link verification) have governing specs and architecture object documents that are sufficient for build planning. Decision log covers four triage rounds (TR-001..TR-004). Eight OpenSpec changes archived; seven capabilities specified in `openspec/specs/`. Claim-provenance rules consolidated into the source-of-truth doc with an explicit M0 deliverable contract.

Points withheld from a perfect 10:

- M0/M3 deliverables (claim-provenance script, ADR cross-link script, vault IPC schemas) are specified with acceptance criteria but not implemented; that's correct rc2 posture but it remains documentation-only.
- ARCH-P2-002 (control-plane DR plan) is referenced as a hook in `replay-and-audit` but the actual sketch ADR has not been authored. Spec acknowledges this as a tracked deferral.
- The 8 baseline ADRs (ADR-0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034) are surfaced in `adr-index.md` as placeholder rows; full metadata lands when M0 verification runs against the v3.2.3.5 baseline.
- ARCH-P2-001 (ADR-0042 drill ambiguity) and ARCH-P3-001 (ADR-0040 corpora composition) remain accepted-track and are documented as non-blocking polish.

## Evidence-backed architecture score after M0

**TBD / 10**

Rescore after the three M0 / M3 deliverables land:

- `scripts/check_claim_provenance.py` (M0)
- `scripts/check_adr_cross_links.py` (M0)
- `scripts/check_vault_ipc_contract.py` + 3 vault IPC schemas (M3)

When all three are in place and CI-wired, the evidence-backed score is expected to land in the 8.5–9.0 range subject to baseline-ADR cross-link results.

## Checklist scoring (rc2)

| Category | Status | Change | Notes |
|---|---|---|---|
| 1. Product wedge clarity | **PASS** | from rc1 PASS | Canonical statement + core flow in 4 target docs; spec governs. |
| 2. MVP scope consistency | **PASS** | from rc1 PASS | `scripts/check_mvp_scope_consistency.py` passes. |
| 3. ADR inventory and supersession | **PASS** | from rc1 PASS-with-tracked-gaps | rc2 adds the `adr-cross-link-verification` capability and the placeholder Baseline-ADRs section. |
| 4. Claim provenance | **PASS** | **from rc1 FAIL** | Rules + spec landed (`fix-claim-provenance`); script is an M0 deliverable with explicit acceptance criteria. Matches the rc2 target verbatim ("either fixed or explicitly marked as M0 deliverable with acceptance criteria"). |
| 5. Investigation tape object | **PASS** | **from rc1 PARTIAL** | Full object spec (`investigation-tape`); 8 field categories; lifecycle states; customer-facing surface; MVP-required vs. post-MVP classification. |
| 6. Replay correctness | **PASS** | **from rc1 PARTIAL** | `replay-and-audit` capability — recorded-output vs. forensic, hash verification, schema/tool/model version pinning, deterministic verdict recompute. |
| 7. EDR handoff correctness | **PASS** | **from rc1 PARTIAL** | 14-field record spec (`edr-handoff`); approval modes; idempotency; rollback classes (automatic / manual_documented / irreversible). |
| 8. Audit, DR, and tenant lifecycle | **PASS-with-tracked-gaps** | **from rc1 PARTIAL** | Audit chain spec (`replay-and-audit`); canonicalization, concurrent-insert, root signature, unsigned tail, DR restore-gap with declared-loss-window event preserved verbatim. ARCH-P2-002 (control-plane DR plan sketch) remains accepted-track and explicitly DEFERRED; rc2 target permits this. |
| 9. Vault / authorization | **PASS-with-tracked-gaps** | **from rc1 UNAUDITED** | Full record spec (`vault-authorization`); 9-rule verification; replay protection via nonces; compromise response; M3 IPC schemas tracked as deliverables with acceptance criteria. Cross-link to baseline ADR-0028 / ADR-0034 deferred to M0 verification. **No longer UNAUDITED — rc2 target met.** |
| 10. Evidence status | **PASS** | **from rc1 PARTIAL** | All M0/M3 deliverables (claim-provenance script, ADR cross-link script, vault IPC schemas) are explicitly enumerated with acceptance criteria. |
| 11. Schedule realism | **PASS** | from rc1 PASS | M0 / M1 / M2 / M3 / M4 / M5 / M6 / M9 / M10 separation in patch + handoff. |
| 12. Customer validation workflow | **PRESENT** | from rc1 PRESENT | `architecture/customer-validation-workflow.md` exists; depth-audit not in rc2 scope. |

Twelve of twelve categories at PASS, PASS-with-tracked-gaps, or PRESENT. Zero categories at FAIL or UNAUDITED.

## Remaining non-blocking issues

| ID | GH issue | Severity | Status | Why non-blocking for rc2 |
|---|---|---|---|---|
| ARCH-P1-002 | #3 | P1 | deferred | Founder/legal decision (ADR-0043 source-model pivot). Architecture review proceeds in parallel; only the bootstrap baseline tag is gated. Not architecture-mechanical. |
| ARCH-P2-001 | #4 | P2 | accepted | Track-but-defer. ADR-0042 drill ambiguity (scheduled vs. contingency). Not freeze-blocking. |
| ARCH-P2-002 | #5 | P2 | accepted | Track-but-defer. ADR-0038 control-plane DR plan sketch. `replay-and-audit` references the hook; sketch ADR lands in a follow-up. |
| ARCH-P3-001 | #6 | P3 | accepted | Polish. ADR-0040 corpora composition under-specified. Not freeze-blocking. |

## Tracked M0 / M3 deliverables

Four deliverables with explicit acceptance criteria, drawn from the rc2 spec set:

| Deliverable | Spec | Milestone | Acceptance criteria |
|---|---|---|---|
| `scripts/check_claim_provenance.py` | `claim-provenance` | M0 | 4 criteria locked in spec. |
| `scripts/check_adr_cross_links.py` | `adr-cross-link-verification` | M0 | 4 criteria locked in spec. |
| `architecture/blueprint/schemas/vault_request.schema.json` | `vault-authorization` | M3 | 4 criteria locked in spec (metadata triple, fixtures, fitness function ref, field encoding). |
| `architecture/blueprint/schemas/vault_response.schema.json` | `vault-authorization` | M3 | same |
| `architecture/blueprint/schemas/vault_audit_envelope.schema.json` | `vault-authorization` | M3 | same |
| `scripts/check_vault_ipc_contract.py` | `vault-authorization` | M3 | implied by the schema acceptance criteria; references the three schemas. |

Plus two existing scripts already in tree:

- `scripts/check_mvp_scope_consistency.py` — exists, passes today.
- (existing patch-tree fixture-presence checks) — exist in patch tree.

## Freeze decision

**Freeze: yes — tag `architecture-rc2`.**

The rc2 target is met:

- Documents-only score 8.5/10 (target: ≥ 8.3) ✅
- All 12 categories PASS, PASS-with-tracked-gaps, or PRESENT (no FAIL, no UNAUDITED) ✅
- Vault/authorization moved from UNAUDITED to PASS-with-tracked-gaps ✅
- Tape, handoff, replay, audit objects all defined to the build-planning bar ✅
- Claim provenance fixed (rules + spec) with M0 deliverable explicitly marked with acceptance criteria ✅

A subsequent `architecture-rc3` (or `architecture-final`) will follow once M0 deliverables (claim-provenance + ADR cross-link verification) land and the M3 vault IPC schemas are produced. The rc3 target should be: every PASS-with-tracked-gaps moves to strict PASS, evidence-backed score ≥ 8.5.
