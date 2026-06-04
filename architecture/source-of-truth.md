# Architecture Source of Truth

**Baseline:** v3.2.5.0-baseline-consolidated (2026-05-19)

This repository is finalized through an architecture release-candidate process.

## Source-of-truth hierarchy

1. `architecture/source-of-truth.md`
2. `architecture/review/finalization-checklist.md`
3. `architecture/adr-index.md`
4. Active ADRs
5. Invariants
6. Main architecture documents
7. Handover / milestone documents
8. Customer-facing architecture docs
9. OpenSpec change records
10. Historical / superseded ADRs

If two documents conflict, the higher source in this hierarchy governs unless a newer active ADR explicitly supersedes it.

## Current product wedge

### Internal (engineering and architecture documents)

Zovark is the tape recorder for cybersecurity investigations.

The core flow is:

EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.

### External (customer-facing, investor-facing, partner-facing)

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

Customer description: Before your SOC isolates a host or disables a user, Zovark shows the evidence, explains the verdict, records the approval path, and creates a replayable proof package.

The product hero artifacts are the approval-required EDR action card and the replayable proof package. The investigation tape is the internal proof substrate that produces them.

### Primary differentiator

ADR-0052 clarifies the buying-wedge emphasis: deterministic replay and evidence
integrity are the primary customer-facing differentiator.

The current architecture direction is hybrid inference with RamaLama as the
planned local-SLM runtime paired with approved cloud inference where tenant
policy allows it. ADR-0009 and ADR-0052 name this direction for architecture
planning only; it does not add RamaLama runtime implementation, tenant
controls, deployment automation, benchmarks, or customer-ready topology
selection.

Air-gap is an older deployment philosophy and a possible regulated-deployment
target, not the headline wedge and not a current runtime capability claimed by
this architecture-only PR. Any air-gap profile must remain pending until runtime
support, operator controls, validation, and deployment evidence exist.

The topology choice does not change the replay/evidence-integrity direction:
reconciled replay work should not re-inference and should rely on recorded
model-visible inputs, outputs, provenance, hashes, and verdict inputs.

## Finalization rule

The architecture is frozen only when:

- open P0 issues = 0,
- MVP contradictions = 0,
- customer-facing false claims = 0,
- active ADR index is current,
- missing evidence is labeled M0/future,
- release-candidate scorecard is complete.

## ADRs

All 53 ADR numbers (ADR-0001 through ADR-0053) accounted for in one of five
categories below.

### Binding (26)

Files exist at `architecture/adr/`. Status: active/proposed/amended per
`scripts/check_adr_cross_links.py`.

| ADR | Title |
|---|---|
| ADR-0001 | Zovark v1.0 foundation |
| ADR-0002 | Six-stage pipeline as architectural invariant |
| ADR-0004 | Inference layer abstraction |
| ADR-0006 | Data Flywheel - Opt-In Pooled With Tenant-First Benefits |
| ADR-0007 | Webhook-only ingest |
| ADR-0009 | Two-Model Architecture And RamaLama Local-SLM Runtime |
| ADR-0019 | Mesh Agent Pool - Concurrent Investigation Processing |
| ADR-0020 | Tape Recorder - Replay-Grade Investigation Record |
| ADR-0023 | Sigma Rule Generation Pipeline |
| ADR-0025 | Audit chain canonicalization and concurrent-insert semantics |
| ADR-0029 | Sigma Generation Scope Reduction and Manual Export Boundary |
| ADR-0038 | Control Plane and Customer-Instance Authority Boundary |
| ADR-0039 | Update Factory and Signed Bundle Distribution |
| ADR-0040 | Research Pipeline and Gated Candidate Promotion |
| ADR-0041 | Telemetry Boundary |
| ADR-0042 | Cryptographic Key Management |
| ADR-0044 | Disaster Recovery & Business Continuity (SaaS topology) |
| ADR-0045 | Customer Offboarding, GDPR Article 17, and Legal Hold |
| ADR-0046 | Deterministic Verdict Canonicalization |
| ADR-0047 | Replay Compatibility Matrix and Failure Modes |
| ADR-0048 | Healer Runtime Defense-in-Depth |
| ADR-0049 | Sigma Alert-Budget Governance |
| ADR-0050 | On-Call, Paging, and Vendor-Compromise Incident Response |
| ADR-0051 | Calendar Reconciliation |
| ADR-0052 | Deterministic Replay as Primary Differentiator |
| ADR-0053 | Runtime Proof-Loop Completion Criteria |

### Proposed / pending founder sign-off (1)

File exists at `architecture/adr/`. Not binding until the stated approval
condition is complete.

| ADR | Title | Approval gate |
|---|---|---|
| ADR-0043 | Open-Source Release Strategy | M1-DECISION-001 founder sign-off |

ADR-0043 may be used as a working assumption only where the ADR itself says so.
It is not binding architecture law until M1-DECISION-001 founder approval
occurs.

Inventory arithmetic: 26 binding + 1 proposed/pending-founder + 11 superseded
plus 4 retired plus 11 covered-by-invariant = 53 ADRs.

