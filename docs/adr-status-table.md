# ADR Status Table

Status: ADR status summary. This document does not import ADR files, claim full
ADR sync, or make recovered ADR material automatically authoritative.

## Source Classification

The current repo visibly carries `ADR-0038` through `ADR-0043` in the patch tree
plus the v3.2.4.4 `ADR-0009` amendment and proposed `ADR-0052` positioning ADR
under `architecture/adr/`.
`ADR-0001` through `ADR-0035` are candidate predecessor baseline material.
`ADR-0036` and `ADR-0037` are recovered predecessor baseline constraints.
`ADR-0044` through `ADR-0051` are recovered older material and are not
automatically active current source of truth until reconciled.

## ADR Table

| ADR ID | Title | Source | Status | Applies to current build | Authority | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| ADR-0001 | Zovark v1.0 foundation | Candidate predecessor baseline material | accepted in candidate source | unknown | candidate historical | Not imported as canonical current ADR file. |
| ADR-0002 | Six-stage pipeline as architectural invariant | Candidate predecessor baseline material | accepted in candidate source | unknown | candidate historical | Needs mapping to current fixture/proof path before runtime claims. |
| ADR-0003 | Multi-tenant row-level security as architectural invariant | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No live multi-tenant DB exists in current repo. |
| ADR-0004 | Inference layer abstraction | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No live LLM runtime exists in current repo. |
| ADR-0005 | Tape Recorder as primary marketing wedge | Candidate predecessor baseline material | accepted in candidate source | partial | candidate historical | Current language should stay proof/Replay bounded. |
| ADR-0006 | Data flywheel, opt-in pooled with tenant-first benefits | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No customer data pooling exists. |
| ADR-0007 | Webhook-only ingest | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | AlertForge ingest contract is future work. |
| ADR-0008 | Deployment topology phasing | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No production deployment topology is implemented. |
| ADR-0009 | Two-model architecture, fast and code | Candidate predecessor baseline material plus v3.2.4.4 amendment | accepted in candidate source; amended | active constraint | recovered amendment, not runtime implementation | RamaLama is named for planned local-SLM runtime architecture. Local-only and hybrid RamaLama inference are approved target topology choices only after runtime implementation, operator controls, and validation; they are not current customer-selectable runtime capabilities. |
| ADR-0010 | Open-source schemas only | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Aligns with ADR-0036 schema boundary. |
| ADR-0011 | Cloud-first launch, air-gap as later topology | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | Amended by visible ADR-0038 boundary; reconcile before runtime topology. |
| ADR-0012 | Engineering team builds in compressed timeframe with parallel execution | Candidate predecessor baseline material | superseded in candidate source | no | candidate historical | Do not use for current build planning. |
| ADR-0013 | No paid components in production codebase | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Dependency policy concern, not runtime proof. |
| ADR-0014 | WASM scope defense-in-depth for pure computation tools only | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No WASM runtime is implemented. |
| ADR-0015 | Schema-first development | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Supports explicit contracts and validation. |
| ADR-0016 | Dead-code zero as PR-level merge gate | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Supports scoped changes and no unused runtime skeletons. |
| ADR-0017 | Retired vocabulary list | Candidate predecessor baseline material | accepted in candidate source | unknown | candidate historical | Needs review before customer-facing language. |
| ADR-0018 | Product horizon | Candidate predecessor baseline material | accepted in candidate source | unknown | candidate historical | Do not use for readiness claims. |
| ADR-0019 | Mesh agent pool concurrent investigation processing | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No mesh runtime or scale claim exists. |
| ADR-0020 | Tape Recorder replay-grade investigation record | Candidate predecessor baseline material | accepted in candidate source | partial | candidate historical | Aligns conceptually with proof/Replay, but terminology needs reconciliation. |
| ADR-0021 | EDR handover autonomous response with reversibility | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No live EDR execution exists. |
| ADR-0022 | Healer service read-only operational diagnosis | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No healer runtime exists. |
| ADR-0023 | Sigma rule generation pipeline | Candidate predecessor baseline material | amended in candidate source | deferred | candidate historical | Sigma generation is not current scope. |
| ADR-0024 | SaaS operations, disaster recovery, tenant lifecycle, legal hold | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | Reconcile before SaaS/control-plane work. |
| ADR-0025 | Audit chain canonicalization and concurrent insert semantics | Candidate predecessor baseline material | accepted in candidate source | partial | candidate historical | Current proof artifacts are deterministic; concurrent runtime insert behavior is not implemented. |
| ADR-0026 | Replay compatibility matrix and migration semantics | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Aligns with offline Replay compatibility work. |
| ADR-0027 | Verdict determinism canonicalization | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Aligns with deterministic verifier behavior. |
| ADR-0028 | Credential vault threat model and runtime authorization | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No Vault/runtime authorization exists. |
| ADR-0029 | Sigma generation FP governance and MVP scope reduction | Candidate predecessor baseline material | accepted in candidate source | partial | candidate historical | False-positive reasoning exists; Sigma generation does not. |
| ADR-0030 | Bootstrap acceptance via failing fixture tests | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Aligns with static and realistic fixture validation. |
| ADR-0031 | Benchmark provenance and capacity claim policy | Candidate predecessor baseline material | accepted in candidate source | active constraint | candidate historical | Benchmark/customer claims remain forbidden without evidence. |
| ADR-0032 | Schedule realism supersedes ADR-0012 | Candidate predecessor baseline material | accepted in candidate source | partial | candidate historical | Older recovered material may supersede this through ADR-0051; do not apply silently. |
| ADR-0033 | Open standards and schema registry | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | Broader schema registry is not implemented. |
| ADR-0034 | Tenant DEK rotation policy | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No tenant key-management runtime exists. |
| ADR-0035 | Open-source on-call and paging stack | Candidate predecessor baseline material | accepted in candidate source | deferred | candidate historical | No on-call/paging stack exists. |
| ADR-0036 | Open-source schema boundary | Recovered predecessor baseline material | accepted in recovered source | active constraint | recovered historical, not imported canonical | Canonical Zovark schemas must be source-available; vendor schemas are mapping/export surfaces only. |
| ADR-0037 | Feature lifecycle and dead-code housekeeping | Recovered predecessor baseline material | accepted in recovered source | active constraint | recovered historical, not imported canonical | New product, CLI, schema, service, benchmark, or integration work needs feature-lifecycle alignment. |
| ADR-0038 | Control Plane and Customer-Instance Authority Boundary | Visible current repo/patch ADR | proposed | deferred | current visible patch ADR | Reconcile before live control-plane work. |
| ADR-0039 | Update Factory and Signed Bundle Distribution | Visible current repo/patch ADR | proposed | deferred | current visible patch ADR | Signing, update factory, SLSA, and in-toto remain out of scope. |
| ADR-0040 | Research Pipeline and Gated Candidate Promotion | Visible current repo/patch ADR | proposed | deferred | current visible patch ADR | Supports gated promotion; no research runtime is implemented. |
| ADR-0041 | Telemetry Boundary | Visible current repo/patch ADR | proposed | deferred | current visible patch ADR | No telemetry runtime is implemented. |
| ADR-0042 | Cryptographic Key Management | Visible current repo/patch ADR | proposed | deferred | current visible patch ADR | No key-management runtime is implemented. |
| ADR-0043 | Open-Source Release Strategy | Visible current repo/patch ADR | proposed strategic pivot | deferred | current visible patch ADR | Release positioning remains future governance work. |
| ADR-0044 | Disaster Recovery & Business Continuity | Recovered older material | recovered | unknown | not automatically active | Must be reconciled before use as current source of truth. |
| ADR-0045 | Customer Offboarding, GDPR Article 17, and Legal Hold | Recovered older material | recovered | unknown | not automatically active | Must be reconciled before customer/legal lifecycle claims. |
| ADR-0046 | Deterministic Verdict Canonicalization | Recovered older material | recovered | unknown | not automatically active | Likely overlaps current direction; do not claim compliance until reconciled. |
| ADR-0047 | Replay Compatibility Matrix and Failure Modes | Recovered older material | recovered | unknown | not automatically active | Likely overlaps current direction; do not claim compliance until reconciled. |
| ADR-0048 | Healer Runtime Defense-in-Depth | Recovered older material | recovered | unknown | not automatically active | No healer runtime exists. |
| ADR-0049 | Sigma Alert-Budget Governance | Recovered older material | recovered | unknown | not automatically active | Sigma governance remains future work. |
| ADR-0050 | On-Call, Paging, and Vendor-Compromise Incident Response | Recovered older material | recovered | unknown | not automatically active | No operational paging or vendor-compromise workflow exists. |
| ADR-0051 | Calendar Reconciliation | Recovered older material | recovered | unknown | not automatically active | Older source says it supersedes ADR-0012 and ADR-0032; do not apply silently. |
| ADR-0052 | Deterministic Replay as Primary Differentiator | v3.2.4.4 amendment ADR | proposed | active positioning constraint | proposed current amendment | Deterministic replay and evidence integrity are the primary differentiator; air-gap is a planned regulated-deployment target, not a current supported deployment profile. |

## Current Position

This table is an operational summary, not a canonical ADR import. The
architecture is not fully ADR-synced until recovered material is imported or
explicitly classified as active, deferred, superseded, stale, or
non-authoritative through a scoped governance PR.