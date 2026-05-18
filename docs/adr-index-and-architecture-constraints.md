# ADR Index And Architecture Constraints

Status: docs-only constraint index.

This document indexes ADRs and architecture-governing decision records that affect
post-Slice-001 work. It does not resolve all conflicts, freeze a new architecture,
define a Capability Identity Contract, change proof-package schemas, or authorize
runtime work. Conflicts and open constraints feed PR #27 (V3 asset inventory and
v4.1 domain map) and PR #29 (Capability Identity Contract and final architecture
synthesis).

## Current Repo State

| Field | Value |
|---|---|
| Branch | `docs/adr-index-architecture-constraints` |
| Base HEAD | `5a052b7 Document V3 ground-truth check` |
| Tracked worktree before this document | Clean |
| Local-only untracked files | `.vscode/`, `uv.lock`, `zovark-yc-demo.zip` |

## Source-Of-Truth Hierarchy

`architecture/source-of-truth.md` defines the governing order:

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

When sources conflict, the higher source governs unless a newer active ADR
explicitly supersedes it. This index uses that hierarchy when classifying
constraints.

## Source Inventory

| Source | Role | Constraint impact |
|---|---|---|
| `architecture/source-of-truth.md` | Highest local architecture authority | Sets internal/external product wedge and freeze rule. |
| `architecture/adr-index.md` | Current ADR status index | Lists visible patch ADRs 0038-0043, the v3.2.4.4 ADR-0009 amendment, proposed ADR-0052, and placeholder baseline ADRs 0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034. |
| Patch ADRs under `zovark-v3.2.4.6-engineering-ready/.../architecture/adr/` | Visible ADR bodies | Define proposed control-plane, update, research, telemetry, key-management, and release-strategy constraints. |
| `architecture/review/decision-log.md` | Release-candidate decision record | Records rc2/rc3 freezes, scope decisions, and post-rc3 spec hygiene. |
| `architecture/review/issue-ledger.yaml` | Architecture issue ledger | Records open/deferred conflicts such as ADR-0043 founder sign-off and DR/key-drill ambiguity. |
| `openspec/specs/` | Binding capability specs | Govern product wedge, tape, handoff, replay/audit, vault authorization, claim provenance, ADR cross-links, release-candidate process, and build-planning artifacts. |
| `architecture/objects/` | Derived object architecture | Useful explanations, but direct edits require corresponding OpenSpec changes. |
| `docs/architecture-reconciliation-v4-1-to-slice-001.md` | Planning note | Reconnects Slice 001 proof spine to broader v4.1 mesh; does not supersede source-of-truth hierarchy. |
| `docs/post-slice-001-roadmap.md` | Planning note | Sequences Replay V2, verification detail, manifest/provenance, AI Investigation Trace, and runtime work. |
| `docs/v3-ground-truth-check.md` | Factual repo inspection | Establishes V3 tool-calling as default in `Zovark_final` and V2 codegen/sandbox as legacy/fallback. |
| PR #24 code/tests (`zovark/slice001/cli.py`, `tests/test_cli_verify.py`) | Customer-readable verification behavior | Adds bounded CLI verification language; there is no separate `docs/customer-readable-verification-summary.md`. |
| `/tmp/zovark_final_groundtruth` (`Zovark_final`) | Older product/runtime repo inspection copy | Provides runtime facts and ADR-equivalent OpenSpec records for V3 absorption. |

## ADR And Decision Record Index

