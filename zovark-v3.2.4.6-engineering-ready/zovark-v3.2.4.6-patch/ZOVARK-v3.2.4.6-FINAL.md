# ZOVARK v3.2.4.6 - Engineering-Ready Baseline Package

## Summary

v3.2.4.6 is the current patch package for starting M1 engineering work after it is applied to the v3.2.3.5 baseline and post-apply gates pass. It remains a bootstrap/architecture package: it does not implement runtime tenant isolation, replay, audit chain, update factory, telemetry emitter enforcement, HSM integration, or Research Pipeline runtime.

## What This Package Adds

- Source-of-truth hierarchy: `architecture/source-of-truth.md`.
- ADR inventory for shipped ADRs 0038-0043: `architecture/adr-index.md`.
- Claim-provenance convention: `architecture/claims/claim-provenance.md`.
- MVP boundary: `architecture/mvp-scope.md`.
- Design-partner validation workflow: `architecture/customer-validation-workflow.md`.
- Restore-gap semantics: `architecture/disaster-recovery-restore-gap.md` and `invariants.md`.
- Engineering handoff: `ENGINEERING-READY-HANDOFF.md`.
- Draft Tier B license text: `LICENSE-source-available.md`.

## Current Gate Status

The patch-tree ship-time gate is:

```bash
bash scripts/run_shiptime_tests.sh
```

Manifest self-test is run separately with:

```bash
python3 scripts/apply_v3_2_4_6.py --patch-root . --verify-patch-tree-hash
```

## Open Decisions Before Tag

Do not tag until M1-DECISION-001 is resolved.

- M1-DECISION-001: accept, amend, or reject ADR-0043 source model.
- Finalize `LICENSE-source-available.md` with counsel review before any Tier B release.
- Add the post-apply baseline cross-link gate for ADR/file references.
- Replace placeholder owner handles before production-code PRs.

## Implementation Boundary

Engineers may implement against the schemas, invariants, ADRs, and source-of-truth hierarchy in this package. Any runtime enforcement described as M2, M3, M4, M5, M6, M9, or M10 is planned work, not current evidence.
