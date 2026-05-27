# Architecture Decision Record (ADR) Index

This is the source of truth for the status of all architectural decisions.

Authoritative ADRs currently live under `architecture/adr/`. This
consolidation snapshot ships the promoted ADR files at that path; retired and
superseded predecessor items are tracked in the consolidation source-of-truth
work.

All six visible patch ADRs are status **proposed** and become **accepted** on merge of
M1-ARCH-001 (ADR-0042 also requires M1-ARCH-002). ADR-0043 additionally requires
founder sign-off (M1-DECISION-001) before tagging the bootstrap baseline.

This branch also carries a targeted v3.2.4.4 positioning amendment:

- `architecture/adr/0009-two-model-architecture.md` amends predecessor
  ADR-0009 to name RamaLama as the local-SLM runtime and to make
  cloud-only, local-only, and hybrid inference topology choices explicit.
- `architecture/adr/0052-positioning-deterministic-replay.md` proposes
  deterministic replay and evidence integrity as the primary customer-facing
  differentiator.
- `architecture/adr/0053-runtime-proof-loop-completion-criteria.md` defines
  scoped deterministic replay proof-loop completion criteria and the boundary
  that separates that proof loop from readiness and external-claim lanes.

These files are documentation/ADR amendments only. They do not import the full
predecessor ADR baseline, implement RamaLama, or change runtime behavior.

| ADR | Title | Status | Scope | Affected invariants | Supersedes | Superseded by | Amends | Amended by | Implementation status | Customer-facing impact | Related files | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-0038 | Control Plane and Customer-Instance Authority Boundary | proposed | M1 architecture; M2/M10 enforcement | INV-001, INV-003, INV-029, INV-032 | none | none | ADR-0011 | none | document-only in this patch except schema-presence checks; runtime data-classification enforcement planned M2 | yes | `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/adr/0038-control-plane-and-customer-instance-authority-boundary.md`, `.../architecture/blueprint/schemas/control_plane_instance_status.schema.json` | Active proposal. Does not implement runtime data-classification enforcement or DR drills. |
| ADR-0039 | Update Factory and Signed Bundle Distribution | proposed | M1 architecture; M4 implementation | INV-003, INV-009, INV-023, INV-031 | none | none | none | none | schema and example support in this patch; runtime implementation planned M4 | yes | `.../architecture/adr/0039-update-factory-and-signed-bundle-distribution.md`, `.../architecture/blueprint/schemas/update_bundle_signed.schema.json` | Active proposal. Verification CLI, release ledger, reproducible-build environment, SBOM generation, attestation generation, and rollback execution are planned deliverables. |
| ADR-0040 | Research Pipeline and Gated Candidate Promotion | proposed | post-MVP/M6 | INV-007, INV-023, INV-024, INV-030, INV-031 | none | none | none | none | schema/example support in this patch; runtime implementation planned M6 | no | `.../architecture/adr/0040-research-pipeline-and-gated-candidate-promotion.md`, `.../architecture/blueprint/schemas/update_candidate.schema.json`, `.../architecture/blueprint/schemas/update_promotion_decision.schema.json` | Active proposal. Supports a future improvement loop; not design-partner MVP runtime behavior. |
| ADR-0041 | Telemetry Boundary | proposed | M1 architecture; M2 enforcement | INV-029, INV-032 | none | none | none | none | schema and example checks implemented; runtime emitter scan/audit logging planned M2 | yes | `.../architecture/adr/0041-telemetry-boundary.md`, `.../architecture/telemetry-justification.md`, `.../architecture/blueprint/schemas/telemetry_envelope.schema.json` | Active proposal. `check_telemetry_boundary.py` is not present and remains an M2 deliverable. |
| ADR-0042 | Cryptographic Key Management | proposed | M1 architecture; M4 implementation | INV-031 | unsafe old-key transition pattern | none | none | none | document-only in this patch; HSM/key-ledger gates planned M4 | yes | `.../architecture/adr/0042-cryptographic-key-management.md`, `.../SECURITY-VULN-DISCLOSURE.md` | Active proposal. No HSM, key ledger, or rotation-age script exists in this tree. |
| ADR-0043 | Open-Source Release Strategy | proposed strategic pivot | M1 decision; M1/M6 release operations | INV-009, INV-027, INV-031 | closed-source commercial scope statement | none | none | none | proposed decision plus draft license text; release-channel implementation not present | yes | `.../architecture/adr/0043-open-source-release-strategy.md`, `.../LICENSE-source-available.md` | Founder sign-off and counsel review required before acceptance. |
| ADR-0052 | Deterministic Replay as Primary Differentiator | proposed | positioning; customer-facing story; no runtime implementation | INV-022, INV-036, INV-039 | none | none | ADR-0009 | none | document-only; no benchmarks, runtime, or customer-readiness material | yes | `architecture/adr/0052-positioning-deterministic-replay.md`, `docs/positioning.md` | Positions deterministic replay/evidence integrity as primary differentiator; air-gap remains a planned regulated-deployment target pending runtime support, operator controls, validation, and deployment evidence. |
| ADR-0053 | Runtime Proof-Loop Completion Criteria | accepted | deterministic replay proof-loop completion authority; no runtime implementation | INV-036, INV-039 | none | none | none | none | schema and proof authority artifact only; runtime import/update is follow-up work | no | `architecture/adr/0053-runtime-proof-loop-completion-criteria.md`, `architecture/proof/runtime-proof-loop-completion.yaml`, `architecture/blueprint/schemas/runtime_proof_loop_completion.schema.json` | Defines scoped proof-loop completion criteria without AlertForge, benchmark, dashboard, customer, product, production, compliance, SLA, audit-chain, or replay-engine readiness claims. |

