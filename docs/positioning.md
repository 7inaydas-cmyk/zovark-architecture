# Zovark Positioning

Status: positioning guidance only. This document does not implement runtime
behavior, RamaLama integration, benchmarks, customer-readiness material, or
outreach.

## Lead

Zovark's positioning direction is replay-grade evidence integrity: every
investigation should produce a byte-identical-replayable record, replay should
not re-inference, and auditors should be able to verify verdicts offline after
the original model is retired. Recovered ADR-0046, ADR-0047, and INV-039 remain
candidate material until reconciled into the current baseline.

## Customer-Facing Summary

Zovark is the audit-grade evidence layer for AI-assisted SOC response. Before
your SOC isolates a host or disables a user, Zovark should show the evidence,
explain the verdict, record the approval path, and create replayable evidence.

The customer-facing differentiator is deterministic replay plus evidence
integrity. Air-gap deployment remains a possible regulated-deployment target,
but it is a planned topology target rather than the headline and is not a
current supported deployment profile.

## Topology

Zovark's architecture direction includes cloud, hybrid, and air-gap topology
targets. Hybrid inference with RamaLama as the planned local-SLM runtime is the
current direction, paired with approved cloud inference where tenant policy
allows it. Non-cloud and air-gap profiles remain pending until the relevant
runtime support, operator controls, validation, and deployment evidence exist.
Customer-instance authority remains governed by ADR-0038. Telemetry mode is
governed by ADR-0041. The topology choice does not change the replay
positioning direction.

## Inference

Zovark's architecture direction includes cloud LLM, local SLM through RamaLama,
or hybrid inference topologies. RamaLama is the named local-SLM runtime under
the ADR-0009 amendment, pending runtime implementation. The customer chooses the
topology per tenant configuration only once the relevant runtime support,
operator controls, and validation exist.

Replay should not re-inference for any topology. Reconciled replay work should
use the recorded model-visible inputs, outputs, provenance, hashes, and verdict
inputs captured at investigation time.

## Evidence Integrity

Evidence integrity is the positioning direction. Recovered ADR-0046, recovered
ADR-0047, and recovered INV-039 describe candidate deterministic verdict,
replay-record, and bounded-context material that must be reconciled before it is
cited as active current architecture or customer-facing commitment.

Until that reconciliation lands, the proof story should be framed as planned
architecture direction: captured evidence, canonical verdict input,
deterministic verdict, replay-compatible record, and offline verification that
does not call live models or tools.

## Anti-Claims

This positioning does not claim:

- 100% detection;
- autonomous response readiness;
- production SOC readiness;
- legal admissibility;
- compliance certification;
- tamper-proof evidence;
- benchmarked capacity, latency, false-positive, false-negative, or accuracy
  numbers without a benchmark artifact per INV-022;
- that air-gap deployment is required for deterministic replay;
- that air-gap is a current supported deployment profile;
- that RamaLama is implemented in this architecture repo;
- that recovered ADR-0046, ADR-0047, or INV-039 are active current source before
  reconciliation; or
- that customer outreach or customer-readiness material is complete.