| ID / path | Title / status | Decision summary | Affected domains | Constraints imposed | V3 absorption relevance | v4.1 relevance | Slice proof-package relevance | Replay V2 relevance | PR #24 relevance | PR #25 relevance | New ADR needed? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `architecture/source-of-truth.md` | Architecture Source of Truth / active | Establishes source hierarchy, internal tape-recorder wedge, external audit-grade evidence-layer wedge, and freeze rule. | Product, governance, docs | Future conflicts resolve by hierarchy; architecture freezes require zero P0, zero MVP contradictions, zero customer-facing false claims, current ADR index, labeled missing evidence, and scorecard completion. | V3 absorption must not override current proof wedge without a spec/ADR path. | v4.1 must be mapped beneath the current hierarchy. | Slice 001 remains the deterministic proof spine. | Replay V2 must remain bounded by audit-grade evidence-layer positioning. | Customer-readable summary must avoid overclaims. | V3 runtime claims must be factual and not reposition the current repo as full V3 runtime. | No for hierarchy itself; yes for any substantive wedge change. |
| `architecture/adr-index.md` | ADR Index / active | Visible patch ADRs 0038-0043 are proposed; baseline ADRs 0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034 are placeholder rows pending post-apply verification. | Governance, ADR process | Do not treat missing baseline ADR bodies as fully inspected; run cross-link verification when baseline ADRs are applied. | V3 absorption cannot depend on unverified baseline ADR details without confirming them. | v4.1 references to baseline invariants remain provisional until post-apply verification. | Current proof package can rely only on specs/tests already in this repo. | Replay V2 cannot assume future baseline ADR contents. | No direct effect. | Ground-truth doc should stay factual and not infer missing ADR bodies. | Yes if baseline ADR import/verification changes scope or if new baseline references are added. |
| ADR-0009 amendment | Two-Model Architecture And RamaLama Local-SLM Runtime / accepted, amended | Names RamaLama as the canonical local-SLM runtime and clarifies cloud-only, local-only, and hybrid inference topology choices. | Inference, topology, replay provenance | Local inference is first-class but not mandatory; replay never re-inferences regardless of original inference source. | V3 local-inference salvage work must be retrained/reworked under bounded-envelope semantics before import. | v4.1 inference topology now has a named local-SLM runtime. | Current proof package still has no live LLM runtime. | Replay V2 remains recorded-output/offline and must not re-prompt. | No direct effect. | Ground-truth docs should distinguish architecture naming from implementation. | Yes before RamaLama implementation or inference gateway runtime. |
| ADR-0038 | Control Plane and Customer-Instance Authority Boundary / proposed | Separates Zovark control plane from customer instance; control plane never holds evidence, raw alerts, investigation records, vault material, EDR credentials, audit logs, or replay records. | Control plane, tenant authority, telemetry, deployment | Customer instance remains tenant-data authoritative; SaaS/hybrid/air-gap API parity; DR sketch deferred. | V3 runtime absorption must preserve customer-data authority boundaries. | v4.1 control plane and deployment profiles inherit this boundary. | Slice proof package remains local/customer-side; no control-plane dependency. | Offline verification aligns with air-gap/offline-package model. | Verification output must not imply data left the customer package. | V3 default runtime may have control-plane-like services, but absorption must classify them against this boundary. | New ADR likely needed before importing live control-plane/runtime work. |
| ADR-0039 | Update Factory and Signed Bundle Distribution / proposed | Future update bundles require reproducible builds, two independent signatures, SBOM, attestation, compatibility matrix, rollback metadata, air-gap export, and ledger. | Supply chain, release, update, air-gap | No single-signer releases; offline verification required for update bundles; runtime implementation M4. | V3 assets imported into current repo must not be treated as trusted release artifacts without update-factory controls. | v4.1 signed manifest/update concepts map here. | Slice 001 proof-package files are not release bundles and are unsigned. | Manifest/provenance/signing remain later than current verifier phases. | Summary must not claim cryptographic signing. | V3 ground-truth facts are source observations, not signed release claims. | Yes before package manifest/provenance/signing or update-bundle work. |
| ADR-0040 | Research Pipeline and Gated Candidate Promotion / proposed | Future research pipeline generates candidate artifacts only and submits them to a promotion queue; no direct runtime mutation. | Research, candidate generation, promotion, protected paths | Protected paths require higher review; candidate outputs never become runtime authoritative until promoted. | V3 tool/plan absorption must classify assets as existing runtime facts or candidate imports and avoid silent promotion. | v4.1 Learning/Research Pipeline maps here. | Slice proof-package logic is protected-path-like and should not be auto-mutated. | Verifier/replay code should be treated as protected high-risk paths. | No direct effect beyond avoiding inflated claims. | V3 tool/plan counts should not imply automatic import. | Yes for V3 asset promotion rules or Capability Identity Contract. |
| ADR-0041 | Telemetry Boundary / proposed | Defines allowlisted customer-instance to control-plane telemetry and forbids customer evidence, raw alerts, investigation records, audit logs, replay records, secrets, PII, hostnames, and IPs crossing the boundary. | Telemetry, privacy, customer trust | Telemetry is allowlist-only and customer-auditable; adding fields requires ADR amendment and customer notice. | V3 runtime telemetry/observability must be checked against this boundary. | v4.1 Observability and Control Plane cannot ingest investigation evidence by default. | Slice 001 has no telemetry and no network calls. | Offline verifier must not call network or emit telemetry. | Verification summary correctly says no external state was used. | V3 observability claims must be separated from current proof repo. | Yes before introducing telemetry runtime or customer-instance outbound payloads. |
| ADR-0042 | Cryptographic Key Management / proposed | Future release-signing keys are HSM-backed; role keys rotate; compromised keys are revoked and never reused. | Signing, keys, release, vault | Software keys unacceptable for production signing; key-ledger/verifiers are M4 deliverables; drill ambiguity is tracked. | V3 absorption cannot claim production signing without key-management implementation. | v4.1 signed roots/manifests rely on this later. | Slice 001 uses deterministic hashes/stubs, not production signing. | Manifest/provenance/signing must not be added casually. | Summary must not claim cryptographic signing. | V3 docs with signing/security claims need provenance. | Yes before production signing or key-ledger implementation. |
| ADR-0043 | Open-Source Release Strategy / proposed strategic pivot | Proposes Apache-2.0 core, source-available customer runtime, closed-source hosted internals; requires founder sign-off. | Licensing, release, customer trust | No closed-source code runs in customer environment if accepted; status still pending. | V3 code absorption is affected by source model and license posture. | v4.1 distribution/release posture affected. | Current proof repo is public code, but this does not settle runtime license strategy. | No direct verifier behavior change. | No direct effect. | V3 ground-truth doc must not assume the strategy is accepted. | Human decision required; likely new or amended ADR after founder decision. |
| ADR-0052 | Deterministic Replay as Primary Differentiator / proposed | Makes deterministic replay and evidence integrity the primary customer-facing differentiator; air-gap remains a planned regulated-deployment target pending runtime support, operator controls, validation, and deployment evidence. | Positioning, replay, evidence integrity | Customer-facing material should lead with replay/evidence integrity and avoid quantified claims without benchmark artifacts. | V3 absorption should support the replay/evidence story, not broad AI SOC or air-gap-only positioning. | v4.1 positioning aligns around replay-compatible evidence. | Current proof package is a concrete proof/replay artifact, not customer-readiness material. | Replay V2 is central to positioning; replay never re-inferences. | Customer-readable summaries stay bounded and non-legal. | Ground-truth reports must not turn topology into the buying wedge. | No for this positioning amendment; yes before benchmark/customer claims. |
| Baseline ADR placeholders | ADR-0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034 / post-apply verified placeholders | Baseline ADR bodies are absent from this repo; IDs are enumerated for later verification. | Control plane, audit erasure, verdict canonicalization, vault threat model, bootstrap evidence, claim provenance, tenant DEK rotation | `scripts/check_adr_cross_links.py` runs in bootstrap mode until baseline ADR bodies are present. | V3 absorption should not infer details beyond current references. | v4.1 mapping may need these baseline decisions to resolve trust-boundary and vault details. | Proof package relies on current specs/tests instead of unseen ADR text. | Replay V2 should not assume baseline details not in current specs. | No direct effect. | Ground-truth doc is intentionally factual without depending on missing ADRs. | Yes if baseline ADRs are imported or contradicted. |
| `openspec/specs/product-wedge/spec.md` | Product Wedge / active spec | External wedge: audit-grade evidence layer for AI-assisted SOC response. Internal wedge: tape recorder for cybersecurity investigations. | Product, docs, positioning | External docs must not lead with AI SOC platform, agent framework, investigation engine, or tape recorder; wedge changes require spec changes. | V3 tools/runtime should be described as future product body, not current external headline. | v4.1 can reconnect to the wedge only as broader architecture. | Slice proof package is the current external demo asset. | Replay V2 strengthens the proof/replay wedge. | Customer-readable verification must stay bounded and non-legal. | Ground-truth doc must avoid turning V3 into the current product claim. | Yes before changing product positioning. |
| `openspec/specs/investigation-tape/spec.md` | Investigation Tape / active spec | Defines tape identity, raw evidence, timeline, findings, verdict, recorded I/O, handoff refs, audit refs, lifecycle, and customer-facing surface. | Tape, evidence, findings, verdict, model/tool recording | Tape state is `recording` or `closed`; replay status is not a tape state; model/tool contributions require `recorded_io`; tape field changes require spec change. | V3 tool/model outputs should map through `recorded_io` or a future trace, not ad hoc fields. | v4.1 Harness/Inference Gateway outputs must be recorded before proof synthesis. | Slice 001 intentionally has no models/tools and uses `model_contribution: false`. | Verifier should treat tape as central substrate and fail closed on tampering. | Summary can say package contents are internally consistent, not complete. | V3 ground-truth hooks (`llm_audit_log`, tool calls) need adapter mapping later. | Yes for AI Investigation Trace V1 or any tape schema change. |
| `openspec/specs/edr-handoff/spec.md` | EDR Handoff / active spec | Defines action recommendation fields, approval mode, idempotency, execution result, rollback plan, audit/replay linkage. | Handoff, action, approval, rollback | MVP allows only `approval_required`; autonomous is post-MVP; target/evidence refs must be valid; handoff changes require spec change. | V3 action/governance concepts must not bypass approval-required proof contract. | v4.1 Action domain maps here but execution runtime is later. | Slice handoff is pending and approval-required. | Verifier re-derives and checks handoff consistency. | Summary can describe approval path, not executed response. | V3 ground-truth governance is separate from current handoff approval semantics. | Yes before importing autonomous/action runtime. |
| `openspec/specs/replay-and-audit/spec.md` | Replay And Audit / active spec | Defines replay state, recorded-output replay, audit-chain entries, canonical hashing, signed roots, unsigned tail, and DR restore-gap event. | Replay, audit, chain, signing semantics | Recorded-output replay cannot call live LLMs/tools; evidence hashes recompute; audit event enum is closed; replay/audit schema changes require spec change. | V3 model/tool runs must be recorded to replay safely; live forensic re-execution creates a new tape. | v4.1 Replay domain maps here. | Slice audit/replay are deterministic local artifacts. | Replay V2 verifier and failure taxonomy are direct extensions of this proof semantics. | Summary must not claim legal admissibility or complete chain of custody. | V3 ground-truth V2/V3 runtime can feed future recorded-output semantics only after trace design. | Yes before schema expansion, manifest/provenance, or richer replay report changes. |
| `openspec/specs/vault-authorization/spec.md` | Vault Authorization / active spec | Defines future authorization record binding action, tenant, target, policy, approval, nonce, signing tag, and state. | Vault, authorization, replay protection | Pre-vault handoffs may use placeholders; runtime vault authorization is M3+; IPC schemas deferred. | V3 governance/autonomy cannot substitute for vault authorization. | v4.1 Vault runtime maps here. | Slice 001 uses placeholder authorization refs only. | Verifier checks current placeholder-derived handoff, not live vault state. | Summary should avoid implying real vault authorization exists. | V3 ground-truth autonomous/governance levels are not current vault approval. | Yes before Vault runtime or authorization execution. |
| `openspec/specs/adr-cross-link/spec.md` | ADR Cross-Link / active spec | Defines bootstrap and post-apply ADR cross-link verification. | Governance, ADR integrity | Adding baseline ADR refs requires spec change; bootstrap mode lists awaiting baseline ADRs. | V3 absorption should add or amend ADR references deliberately. | v4.1 import must pass cross-link discipline. | Current proof repo stays valid in bootstrap mode. | No direct verifier behavior change. | No direct effect. | PR #25 does not replace ADR verification. | Yes if new ADR set or verification rules change. |
| `openspec/specs/build-planning-artifacts/spec.md` | Build Planning Artifacts / active spec | One-page map is derived and cannot introduce new decisions. | Docs, planning | Direct one-pager edits without OpenSpec change are rejected for governing content. | V3 map work belongs in PR #27/#29, not ad hoc one-pager edits. | v4.1 mapping should not override specs. | Slice build slice remains source-governed. | Replay V2 roadmaps are planning notes unless specs change. | No direct effect. | Ground-truth findings are inputs, not one-pager decisions. | Maybe if build-planning artifacts are updated after final synthesis. |
| `openspec/specs/claim-provenance/spec.md` | Claim Provenance / active spec | Quantified claims require allowed provenance tags; customer-facing docs cannot use hypothesis tags. | Claims, docs, validation | Measured claims must point to artifacts; policy commitments name owners and review cadence. | V3 benchmarks and throughput claims need measured artifacts. | v4.1 scale claims need provenance. | Slice proof-package docs must avoid unsupported legal/compliance claims. | Verifier docs must avoid certification/forensic-completeness claims. | Summary deliberately uses bounded proof-language. | Ground-truth benchmark findings remain lab/synthetic unless measured/customer-validated. | Yes only if claim categories or validation rules change. |
| `openspec/specs/release-candidate-process/spec.md` | Release Candidate Process / active spec | rc tags require score thresholds, deferral annotations, and decision-log entries. | Governance, freeze process | Deferred categories must name owner, milestone, and acceptance. | V3 absorption should not be called frozen without scorecard/decision record. | v4.1 reconciliation remains planning until freeze criteria met. | Slice 001 baseline is stable only within its documented contract. | Replay V2 phases should keep explicit non-goals. | No direct effect. | PR #25 is factual discovery, not a freeze. | Yes if freeze policy changes. |
| `architecture/review/decision-log.md` | TR-001 through TR-007 / active decision log | Records issue triage, product wedge fix, claim provenance, vault spec, rc2/rc3 freezes, and post-rc3 hygiene fixes. | Governance, freeze, scope | Zero P0 and explicit deferrals allowed rc3; post-rc3 fixes did not retag. | V3 absorption must preserve decision-log discipline. | v4.1 reconciliation is not a new rc tag. | Current proof work followed rc3 bridge-to-product slice. | Replay V2 should maintain scoped decision records. | No direct effect. | PR #25 records factual conflict, not resolution. | Possibly before final architecture freeze in PR #29. |
| `architecture/review/issue-ledger.yaml` | Architecture issue ledger / active | Tracks open/deferred issues: ADR-0043, ADR-0042 drill ambiguity, ADR-0038 DR sketch, ADR-0040 corpora detail. | Governance, open risk | Deferred issues are real and must not be presented as solved. | V3 absorption may depend on research-pipeline corpora and runtime hygiene. | v4.1 Control Plane/Research Pipeline items remain deferred. | No direct current proof change. | No direct current verifier change. | No direct effect. | Ground-truth check should not resolve these issues. | Yes for ADR-0043, control-plane DR, key drill, or research pipeline details. |
| `docs/architecture-reconciliation-v4-1-to-slice-001.md` | Architecture reconciliation / planning note | Classifies v4.1 components as preserved, deferred, under-specified, or future work after Slice 001. | Roadmap, architecture reconciliation | Does not supersede source-of-truth, OpenSpec, or ADRs. | Establishes that recorded model/tool hooks are the path toward AI Investigation Trace V1. | v4.1 remains broader product body. | Slice 001 is proof spine, not full runtime. | Places Replay V2 before trace/runtime. | No direct effect. | PR #25 refines V3 runtime facts used in later mapping. | Yes for final synthesis and capability contract. |
| `docs/post-slice-001-roadmap.md` | Post-Slice roadmap / planning note | Sequences Replay V2 verifier, replay detail/failure taxonomy, customer-readable verification, manifest/provenance, AI Investigation Trace, then runtime. | Roadmap | Planning note only; package-contract changes require explicit later work. | V3 bridge comes after verification semantics. | v4.1 runtime waits until proof/trace semantics stabilize. | Freezes nine-file Slice 001 contract until explicit change. | Directly governs current Replay V2 sequence. | PR #24 fits Phase 3 summary. | PR #25 is a new factual input before ADR index and inventory. | Yes for manifest/provenance or final architecture. |
| `docs/v3-ground-truth-check.md` | V3 Ground-Truth Check / factual report | Determines V3 deterministic tools are active/default in `Zovark_final`; V2 codegen/sandbox exists as feature-flagged legacy/fallback; docs conflict. | V3 absorption, runtime archaeology | Does not implement, freeze, or import V3; non-grounded product terms are not current runtime reality. | Provides factual basis for PR #27 asset inventory and PR #29 synthesis. | Helps map older runtime into v4.1 domains. | No direct Slice proof behavior change. | Future V3-generated packages must still verify through Replay V2. | No direct effect. | This is the authoritative current ground-truth report. | Yes for V3 absorption and Capability Identity Contract. |
| PR #24 behavior (`cli.py`, `test_cli_verify.py`) | Customer-readable verification summary / implemented behavior | CLI verify success/failure output explains deterministic verification and boundaries. | CLI, customer demo, verifier UX | Must remain deterministic and avoid legal/certification/signing/completeness claims. | V3 story shown to customers must be future direction, not shipped current behavior. | Helps explain proof wedge externally. | No package artifact change. | Presents verifier results to users. | This is the PR #24 output; no standalone docs file exists. | No direct effect. | No unless output becomes governed customer-facing spec. |
| `Zovark_final` `CLAUDE.md` and `docs/V3_MIGRATION_REPORT.md` | V3 deterministic tool-calling docs / older runtime evidence | V3 uses saved plans or LLM tool selection over deterministic tools; V2 sandbox behind `ZOVARK_EXECUTION_MODE=sandbox`. | V3 runtime, tools, governance, DB | Tool/plan counts drift by ref; benchmark claims need provenance; exact Fast/Reasoning names not present. | Primary input for V3 asset inventory. | Maps to v4.1 Harness, Inference Gateway, Action/State/Replay/Learning/Observability. | No direct current proof change. | Future V3 fixture outputs should be wrapped into current proof package. | Customer demos must not imply this is shipped in current repo. | Supports PR #25 verdict C. | Yes for V3-to-proof adapter and trace contract. |
| `Zovark_final` `docs/ARCHITECTURE.md`, `pipeline_stages.md`, `pipeline_map.md` | Stale V2 codegen/sandbox architecture docs | Describe Python code generation, AST prefilter, Docker sandbox, and template promotion. | Legacy runtime, sandbox, LLM codegen | Must be marked stale/legacy when absorbed; cannot be treated as current V3 default. | V2 path may matter as fallback fixture source. | v4.1 may inherit sandbox/security lessons but not current default truth. | No direct current proof change. | Future verifier does not execute sandbox. | No direct effect. | PR #25 identifies these as stale/conflicting docs. | Maybe for stale-doc cleanup after inventory. |
| `Zovark_final` `openspec/changes/archive/2026-04-15-stabilize-runtime-hygiene/` | Runtime hygiene decision record | Preserves Temporal wire name, removes hardcoded secrets, centralizes LLM key loading, keeps V3 tool path default, limits refactors. | V3 runtime, config, Temporal, secrets | V3 runtime import must keep workflow compatibility and secret hygiene constraints. | v4.1 runtime/platform work should inherit these hygiene decisions. | No direct proof package impact. | No direct verifier impact. | No direct effect. | Supports runtime/default pipeline evidence. | Yes if current repo absorbs runtime config/hygiene policy. |
| `Zovark_final` `openspec/specs/schema-migration-integrity/spec.md` | Schema Migration Integrity / older runtime spec | Migration ledger must match physical schema; Stage 5 dependencies must exist; repairs are auditable. | DB, migrations, runtime reliability | DB-backed runtime cannot trust lying ledger rows; repairs require end-to-end verification. | V3 fixture capture must record DB/ref state and avoid trusting broken ledgers. | v4.1 State domain and runtime DB need this discipline. | Current Slice 001 has no DB. | Current verifier has no DB. | No direct effect. | Supports DB truth section. | Yes before live DB runtime or fixture capture depends on old DB. |

