# ADR-0040 — Research Pipeline and Gated Candidate Promotion

**Status:** Proposed (becomes Accepted on M1-ARCH-001 merge).
**Date:** 30 April 2026.
**Established by:** architecture extension.
**Related:** ADR-0007, ADR-0023, ADR-0029, ADR-0036, ADR-0037, ADR-0038, ADR-0039, ADR-0041.

## Review metadata

- **Scope:** Post-MVP/M6. Not design-partner MVP runtime behavior.
- **Affected invariants:** INV-007, INV-023, INV-024, INV-030, INV-031.
- **Implementation status:** Schema and example checks exist in this patch. Research Pipeline runtime, corpora, promotion queue, embargo queue, and reviewer-capacity operations are M6+ deliverables unless separately pulled forward by ADR.
- **Enforcement mechanism:** Current: `update_candidate.schema.json`, `update_promotion_decision.schema.json`, and examples. Planned M6: no-direct-runtime-mutation gate and promotion-queue enforcement.
- **Supersession/amendment links:** Not superseded and does not supersede another ADR in this tree.
- **Claim provenance:** Soak windows and review windows are policy commitments; corpus timing is a milestone plan, not measured evidence.

## Context

Earlier Zovark concepts included an internal research/improvement loop that generated templates, tools, mappings, and detection candidates. This capability is product-strategically valuable — but only if the autonomy boundary is precisely specified.

## Decision

Zovark will operate a Research Pipeline subsystem that:

- Runs nightly against **fixed corpora** (replay fixtures, dead-code corpora, security-test corpora, benchmark corpora). Corpora land at M5; Research Pipeline runs first at M6. `[policy-commitment:research-owner,milestone-review]`
- Generates **candidate** artifacts only: candidate template, candidate tool, candidate mapping, candidate detection, candidate patch, candidate benchmark, candidate documentation.
- Labels every candidate with a **proposed risk tier** (1, 2, or 3).
- Submits candidates to the **Update Factory promotion queue**, never directly to a release branch.
- Runs in an **environment isolated** from customer data, customer instances, and the Control Plane production database.
- Has **no network access** to customer-controlled networks at runtime.
- For **potential security-vulnerability findings**: routes to embargo queue (separate; private), never to public PR queue.
- Is itself reproducible: every nightly run records its corpus version, runner image SHA, and seed.

## Hard constraint (INV-030)

> No Research Pipeline output is customer-runtime authoritative until promoted by the Update Factory and accepted by customer policy.

## 10. Risk-tiered review

### Tier 1 — low risk

- **Scope:** Non-executable documentation patches, non-authoritative fixtures (benchmark anchors, doc examples), benchmark improvements that don't change measurement methodology.
- **Review:** CI green + 24h soak; no human reviewer required. `[policy-commitment:release-engineering,per-promotion-review]`
- **Tier 1 explicitly does NOT include:** executable code (any language), JSON Schema definitions, CI workflow files, dependency files, generated update bundles, fixture files that act as authoritative test inputs.

### Tier 2 — medium risk

- **Scope:** Template improvements, mapping additions, executable code in non-protected paths, additive public-schema-registry schemas, tool catalog additions.
- **Review:** 1 human reviewer + CI green + 48h soak. `[policy-commitment:release-engineering,per-promotion-review]`

### Tier 3 — high risk

- **Scope:** Anything touching protected paths in §10.1, audit-chain code, vault code, replay code, verdict code, tenant-boundary code, EDR action code, update-factory code, signing/release/telemetry/update code, or Research Pipeline code.
- **Review:** 2 human reviewers + security review + 7-day review window + CI green. `[policy-commitment:security-officer,per-promotion-review]`

### 10.1 Protected paths

The protected path set is:

- `architecture/adr/`
- `architecture/blueprint/schemas/` existing schemas
- `invariants.md`
- `scripts/check_*.py`
- CI workflow files
- signing, release, telemetry, update, audit-chain, vault, replay, verdict, tenant-boundary, EDR-action, and Research Pipeline code paths once they exist

### 10.2 Auto-tiering

```
proposed_tier=1, file_paths intersect protected_dirs   → escalate to Tier 3
proposed_tier=1, file_paths include executable extension → escalate to Tier 2
proposed_tier=2, file_paths intersect protected_dirs   → escalate to Tier 3
proposed_tier=3, file_paths only in docs              → DOES NOT downgrade
                                                          (requires explicit reviewer override)
```

Promotion gate may auto-escalate; never auto-downgrades.

## 11. Security-vulnerability routing

Potential security-vulnerability findings do not enter the public PR queue. They route to the embargo queue described in `SECURITY-VULN-DISCLOSURE.md`. The embargo ledger and its verifier are M2 deliverables and are not present in this patch tree.

## Naming

External / canonical / customer-facing name: **Research Pipeline**. Internal-only references to "autoresearch-inspired" are permitted in engineering documentation; not in marketing, compliance, ADRs, or customer materials.

## Consequences

- Adds a research environment that must be threat-modeled.
- Creates a candidate volume requiring risk-tier triage; M6+ must size human reviewer capacity to expected Tier 2 + Tier 3 flow.
- Enables continuous improvement of templates, tools, mappings, detections.
- Provides a defensible "we did not silently modify your environment" trust posture.

## Alternatives considered

- *No research pipeline*: rejected; foregoes a real product differentiator.
- *Auto-merge low-risk candidates without 24h soak* `[policy-commitment:release-engineering,per-promotion-review]`: rejected; soak catches transient CI false-greens.
- *Allow Research Pipeline to read live customer data*: rejected; violates INV-001 and INV-027 simultaneously.
- *Only humans may touch protected code*: considered; rejected because it eliminates a major Research Pipeline value while Tier 3 already requires 2 reviewers + security + 7-day window `[policy-commitment:security-officer,per-promotion-review]`.
