# ADR-0053: Runtime Proof-Loop Completion Criteria

**Status:** accepted  
**Owner:** replay-owner  
**Established by:** issue #61 follow-up  
**Scope:** architecture authority for scoped deterministic replay proof-loop completion; no runtime implementation

## Context

Runtime has completed the A1-A4 deterministic replay proof chain:

1. Architecture replay authority and replay failure contracts were imported.
2. Runtime proof-status was moved to a checked-in declarative registry.
3. Runtime imported replay tool catalog retirement authority.
4. Runtime proved `REPLAY_TOOL_RETIRED` fail-closed behavior.
5. Runtime proved replay compatibility matrix coverage equality and now emits
   `REPLAY_COMPATIBILITY_MATRIX_COVERAGE_OK`.

Runtime still correctly reports `runtime_proof_loop: incomplete` because
architecture had not defined what completion means. Runtime must not infer
completion from local markers alone.

## Decision

Architecture defines a scoped **deterministic replay proof-loop completion**
authority in `architecture/proof/runtime-proof-loop-completion.yaml`, validated
by `architecture/blueprint/schemas/runtime_proof_loop_completion.schema.json`.

For this scope, `runtime_proof_loop: complete` means only:

- runtime imports or cites architecture-owned completion criteria;
- every required deterministic replay proof marker is present;
- every required marker has checked-in evidence handles;
- replay compatibility matrix coverage equality has been proven;
- no deferred entry classified as blocking remains;
- proof-status remains a declarative reporter.

This completion scope is limited to deterministic replay proof-chain closure.
It is not customer, product, production, compliance, SLA, dashboard, benchmark,
AlertForge, outreach, or runtime-investigation readiness.

## Required Proof Classes

Runtime completion for this scoped proof loop requires evidence for:

- contract metaschema validation;
- scanner and verdict fixture schema validation;
- imported canonical contracts and local schema validation;
- canonical fixtures for verdict input, replay records, and replay failure
  records;
- deterministic verdict derivation proof;
- replay validation and fail-closed cases;
- canonical replay failure-code mapping;
- canonical replay failure-record emission;
- replay compatibility row mapping;
- replay compatibility matrix coverage equality;
- replay tool catalog retirement authority import;
- `REPLAY_TOOL_RETIRED` fail-closed behavior.

The machine-readable artifact lists the required proof markers and evidence
classes. Runtime may not substitute a local hand-written completion rule.

## Deferred Entry Policy

For the scoped deterministic replay proof loop, the current remaining runtime
deferred entries are non-blocking:

| Runtime deferred entry | Completion classification |
|---|---|
| `audit_chain_output` | future-scoped, non-blocking |
| `runtime_investigation_execution` | future-scoped, non-blocking |
| `alertforge_scenario_validation` | non-goal, non-blocking |
| `benchmark_proof` | non-goal, non-blocking |
| `dashboard_and_external_claims` | non-goal, non-blocking |
| `production_sla_compliance_workflows` | non-goal, non-blocking |

Future architecture changes may define separate completion criteria for those
lanes. They do not block this replay proof loop.

## Proof-Status Constraints

Runtime proof-status must remain declarative:

- it must not run pytest;
- it must not parse CI logs;
- it must not infer completion from local state alone;
- it must report architecture provenance for the completion authority it uses;
- it must retain claim-boundary checks.

## Non-Goals

This ADR does not claim or implement:

- AlertForge validation;
- benchmarks;
- dashboard readiness;
- customer outreach readiness;
- customer readiness;
- product readiness;
- production readiness;
- compliance readiness;
- SLA readiness;
- runtime investigation execution;
- audit-chain output;
- replay-engine production readiness.

## Consequences

Runtime may later import this authority and change `runtime_proof_loop` to
`complete` only if its proof-status registry satisfies the architecture-owned
criteria. Until then, `runtime_proof_loop` remains incomplete.

The proof marker for the architecture criteria is:

```
ARCH_RUNTIME_PROOF_LOOP_COMPLETION_CRITERIA_OK
```

## Related

- ADR-0046 deterministic verdict canonicalization
- ADR-0047 replay compatibility matrix and failure modes
- ADR-0052 deterministic replay positioning
- INV-036 replay engine never inferences, substitutes, or degrades
- INV-039 verdict input is canonical and complete
- Issue #61
