# Architecture Current State

Status: current-state documentation. This document does not implement runtime
code, modify adapter or verifier behavior, add schemas, add AlertForge
integration, add benchmarks, or create customer-readiness material.

## Repository Role

This repository is an architecture/reference/proof repository. It is not the
final production runtime repository.

The repository currently captures deterministic proof-package generation,
offline Replay verification, V3-like fixture adaptation, Proof Package V2
reference work, and architecture contracts.

## Implemented Now

The current implemented surface includes:

- static Proof/Replay runner for sanitized V3-like input;
- Proof Package V1 reference generation;
- explicit Proof Package V2 reference generation;
- Replay verifier reference behavior;
- V3 fixture/reference adapter;
- static Proof Package V2 fixtures;
- realistic static scenario validation; and
- Context Compaction Memory architecture contracts.

The static proof/Replay path is:

```text
static or sanitized V3-like input
-> v3_adapter
-> V1 or explicit V2 proof package
-> offline Replay verification
-> local output directory
```

## Not Implemented

The following do not exist in the current implementation:

- final product runtime;
- greenfield runtime repository;
- Context Compaction Memory runtime storage;
- Context Compaction Memory retrieval service;
- AlertForge ingest;
- AlertForge output contract;
- live EDR, SIEM, LLM, DB, Vault, control-plane, or network integration;
- benchmark harness;
- customer-readiness bundle;
- customer outreach workflow;
- signing, anchoring, SLSA, in-toto, legal evidence packaging, or compliance
  certification workflow.

## Current Architecture Boundaries

Proof Package V1 remains V1-only by default. Proof Package V2 generation remains
explicit and versioned.

Replay verification is offline. Replay must not call live systems.

Context Compaction Memory is an architecture/contracts layer only. It defines
how future implementations must avoid unbounded raw tool output in model
context. It does not provide a storage service, retrieval service, adapter
integration, or verifier integration.

AlertForge is treated as a future upstream synthetic alert/scenario generator.
It is not Zovark architecture and has no ingest path in this repository yet.

## Readiness Position

Outreach remains blocked until architecture, local product build, AlertForge
synthetic validation, benchmarks, and evidence-backed readiness exist.

The next implementation steps must preserve:

- V1 default as V1-only;
- explicit V2/additive contracts;
- offline Replay;
- no raw prompt, tool-argument, tool-output, payload, message, note, hidden
  reasoning, or chain-of-thought leakage;
- no customer or benchmark claims without evidence; and
- ADR-0036 and ADR-0037 constraints.
