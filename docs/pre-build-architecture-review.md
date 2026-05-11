# Pre-Build Architecture Review

Status: pre-build review/audit. This document does not implement runtime code,
change adapter or verifier behavior, add live integrations, create customer
readiness material, start outreach, add benchmarks, or make legal,
certification, signing, anchoring, SLSA, or in-toto claims.

## Purpose

This review captures the completed Zovark architecture, Proof Package V2, Replay
verification, V3 adapter, and realistic validation work before local
product/testbed implementation starts.

The current repository is ready for proof-package and adapter-level validation.
It is not yet a runnable local Zovark product/testbed.

## Completed PR Sequence

| PR | Final status | Main output |
| --- | --- | --- |
| #23 | Merged | Replay V2 verification failure taxonomy and customer-readable failure framing. |
| #24 | Merged | Customer-readable verification summary for verifier success and failure output. |
| #25 | Merged | V3 ground-truth check establishing V3 tools mode as default and V2 sandbox/codegen as legacy/fallback. |
| #26 | Merged | ADR index and architecture constraints before V3 absorption work. |
| #27 | Merged | V3 asset inventory and V3-to-v4 domain map grounded in current repository and older runtime evidence. |
| #28 | Merged | V3 fixture capture report before Capability Identity, Trace, and adapter work. |
| #29 | Merged | Capability Identity Contract, final architecture synthesis, implementation sequence, and stale-doc cleanup plan. |
| #30 | Merged | Investigation Trace V1 documentation/spec. |
| #31 | Merged | First V3 fixture-to-proof-package adapter for the existing V1 package contract. |
| #32 | Merged | End-to-end verification that V3-generated V1 proof packages pass Replay V2. |
| #33 | Merged | Narrow pre-discovery docs coherence patch. |
| #34 | Merged | Practitioner Proof Package V2 requirements, V2 contract, and V2 validation plan. |
| #35 | Merged | Proof Package V2 verifier skeleton with explicit version recognition, derived conditions, source-ref resolution, and fail-closed validation. |
| #36 | Merged | Committed static Proof Package V2 fixture validation under `tests/fixtures`. |
| #37 | Merged | Explicit V2 adapter population for `decision_rationale` and `false_positive_reasoning`. |
| #38 | Merged | Explicit V2 adapter population for `context_enrichment` and `visibility_gaps`. |
| #39 | Merged | Explicit V2 adapter population for `approval_record`, `blast_radius`, and `rollback_plan`. |
| #40 | Merged | Explicit V2 adapter population for `compliance_mapping` and `controls_in_place_at_incident`. |
| #41 | Merged | Explicit V2 adapter population and restructuring for `customer_report_v2`. |
| #42 | Merged | Safe V2 trace/context metadata preservation with prompt, tool summary, and nested trace value sanitization. |
| #43 | Merged | Static AlertForge-style realistic scenario validation for generated V2 proof packages. |

## Locked Architecture Decisions

The following decisions are now stable inputs for local implementation unless a
future scoped PR explicitly reopens them:

- Architecture default is Option 2: V3 forward, Slice proof absorbed.
- Slice 001/Proof Package V1 remains the current deterministic nine-file package.
- Proof Package V2 is explicitly versioned as `proof-package-v2/0.1` and is not a
  silent mutation of V1.
- Default V3 adapter generation remains V1-only.
- V2 generation is explicit via `proof_package_version=V2_PACKAGE_CONTRACT`.
- Replay verification is offline and never calls live EDR, SIEM, LLM, DB,
  network, dispatcher, Vault, or external services.
- V2 conditional requirements are derived from verified package evidence, not
  marker booleans.
- V2 `source_refs` must resolve to a trusted reference index derived from
  already-verified V1 evidence.
- Required V2 objects cannot be satisfied by `status: not_applicable`, empty
  `source_refs`, or fabricated references.
- Raw prompts, raw tool arguments, raw tool outputs, payload bodies, messages,
  notes, hidden reasoning, and chain-of-thought must not be emitted by V2 trace
  context.
- Compliance mappings are bounded mappings only. They are not compliance
  certification, legal conclusions, or legal admissibility claims.
- `customer_report_v2` must not self-attest verification at generation time.

## ADR Coverage Status

PR #44 considered the active root ADR index and the major locked architecture
decisions that govern the pre-build proof, replay, adapter, V2, and realistic
validation path.

PR #44 did not perform a complete semantic review of all predecessor baseline ADRs
`ADR-0001` through `ADR-0037`. Current repo metadata records the expected
post-apply baseline count as 43 ADRs, not 46, unless another external ADR source
is later provided.

This repo snapshot visibly ships `ADR-0038` through `ADR-0043`. `ADR-0001`
through `ADR-0037` remain predecessor-baseline material pending post-apply
verification.

### Current ADRs Explicitly Visible In This Repo

- `ADR-0038` Control Plane and Customer-Instance Authority Boundary
- `ADR-0039` Update Factory and Signed Bundle Distribution
- `ADR-0040` Research Pipeline and Gated Candidate Promotion
- `ADR-0041` Telemetry Boundary
- `ADR-0042` Cryptographic Key Management
- `ADR-0043` Open-Source Release Strategy