## Confirmed Constraint Themes

### Product And Positioning

- External positioning is the audit-grade evidence layer for AI-assisted SOC
  response.
- ADR-0052 clarifies that deterministic replay plus evidence integrity is the
  primary differentiator; air-gap remains a planned regulated-deployment target pending runtime support, operator controls, validation, and deployment evidence.
- Internal architecture may use the tape-recorder metaphor.
- Customer-facing docs must not lead with AI SOC platform, generic agent
  framework, investigation engine, or tape recorder.
- Claims must remain bounded: no legal admissibility, certification readiness,
  SLSA compliance, cryptographic signing, transparency-log anchoring, or
  complete-evidence collection unless separately implemented and proven.

### Proof Package And Replay

- Slice 001 is the deterministic local proof-package CLI baseline.
- The current proof-package contract is exactly nine files.
- Replay V2 verifies the exported package offline and must fail closed.
- Manifest, provenance, signing, transparency logs, and schema expansion remain
  out of scope until explicit package-contract work.
- Recorded-output replay must not call live LLMs or live tools.

### V3 Absorption

- `Zovark_final` contains a real V3 deterministic tool-calling implementation.
- V2 codegen/sandbox also exists, but as legacy/fallback when
  `ZOVARK_EXECUTION_MODE=sandbox` or Path D fallback is used.
