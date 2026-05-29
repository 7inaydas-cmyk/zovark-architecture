# Zovark — Fresh-Machine Migration Guide

> **Product anchor.** Zovark turns EDR-style security alerts into deterministic,
> replayable AI-assisted investigation packages that a SOC analyst can inspect and
> approve. Target users: SOC / security operations teams that need auditable AI
> investigation evidence, not opaque summaries.

This guide brings all three Zovark repositories up on a clean machine and runs each
repo's **proven-green** build + test path. It is migration-readiness, not a product
release.

## Current product boundary (what exists today)

- A proven **substrate**: a deterministic local proof-package pipeline (architecture
  Slice 001), a greenfield runtime storage/contract substrate (runtime, Phase 2B), and
  a deterministic PR review-gate model (reviewops).
- **No** live EDR/SIEM/LLM/network integration, no planner/executor/assessor runtime,
  no unattended auto-merge in product, and **no** customer / production / SLA /
  compliance / readiness claims. Those are explicitly out of scope.

## Repositories and verified `main` SHAs

| Repo | GitHub | `main` SHA (verified 2026-05-29) |
|---|---|---|
| architecture | `7inaydas-cmyk/zovark-architecture` | `a980e0351a998b92ca046eddbd884b13f907fa57` * |
| runtime | `7inaydas-cmyk/zovark-runtime` | `e3d100db9b5fbdb0777018a0344c5e23f7dc6ea2` |
| reviewops | `7inaydas-cmyk/zovark-reviewops` | `ef276c88c0d2db14c4b4499681ce0801c8a37e42` |

\* The architecture `main` SHA advances by one commit when the PR that adds this file
merges; clone `main` HEAD (below) for the latest.

## Required tooling

- **Python** 3.11+ (3.12 verified). Architecture & runtime.
- **uv** (Astral) for Python envs/locks — `https://docs.astral.sh/uv/`.
- **Node.js** 22+ (22.22 verified). ReviewOps only; zero runtime dependencies.
- **git**, **gh** (optional, for PR workflows).

## Clone

```bash
mkdir -p ~/zovark && cd ~/zovark
git clone https://github.com/7inaydas-cmyk/zovark-architecture.git
git clone https://github.com/7inaydas-cmyk/zovark-runtime.git
git clone https://github.com/7inaydas-cmyk/zovark-reviewops.git
# Each repo defaults to main HEAD. To pin to a verified SHA, e.g.:
#   (cd zovark-runtime && git checkout e3d100db9b5fbdb0777018a0344c5e23f7dc6ea2)
```

## Build + test (proven green)

### architecture (Python, uv, stdlib-only runtime)

```bash
cd zovark-architecture
# Tests (508):
uv run --with pytest python3 -m pytest tests/ -q
# Validation checks (CI mirrors these). jsonschema is pinned to 4.17.3 because
# scripts/check_schema_contracts.py uses the pre-4.18 RefResolver API for local $defs.
uv run --with "jsonschema==4.17.3" --with PyYAML python3 scripts/check_schema_contracts.py
uv run python3 scripts/check_claim_provenance.py
uv run python3 scripts/check_mvp_scope_consistency.py
uv run python3 scripts/check_adr_cross_links.py
uv run --with "jsonschema==4.17.3" --with PyYAML python3 scripts/validate_yc_demo.py
# Run the Slice 001 pipeline:
uv run python3 -m zovark.slice001 --input samples/edr-sample-001.json --output out/ --tenant-id tenant-001
```
CI: `.github/workflows/checks.yml` runs all of the above on every PR/push to main.

### runtime (Python, uv)

```bash
cd zovark-runtime
# Phase-0 static checks:
uv run python3 scripts/check_contract_manifest.py
uv run python3 scripts/check_invariants.py
uv run python3 scripts/check_no_unbounded_model_context.py
# Tests (235):
uv run --with pytest --with jsonschema --with "PyYAML==6.0.2" python3 -m pytest tests/ -q
# Local proof status:
PYTHONPATH=src uv run python3 -m zovark_runtime.cli proof-status
```
CI: `.github/workflows/invariants.yml` runs the checks + tests on every PR/push to main.
Architecture-source provenance is pinned in `ARCHITECTURE_REPO_SOURCE.md`
(architecture commit `7bad0bb5ac5ac99dec007831dd67352f47255caa`, verified resolvable).

### reviewops (Node, zero-dependency)

```bash
cd zovark-reviewops
# Tests (238):
node --test tests/*.test.ts
```
CI: `.github/workflows/ci.yml` runs the suite + a strict `src` type-check on every PR/push.

## Environment variables (placeholders only — never commit real values)

ReviewOps reads GitHub state through a Nango-backed boundary. Supply these via
deployment configuration only:

```bash
export NANGO_SECRET_KEY=<your-nango-secret-key>
export NANGO_PROVIDER_CONFIG_KEY=<your-nango-provider-config-key>
# Nango connection IDs are supplied at runtime; never hardcode them.
```

Architecture and runtime require **no** secrets for build/test (stdlib + local fixtures).

## Notes for the migrator

- All three repos are clean: local `main` == `origin/main` == GitHub `main`; no unpushed
  commits; working trees clean except a deliberately-untracked
  `architecture/adr-index.draft.md` (an ADR-index enrichment draft pending human review —
  it is authority content, not build input).
- Tracked release artifacts `zovark-v3.2.4.6-engineering-ready.zip` (+`.sha256`) exist in
  architecture history; they are not needed to build.
