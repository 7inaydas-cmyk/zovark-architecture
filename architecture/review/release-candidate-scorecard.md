# Architecture Release Candidate Scorecard

## Status

Architecture release candidate: **rc1 — proposed for freeze (documents-only).**

Scoring date: 2026-05-01.

## Freeze criteria

- [x] Open P0 issues = 0
- [x] MVP contradictions = 0 (`scripts/check_mvp_scope_consistency.py` passes)
- [x] Customer-facing false claims = 0 (no documented false claim found at this stage; full claim-provenance enforcement is the M0 deliverable tracked in ARCH-P1-001)
- [x] Active ADR index current
- [x] Missing evidence labeled M0/future
- [x] Product wedge clear (canonical statement + core flow verified across the 4 target docs; governing spec at `openspec/specs/product-wedge/spec.md`)
- [ ] Investigation tape defined as a structured object (signposted as a concept; full object schema is M1+ work, tracked under future ARCH issues)
- [ ] Replay semantics fully specified (recorded-output replay vs. live inference distinguished in `mvp-scope.md`; deeper semantics — hash verification, schema/tool/catalog version pinning, deterministic verdict recompute — remain M1+ work)
- [ ] EDR handoff record fully specified (signposted as a concept; the canonical record fields — action type, target, tenant, evidence links, policy snapshot, approval mode, authorization record, idempotency key, execution result, rollback plan — are not yet documented as a single object spec)
- [x] Customer validation workflow present (`customer-validation-workflow.md` exists in the patch tree)

The freeze criteria the runbook lists as **hard** for `architecture-rc1` (top six bullets) are all satisfied. The bottom four are documentation depth that will land via subsequent OpenSpec changes (`fix-investigation-tape`, `fix-edr-handoff`, `fix-replay-and-audit-semantics`) when the corresponding ARCH issues are filed and accepted.

## Documents-only architecture score

**7 / 10**

Rationale. The wedge is now coherent, the ADR index is well-structured, the issue ledger and decision log are clean, and triage decisions are recorded. Points lost on tape/handoff/replay object specs (currently signposts, not full definitions) and on the missing claim-provenance enforcement script. Vault/authorization is partially scoped — `ADR-0028` and `ADR-0034` referenced from the patch live in the baseline tree (ADR-0001…0037) and were not audited in this pass.

## Evidence-backed architecture score after M0

**TBD / 10**

M0 has not been completed. Requires:

