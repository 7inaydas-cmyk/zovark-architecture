# ADR-0001: Zovark v1.0 foundation

**Status:** accepted  
**Date:** 2026-04-28  
**Owner:** architect  
**Version context:** v3.2.5.0 consolidation promotion from zovark-v1-bootstrap-v3.2.3.2-final.zip  
**Source classification:** bootstrap predecessor ADR, mechanically normalized for current ADR format
## Context

Zovark v1.0 is a greenfield enterprise security operations center investigation and response product. The product targets enterprise SOCs, regulated industries, and ultimately defense and intelligence customers. The wedge against incumbent AI-SOC copilots rests on two capabilities: replay-grade evidence and coordinated-campaign correlation with autonomous response.

The product is closed-source commercial. Customers receive licensed access. Open-source dependencies and standards-aligned schemas are used throughout, but the product is proprietary. No paid software dependencies are required for production deployment.

## Decision

Zovark is built as a closed-source commercial product targeting cloud SaaS first launch, hybrid enterprise in the next product phase, and air-gap enclave in the phase after that. The architecture is greenfield with explicit out-of-scope items including diode-only topology, federated learning, and confidential computing for cross-customer collaboration.

The two load-bearing capabilities are:

1. Replay-grade investigation records that prove what happened in any investigation and prove the record itself was not altered.
2. Coordinated-campaign correlation across alerts with autonomous EDR response gated by per-tenant policy.

## Consequences

**Positive.** Clear strategic positioning. No license fees on dependencies. Standards-aligned schemas reduce procurement friction with enterprise buyers.

**Negative.** Closed-source means no community contribution path; engineering effort is fully on the team. Three-topology roadmap means the codebase must accommodate all three from the start (no retrofits).

**Risks accepted.** Greenfield means no existing customers. The product must reach first design partner before revenue arrives. Phasing decisions (cloud → hybrid → air-gap) align with sales cycle realism but also commit phase-2 customers to a wait.

## Alternatives Considered

N/A — original ADR did not address this.

## Fitness functions

- `tests/architecture/license-policy.test.py` — verifies no `pyproject.toml`, `package.json`, `Cargo.toml`, or `go.mod` declares a paid dependency.
- `tests/architecture/topology-coverage.test.py` — verifies every adapter declares its topology compatibility (cloud, hybrid, airgap) and that the dependency graph admits all three.

## References

- INV-001 (tenant boundary), INV-003 (air-gap-compatible)
- `zovark.md` §1, §16
