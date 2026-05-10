# Final Architecture Synthesis: V3 Forward, Slice Proof Absorbed

Status: architecture synthesis, docs-only. This document does not implement runtime
code, change the proof-package schema, add a V3 adapter, or freeze a release tag.

## Page One

Architecture default: Option 2 is the default. Zovark moves V3 forward and absorbs
the Slice 001/Replay V2 proof spine into that runtime path.

One-line architecture:

```text
V3 investigates, deterministic proof synthesizes and seals, Replay verifies offline.
```

External wedge remains bounded:

```text
EDR detects. AI investigates. SOC approves. Zovark proves.
```

The standalone verifier CLI remains a packaging and wedge option. It is useful for
showing that an exported proof package can be verified offline, but it is not the
full product architecture by itself.

## Scale Target And Current Evidence

The v4.1 architecture target is 10K alerts/sec at ingestion, narrowed by the funnel
to approximately 100 investigation-worthy events/sec. Current V3 repo evidence does
not prove that target.

Scale decision: A is the current truth. The v4.1 10K alerts/sec to approximately
100 investigation-worthy events/sec target is aspirational, not current. Early
customer validation may proceed only with lower-scale environments that fit current
measured V3 throughput. An ingestion/funnel rebuild is required before any
enterprise-scale pilot.

Current measured V3 evidence from the ground-truth and inventory docs:

- About 1.6 alerts/sec submission throughput was observed in V3 benchmark evidence.
- The benchmark snapshot included 164 completed Path A alerts and 416 pending
  alerts.
- 35 novel alerts were still waiting for LLM tool selection on an RTX 3050-class
  setup.
- Saved-plan completed-path evidence is strong for the completed snapshot.
- Full-corpus completion throughput, production p95/p99 latency, and real customer
  validation were not found.

Early-customer scale story:

- Suitable first design partners should be low-volume or saved-plan-heavy.
- Enterprise ingestion-scale claims should not be made from the current evidence.
- If a pilot requires high-volume live ingestion, Track C must measure the actual
  deployed path before any sales or architecture commitment.

## Track Owners

| Track | Owner | Current Responsibility |
| --- | --- | --- |
| Track A: repo and architecture PRs | repo/architecture maintainer | Keep PRs scoped, reviewed, and grounded in repo evidence. |
| Track B: customer discovery | founder/architect | Capture validated customer signals before turning buyer-pain hypotheses into roadmap commitments. |
| Track C: scale story | engineer with V3 runtime access | Measure submission throughput, completion throughput, latency, path mix, and bottlenecks. |

## Customer Signals To Date

No validated customer signals captured yet.

Immediate next action for Track B: conduct SOC manager, CISO, MDR, incident
commander, or senior detection/response engineer discovery conversations using the
current proof package, verifier success output, and tamper/failure output.

Future customer signal entries must use this format:

- role/title:
- company size band:
- conversation date:
- top three reactions verbatim:
- would-they-pay answer:
- where-would-it-live answer:
- what-is-missing answer:

Buyer-pain hypotheses are secondary signals. They are not roadmap commitments until
validated by repeated customer evidence.

## Component Classification

| Component | Classification | Evidence And Boundary |
| --- | --- | --- |
| Slice 001 proof package | built today, contractually defined | Current repo exports the nine-file package and validates deterministic artifacts. |
| Replay V2 package verifier | built today | Current repo verifies existing package directories offline. |
| Customer-readable verifier CLI | built today | Current CLI renders bounded success/failure explanations without changing package artifacts. |
| V3 tool catalog and runner | built today in older runtime, active default there | `Zovark_final` has tool catalog, plans, runner, and `ZOVARK_EXECUTION_MODE=tools` default. |
| V3 saved-plan deterministic path | active default when a plan matches | Strongest V3 benchmark evidence is saved-plan-heavy. |
| V3 LLM-selected tool path | built today in older runtime, evidence incomplete | Code exists; full representative runtime fixture was not captured. |
| V2 sandbox/codegen path | legacy/fallback | Active through explicit `ZOVARK_EXECUTION_MODE=sandbox` and Path D fallback. |
| Path D fallback | legacy/fallback | Test/code evidence exists; full live fallback fixture was not captured. |
| Governance decisions | built today in older runtime | Observe/assist/autonomous behavior exists, but it does not replace Vault authorization. |
| Institutional knowledge lookup | built today in older runtime | Static test evidence exists; production validation not found. |
| Correlation history lookup | built today in older runtime | Static test evidence exists; production validation not found. |
| Capability Identity Contract | contractually defined | Defined in `docs/capability-identity-contract.md`; no runtime code in this PR. |
| Investigation Trace V1 | deferred until next spec work | Must use fixture evidence and this contract; not implemented here. |
| V3-to-proof adapter | deferred until after trace/contract review | First bridge code must preserve path distinctions. |
| Manifest/provenance/signing | deferred | ADRs and roadmap preserve future option; not implemented now. |
| Live EDR/SIEM connectors | deferred until customer pull | No live connector work in this synthesis. |
| Harness/Inference Gateway runtime | partially built in older runtime, future platform work | Keep V3 forward; do not rebuild runtime before trace/proof semantics are stable. |
| RamaLama/local runtime | aspirational or not found in repo evidence | Do not claim current implementation. |
| WASM content safety | aspirational or not found in repo evidence | Do not claim current implementation. |
| v4.1 10K alerts/sec target | aspirational v4.1 target | Current measured evidence does not prove this target. |
| Fast Mode / Reasoning Mode | deferred until customer pull and trace design | Exact names are product-mode language, not current repo runtime terms. |