- `scripts/check_claim_provenance.py` (ARCH-P1-001) implemented, runs in CI, customer-facing docs pass.
- ADR-0001…0037 baseline ADRs verified post-apply (referenced in patch's `adr-index.md` notes).
- Telemetry boundary check `check_telemetry_boundary.py` (per ADR-0041 implementation status notes).

Rescore after M0 close-out.

## Checklist scoring

| Category | Pass/Fail | Notes |
|---|---|---|
| Product wedge clarity | **PASS** | Canonical statement + core flow in 4 target docs; spec governs future changes; no drift framing found. |
| MVP scope consistency | **PASS** | `mvp-scope.md` separates M0 / Design-Partner MVP / Out-Of-MVP / Post-MVP / GA explicitly; `scripts/check_mvp_scope_consistency.py` returns 0. |
| ADR inventory and supersession | **PASS** | All 6 ADRs (0038–0043) in `architecture/adr-index.md` with 13-column metadata; all `proposed`; ADR-0038 amends ADR-0011 surfaced; no active-active contradictions. ADRs 0001–0037 are in the predecessor baseline and listed as post-apply verification. |
| Claim provenance | **FAIL** | `scripts/check_claim_provenance.py` missing (ARCH-P1-001 open / GitHub #2). `architecture/claims/claim-provenance.md` is empty; rules documented only in the patch-tree version. Architecture-blocker for customer-facing review, not for documents-only freeze. |
| Investigation tape object | **PARTIAL** | Wedge signpost names tape as the central recorded object and lists its conceptual contents (raw evidence, timeline, findings, verdict, EDR handoff record, rollback plan, replay state, audit references). No structured object definition exists yet; no schema. |
| Replay correctness | **PARTIAL** | `mvp-scope.md` distinguishes recorded-output replay from live inference. Schema/tool/catalog version pinning, evidence-hash verification, deterministic verdict recompute, and forensic re-execution distinction are not yet documented. |
| EDR handoff correctness | **PARTIAL** | Wedge signpost names handoff as replayable, evidence-linked, and reversible. The canonical 10-field record (action type, target, tenant, evidence links, policy snapshot, approval mode, authorization record, idempotency key, execution result, rollback plan) is not yet a documented object spec. |
| Audit, DR, and tenant lifecycle | **PARTIAL** | Restore-gap semantics in `disaster-recovery-restore-gap.md`; audit chain referenced in invariants. Control-plane DR plan deferred (ARCH-P2-002 / GitHub #5). Same-region HA vs cross-region DR not explicit. |
| Vault / authorization | **UNAUDITED** | Vault-related ADRs (0028 vault threat model, 0034 tenant DEK rotation) referenced from the patch live in the baseline tree (ADR-0001…0037) and were not audited in this pass. INV-019 enforces vault per-action authorization. Schema for IPC envelope between callers and vault is flagged as a DD-blocker by the patch. |
| Evidence status | **PARTIAL** | Existing scripts (telemetry / control-plane / patch-self-test / shiptime / release-metadata) are real and listed. Missing scripts (claim-provenance, telemetry-boundary runtime, key-rotation-age) are labeled as M-N deliverables. ARCH-P1-001 tracks the claim-provenance gap. |
| Schedule realism | **PASS** | M0 / M1 / M2 / M3 / M4 / M5 / M6 / M9 / M10 separation appears in `ENGINEERING-READY-HANDOFF.md` and ADR scope notes. Old schedules superseded by `v3.2.4.6-FINAL.md`. Provenance tags in place where claims appear. |
| Customer validation workflow | **PRESENT** | `architecture/customer-validation-workflow.md` exists in the patch tree. Depth not audited in this pass. |

## Remaining non-blocking issues

| ID | GH issue | Severity | Status | Why non-blocking |
|---|---|---|---|---|
| ARCH-P1-001 | #2 | P1 | accepted | Architecture-blocker for customer-facing review, not for documents-only freeze. Held per locked plan; revisit when customer review timing is set. |
| ARCH-P1-002 | #3 | P1 | deferred | Founder/legal decision (ADR-0043 source-model pivot). Architecture review can proceed in parallel; only the bootstrap baseline tag is gated. |
| ARCH-P2-001 | #4 | P2 | accepted | Track-but-defer. Not freeze-blocking. |
| ARCH-P2-002 | #5 | P2 | accepted | Track-but-defer. Becomes load-bearing at M2. |
| ARCH-P3-001 | #6 | P3 | accepted | Polish. Not freeze-blocking. |

## Freeze decision

**Freeze: yes — tag `architecture-rc1`.**

The runbook's hard freeze criteria are met:

- Open P0 issues = 0.
- MVP contradictions = 0.
- Customer-facing false claims = 0 (no documented false claim found at this stage).
- Active ADR index current.
- Missing evidence labeled M0/future.
- Product wedge clear.
- Customer validation workflow present.

Documents-only score is 7/10. Evidence-backed score is held until M0 closes (claim-provenance script + baseline-ADR cross-link verification). The four "PARTIAL" categories (tape object, replay, EDR handoff record, audit/DR/lifecycle) are object-schema work that the bootstrap package does not pretend to complete; they are visible as future work via the tracked P1/P2/P3 issues and via the open OpenSpec change names suggested in the runbook.

Tagging `architecture-rc1` freezes the **documents-only** architecture release candidate. A subsequent `architecture-rc2` (or `architecture-final`) will follow once M0 deliverables land and the tape/handoff/replay/audit object schemas are specified.
