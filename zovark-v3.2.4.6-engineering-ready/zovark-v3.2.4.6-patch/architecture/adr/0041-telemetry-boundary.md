# ADR-0041 — Telemetry Boundary

**Status:** Proposed (becomes Accepted on M1-ARCH-001 merge).
**Date:** 30 April 2026.
**Established by:** architecture extension.
**Related:** ADR-0001, ADR-0003, ADR-0010, ADR-0024, ADR-0036, ADR-0038.

## Review metadata

- **Scope:** M1 architecture; M2 runtime telemetry enforcement.
- **Affected invariants:** INV-029, INV-032.
- **Implementation status:** Partial in this patch. `telemetry_envelope.schema.json`, examples, `architecture/telemetry-justification.md`, and schema checks exist. Runtime emitter scanning, customer-side telemetry audit log, preview command, and notice workflow are M2 deliverables.
- **Enforcement mechanism:** Current: schema/example validation and payload-kind binding. Planned M2: `check_telemetry_boundary.py` emitter allowlist gate and customer-side audit-log verification.
- **Supersession/amendment links:** Not superseded and does not supersede another ADR in this tree.
- **Claim provenance:** Telemetry intervals and notice windows are policy commitments, not measured performance claims.

## Context

The customer-instance → control-plane data flow is the trust contract that determines whether regulated buyers will permit the control plane at all. The flow must be enumerable, schema-validated, customer-auditable, and verifiably free of customer evidence.

## Decision

Zovark will define and enforce a Telemetry Boundary that:

- Specifies every field that may cross the customer→control-plane boundary in **`telemetry_envelope.schema.json`**.
- Enforces schema shape today through schema/example validation. The runtime allowlist gate **`check_telemetry_boundary.py`** is an M2 deliverable: code that emits a non-allowlisted field must fail the gate when the runtime emitter exists.
- Writes every outbound payload to a customer-side future **`telemetry_audit_log.jsonl`** (append-only) so the customer can audit what left their network. Audit-log implementation is an M2 deliverable.
- Defines **"anonymized"** operationally: stable salted hash with **per-customer salt**; salt **never crosses the boundary**.
- Provides a customer-side **`telemetry-preview` mode**: customer can run `zovark telemetry preview` to see exactly what would be sent.

## Four telemetry modes

| Mode | Behavior | Default for |
|---|---|---|
| `live` | Continuous, batched every 60s `[policy-commitment:product-owner,release-review]` | SaaS (opt-in) |
| `batched` | Buffered locally, sent every 24h `[policy-commitment:product-owner,release-review]` | Hybrid (default) |
| `manual` | Buffered locally, sent only on `zovark telemetry send` | Regulated SaaS |
| `disabled` | Nothing leaves; control-plane interactions become offline-package only | Air-gap (default) |

## Allowlisted telemetry fields (initial set, M2)

Envelope-frame fields:

`envelope_version`, `instance_pseudonym`, `sent_at`, `payload_kind`, `payload`, `customer_audit_id`.

Payload kinds:

- `status`
- `health`
- `failure_signature`
- `none`

`status` payload fields:

`bundle_version`, `schema_version`, `feature_registry_version`, `adapter_versions`, `tool_catalog_version`, `topology_mode`, `disabled_capabilities`.

`health` payload fields:

`health_status`, `last_successful_replay_timestamp`, `last_audit_chain_verification_timestamp`, `last_update_applied_version`, `failed_update_attempts_count`.

`failure_signature` payload fields:

`signature_hash`, `component`, `occurred_at`.

`none` payload fields:

No fields. The payload is an empty object.

## Field-justification document

Field-justification document at `architecture/telemetry-justification.md`. New field additions require ADR-0041 amendment + 30-day customer notice + opt-out window. `[policy-commitment:product-owner,release-review]`

## Forbidden fields

No exception. No opt-in. No "anonymized version of this is fine":

Raw alerts, investigation evidence, tenant secrets, EDR credentials, audit log entries, replay records, customer PII, customer hostnames, customer IPs (other than synthetic test ranges), specific Sigma rules deployed, customer-defined templates, EDR action history, vault audit entries, Healer findings, Mesh investigation summaries.

## Consequences

- Customer trust posture: "you can audit every byte that leaves your network."
- New telemetry fields require an ADR amendment + customer notice — small ongoing engineering cost.
- Disabled telemetry mode becomes the air-gap default.
- The audit log itself uses the existing audit_event schema for hash-chain consistency.

## Alternatives considered

- *Implicit telemetry*: rejected; impossible to audit.
- *Telemetry blocklist instead of allowlist*: rejected; allowlist is the only model that fails closed.
- *Anonymized customer evidence (e.g., hashed alert content)*: rejected; hashing reversible by attacker with corpus access.
- *Per-customer-per-field opt-in*: considered; rejected as too operationally complex for v1.0; revisit M11+.
