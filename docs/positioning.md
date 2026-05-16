# Zovark Positioning

Status: positioning guidance only. This document does not implement runtime
behavior, RamaLama integration, benchmarks, customer-readiness material, or
outreach.

## Lead

Every investigation produces a byte-identical-replayable record. Replay never
re-inferences. Auditors verify verdicts offline, forever, regardless of model
availability.

## Customer-Facing Summary

Zovark is the audit-grade evidence layer for AI-assisted SOC response. Before
your SOC isolates a host or disables a user, Zovark shows the evidence, explains
the verdict, records the approval path, and creates a replayable proof package.

The customer-facing differentiator is deterministic replay plus evidence
integrity. Air-gap deployment remains important for regulated buyers, but it is
a topology option rather than the headline.

## Topology

Zovark supports cloud, hybrid, and air-gap topology choices. Customer-instance
authority remains governed by ADR-0038. Telemetry mode is governed by ADR-0041.
The topology choice does not change the replay invariant.

## Inference

Zovark supports cloud LLM, local SLM through RamaLama, or hybrid inference
topologies. RamaLama is the named local-SLM runtime under the ADR-0009
amendment. The customer chooses the topology per tenant configuration.

Replay never re-inferences for any topology. Replay uses the recorded
model-visible inputs, outputs, provenance, hashes, and verdict inputs captured at
investigation time.

## Evidence Integrity

Evidence integrity depends on deterministic verdict canonicalization under
ADR-0046, replay compatibility and failure modes under ADR-0047, and the
recording invariants tracked by INV-036 and INV-039.

The proof story is: captured evidence, canonical verdict input, deterministic
verdict, replay-compatible record, and offline verification that does not call
live models or tools.

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
- that RamaLama is implemented in this architecture repo; or
- that customer outreach or customer-readiness material is complete.