### Superseded (11)

Originally accepted; superseded by newer ADR(s). No ADR files exist — the
directory contains only currently-binding ADRs per validator constraint
`STATUS_VALID = {active, proposed, amended}`. Tracked here for traceability
only.

| ADR | Original Title | Superseded by |
|---|---|---|
| ADR-0005 | Tape recorder as primary marketing wedge | ADR-0052 |
| ADR-0008 | Deployment topology phasing | ADR-0052 (also ADR-0038, ADR-0041) |
| ADR-0011 | Cloud-first launch, air-gap as later topology | ADR-0052 (also ADR-0038) |
| ADR-0012 | Engineering team builds in compressed timeframe with parallel execution | ADR-0051 |
| ADR-0024 | SaaS operations, disaster recovery, tenant lifecycle, legal hold | ADR-0044 (also ADR-0045) |
| ADR-0026 | Replay compatibility matrix and migration semantics | ADR-0047 |
| ADR-0027 | Verdict determinism canonicalization | ADR-0046 |
| ADR-0028 | Credential vault threat model and runtime authorization | ADR-0042 |
| ADR-0032 | Schedule realism (supersedes ADR-0012) | ADR-0051 |
| ADR-0034 | Tenant DEK rotation policy | ADR-0042 |
| ADR-0035 | Open-source on-call and paging stack | ADR-0050 |

Titles read from bootstrap source at
`/tmp/bootstrap-v3.2.3.2-staged/zovark-v1-bootstrap-v3.2.3.2/architecture/adr/`.

### Retired (4)

Original decisions not carried forward. No ADR files; not binding.

| ADR | Original Title | Reason |
|---|---|---|
| ADR-0018 | 18-month product horizon | Audit determined content not worth promoting |
| ADR-0021 | EDR handover — autonomous response with reversibility | Autonomous-response capability not in current architecture |
| ADR-0036 | Open-source schema boundary (recovered gap) | Binding intent captured by INV-027 |
| ADR-0037 | Feature lifecycle and dead-code housekeeping (recovered gap) | Binding intent captured by INV-028 |

### Covered by Invariant (11)

Binding intent fully captured by an existing invariant. No separate ADR file.

| ADR | Covered by | Note |
|---|---|---|
| ADR-0003 | INV-001 | Tenant boundary |
| ADR-0010 | INV-025, INV-027 | Open standards binding, open-source schema boundary |
| ADR-0013 | INV-009 | Open-source-only dependencies |
| ADR-0014 | INV-010, INV-011 | WASM scope locked, Wasmtime configuration locked |
| ADR-0015 | INV-008 | Schema first |
| ADR-0016 | INV-007 | Zero dead code |
| ADR-0017 | INV-013 | No retired vocabulary |
| ADR-0022 | INV-014 | Healer is read-only |
| ADR-0030 | INV-023 | Bootstrap enforcement evidence |
| ADR-0031 | INV-022 | Quantified claim provenance |
| ADR-0033 | INV-025, INV-027 | Open standards binding, open-source schema boundary |

## Invariants (39)

All binding at `architecture/invariants.md`.

| INV | Title |
|---|---|
| INV-001 | Tenant boundary |
| INV-002 | Fail closed |
| INV-003 | Air-gap compatible |
| INV-004 | Deterministic verdict |
| INV-005 | Replayable |
| INV-006 | Tamper evident |
| INV-007 | Zero dead code |
| INV-008 | Schema first |
| INV-009 | Open-source-only dependencies |
| INV-010 | WASM scope locked |
| INV-011 | Wasmtime configuration locked |
| INV-012 | Explicit boundaries |
| INV-013 | No retired vocabulary |
| INV-014 | Healer is read-only |
| INV-015 | Sigma rules require analyst approval |
| INV-016 | Audit canonicalization |
| INV-017 | Replay fails closed on incompatibility |
| INV-018 | Verdict canonicalization |
| INV-019 | Vault per-action authorization |
| INV-020 | Immutable audit erasure boundary |
| INV-021 | Tenant usage attribution |
| INV-022 | Quantified claim provenance |
| INV-023 | Bootstrap enforcement evidence |
| INV-024 | MVP scope consistency |
| INV-025 | Open standards binding |
| INV-026 | Integer-only numeric precision in deterministic paths |
| INV-027 | Open-source schema boundary |
| INV-028 | Feature lifecycle and dead-code housekeeping |
| INV-029 | Customer Instance Tenant-Data Authority |
| INV-030 | Research Pipeline Output Is Not Customer-Runtime Authoritative |
| INV-031 | All Update Bundles Signed and Offline-Verifiable |
| INV-032 | Telemetry Crossing the Boundary Is Enumerable and Customer-Auditable |
| INV-033 | DR drill cadence is enforced |
| INV-034 | Customer-data deletion within 30-day window via DEK destruction |
| INV-035 | Audit-chain encrypted with separate audit DEK; survives customer offboarding for regulatory minimum |
| INV-036 | Replay engine never inferences, substitutes, or degrades |
| INV-037 | Healer runtime is sandboxed via process, DB, network, and credential isolation |
| INV-038 | Sigma rule publication is governed by alert budget, corpus freshness, drift detection, and analyst approval |
| INV-039 | Verdict input is canonical and complete; no forbidden inputs |

