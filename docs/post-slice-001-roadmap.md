# Post-Slice 001 Roadmap

Status: planning note, docs-only.

Slice 001 is the deterministic proof-package baseline. The next work should
extend verification and investigation semantics without destabilizing that
baseline.

## Baseline To Freeze

Slice 001 is complete when the README/sample finalization is merged and the
current validation suite remains green.

The frozen Slice 001 contract is:

- static input sample
- deterministic local CLI
- no live EDR
- no live LLM
- no network calls
- no database
- no dispatcher
- no autonomous response
- proof package containing the current nine documented output files

This baseline should be treated as the proof spine for later work.

## Phase 0: Architecture Reconciliation

Type: docs only.

Purpose:

- Compare the v4.1 autonomous investigation mesh with Slice 001.
- Classify what was preserved, deferred, under-specified, or intentionally out
  of scope.
- Prevent future PRs from confusing proof-package scope with full runtime scope.

Allowed files:

- `docs/architecture-reconciliation-v4-1-to-slice-001.md`
- `docs/post-slice-001-roadmap.md`

No code, schema, runtime, or artifact contract changes belong in this phase.

## Phase 1: Slice 001 Freeze

Type: release hygiene.

Purpose:

- Mark Slice 001 as the stable local proof-package baseline.
- Record the validation commands and expected artifact set.
- Keep the package contract unchanged until a separate spec change explicitly
  changes it.

Do not add Replay V2, AI Investigation Trace, or runtime integrations during
the freeze.

## Phase 2: Replay V2 Package Verifier

Type: code, still local and deterministic.

Goal:

```text
Given only the exported proof-package directory, verify the package offline.
```

Initial scope:

- Verify the expected output file set.
- Parse all JSON artifacts.
- Recompute evidence hashes from `raw_content`.
- Resolve timeline and finding evidence references.
- Recompute the verdict.
- Recompute the handoff.
- Recompute the audit entry.
- Recompute the replay report.
- Fail closed on tampering or missing artifacts.

Initial non-goals:

- no manifest file
- no provenance file
- no signing
- no transparency log
- no live EDR
- no LLM or tool calls
- no network calls
- no schema expansion unless the verifier requires a documented spec change

## Phase 3: Replay Detail Expansion

Type: code and schema only if explicitly approved.

Purpose:

- Add typed verification failure reasons.
- Add a customer-readable verification summary.
- Make replay mismatch reasons clearer without changing the product into a
  forensic-completeness claim.

Do not introduce legal admissibility, certification, SLSA, or complete-evidence
claims.

## Phase 4: Manifest And Provenance

Type: package contract evolution.

Purpose:

- Add artifact hashes.
- Add verifier version.
- Add rule/spec/code pins.
- Add deterministic package metadata.

This phase should happen only after the package verifier contract is stable. It
should be proposed as an explicit package-contract change.

## Phase 5: AI Investigation Trace V1

Type: spec first, then code.

Purpose:

- Restore the investigation body without weakening replay.
- Record model and tool inputs/outputs through existing hooks.
- Separate candidate findings from accepted and rejected findings.
- Preserve deterministic accept/reject logic after non-deterministic model or
  tool output has been recorded.

Likely concepts:

- model invocation record
- tool call record
- investigation trace
- hypothesis record
- candidate finding
- accepted finding
- rejected finding

The governing rule:

```text
Model or tool output may propose. Deterministic synthesis accepts or rejects.
Replay verifies recorded outputs; it does not call live models or tools.
```

## Phase 6: Fast Mode And Reasoning Mode

Type: product-mode design after trace semantics exist.

Fast Mode should mean quick triage over recorded and bounded evidence.

Reasoning Mode should mean deeper hypothesis testing, correlation, and
contradiction checks over recorded and bounded evidence.

Do not implement either mode as an unrecorded black-box LLM path.

## Phase 7: Harness And Inference Gateway MVP

Type: runtime architecture.

Purpose:

- Introduce the Harness around trace and synthesis semantics.
- Add Inference Gateway only after recorded invocation contracts are stable.
- Preserve no-live-call replay semantics.
- Add egress policy before any cloud model provider path.

This is where local model runtime, cloud routing, fallback behavior, and model
version pinning become operational concerns.

## Phase 8: Runtime And Enterprise Platform

Type: later platform work.

Candidate scope:

- live EDR connectors
- SIEM ingestion
- action adapters
- Vault runtime authorization
- dispatcher
- deployment profiles
- observability
- WORM or HSM-backed evidence services

These should not be built before package verification and investigation trace
semantics are stable.

## PR Sequence

Recommended sequence after Slice 001:

1. Docs-only architecture reconciliation.
2. Slice 001 freeze marker or release note.
3. Replay V2 package verifier for the existing package contract.
4. Replay V2 verification details.
5. Manifest/provenance package-contract proposal.
6. AI Investigation Trace V1 spec.
7. AI Investigation Trace V1 implementation.
8. Fast Mode and Reasoning Mode product-mode design.
9. Harness and Inference Gateway MVP.
10. Live integrations and enterprise runtime.

Every step should preserve the rule that proof and replay semantics are defined
before runtime breadth is added.