- Tool/plan counts are ref-sensitive. `v3.0.0` matches 34 tools / 24 plans;
  current default branch has 39 tools and 25 plan keys.
- The exact names Fast Mode and Reasoning Mode were not found as current runtime
  mode names. They remain product-mode language until a future design makes them
  concrete.
- V3 assets must be inventoried before they are mapped into proof-package or
  investigation-trace semantics.

### Runtime And Platform

- Live EDR, Vault runtime, Control Plane, telemetry, database, dispatchers,
  Temporal runtime, RamaLama/local inference, WASM, Sentry, and action execution
  are later runtime/platform work.
- Control Plane must not hold customer evidence, raw alerts, investigations,
  audit logs, replay records, EDR credentials, vault material, secrets, PII,
  hostnames, or customer IPs.
- Telemetry must be allowlisted and customer-auditable before runtime telemetry
  exists.
- Production signing/key management requires future HSM/key-ledger work; current
  deterministic hashes are not production signing.

## Conflicts And Ambiguity

| Conflict / ambiguity | Current status | Why it matters | Feeds |
|---|---|---|---|
| Baseline ADR bodies 0001-0037 are absent | Bootstrap-mode verification only | References to baseline ADRs are placeholders until post-apply verification. | PR #26 follow-up if baseline imported; PR #29 if constraints are needed. |
| ADR-0043 source model remains proposed strategic pivot | Deferred founder/legal decision | Affects public/open-source/source-available posture and customer trust language. | PR #29 or separate founder ADR decision. |
| V3 docs conflict with V2 stale docs in `Zovark_final` | PR #25 classified current truth as V3 tools default, V2 sandbox legacy/fallback | Asset inventory must distinguish active runtime from stale architecture docs. | PR #27. |
| `InvestigationWorkflowV2` name persists while V3 tools are default | Preserved wire name for compatibility | Avoid mistaking workflow wire name for V2 runtime truth. | PR #27, PR #31. |
| PR #24 has no standalone docs file | Implemented as CLI output/tests | Future docs should cite behavior, not a missing document. | PR #29 if customer-facing verification becomes a formal capability. |
| v4.1 broader mesh vs Slice 001 proof CLI | Reconciled as hierarchy, not merged architecture | Prevents proof spine from being mistaken for full runtime, or vice versa. | PR #27 and PR #29. |
| Manifest/provenance desire vs current nine-file contract | Explicitly deferred | Avoid package-contract drift during verifier work. | Future package-contract PR, not PR #26/#27. |
| AI Investigation Trace hooks exist but schema does not | Deferred after Replay V2 | Avoid black-box model/tool execution before recorded-output semantics are designed. | PR #30. |
| V3 benchmark claims are lab/synthetic/ref-sensitive | Not customer-validated | Prevents unsupported scale or accuracy claims. | Track C scale story; PR #29. |

