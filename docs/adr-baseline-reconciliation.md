# ADR Baseline Reconciliation Review

Status: docs-only reconciliation review. This document does not import old ADR
files, change runtime code, change adapter behavior, change verifier behavior,
change schemas, start AlertForge integration, create benchmarks, or prepare
customer-readiness material.

## Source Situation

The exact `zovark-v1-bootstrap-v3.2.3.5` predecessor baseline package or folder
was not found during local ADR discovery. Candidate predecessor baseline material
was found in older `v3.2.3`, `v3.2.3.2`, and `v3.2.1` bootstrap zips.

Candidate split ADR files were found for `ADR-0001` through `ADR-0035`.
Current visible patch ADRs are `ADR-0038` through `ADR-0043` under the
`zovark-v3.2.4.6` patch tree.

Representative candidate predecessor source path used in this review:

```text
/home/excelsior/Downloads/Old/files/zovark-v1-bootstrap-v3.2.3-final.zip!/zovark-v1-bootstrap-v3.2.3/architecture/adr/
```

Current visible ADR source path:

```text
zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/adr/
```

## Post-PR #45 ADR Recovery Update

PR #45's discovery conclusion was correct for the visible repo and local-disk
search available at the time. Newer recovery from older uploaded/session
architecture material changes the ADR inventory, but does not silently merge the
recovered material into the current implementation or make it automatically
current repo source of truth.

Corrected ADR source classification:

- `ADR-0001` through `ADR-0035`: candidate predecessor baseline material.
- `ADR-0036` through `ADR-0037`: recovered predecessor baseline material from
  older uploaded/session architecture material.
- `ADR-0038` through `ADR-0043`: visible current repo/patch ADRs.
- `ADR-0044` through `ADR-0051`: recovered older `v3.2.4.3` patch material; not
  automatically current active source of truth.

Source/provenance notes:

- The current repo visibly carried only `ADR-0038` through `ADR-0043` during the
  earlier discovery pass.
- Older uploaded/session architecture material carried `ADR-0036`, `ADR-0037`,
  and `ADR-0044` through `ADR-0051`.
- The Zovark Architecture v4.1 technical architecture spec reflects many later
  ADR themes, but is not itself an ADR index or ADR source file.
- Exact durable file paths for the recovered uploaded/session material are not
  recorded in this repo. The recovered material should be imported or attached in
  a future source-of-truth PR before being treated as canonical.

Recovered predecessor baseline ADRs:

- `ADR-0036` — Open-source schema boundary. Status: accepted. Date:
  2026-04-29. Version context: `v3.2.3.5`. Source classification: recovered
  predecessor baseline material from older uploaded/session architecture
  material.
  Key implication: canonical Zovark schemas must be Apache-2.0/source-available;
  vendor or proprietary schemas are export mappings only; vendor schemas must
  not be canonical dependencies for replay, audit, storage, verdict, or customer
  evidence.
  Build impact: constrains OCSF normalization, schema registry work,
  proof-package evidence schema decisions, Replay compatibility, customer
  evidence exports, and future SIEM/EDR mapping work.
- `ADR-0037` — Feature lifecycle and dead-code housekeeping. Status: accepted.
  Date: 2026-04-29. Version context: `v3.2.3.5`. Source classification:
  recovered predecessor baseline material from older uploaded/session
  architecture material.
  Key implication: every product feature must have a durable `F-NNN` feature ID
  and lifecycle state; no orphan schemas; no hidden flags; no future plugin
  skeletons; no unused services; no docs referencing missing scripts/tests; and
  the first 37 ADRs are locked v1.0 architectural memory.
  Build impact: no new local testbed CLI, AlertForge ingest path, benchmark
  harness, product component, feature flag, service, or schema should be added
  without checking feature-registry/lifecycle alignment.

Recovered older `v3.2.4.3` patch material:

- `ADR-0044` — Disaster Recovery & Business Continuity
- `ADR-0045` — Customer Offboarding, GDPR Article 17, and Legal Hold
- `ADR-0046` — Deterministic Verdict Canonicalization
- `ADR-0047` — Replay Compatibility Matrix and Failure Modes
- `ADR-0048` — Healer Runtime Defense-in-Depth
- `ADR-0049` — Sigma Alert-Budget Governance
- `ADR-0050` — On-Call, Paging, and Vendor-Compromise Incident Response
- `ADR-0051` — Calendar Reconciliation

