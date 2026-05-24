# ADR-0004: Inference layer abstraction

**Status:** accepted  
**Date:** 2026-04-28  
**Owner:** architect  
**Version context:** v3.2.5.0 consolidation promotion from zovark-v1-bootstrap-v3.2.3.2-final.zip  
**Source classification:** bootstrap predecessor ADR, mechanically normalized for current ADR format
## Context

Language model substrate is expected to evolve substantially over the 18-month product horizon. Coupling the application directly to a specific model API or runtime would force codebase-wide changes on every model swap. The product also ships in three deployment topologies (cloud, hybrid, air-gap) with different inference backends (continuous-batching for GPU, CPU-fallback for branch). The same code path must serve all three.

## Decision

All language-model calls route through a gateway abstraction with an OpenAI-compatible API. Configuration-level switch determines local versus cloud transport. Backends are pluggable: continuous-batching for GPU deployments (default cloud), CPU-fallback for branch deployments and air-gap fallback.

Models ship as OCI artifacts. Cloud deployments pull from a hosted artifact registry (signed). Air-gap deployments load from offline bundles. Model lifecycle (pull, canary, activate, rollback) is managed by `zvadmin`.

## Consequences

**Positive.** Model swaps are configuration changes, not code changes. Same code path serves all three topologies. Cloud benchmark transport during development uses the same gateway as production.

**Negative.** The gateway is a critical-path component. Bugs in the gateway affect every investigation. Mitigation: extensive testing in `tests/contract/inference/`.

## Alternatives Considered

N/A — original ADR did not address this.

## Fitness functions

- `tests/architecture/inference-gateway-only.test.py` — static AST walk asserting no module makes language-model API calls outside the gateway.
- `tests/contract/inference/openai-compat.test.py` — asserts the gateway implements the OpenAI-compatible API surface against a recorded test corpus.

## References

- INV-003 (air-gap-compatible)
- `zovark.md` §9