## Architecture Constraints For Upcoming PRs

| Upcoming PR | Constraint from this index |
|---|---|
| PR #27 V3 asset inventory + v4.1 domain map | Must inventory assets without importing them, must mark active vs stale/ref-specific, and must map through source-of-truth hierarchy. |
| PR #28 V3 fixture capture | Must capture representative fixtures without schema changes or DB/runtime broadening; must record branch/ref/environment and avoid trusting stale benchmark claims. |
| PR #29 Capability Identity Contract + final architecture synthesis | Must resolve or explicitly defer conflicts, name owners for open constraints, and decide which new ADRs/spec changes are required. |
| PR #30 Investigation Trace V1 spec | Must build on `recorded_io`, model/tool pins, prompt/response hashes, and recorded-output replay. No unrecorded live model/tool replay. |
| PR #31 V3 fixture to proof-package adapter | Must adapt fixtures into the existing proof-package semantics without changing the nine-file contract unless a prior spec PR authorizes it. |
| PR #32 Verify generated V3 proof package with Replay V2 | Must use the landed offline package verifier and fail closed on tampering or inconsistent exported artifacts. |

## New ADR / Spec Need Register

| Potential decision | Needed before | Current trigger |
|---|---|---|
| V3 absorption and Capability Identity Contract | PR #29 | Decide how V3 tools/plans, skills, tasks, and governance become stable identities in the proof architecture. |
| AI Investigation Trace V1 | PR #30 | Define model/tool invocation records, hypotheses, candidate findings, accepted/rejected findings, and deterministic synthesis boundaries. |
| Package manifest/provenance | Future package-contract PR | Add artifact hashes, verifier version, rule/spec/code pins, and deterministic package metadata. |
| Fast Mode / Reasoning Mode product modes | After Investigation Trace and Harness semantics | Product-mode names are not current repo terms and need grounding. |
| Harness / Inference Gateway MVP | Later runtime phase | Introduce model/tool routing after recorded invocation contracts are stable. |
| Vault runtime authorization | Before live action execution | Replace bootstrap placeholder authorization refs with real signed authorization records. |
| Control Plane and telemetry runtime | Before any customer-instance outbound telemetry | Enforce ADR-0038/0041 data-boundary constraints. |
| ADR-0043 source model decision | Before public baseline/source release commitment | Founder/legal decision remains pending. |
| Control-plane DR sketch | M2 or before control plane implementation | ARCH-P2-002 remains accepted-track. |
| ADR-0042 drill clarification | Before key-management implementation | ARCH-P2-001 remains accepted-track. |

## Explicit Non-Resolution Statement

This PR indexes constraints only. It does not:

- resolve all conflicts,
- rewrite the roadmap,
- change runtime code,
- change tests,
- change proof-package schemas,
- add manifest or provenance files,
- implement Capability Identity Contract,
- implement Investigation Trace,
- capture V3 fixtures,
- build a V3-to-proof adapter,
- alter Replay V2 behavior,
- introduce live EDR, LLM/runtime, network, DB, Vault, dispatcher, Sentry, or
  deployed runtime work.

Conflicts listed above feed PR #27 and PR #29.
