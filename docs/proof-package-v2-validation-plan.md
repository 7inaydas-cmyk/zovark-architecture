# Proof Package V2 Validation Plan

Status: docs-only validation plan. This document does not implement Proof Package
V2, change Proof Package V1, modify the verifier, alter the V3 adapter, or add
tests.

## Purpose

This plan defines the validation sequence required before Proof Package V2 is used
in customer discovery. V2 must remain deterministic, V1-compatible, and bounded by
recorded evidence.

## Validation Sequence

### Phase 1: V2 Static Fixture Validation

Goal: prove that the V2 object model can represent realistic incident packages
without live systems.

Inputs:

- sanitized static V3 fixture shapes
- current V1 generated proof package outputs
- documented V3 fixture gaps
- expected V2 objects from `docs/proof-package-v2-contract.md`

Checks:

- every required V2 object is present or has `status: unavailable` plus
  `data_unavailable_reason`
- conditional objects are present when their triggering condition is present
- evidence refs resolve to V1 evidence IDs or documented V3 trace refs
- no raw model chain-of-thought is present
- raw system prompts are not exported by default
- prompt/model identity uses hashes, versions, model refs, fingerprints, or
  redacted references
- compliance mappings are versioned mappings, not certifications
- V1 package verification still passes independently

Exit criteria:

- at least one deterministic tools scenario validates
- at least one LLM-selected tools scenario validates if fixture data exists
- at least one sandbox fallback or explicit sandbox scenario validates if fixture
  data exists
- unavailable fields are explicit and deterministic

### Phase 2: V2 Verifier Skeleton In Later PR

Goal: add fail-closed verifier support for V2 package shape.

Required verifier behavior:

- detect package version
- continue verifying V1 packages
- reject malformed V2 packages
- reject missing required V2 objects
- reject conditional-object omissions when trigger evidence exists
- verify object hashes after canonical serialization
- verify refs into V1 evidence and V2 trace/capability objects
- verify `null` plus `data_unavailable_reason` for unavailable values
- avoid live EDR, SIEM, LLM, DB, network, dispatcher, Vault runtime, or external
  calls

Non-goals:

- signing
- external anchoring
- transparency logs
- compliance certification
- legal admissibility claims

### Phase 3: V3 Adapter Population PRs

Goal: populate V2 objects from V3 fixture or runtime output without hiding gaps.

Required adapter behavior:

- preserve V1 package generation and verification
- populate V2 objects only from recorded V3 data or deterministic synthesis
- use `null` plus `data_unavailable_reason` for missing V3 data
- preserve execution-path distinctions:
  - deterministic tools
  - LLM-selected tools
  - sandbox fallback
  - explicit sandbox mode
- preserve prompt/model/code/sandbox identity where available
- avoid adding raw chain-of-thought or raw system prompts by default

Exit criteria:

- generated V2 package verifies with the V2 verifier skeleton
- V1 verifier still accepts the V1 package path
- deterministic outputs are byte-stable across repeated runs

### Phase 4: AlertForge Or Realistic Scenario Validation

Goal: validate V2 package content against realistic practitioner scenarios before
customer outreach.

Scenario coverage:

- malicious alert with deterministic saved-plan path
- malicious or suspicious alert requiring LLM-selected tools
- benign or false-positive scenario requiring explicit rejection reasoning
- sandbox fallback or explicit sandbox scenario if represented by V3 data
- visibility-gap scenario where important telemetry is unavailable
- approval-required scenario
- scenario with customer-supplied controls unavailable

Checks:

- `decision_rationale` cites evidence IDs
- `false_positive_reasoning` exists when relevant
- `context_enrichment` distinguishes recorded context from unavailable live lookup
- `visibility_gaps` are visible and bounded
- `approval_record` matches handoff/governance evidence
- `blast_radius` is present when action or impact language exists
- `rollback_plan` is present when response action is proposed
- `compliance_mapping` is versioned and labeled as mapping only
- `controls_in_place_at_incident` is customer-supplied or explicitly unavailable
- `customer_report_v2` remains bounded and does not overclaim

Exit criteria:

- realistic scenarios pass deterministic verification
- limitations are visible in the customer-readable report
- no legal, certification, SLSA, signing, external anchoring, or forensic
  completeness claims appear

### Phase 5: Customer-Readiness Package

Goal: prepare a bounded package for customer discovery only after validation passes.

Customer-readiness requirements:

- label V1 current behavior and V2 validated behavior separately
- include verifier success output and a tamper/failure example
- show at least one realistic scenario package
- include limitations and visibility gaps
- avoid claims of legal admissibility, compliance certification, signing, external
  anchoring, or complete evidence collection

Gate:

- customer outreach using Proof Package V2 language starts only after realistic
  scenario validation passes and the readiness package distinguishes implemented
  behavior from planned behavior.

## Required Future PR Boundaries

1. V2 static fixtures and fixture validation.
2. V2 verifier skeleton.
3. V3 adapter population for V2 objects.
4. AlertForge or realistic scenario validation.
5. Customer-readiness package.

Each PR should preserve V1 compatibility and keep replay offline.