### Baseline ADR Placeholders Tracked By The Cross-Link Script

- `ADR-0011`
- `ADR-0024`
- `ADR-0025`
- `ADR-0027`
- `ADR-0028`
- `ADR-0030`
- `ADR-0031`
- `ADR-0034`

### ADR Review Limitation

`scripts/check_adr_cross_links.py` passing in bootstrap mode proves structural
cross-link presence. It does not prove full semantic consistency of every
predecessor ADR.

Do not claim all ADRs were reviewed until the full baseline ADR files are present
or explicitly imported.

### Build-Readiness Implication

Before local product/testbed build, perform an ADR-by-ADR applicability review if
the predecessor ADR set is available. Classify each ADR as:

- active for current local build
- deferred
- superseded
- stale
- unknown / source missing

## Implemented Pieces

| Area | Implemented now | Primary files |
| --- | --- | --- |
| Deterministic V1 proof package | Static input to nine-file proof package. | `zovark/slice001/cli.py`, `zovark/slice001/writer.py`, `zovark/slice001/*` |
| Replay V2 verifier | Offline V1 and V2 package verification. | `zovark/slice001/package_verifier.py` |
| V3 fixture adapter | Representative V3 fixture shape to V1 or explicit V2 package. | `zovark/slice001/v3_adapter.py` |
| V2 verifier skeleton | Version-aware V2 marker validation, required/conditional object checks, condition derivation, source-ref resolution. | `zovark/slice001/package_verifier.py`, `tests/test_package_verifier.py` |
| V2 adapter population | Practitioner object population for the V2 object set currently supported by the adapter. | `zovark/slice001/v3_adapter.py`, `tests/test_v3_adapter.py` |
| Static V2 fixture | Durable V2 fixture under test fixtures. | `tests/fixtures/proof-package-v2/response-action/` |
| Realistic static scenario validation | AlertForge-style V3-like scenario generates and verifies V2 output. | `tests/fixtures/v3-realistic-scenarios/`, `tests/test_v2_realistic_scenario_validation.py` |

## Documented But Not Implemented As Runtime

| Area | Current state | Notes |
| --- | --- | --- |
| Capability Identity Contract | Documented contract. | No first-class runtime Capability Identity objects are emitted by current generated packages. |
| Investigation Trace V1 | Documented trace specification. | Current adapter preserves safe V2 trace/context metadata, but does not emit first-class Trace V1 records. |
| Final architecture synthesis | Documented architecture default and boundaries. | It is a planning artifact, not a release tag or runtime freeze. |
| Stale-doc cleanup plan | Documented plan. | Cleanup execution remains separate and has not been performed here. |
| Proof Package V2 contract and validation plan | Documented and partially implemented through verifier/adapter/tests. | The docs still contain some future-looking language from before PRs #35-#43. |

## Future-Looking Or Deferred Pieces

- Local product/testbed implementation around V3 runtime execution.
- AlertForge ingestion integration.
- Live SIEM/EDR connectors.
- Live LLM/tool runtime integration.
- Product API/dashboard workflow.
- Production installation workflow.
- Benchmarks and scale measurements for the local product path.
- Customer-readiness bundle.
- Customer outreach.
- Signing, manifest/provenance, anchoring, SLSA, in-toto, or legal evidence
  packaging.
- Compliance certification or legal admissibility claims.

## Stale Or Risky Assumptions

- Some docs written before PRs #35-#43 still describe V2 verifier and adapter
  population as future work. Current code now implements a V2 verifier skeleton,
  V2 adapter population, and realistic static validation, but those docs were not
  fully rewritten.
- No validated customer signals are recorded in the architecture docs.
- Current V3 scale evidence remains benchmark/lab evidence and does not support
  enterprise ingestion claims.
- Current adapter consumes representative fixture shapes, not live V3 runtime
  records from the older product repo.
- Realistic scenario validation is a static fixture gate, not a live AlertForge
  integration.
- AlertForge output schema is not yet a committed integration contract.
- The local repo has no product runner that chains AlertForge -> ingest -> V3
  investigation -> V2 package -> verifier outside tests.
- V2 `customer_report_v2` is generated inside `proof-package-v2.json`, while the
  V1 `customer-report.md` remains the nine-file package Markdown artifact.
- Proof Package V2 is verified for structural and deterministic consistency, not
  upstream evidence completeness.
- Full predecessor ADR baseline reconciliation is not complete.

## Build Readiness Verdict

The repo is ready for a narrow local build that exercises the existing Slice 001
CLI, the V3 fixture adapter Python API, and Replay verification against static
fixtures.

The repo is not yet ready for a full local Zovark product/testbed run. Before
that, the project needs an explicit local workflow, an AlertForge fixture/output
contract, and a product-level command or script that drives the implemented
proof path without relying on ad hoc test helpers. It also needs predecessor ADR
baseline reconciliation if the full ADR source set is available.
