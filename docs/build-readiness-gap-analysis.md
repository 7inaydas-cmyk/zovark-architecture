# Build Readiness Gap Analysis

Status: pre-build gap analysis. This document does not implement local product
runtime, tests, scripts, benchmarks, live integrations, or customer-readiness
material.

## Current Runnable Surface

The repository currently supports:

- Running the deterministic Slice 001 CLI against a static EDR sample.
- Verifying an exported V1 proof package offline.
- Using Python APIs to generate V1 or explicit V2 proof packages from
  representative V3-like fixtures.
- Running pytest validation for the adapter, verifier, static fixtures, and
  realistic static scenario.

The repository does not yet support a one-command local Zovark product/testbed
run.

## What Works On A Test Machine Today

From the repository root:

```bash
python -m zovark.slice001 --input samples/edr-sample-001.json --output out/ --tenant-id tenant-001
python -m zovark.slice001 verify --package out/
```

For development validation:

```bash
uv run --with pytest python3 -m pytest tests/ -q
git diff --check
python3 scripts/check_adr_cross_links.py
python3 scripts/check_claim_provenance.py
```

The realistic V2 validation path currently exists as tests, not as a product
command:

```bash
uv run --with pytest python3 -m pytest tests/test_v2_realistic_scenario_validation.py -q
```

Context Compaction Memory now exists only as architecture/contracts. It is not a
runtime memory service and is not wired into the local proof/Replay runner.

## Install Gaps

- No console script is declared in `pyproject.toml`.
- No committed lockfile policy exists for `uv.lock`; it remains local-only in
  this working tree.
- README documents Slice 001, not a product/testbed runner.
- No install guide exists for running the V3 adapter/V2 generation path outside
  pytest.
- No local environment template exists for future V3 runtime, AlertForge, or
  product/testbed settings.
- No runtime configuration exists for future `investigation_memory` storage or
  bounded retrieval because that layer is architecture/contracts only.

## Runtime Gaps

- No local product orchestrator exists.
- No command currently chains:

```text
AlertForge scenario -> Zovark ingest -> V3 fixture adapter -> V2 package -> verifier
```

- No live V3 runtime from `Zovark_final` is wired into this repository.
- No live SIEM, EDR, LLM, DB, network, dispatcher, Vault, or dashboard runtime is
  part of the current implementation.
- A local static proof/Replay testbed runner exists for the implemented
  fixture-to-package path. No product compose file or live runtime startup script
  exists.
- No persisted output directory policy exists for generated V2 proof packages
  outside temporary test directories.

## Missing Commands Or Scripts

Current local proof/Replay testbed command:

```bash
python3 -m zovark.slice001.local_testbed \
  --input samples/v3-local-proof-fixture.json \
  --output .tmp/local-testbed-v2 \
  --package-version v2
```

Useful future commands before broader local product/testbed work starts:

- Run the realistic static scenario validation without relying on pytest helper
  internals.
- Clean temporary generated package output directories.
- Compare two generated packages for deterministic equality.
- Optionally run a bounded preflight that checks Python version and expected file
  layout.

These future commands should be added only in scoped implementation PRs.

## Missing Environment Assumptions

Before a local testbed build, define:

- Python version floor and install command.
- Whether `uv` is required or optional for local workflows.
- Whether generated package outputs live under `out/`, `tmp/`, or another ignored
  directory.
- Whether AlertForge outputs one JSON file per scenario or a scenario directory.
- Whether AlertForge emits already-sanitized fields or Zovark must reject unsafe
  fields at the integration boundary.
- Whether future V3 runtime state is in this repo, the older `Zovark_final` repo,
  or a separate local service.
- Whether local scenario validation should run without any network access.

## Missing Local Validation Workflow

Current validation is strong for repository tests and now has a local static
proof/Replay workflow. It is still not a product runtime workflow.

Current and future workflow before product/testbed implementation:

1. Run Slice 001 sample generation and verification.
2. Run the local testbed V3 fixture -> V1 generation and verification.
3. Run the local testbed V3 fixture -> explicit V2 generation and verification.
4. Run realistic static scenario validation.
5. Run raw-leak assertions against generated V2 package artifacts.
6. Confirm no customer-readiness, legal, certification, signing, anchoring, or
   live-integration artifacts were generated.

## Blocking Gaps Before Local Product/Testbed Build

- No product entrypoint exists.
- No AlertForge output contract exists.
- No Zovark ingest contract for AlertForge outputs exists.
- No runtime Context Compaction Memory storage or retrieval service exists.
- No local product runtime dependency model exists.
- No generated-package output lifecycle is defined beyond local `.tmp/` examples.
- No benchmark command exists.
- No customer-ready artifact policy exists.

## Non-Blocking But Risky Gaps

- Some docs are stale relative to the now-implemented V2 verifier and adapter
  population slices.
- Current realistic validation uses one static AlertForge-style scenario.
- The adapter is fixture-oriented and does not yet consume durable runtime records.
- Full Investigation Trace V1 and Capability Identity objects remain documented,
  not implemented.
- Scale evidence remains lab/benchmark evidence, not a current product claim.

## Build-Readiness Recommendation

The smallest safe next build work should be local workflow plumbing around the
already-implemented static path, not live integrations.

Implemented first local workflow target:

```text
local fixture command -> explicit V2 package generation -> offline verifier -> leak/determinism checks
```

Feature-lifecycle boundary: no current applied/root
`product/features/feature-registry.yaml` file is present in this repo snapshot.
The recovered patch-tree feature-registry append was inspected for context, and
the local runner is treated as `F-002` Replay/tape workflow plumbing rather than
a new product feature. Any future product/testbed component, AlertForge contract
or importer, benchmark harness, service, feature flag, or customer-facing
workflow must perform explicit feature-registry alignment under INV-028.

AlertForge integration still waits until the AlertForge output contract and
Zovark ingest requirements are explicit.

Before greenfield runtime or AlertForge integration work, the Context Compaction
Memory contracts must be treated as a design constraint: no model should receive
unbounded raw tool output, and future proof/replay records need memory refs,
content hashes, bounded envelopes, and retrieval audit refs rather than LLM-made
canonical summaries.
