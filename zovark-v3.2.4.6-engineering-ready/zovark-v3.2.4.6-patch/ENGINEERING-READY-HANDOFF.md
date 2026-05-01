# Zovark v3.2.4.6 Engineering Handoff

## Purpose

This package is an engineering-ready architecture and patch bundle for starting M1 build work after applying it to the v3.2.3.5 baseline. It is still an architecture/bootstrap package, not a runtime implementation.

## Source Of Truth

- Patch contents and hashes: `PATCH-MANIFEST.json`.
- Apply procedure: `PATCH-README.md`.
- Conflict-resolution hierarchy: `architecture/source-of-truth.md`.
- ADR inventory: `architecture/adr-index.md`.
- Invariants and milestone status: `invariants.md`.
- Product wedge and MVP boundary: `architecture/mvp-scope.md`.
- Claim tagging rules: `architecture/claims/claim-provenance.md`.

## Current Build Boundary

M1 can start only after:

1. `scripts/apply_v3_2_4_6.py --verify-patch-tree-hash` passes on the unpacked patch.
2. The patch is applied to a clean v3.2.3.5 baseline.
3. Anchored fragments are applied.
4. `scripts/check_post_apply.py --repo-root <repo>` passes.
5. `verify-bootstrap.sh` and `scripts/bootstrap-acceptance.sh` pass in the post-apply repo.
6. M1-DECISION-001 resolves ADR-0043 source-model posture.

## What Engineers May Treat As Implemented

- Schema-level contracts shipped in `architecture/blueprint/schemas/*.schema.json`.
- Patch-tree checks shipped in `scripts/`.
- Patch-tree ship-time evidence in `ops/compliance/v3.2.4.6-shiptime-transcript.txt`.
- Draft source-available license text in `LICENSE-source-available.md`, pending founder sign-off and counsel review.

## What Engineers Must Treat As Planned

- Runtime tenant isolation enforcement.
- Runtime telemetry emitter scan and customer telemetry audit log.
- Update Factory runtime, bundle CLI verification, SBOM generation, reproducible build system, and update ledger.
- HSM integration, key ledger, key rotation-age checks, revoked-key checks, and compromise drills.
- Research Pipeline runtime and no-direct-runtime-mutation enforcement.
- Replay engine, runtime audit hash chain, verdict canonicalization, legal-hold retention, offboarding, and DR restore drills.
- Claim-provenance checker.

## First Engineering Work Items

1. Add a post-apply cross-link gate for baseline ADR/file references.
2. Implement `scripts/check_claim_provenance.py`.
3. Replace placeholder owners in `OWNERS.yaml` and switch owner checks to hard mode for production-code PRs.
4. Draft ADR-0038 DR detail: RPO/RTO, same-region HA, cross-region DR, restore drills, and restore-gap audit events.
5. Finalize ADR-0043 source model and license review.
6. Implement the customer validation scorecard flow before design-partner onboarding.