Older `v3.2.4.3` material says `ADR-0012` and `ADR-0032` are superseded by
`ADR-0051`. Do not apply that supersession silently to current repo behavior
until the recovered later ADRs are reconciled.

This review does not claim the architecture is fully ADR-synced. That claim is
forbidden until recovered `ADR-0036` through `ADR-0051` material is reconciled
against current repo direction or explicitly classified as historical,
deferred, superseded, stale, or non-authoritative.

## Current Architecture Baseline Used For Reconciliation

This table classifies candidate ADRs against the current local-build direction:

- governed autonomous SOC investigation mesh
- deterministic proof package
- offline Replay verifier
- V3 forward, Slice proof absorbed
- explicit Proof Package V2
- V1 default remains V1-only
- no raw prompts, tool arguments, tool outputs, payloads, messages, notes, or
  hidden reasoning leakage
- AlertForge as synthetic alert/scenario generator, not Zovark architecture
- no customer outreach until architecture, build, AlertForge-style tests, and
  benchmark evidence are ready

Applicability values are limited to `active`, `deferred`, `superseded`, `stale`,
or `unknown`. Conflict risk values are limited to `none`, `possible`,
`blocking`, or `unknown`.

## ADR Inventory

| ADR ID | Title | Status | Source path | Source classification | Applicability to current local build | Conflict risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-0001 | Zovark v1.0 foundation | accepted | candidate zip `0001-zovark-v1-0-foundation.md` | candidate predecessor baseline | active | possible | Broad foundation appears compatible with the mesh/proof direction, but source is candidate material until imported or accepted. |
| ADR-0002 | Six-stage pipeline as architectural invariant | accepted | candidate zip `0002-six-stage-pipeline-as-architectural-invariant.md` | candidate predecessor baseline | unknown | possible | Needs semantic mapping to the V3 forward path; do not force a six-stage runtime shape into the current adapter/proof work without review. |
| ADR-0003 | Multi-tenant row-level security as architectural invariant | accepted | candidate zip `0003-multi-tenant-row-level-security-as-architectural-invariant.md` | candidate predecessor baseline | deferred | none | Current local build is proof/Replay/testbed focused and has no live multi-tenant DB requirement. Track before SaaS/runtime work. |
| ADR-0004 | Inference layer abstraction | accepted | candidate zip `0004-inference-layer-abstraction.md` | candidate predecessor baseline | deferred | possible | Compatible with model references and explicit V2 trace metadata, but local build should not introduce live LLM dependencies. |
| ADR-0005 | Tape Recorder as primary marketing wedge | accepted | candidate zip `0005-tape-recorder-as-primary-marketing-wedge.md` | candidate predecessor baseline | active | possible | Tension area. Current language favors deterministic proof package and Replay; avoid reverting to broad tape-recorder marketing claims. |
| ADR-0006 | Data flywheel, opt-in pooled with tenant-first benefits | accepted | candidate zip `0006-data-flywheel-opt-in-pooled-with-tenant-first-benefits.md` | candidate predecessor baseline | deferred | possible | No customer data pooling or outreach should start from the local build path. Requires privacy and customer validation before use. |
| ADR-0007 | Webhook-only ingest | accepted | candidate zip `0007-webhook-only-ingest.md` | candidate predecessor baseline | deferred | possible | Tension area. AlertForge is a synthetic scenario generator, not architecture; ingest contract is future work and should not be assumed webhook-only yet. |
| ADR-0008 | Deployment topology phasing | accepted | candidate zip `0008-deployment-topology-phasing.md` | candidate predecessor baseline | deferred | possible | Local testbed can proceed without deciding cloud/hybrid/air-gap deployment topology. |
| ADR-0009 | Two-model architecture, fast and code | accepted | candidate zip `0009-two-model-architecture-fast-and-code.md` | candidate predecessor baseline | deferred | possible | Tension area. Current work records model identity safely but forbids live LLM calls and raw prompt capture in proof packages. |
| ADR-0010 | Open-source schemas only | accepted | candidate zip `0010-open-source-schemas-only.md` | candidate predecessor baseline | active | possible | Tension area. Current V1/V2 proof-package contracts are explicit, but schema/version source-of-truth needs review before broader schema claims. |
| ADR-0011 | Cloud-first launch, air-gap as later topology | accepted | candidate zip `0011-cloud-first-launch-air-gap-as-later-topology.md` | candidate predecessor baseline | deferred | possible | Tension area and amended by ADR-0038. Offline Replay and customer-instance authority keep air-gap/offline verification relevant. |
| ADR-0012 | Engineering team builds in compressed timeframe with parallel execution | superseded | candidate zip `0012-engineering-team-builds-in-compressed-timeframe-with-paralle.md` | candidate predecessor baseline | superseded | none | Superseded by ADR-0032; do not use for current build planning. |
| ADR-0013 | No paid components in production codebase | accepted | candidate zip `0013-no-paid-components-in-production-codebase.md` | candidate predecessor baseline | active | none | Compatible with local build if dependencies remain explicit and reviewable. |
| ADR-0014 | WASM scope defense-in-depth for pure computation tools only | accepted | candidate zip `0014-wasm-scope-defense-in-depth-for-pure-computation-tools-only.md` | candidate predecessor baseline | deferred | possible | No WASM runtime should be added during local build unless separately scoped. |
| ADR-0015 | Schema-first development | accepted | candidate zip `0015-schema-first-development.md` | candidate predecessor baseline | active | none | Compatible with Proof Package V1/V2 contracts and verifier gates. |
| ADR-0016 | Dead-code zero as PR-level merge gate | accepted | candidate zip `0016-dead-code-zero-as-pr-level-merge-gate.md` | candidate predecessor baseline | active | none | Build hygiene concern; not blocking this docs reconciliation. |
| ADR-0017 | Retired vocabulary list | accepted | candidate zip `0017-retired-vocabulary-list.md` | candidate predecessor baseline | active | possible | Needs review against current docs before customer-facing language. |
| ADR-0018 | 18-month product horizon | accepted | candidate zip `0018-18-month-product-horizon.md` | candidate predecessor baseline | unknown | possible | Product-horizon claims should not steer local build until reconciled with current proof/V2 validation sequence. |
| ADR-0019 | Mesh agent pool concurrent investigation processing | accepted | candidate zip `0019-mesh-agent-pool-concurrent-investigation-processing.md` | candidate predecessor baseline | deferred | possible | Tension area. Current local build should not claim production concurrency or mesh scale before benchmark evidence. |
| ADR-0020 | Tape Recorder replay-grade investigation record | accepted | candidate zip `0020-tape-recorder-replay-grade-investigation-record.md` | candidate predecessor baseline | active | possible | Tension area but mostly aligned with Investigation Trace V1, Proof Package V2, and offline Replay. Needs terminology alignment. |
| ADR-0021 | EDR handover autonomous response with reversibility | accepted | candidate zip `0021-edr-handover-autonomous-response-with-reversibility.md` | candidate predecessor baseline | deferred | possible | Tension area. Current proof packages may record handoff/action evidence, but no live EDR execution or autonomous response is in scope. |
| ADR-0022 | Healer service read-only operational diagnosis | accepted | candidate zip `0022-healer-service-read-only-operational-diagnosis.md` | candidate predecessor baseline | stale | possible | No current local-build path implements a healer service. Reassess before importing. |
| ADR-0023 | Sigma rule generation pipeline | accepted, amended by ADR-0029 | candidate zip `0023-sigma-rule-generation-pipeline.md` | candidate predecessor baseline | deferred | possible | Tension area. Sigma generation is not part of current Proof Package V2 or AlertForge-style validation work. |
| ADR-0024 | SaaS operations, disaster recovery, tenant lifecycle, legal hold | accepted | candidate zip `0024-saas-operations-disaster-recovery-tenant-lifecycle-legal-hol.md` | candidate predecessor baseline | deferred | possible | Relevant before SaaS/control-plane build; not needed for local proof-package testbed. |
| ADR-0025 | Audit chain canonicalization and concurrent insert semantics | accepted | candidate zip `0025-audit-chain-canonicalization-and-concurrent-insert-semantics.md` | candidate predecessor baseline | active | possible | Compatible with deterministic proof and Replay, but concurrent insert behavior is not exercised by static local proof generation. |
| ADR-0026 | Replay compatibility matrix and migration semantics | accepted | candidate zip `0026-replay-compatibility-matrix-and-migration-semantics.md` | candidate predecessor baseline | active | none | Aligned with V1 compatibility and explicit V2 verifier support. |
| ADR-0027 | Verdict determinism canonicalization | accepted | candidate zip `0027-verdict-determinism-canonicalization.md` | candidate predecessor baseline | active | none | Aligned with deterministic verdict handling and V3 adapter hardening. |
| ADR-0028 | Credential vault threat model and runtime authorization | accepted | candidate zip `0028-credential-vault-threat-model-and-runtime-authorization.md` | candidate predecessor baseline | deferred | possible | Blocks live response/runtime authorization work, not local proof package generation. |
| ADR-0029 | Sigma generation FP governance and MVP scope reduction | accepted | candidate zip `0029-sigma-generation-fp-governance-and-mvp-scope-reduction.md` | candidate predecessor baseline | active | possible | Tension area. False-positive reasoning is active in V2; Sigma generation remains deferred. |
| ADR-0030 | Bootstrap acceptance via failing fixture tests | accepted | candidate zip `0030-bootstrap-acceptance-via-failing-fixture-tests.md` | candidate predecessor baseline | active | none | Aligned with V2 static fixture and realistic scenario validation. |
| ADR-0031 | Benchmark provenance and capacity claim policy | accepted | candidate zip `0031-benchmark-provenance-and-capacity-claim-policy.md` | candidate predecessor baseline | active | none | Tension area but aligned. Scale and capacity claims stay forbidden until measured evidence exists. |
| ADR-0032 | Schedule realism supersedes ADR-0012 | accepted | candidate zip `0032-schedule-realism-supersedes-adr-0012.md` | candidate predecessor baseline | active | none | Compatible with current staged PR sequence and guarded scope. |
| ADR-0033 | Open standards and schema registry | accepted | candidate zip `0033-open-standards-and-schema-registry.md` | candidate predecessor baseline | deferred | possible | Tension area. Current V2 contract exists, but broader schema registry behavior is not implemented. |
| ADR-0034 | Tenant DEK rotation policy | accepted | candidate zip `0034-tenant-dek-rotation-policy.md` | candidate predecessor baseline | deferred | possible | Relevant to future key/customer-instance work, not current local proof-package build. |
| ADR-0035 | Open-source on-call and paging stack | accepted | candidate zip `0035-open-source-on-call-and-paging-stack.md` | candidate predecessor baseline | deferred | possible | Tension area. No on-call/paging stack should be added before product runtime exists. |
| ADR-0036 | Open-source schema boundary | accepted | recovered older uploaded/session architecture material | recovered predecessor baseline material | active | possible | Not imported as current repo ADR source of truth. Constrains canonical schema licensing, OCSF normalization, schema registry work, proof-package evidence schemas, Replay compatibility, customer evidence exports, and future SIEM/EDR mappings. |
| ADR-0037 | Feature lifecycle and dead-code housekeeping | accepted | recovered older uploaded/session architecture material | recovered predecessor baseline material | active | possible | Not imported as current repo ADR source of truth. Requires durable `F-NNN` feature IDs and lifecycle state before new local testbed CLI, AlertForge ingest, benchmark harness, product component, feature flag, service, or schema work. |
| ADR-0038 | Control Plane and Customer-Instance Authority Boundary | proposed | current visible ADR `0038-control-plane-and-customer-instance-authority-boundary.md` | current visible ADR | deferred | possible | Boundary is relevant before live control-plane work. Local proof/replay build should keep customer-data authority local. |
| ADR-0039 | Update Factory and Signed Bundle Distribution | proposed | current visible ADR `0039-update-factory-and-signed-bundle-distribution.md` | current visible ADR | deferred | possible | Signing, bundles, SLSA, and in-toto remain out of scope for the local proof build. |
| ADR-0040 | Research Pipeline and Gated Candidate Promotion | proposed | current visible ADR `0040-research-pipeline-and-gated-candidate-promotion.md` | current visible ADR | deferred | possible | Supports the rule that AlertForge outputs and candidate artifacts are not automatically architecture or runtime truth. |
| ADR-0041 | Telemetry Boundary | proposed | current visible ADR `0041-telemetry-boundary.md` | current visible ADR | deferred | possible | Do not add telemetry or outbound reporting during local build without a scoped decision. |
| ADR-0042 | Cryptographic Key Management | proposed | current visible ADR `0042-cryptographic-key-management.md` | current visible ADR | deferred | possible | Blocks key-management/signing claims, not offline proof-package generation. |
| ADR-0043 | Open-Source Release Strategy | proposed strategic pivot | current visible ADR `0043-open-source-release-strategy.md` | current visible ADR | deferred | possible | Requires founder/counsel sign-off before release-positioning decisions. Not a local-build blocker. |
| ADR-0044 | Disaster Recovery & Business Continuity | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | unknown | Not part of the current visible repo ADR set. Must be reconciled before use as active architecture. |
| ADR-0045 | Customer Offboarding, GDPR Article 17, and Legal Hold | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | unknown | Not part of the current visible repo ADR set. Must be reconciled before use as active architecture. |
| ADR-0046 | Deterministic Verdict Canonicalization | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Likely overlaps current deterministic verdict and Replay direction, but must be reconciled before claiming compliance. |
| ADR-0047 | Replay Compatibility Matrix and Failure Modes | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Likely overlaps V1/V2 verifier compatibility work, but must be reconciled before being treated as active source of truth. |
| ADR-0048 | Healer Runtime Defense-in-Depth | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Runtime healer work is not implemented in the current proof-package path; reconcile before runtime claims. |
| ADR-0049 | Sigma Alert-Budget Governance | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Sigma generation and alert-budget governance remain outside the current local proof/Replay path. |
| ADR-0050 | On-Call, Paging, and Vendor-Compromise Incident Response | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Operational on-call, paging, and vendor-compromise incident response are not current local-build work. |
| ADR-0051 | Calendar Reconciliation | recovered | older `v3.2.4.3` architecture material | recovered older patch material | unknown | possible | Older material says this supersedes `ADR-0012` and `ADR-0032`; do not apply that supersession until reconciled. |