## Baseline ADRs (post-apply verified)

The patch ADRs 0038-0043 amend or reference baseline ADRs from the v3.2.3.5
predecessor. The baseline ADR files are not in this finalization repo. The rows
below are placeholders pending the M0 verification step specified by the
`adr-cross-link-verification` capability (`openspec/specs/adr-cross-link-verification/spec.md`).
Once `scripts/check_adr_cross_links.py` (M0 deliverable) runs successfully, a
reviewer merges the script-generated `architecture/adr-index.draft.md` here to
populate full metadata.

| ADR | Short name | Verification status | Reference site(s) |
|---|---|---|---|
| ADR-0011 | (control-plane authority predecessor) | post-apply-verified | Amended by ADR-0038. |
| ADR-0009 | (two-model architecture) | amendment-present | Amended by `architecture/adr/0009-two-model-architecture.md`; full predecessor source remains external baseline material. |
| ADR-0024 | (audit erasure / tenant usage) | post-apply-verified | `invariants.md` INV-020, INV-021. |
| ADR-0025 | (audit erasure boundary) | post-apply-verified | `invariants.md` INV-020. |
| ADR-0027 | (verdict canonicalization) | post-apply-verified | `invariants.md` INV-018. |
| ADR-0028 | (vault threat model) | post-apply-verified | `invariants.md` INV-019; rc2 `vault-authorization` spec. |
| ADR-0030 | (bootstrap evidence: pass+fail fixtures) | post-apply-verified | `invariants.md` INV-023. |
| ADR-0031 | (claim-provenance benchmark artifacts) | post-apply-verified | `invariants.md` INV-022; rc2 `claim-provenance` spec. |
| ADR-0034 | (tenant DEK rotation) | post-apply-verified | DD-blocker M3-DEPENDENCY-002; rc2 `vault-authorization` spec. |

## Human decisions still needed

- M1-DECISION-001: accept, amend, or reject ADR-0043 source model.
- ADR-0042 customer-side escrow recovery procedure.
- ADR-0038 DR plan details: RPO/RTO, same-region HA vs cross-region DR, restore-drill cadence.
- Post-apply cross-link gate for baseline ADRs 0001-0037 and baseline files.

## Status definitions

- **active**: Current guidance.
- **superseded**: Replaced by a newer ADR.
- **historical**: Relevant for context but no longer guidance.
- **proposed**: Under review; not yet binding.
- **proposed strategic pivot**: Proposed decision that reverses or significantly amends a prior position; requires explicit human sign-off before acceptance.
- **amended**: Modified by a later ADR but still partially current.
- **rejected**: Considered and not accepted.

## Scope definitions

- **M0**: Bootstrap deliverables; pre-engineering.
- **MVP**: Design-partner MVP runtime.
- **post-MVP**: Beyond MVP, before GA.
- **GA**: General availability.
- **future**: Not yet scheduled.
- **unknown**: Scope not yet determined.

## Implementation status definitions

- **document-only**: ADR text present, no runtime or supporting artifacts.
- **planned**: Scheduled for a specific milestone, not yet present.
- **M0 deliverable**: Required before engineering starts.
- **MVP implementation**: Implemented for design-partner MVP.
- **post-MVP**: Implemented after MVP.
- **implemented**: Fully realized including runtime + tests + runbook.
