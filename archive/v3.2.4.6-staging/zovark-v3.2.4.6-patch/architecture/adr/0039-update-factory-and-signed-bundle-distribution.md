# ADR-0039 — Update Factory and Signed Bundle Distribution

**Status:** Proposed (becomes Accepted on M1-ARCH-001 merge).
**Date:** 30 April 2026.
**Established by:** architecture extension.
**Related:** ADR-0010, ADR-0013, ADR-0033, ADR-0036, ADR-0038, ADR-0040, ADR-0042.

## Review metadata

- **Scope:** M1 architecture; M4 update-bundle runtime implementation.
- **Affected invariants:** INV-003, INV-009, INV-023, INV-031.
- **Implementation status:** Partial in this patch. `update_bundle_signed.schema.json` and examples exist. Build infrastructure, verification CLI, release ledger, reproducible-build environment, SBOM generation, attestation generation, and rollback execution are M4 deliverables.
- **Enforcement mechanism:** Current: schema/example validation in `scripts/run_shiptime_tests.sh`. Planned M4: bundle verification command, signed-bundle CI gates, release-ledger verification, reproducible-build verification.
- **Supersession/amendment links:** Not superseded and does not supersede another ADR in this tree.
- **Claim provenance:** SLSA and CycloneDX versions are policy targets. No measured supply-chain claim is made.

## Context

Update bundles distributed to customer instances must be cryptographically verifiable, supply-chain-attested, reproducible, and air-gap-transportable. AI-generated code that becomes part of an update bundle must not bypass these requirements. The SolarWinds-class threat (compromise of the build environment inserting malicious code into signed bundles) must be defeated by design.

## Decision

Zovark will operate an Update Factory subsystem that:

- Builds every release bundle **reproducibly**: bundle hash must be re-derivable from source by any third party using the published build script.
- Requires **two independent signatures** on every release bundle: release-engineer key + security-officer key. Single-signature bundles are **invalid by policy**. **No emergency exception.** `[policy-commitment:security-officer,per-release-review]`
- Attaches a **Sigstore (cosign) attestation** referencing the exact source commit and build steps (SLSA L3 minimum). `[policy-commitment:release-engineering,per-release-review]`
- Includes a **complete CycloneDX 1.5 SBOM** with dependency provenance to the point of build. `[policy-commitment:release-engineering,per-release-review]`
- Includes a **compatibility matrix** declaring which `schema_version` / `feature_registry_version` / `runtime_version` ranges the bundle is valid for.
- Includes **rollback metadata** sufficient for a customer to revert to the prior version.
- Generates an **air-gap export package**: a self-contained tarball containing bundle + signatures + attestation + SBOM + verification script that runs without internet access.
- Logs every bundle issuance to a future **append-only `update-factory-ledger.jsonl`** (hash-chained). The ledger and verifier are M4 deliverables.
- Cryptographic key management per ADR-0042.

## Reproducible build contract

```
Build environment is pinned:
  Base image:   pinned by SHA-256 digest, not tag
  Toolchain:    pinned by SHA-256 digest
  Dependencies: pinned by --require-hashes (M1-CI-001)
  Build cmd:    deterministic; no timestamps; no random ordering

Third-party verification:
  git checkout <source-commit>
  docker run --rm -v $(pwd):/src \
    zovark/build-env@sha256:<digest> \
    make bundle
  sha256sum dist/zovark-bundle-*.tar.gz
  # must match the bundle's published hash

If the third-party hash does not match, the bundle is invalid by definition.
```

## Customer-side verification (M4 deliverable)

```
zovark update verify <bundle-path>
```

The future command performs (fail-closed):
1. Bundle structure validation against `update_bundle_signed.schema.json`.
2. Both signatures verified against published Zovark root keys.
3. Sigstore attestation chain verified.
4. SBOM hash verified.
5. Compatibility matrix checked against this customer instance's versions.
6. Reproducibility hash compared (optional; requires source).
7. Output: `VERIFIED` or `FAILED <reason>`.

## Consequences

- Adds a multi-key signing infrastructure with key-rotation policy (ADR-0042).
- Requires a reproducible-build CI environment with pinned base images and pinned toolchains.
- Customer-side bundle verification becomes a single offline-runnable command after M4 implementation.
- Single-signature workflows are forbidden. Even emergency patches require two signers.
- The build environment itself becomes a security-critical asset and is threat-modeled.

## Alternatives considered

- *Single-signature bundles for emergency patches*: rejected; any exception erodes the supply-chain guarantee.
- *Online-only attestation*: rejected; incompatible with air-gap.
- *Skip reproducibility*: rejected; defeats SolarWinds-class threat model.
- *Three-key signing*: considered; rejected for v1.0 (operational complexity > marginal security gain). Revisit M11+.