## Architecture Rule Set

1. V3 forward is the default. Do not rebuild around the standalone Slice proof CLI.
2. Slice proof is absorbed as the deterministic proof/replay spine.
3. Replay never calls live systems. It verifies exported and recorded artifacts only.
4. Proof packages must visibly distinguish deterministic tools, LLM-selected tools,
   and sandbox fallback once V3 output is adapted.
5. The proof schema is not frozen forever. Controlled schema bumps are allowed if
   fixture evidence exposes gaps.
6. Governance decisions are policy evidence, not autonomous authorization or Vault
   authorization.
7. Model/tool outputs can support findings only when recorded and replay-safe.
8. Buyer-pain hypotheses stay secondary until customer discovery validates them.

## Scale Story

Measured numbers available in repo evidence:

- Submission throughput: about 1.6 alerts/sec in V3 benchmark evidence.
- Completed Path A alerts in benchmark snapshot: 164.
- Pending alerts in benchmark snapshot: 416.
- Novel alerts waiting for LLM tool selection: 35.
- Full-corpus completion throughput: not measured in this PR.
- Customer-validated throughput: not found.

Methodology available in repo evidence:

- Lab/benchmark evidence from `Zovark_final` V3 benchmark documentation.
- Static code and test inspection for paths that could not be reproduced locally.

Environment:

- The benchmark evidence references RTX 3050-class LLM bottleneck behavior.
- This PR did not run a new V3 benchmark.

Suitable customer-size range:

- Early pilots should fit low-volume or saved-plan-heavy workflows.
- High-volume enterprise ingestion should wait for Track C measurements.

Gap versus v4.1:

- v4.1 target: 10K alerts/sec ingestion and about 100 investigation-worthy events/sec.
- Current evidence: about 1.6 alerts/sec submission in benchmark evidence and incomplete
  completion-throughput proof.
- Risk: ingestion/funnel scale may need new measurement or rebuild before enterprise
  deployment claims.

## Replay And Proof Boundary

The current Replay V2 verifier proves internal consistency of exported package
contents against the deterministic verifier. It does not prove:

- legal admissibility
- certification readiness
- cryptographic signing
- transparency-log anchoring
- completeness of upstream evidence collection
- production forensic completeness

Future V3 proof packages should preserve these distinctions:

- saved-plan deterministic tool execution
- LLM-selected tool execution
- explicit sandbox execution
- sandbox fallback after tool-runner error
- governance policy decision
- institutional knowledge context
- correlation history context

## Architecture Freeze Trigger

This document defines a planning freeze trigger. It does not create a release tag or
freeze runtime code.

For implementation sequencing, this synthesis should remain stable until the earliest
of:

- first paying customer
- first failed pilot
- six months from the freeze date
- first significant customer signal contradicting current decisions

If any trigger occurs, reopen the affected architecture decision with an ADR or
architecture-governing decision record before changing proof, trace, or runtime
contracts.

## Known Conflicts And Open Questions

- Local-only inference, OpenAI-compatible endpoints, and future model runtime policy
  are not fully reconciled.
- V3 fixture capture did not produce full live fixtures for every required path.
- Durable per-tool call records were not found in fixture capture.
- Customer signals have not been captured yet.
- Current V3 scale evidence is not enough for v4.1 enterprise-scale claims.
- Older V2 architecture docs remain stale and require banner/archive cleanup.

## Next Architecture Step

The next architecture step is Investigation Trace V1, grounded in:

- this synthesis
- the Capability Identity Contract
- V3 fixture capture evidence
- the Replay V2 offline verification boundary

The next step is not live EDR integration, Capability Gateway runtime, manifest
signing, or a broad runtime rebuild.