## Likely Tension Areas

The following ADRs need special attention before they are treated as binding for
local product/testbed work:

- `ADR-0005` Tape Recorder as primary marketing wedge: current architecture is
  proof-package and offline Replay centered. Marketing language must stay bounded.
- `ADR-0007` Webhook-only ingest: AlertForge is a synthetic scenario generator,
  not the Zovark architecture. The ingest contract remains future work.
- `ADR-0009` Two-model architecture, fast and code: current proof packages may
  preserve safe model metadata, but no raw prompts, live LLM calls, or hidden
  reasoning capture are allowed.
- `ADR-0010` Open-source schemas only: V1/V2 contracts exist, but broader schema
  registry obligations remain unreconciled.
- `ADR-0011` Cloud-first launch, air-gap later: current offline Replay and
  customer-instance authority boundaries keep offline verification important.
- `ADR-0019` Mesh agent pool concurrent investigation processing: no concurrency
  or capacity claim should be made before benchmark evidence exists.
- `ADR-0020` Tape Recorder replay-grade investigation record: likely aligned with
  Investigation Trace V1 and Proof Package V2, but terminology must be reconciled.
- `ADR-0021` EDR handover autonomous response with reversibility: proof packages
  may record action evidence; live EDR execution remains out of scope.
- `ADR-0023` and `ADR-0029` Sigma rule generation and FP governance: V2
  false-positive reasoning is active; Sigma generation remains deferred.