## Schemas (28)

Located at `architecture/blueprint/schemas/`. Alphabetical:

- audit_chain_root.schema.json
- audit_event.schema.json
- benchmark_artifact.schema.json
- campaign_record.schema.json
- control_plane_instance_status.schema.json
- crypto_shred_certificate.schema.json
- dr_drill_report.schema.json
- dr_restore_completed_event.schema.json
- finding.schema.json
- learning_pack.schema.json
- legal_hold_certificate.schema.json
- recommended_action.schema.json
- replay-compatibility.schema.json
- replay_failure_record.schema.json
- replay_record.schema.json
- replay_tool_catalog.schema.json
- research_experiment_result.schema.json
- retention_certificate.schema.json
- runtime_proof_loop_completion.schema.json
- scanner_finding_envelope.schema.json
- telemetry_envelope.schema.json
- tenant_usage_event.schema.json
- update_bundle.schema.json
- update_bundle_signed.schema.json
- update_candidate.schema.json
- update_promotion_decision.schema.json
- verdict_envelope.schema.json
- verdict_input.schema.json

### Known gaps

> Tracker note: the `issue #NN` and `PR #NN` references in this section and in "Consolidation history" refer to the `7inaydas-cmyk/zovark-architecture` tracker, not any downstream consumer repo.

- Resolved during issue #53 follow-up: `verdict_input.schema.json` and
  `replay_record.schema.json` were added as bounded architecture contracts for
  deterministic verdict/replay proof. Runtime derivation and replay-engine
  enforcement remain deferred to M5 per INV-036 and INV-039.
- Resolved during issue #55 follow-up: `replay_failure_record.schema.json` and
  the expanded replay compatibility failure-code vocabulary define canonical
  failure reporting authority. Runtime coverage mapping and replay-engine
  enforcement remain deferred to M5 per INV-036.
- Resolved during issue #57 follow-up: `architecture/replay-compatibility.yaml`
  now defines bounded replay compatibility row/outcome authority for canonical
  failure codes. Runtime row mapping, runtime coverage claims, and replay-engine
  enforcement remain deferred to M5 per INV-036.
- Resolved during issue #59 follow-up: `replay_tool_catalog.schema.json` and
  `architecture/replay/catalogs/` define bounded replay tool catalog retirement
  authority for `REPLAY_TOOL_RETIRED`. Runtime retired-tool validation, runtime
  coverage claims, and replay-engine enforcement remain deferred to M5 per
  INV-036.
- Resolved during issue #61 follow-up:
  `runtime_proof_loop_completion.schema.json` and
  `architecture/proof/runtime-proof-loop-completion.yaml` define bounded
  architecture authority for scoped deterministic replay proof-loop completion.
  This authority does not imply AlertForge, benchmark, dashboard, customer,
  product, production, compliance, SLA, audit-chain, or replay-engine readiness.
- Resolved during PR #52 review: `bad.schema.json` and `good.schema.json` were
  removed from the authoritative schema inventory because they were
  fixture-like placeholders, not production schemas.

## Archive

`archive/v3.2.4.6-staging/` contains pre-promotion staged content from the
v3.2.4.6 era. All unique content has been promoted to authoritative paths
above. The archive is reference-only, not validator-enforced, not authoritative.

## Consolidation history

This baseline was established by the v3.2.5.0 consolidation effort (closed
2026-05-19, eleven commits). The consolidation:

- Carried over INV-001-032 and 25 schemas from PR #51 review state (commit 1);
  PR #52 review later removed two fixture-like placeholders, leaving 23
  authoritative schemas
- Extracted INV-033-039 from ZOVARK-v3.2.4.3-CLOSURE.md (commit 2)
- Extracted ADR-0046 and ADR-0047 from the same closure document to bypass the
  v3.2.4.3 parser bug (commit 3)
- Promoted 16 MINOR-FIX ADRs from bootstrap-v3.2.3.2 and v3.2.4.3/4.6 sources
  (commits 4 and 5)
- Rewrote 6 MAJOR-REWRITE ADRs (commit 6)
- Archived the v3.2.4.6 staged subtree (commit 7)
- Removed the obsolete patch-directory check from
  `scripts/check_adr_cross_links.py` (commit 8)
- Repointed 42 ADR-0036/0037 references to INV-027/INV-028 and removed orphan
  recovery framing (commit 9)
- Removed 131 instances of pre-consolidation framing language ("candidate",
  "recovered", "pending reconciliation") while preserving 96 legitimate uses
  (commit 10)
- Expanded this source-of-truth document with full inventory (commit 11)

Subsequent architecture changes must amend this document alongside the relevant
ADR/invariant/schema file changes.
