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

## Install Gaps

- No console script is declared in `pyproject.toml`.
- No committed lockfile policy exists for `uv.lock`; it remains local-only in
  this working tree.
- README documents Slice 001, not a product/testbed runner.
- No install guide exists for running the V3 adapter/V2 generation path outside
  pytest.
- No local environment template exists for future V3 runtime, AlertForge, or
  product/testbed settings.

## Runtime Gaps

- No local product orchestrator exists.
- No command currently chains:

```text
AlertForge scenario -> Zovark ingest -> V3 fixture adapter -> V2 package -> verifier
```

- No live V3 runtime from `Zovark_final` is wired into this repository.
- No live SIEM, EDR, LLM, DB, network, dispatcher, Vault, or dashboard runtime is
  part of the current implementation.
- No local testbed compose file or startup script exists for the pre-build
  product path.
- No persisted output directory policy exists for generated V2 proof packages
  outside temporary test directories.

## Missing Commands Or Scripts

Useful future commands before local product/testbed work starts:

- Generate a V2 package from a specified V3-like JSON fixture.
- Verify a generated V2 package and print the deterministic verifier summary.
- Run the realistic static scenario validation without relying on pytest helper
  internals.
- Clean temporary generated package output directories.
- Compare two generated packages for deterministic equality.
- Optionally run a bounded preflight that checks Python version and expected file
  layout.

These commands should be added only in a scoped implementation PR. This review
does not add them.

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

Current validation is strong for repository tests but not yet packaged as a
local build workflow.

Recommended future workflow before product/testbed implementation:

1. Run Slice 001 sample generation and verification.
2. Run V3 fixture -> V1 generation and verification.
3. Run V3 fixture -> explicit V2 generation and verification.
4. Run realistic static scenario validation.
5. Run raw-leak assertions against generated V2 package artifacts.
6. Confirm no customer-readiness, legal, certification, signing, anchoring, or
   live-integration artifacts were generated.

## Blocking Gaps Before Local Product/Testbed Build

- No product entrypoint exists.
- No AlertForge output contract exists.
- No Zovark ingest contract for AlertForge outputs exists.
- No local product runtime dependency model exists.
- No generated-package output lifecycle is defined.
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

Recommended first implementation target:

```text
local fixture command -> explicit V2 package generation -> offline verifier -> leak/determinism checks
```

AlertForge integration should wait until the AlertForge output contract and
Zovark ingest requirements are explicit.