- `ADR-0031` Benchmark provenance and capacity claim policy: capacity claims are
  forbidden until measured and provenance-backed.
- `ADR-0033` Open standards and schema registry: broader registry behavior is not
  implemented.
- `ADR-0035` Open-source on-call and paging stack: operational paging is not part
  of the current local build path.
- `ADR-0036` Open-source schema boundary: local build, schema registry,
  proof-package evidence, Replay compatibility, customer export, OCSF, and
  SIEM/EDR mapping work must not make vendor/proprietary schemas canonical.
- `ADR-0037` Feature lifecycle and dead-code housekeeping: any new CLI, service,
  feature flag, schema, benchmark harness, AlertForge ingest path, or product
  component needs feature-registry/lifecycle alignment before implementation.
- Context Compaction Memory contracts: architecture/contracts-only schema work
  should remain non-runtime until feature lifecycle alignment is performed for
  any future storage or retrieval implementation.
- `ADR-0044` through `ADR-0051`: recovered older `v3.2.4.3` material may contain
  relevant later decisions, but none are current active source of truth until
  reconciled.

## Build-Readiness Verdict

Local testbed build should not start until this ADR recovery correction is
reviewed and merged. After this correction, narrow local testbed work can proceed
only if it stays inside the current implemented proof-package boundary:

- generate V1 or explicit V2 proof packages from static or sanitized V3-like
  inputs
- verify packages with offline Replay
- preserve V1 default as V1-only
- prevent raw prompt, tool argument, tool output, payload, message, note, and
  hidden-reasoning leakage
- keep AlertForge as an upstream synthetic scenario generator, not architecture
- respect `ADR-0036` schema-boundary constraints
- respect `ADR-0037` feature-lifecycle discipline
- make no claim of full compliance with recovered `ADR-0044` through `ADR-0051`
- make no live control plane, telemetry, Vault, signing, legal, compliance,
  customer, or benchmark claims

Recovered ADRs that block full architecture sync until reconciled:

- `ADR-0036`: recovered, not imported/reconciled as current source of truth
- `ADR-0037`: recovered, not imported/reconciled as current source of truth
- `ADR-0044` through `ADR-0051`: recovered older patch material, not active
  current source of truth until classified against current repo direction

Blocking or deferred for specific future work:

- `ADR-0028`, `ADR-0038`, `ADR-0041`, and `ADR-0042` before live control-plane,
  telemetry, Vault, key-management, signing, or customer-instance enforcement
  work.
- `ADR-0039` before update factory, signed bundles, SLSA, in-toto, or anchoring
  work.
- `ADR-0021` before live EDR response execution.
- `ADR-0023`, `ADR-0029`, and `ADR-0033` before Sigma generation or broader
  schema-registry work.

