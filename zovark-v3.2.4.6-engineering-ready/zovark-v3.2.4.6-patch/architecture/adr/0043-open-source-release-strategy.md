# ADR-0043 — Open-Source Release Strategy

**Status:** **PROPOSED — STRATEGIC PIVOT pending founder sign-off.**
**Date:** 30 April 2026.
**Established by:** architecture extension; explicitly flagged as a strategic pivot in v3.2.4.5.
**Related:** ADR-0010 (open-source schemas), ADR-0013 (no paid components), ADR-0036 (open-source schema boundary).

## Review metadata

- **Scope:** M1 founder decision; release-channel implementation spans M1 through M6+.
- **Affected invariants:** INV-009, INV-027, INV-031.
- **Implementation status:** Proposed decision plus draft license text in `LICENSE-source-available.md`. Public repositories, source mirrors, contribution policy, and customer mirror access are not present in this tree.
- **Enforcement mechanism:** Current: none beyond documentation and shipped draft license. Planned: license finalization, repository publication checklist, and release-bundle source-link checks.
- **Supersession/amendment links:** Supersedes the prior closed-source commercial scope statement if accepted. Not superseded.
- **Claim provenance:** Schedule entries are planning commitments by milestone. No measured adoption or trust claim is made.

## Strategic-pivot disclosure

> The original Zovark evaluation scope said: *"closed-source commercial. No open-source release planned."*
>
> This ADR proposes a different posture: an Apache-2.0 open-source core for schemas/standards/scripts, plus a source-available license for the customer-runtime code, with closed-source confined to Zovark-internal hosted systems.
>
> **This is a strategic pivot, not a mechanical fix.** It must be signed off by the founder before being treated as accepted. Until then it is `PROPOSED-STRATEGIC-PIVOT`. M1 work proceeds on the assumption that this ADR's posture is the working assumption, but the founder may reject or amend it; if they do, the schemas (which already say `x-zovark-open-source: true` per ADR-0010, accepted in earlier baselines) remain unaffected, and the runtime-code licensing decision remains open.
>
> A sign-off slot for this ADR is tracked as **M1-DECISION-001** in `DD_BLOCKERS-v3.2.4.5-additions.md`.

## Context

ADR-0010 says **schemas** are open-source. ADR-0013 says no **paid components** in production. Neither says whether Zovark's own **code** is open-source, source-available, or closed. This is a trust-positioning decision for every regulated-buyer conversation:

- "We're Apache-2.0 core" carries strongest trust.
- "We're source-available with audit and modify-for-self-hosted-use rights" carries strong trust without giving up competitive defensibility.
- "We're closed-source SaaS with an attestation" carries weak trust.

This ADR must be decided before public schema-registry schemas attract a developer community asking "where's the code?".

## Decision (proposed)

Zovark adopts a **three-tier release strategy**.

### Tier A — Apache-2.0 open-source (public GitHub)

- All canonical schemas (`architecture/blueprint/schemas/*.schema.json`) — already public per ADR-0010.
- Open standards registry (`architecture/standards/open-standards-registry.yaml`).
- Mapping definitions to OCSF, Sigma, MITRE ATT&CK, OpenTelemetry.
- All bootstrap-acceptance fixtures.
- The `verify-bootstrap.sh` and `bootstrap-acceptance.sh` scripts.
- All `scripts/check_*.py` enforcement scripts.
- All ADRs and the invariants document.
- The `update_bundle_signed.schema.json` and `telemetry_envelope.schema.json` (so customers can write their own verifiers).
- The `zovark update verify` CLI command source.

### Tier B — Source-available with product

License: Zovark Source-Available v1.0 — read, audit, modify-for-self-hosted-use; no fork-and-redistribute.

- Reference implementation of the six-stage pipeline (INGEST through STORE).
- Mesh agent pool implementation.
- Tape recorder implementation.
- Audit chain implementation.
- Vault implementation.
- EDR adapter implementation.
- Customer Instance subsystem code.
- zvadmin code.
- Healer service code.

Customers can read every line of code that runs in their environment. They cannot fork-and-redistribute as a competing product. This matches the trust posture of HashiCorp BSL or Elastic SSPL but with a Zovark-specific license that explicitly allows audit, modification for own use, and security research.

### Tier C — Closed-source (hosted by Zovark)

- Control Plane production code.
- Update Factory build infrastructure.
- Research Pipeline runners.
- Zovark internal tooling (deployment automation, customer support tooling).

Customers never see this code; **it never runs in their environment.**

## Critical rule

**No closed-source code runs in a customer environment.** Every byte of code that touches customer data is at minimum source-available (Tier B). This is the trust contract.

## Public release channel

- `zovark/zovark` — public GitHub for Apache-2.0 portions.
- `zovark/zovark-core` — separate repo for source-available portions, with separate license file.

Customer instances pull binaries built by the Update Factory; source is mirrored to a private read-only customer-accessible repository.

## Patent grant

Apache-2.0 carries a patent grant. Zovark contributes any patents covering Apache-2.0 portions to a defensive patent pool (decision deferred to a future ADR if and when Zovark holds patents).

## Open-source release schedule

- **M1:** Apache-2.0 portions land in `zovark/zovark` GitHub, public — **only after this ADR is signed off as Accepted.** `[policy-commitment:release-engineering,milestone-review]`
- **M2-M5:** Tier B portions land in private mirror; selective Apache-2.0 components moved up. `[policy-commitment:release-engineering,milestone-review]`
- **M6+:** Full Tier B mirror available to customers under license click-through. `[policy-commitment:release-engineering,milestone-review]`

## Consequences

- Strongest possible trust posture for regulated buyers ("you can read every line that runs in your environment").
- Defensive against competitive forks (Tier B license restrictions).
- Increased contributor surface: Apache-2.0 schemas may attract community contributions.
- Operational overhead: maintaining two licenses, two release channels, two contribution policies.
- Marketing alignment: every reference to "open-source" in customer materials specifies which tier (A or B).
- **Material change to commercial posture** vs. the original "closed-source commercial" scope. Founder must decide.

## Alternatives considered

- *Fully Apache-2.0 (everything open)*: rejected; gives away competitive defensibility; encourages forks of the runtime.
- *Fully closed-source* (the original evaluation-scope posture): the founder may choose this; in that case ADR-0043 is rejected and Zovark ships closed-source binaries with attestations only. Regulated buyers may push back during procurement.
- *AGPL-3.0 for runtime*: rejected; AGPL viral terms create deployment friction; ADR-0036 already excludes AGPL from canonical schemas.
- *BSL (Business Source License)*: considered; rejected because BSL converts to Apache-2.0 after a delay, which we don't commit to.

## Counts referenced from this ADR

The earlier draft of this ADR mentioned specific fixture counts ("53 baseline + 3 = 56") that drifted between versions. v3.2.4.5 removes hardcoded counts; **all count references defer to `VERSION_METADATA.json`** as the structural source of truth. Any "X + Y = Z" arithmetic must be derived from that file at apply time, not hardcoded in prose.
