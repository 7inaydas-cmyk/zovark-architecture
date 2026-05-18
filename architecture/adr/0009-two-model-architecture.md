# ADR-0009: Two-Model Architecture And RamaLama Local-SLM Runtime

**Status:** accepted, amended by v3.2.4.4 positioning pivot  
**Original date:** 2026-04-28  
**Amendment date:** 2026-05-16  
**Version context:** predecessor baseline plus v3.2.4.4 amendment  
**Source classification:** recovered predecessor ADR amendment; not runtime code

## Context

The predecessor ADR-0009 established a two-model architecture: a FAST role for
tool selection and parameter filling, and a CODE role for complex investigation
generation and verdict-summary work. The original operational simplification was
that v1.0 could deploy one model behind both roles and split later if
benchmarks justified it.

Subsequent architecture work clarified that deterministic replay, not air-gap
deployment alone, is the primary buyer-facing differentiator. At the same time,
the local inference surface needs a named runtime so the architecture can speak
precisely about local-only and hybrid inference without treating local inference
as an undefined future option.

## Amendment Decision

RamaLama is the canonical local-SLM runtime for Zovark's local inference
topology. This names the local runtime surface; it does not add runtime code,
model weights, deployment automation, benchmarks, customer-readiness material, or
live integration in this repo.

Zovark supports three inference topologies:

- **Cloud-only:** model calls are served by an approved cloud LLM provider.
- **Local-only:** model calls are served locally through RamaLama after runtime
  support is implemented.
- **Hybrid:** tenant policy can route some calls to a cloud LLM and some calls to
  local SLM inference through RamaLama after runtime support is implemented.

Local-only and hybrid inference are approved target topology choices, not
current runtime capabilities. They become selectable only after the
corresponding runtime implementation, operator controls, and validation are in
place.

The replay-record provenance invariant is unchanged across all three
topologies: replay never re-inferences regardless of the original inference
source. Replay uses the recorded model-visible inputs, recorded outputs,
provenance, hashes, and verdict inputs captured at investigation time.

## Consequences

### Positive

- Names a concrete local-SLM runtime for architecture and future implementation
  planning.
- Keeps cloud, local, and hybrid topology targets explicit and tenant-scoped.
- Preserves deterministic replay as the trust boundary across inference
  providers.
- Avoids treating air-gap deployment as the sole or primary buying wedge.

### Negative

- RamaLama becomes an architectural dependency for local-SLM planning and must be
  reconciled before implementation work.
- Any future RamaLama integration must still satisfy Context Compaction Memory:
  no model receives unbounded raw tool output.
- Existing local-inference artifacts may need retraining or adapter changes
  before they are portable to bounded-envelope semantics.

## Alternatives Considered

- **Keep local inference unnamed.** Rejected because it leaves local-only and
  hybrid topology claims ambiguous.
- **Keep local inference deferred as an architecture decision.** Rejected
  because regulated and sovereignty buyers may require local-only inference as a
  target tenant topology once the corresponding runtime support, controls, and
  validation exist.
- **Make local inference mandatory.** Rejected because deterministic replay does
  not require local inference; cloud-only remains a valid topology when tenant
  policy permits it.
- **Treat model replay as re-inference.** Rejected because model outputs are not
  stable across providers, model versions, hardware, or inference engines.

## Scope Boundary

This amendment does not implement RamaLama, introduce live LLM calls, change
Proof Package V1/V2 contracts, change Replay verifier behavior, add benchmarks,
or make customer-readiness claims. This amendment does not make local-only or
hybrid RamaLama inference available as a runtime capability.

## Related

- ADR-0047: Replay Compatibility Matrix and Failure Modes
- ADR-0052: Deterministic Replay as Primary Differentiator
- INV-004, INV-005, INV-036, INV-039