Non-blocking but tracked for the local testbed:

- `ADR-0005`, `ADR-0020`, and `ADR-0030` because they are broadly aligned with
  proof/replay/test fixtures but need vocabulary discipline.
- `ADR-0007` because ingest remains a future contract and AlertForge must not be
  treated as Zovark architecture.
- `ADR-0019` and `ADR-0031` because local validation cannot become scale or
  capacity marketing.
- `ADR-0035` because on-call/paging is operational product work, not proof-package
  testbed work.

Forbidden claims until benchmark evidence exists:

- enterprise-scale ingestion support
- v4.1 scale target achievement
- production p95 or p99 latency
- production throughput or concurrency readiness
- customer-readiness or outreach readiness
- legal admissibility
- compliance certification
- signed/anchored provenance
- forensic completeness

## Future Reconciliation Work

Before implementation touching schemas, external mappings, feature flags, CLIs,
services, adapters, AlertForge ingest, benchmark harnesses, or customer
artifacts:

- check `ADR-0036` schema boundary
- check `ADR-0037` feature lifecycle
- classify `ADR-0044` through `ADR-0051` as `active`, `deferred`,
  `superseded`, `stale`, or `unknown` against current v4.1/current repo
  direction
- decide whether recovered ADR files should be imported into the repo as
  historical ADRs, current ADRs, or appendix/source material

The architecture must continue to state that it is not fully ADR-synced until
the recovered `ADR-0036` through `ADR-0051` material is imported/reconciled or
explicitly classified as historical, deferred, superseded, stale, or
non-authoritative.

The current safety constraints remain unchanged:

- V1 default remains V1-only
- V2 generation remains explicit
- Replay verification remains offline
- raw prompts, tool arguments, tool outputs, payloads, messages, notes, and
  hidden reasoning must not be emitted
- evidence must not be invented
- unsupported benchmark, customer, legal, compliance, or signing claims remain
  forbidden
