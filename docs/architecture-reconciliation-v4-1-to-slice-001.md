# Architecture Reconciliation: v4.1 To Slice 001

Status: planning note, docs-only.

This document reconciles the broader Zovark v4.1 architecture with the current
Slice 001 implementation. It does not supersede
`architecture/source-of-truth.md`, OpenSpec, ADRs, or the Slice 001 specs. Its
purpose is to prevent architecture drift after the deterministic proof-package
slice.

## Working Hierarchy

Use this hierarchy when deciding what belongs in which slice:

1. Product thesis: Zovark is the proof-first AI investigation layer for
   high-stakes SOC response.
2. Full architecture baseline: the v4.1 autonomous investigation mesh.
3. Current implementation baseline: Slice 001 deterministic proof-package CLI.
4. Near-term wedge: offline verification of the exported proof package.
5. Next product body: recorded AI and tool investigation traces.
6. Later runtime: live ingestion, Harness, Inference Gateway, action adapters,
   Vault runtime, deployment profiles, and observability.

The practical product frame is:

```text
AI investigates. Deterministic synthesis decides. Humans approve. Zovark proves.
```

The current external wedge remains:

```text
EDR detects. AI investigates. SOC approves. Zovark proves.
```

## What Slice 001 Proved

Slice 001 intentionally narrowed the product to a deterministic local proof
spine:

```text
static EDR JSON
-> evidence ledger
-> investigation tape
-> timeline
-> findings
-> verdict
-> approval-required handoff
-> audit seal
-> replay report
-> proof package
-> CLI
```

This is not the full v4.1 mesh, and it should not be described as one. It is the
minimum proof package that demonstrates the product wedge without live EDR,
live models, network calls, database state, dispatchers, or autonomous response.

## v4.1 Component Classification

| v4.1 component | Slice 001 status | Classification | Next home |
|---|---|---|---|
| Ingestion | Static JSON loader only | Preserved narrowly | Live ingestion later |
| Funnel | Not implemented | Intentionally deferred | Later runtime/platform |
| Threat Intelligence | Not implemented | Intentionally deferred | Later runtime/platform |
| Harness | Replaced by direct local module pipeline | Under-specified for current repo | AI Investigation Trace, then Harness MVP |
| Fact lane | Not implemented | Accidentally absent as a named product concept | AI Investigation Trace V1 |
| Threat lane | Not implemented | Accidentally absent as a named product concept | AI Investigation Trace V1 |
| Deterministic Synthesis Engine | Rule findings and verdict derivation | Preserved narrowly | Expand after trace schema stabilizes |
| Inference Gateway | No runtime; hooks exist through recorded model/tool fields | Intentionally deferred | Harness/Inference Gateway MVP |
| Temporal workflow history | No Temporal runtime | Intentionally deferred | Later runtime/platform |
| Recorded model/tool invocations | `recorded_io` hooks exist; absent in Slice 001 output | Preserved as hooks | AI Investigation Trace V1 |
| Cloud egress policy | Not needed because Slice 001 has no network calls | Intentionally deferred | Inference Gateway |
| Action domain | Approval-required handoff only; no execution | Preserved narrowly | Later action runtime |
| State domain | File artifacts only; no database | Intentionally deferred | Later runtime/platform |
| Replay domain | Replay report exists; package-level verifier absent | Preserved narrowly | Replay V2 |
| Audit chain | Close audit entry exists | Preserved narrowly | Manifest/provenance later |
| Evidence chain | Evidence hashes and raw content exist | Preserved narrowly | Replay V2 and manifest/provenance |
| Signed manifest | Not implemented | Intentionally deferred | Manifest/provenance phase |
| Evidentiary package | Not implemented as a legal services artifact | Intentionally deferred | Later high-trust services |
| Deployment profiles | Not implemented | Intentionally deferred | Later platform work |
| RamaLama/local inference | Not implemented | Intentionally deferred | Harness/Inference Gateway MVP |
| WASM content safety | Not implemented | Intentionally deferred | Later platform work |
| Contract registry | OpenSpec and validators exist; runtime registry absent | Partially preserved | Later contract hardening |
| Semantic invariants | Tests and validators cover Slice 001 invariants | Partially preserved | Later contract tests |
| Replay V2 package verifier | Not implemented | Should become next slice | Slice 002 |
| AI Investigation Trace V1 | Not implemented | Should follow Replay V2 | Slice 003 |
| Fast Mode | Not present as repo terminology | Product-mode language only | After trace and Harness exist |
| Reasoning Mode | Not present as repo terminology | Product-mode language only | After trace and Harness exist |

## What Was Preserved

The current repo preserved the important proof semantics:

- Evidence entries are content-addressed.
- Timeline and finding references resolve to evidence IDs.
- Findings are rule-based in Slice 001.
- Verdicts are deterministic functions of findings and evidence.
- Handoff remains approval-required with pending execution.
- Audit entries seal deterministic snapshots.
- Replay reports fail closed on corruption.
- The output is a deterministic local proof package.

The repo also preserved post-Slice hooks for model/tool work:

- `recorded_io`
- `model_contribution`
- `model_versions_pin`
- `tool_catalog_pin`
- `prompt_hash`
- `response_hash`
- `model_inference`
- `tool_call`
- recorded-output replay with no live model or tool calls

Those hooks should be used for AI Investigation Trace V1 instead of adding a
black-box LLM path.

## What Was Narrowed Intentionally

Slice 001 excludes:

- live EDR ingestion
- live LLM calls
- live tool calls
- network calls
- databases
- dispatchers
- Vault runtime
- RamaLama or other model runtime
- WASM runtime
- autonomous response
- deployment profiles
- observability runtime

These exclusions are part of the proof-spine strategy, not evidence that the
larger architecture was abandoned.

## What Was Under-Specified

The current implementation does not yet provide a first-class investigation
body. The v4.1 Harness, Fact lane, Threat lane, and Inference Gateway concepts
are not expressed as concrete current-repo artifacts beyond the model/tool
recording hooks.

This should be restored deliberately after the proof package can be verified
offline. The first recovery step should be trace schema and deterministic
accept/reject semantics, not live model execution.

## Recommended Restoration Order

1. Finish and freeze Slice 001 as the deterministic proof-package CLI.
2. Build an offline package verifier for the existing proof package.
3. Add replay details and typed verification failure reasons.
4. Add manifest/provenance only after the verifier stabilizes.
5. Add AI Investigation Trace V1 using existing recorded model/tool hooks.
6. Productize Fast Mode and Reasoning Mode only after traces exist.
7. Implement Harness and Inference Gateway only after proof and trace semantics
   are stable.
8. Add live integrations, Vault runtime, action execution, deployment profiles,
   and observability later.

## Non-Goals For The Reconciliation

This reconciliation does not authorize:

- Replay V2 implementation
- manifest or provenance files
- package-level verifier CLI
- replay-report schema changes
- AI Investigation Trace implementation
- Fast Mode or Reasoning Mode implementation
- Harness or Inference Gateway runtime
- RamaLama, WASM, Temporal, Vault, database, Sentry, or dispatcher work
- live EDR or autonomous response

Those require separate scoped PRs.
