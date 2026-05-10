# Proof Package V2 Contract

Status: docs-only contract. This document defines a future Proof Package V2 shape
for validation planning. It does not change the current nine-file Proof Package
V1 implementation, V3 adapter behavior, Replay V2 verifier behavior, tests, or
runtime code.

## Versioning Decision

Proof Package V1 remains the current nine-file deterministic package:

- `investigation-tape.json`
- `evidence-ledger.json`
- `timeline.json`
- `findings.json`
- `verdict.json`
- `edr-handoff.json`
- `audit-chain-entry.json`
- `replay-report.json`
- `customer-report.md`

Proof Package V2 is a versioned practitioner-grade extension. It must not be
silently substituted for V1. Replay must continue verifying V1, and V2 verifier
support must be implemented in a later PR before any V2 package is treated as
verified behavior.

## Contract Principles

- V2 preserves deterministic verification.
- V2 preserves V1 compatibility.
- V2 records structured rationale, not raw model chain-of-thought.
- V2 does not expose raw system prompts by default.
- V2 prefers `prompt_hash`, `prompt_version`, `model_ref`,
  `model_fingerprint`, and redacted prompt references for model-backed work.
- V2 does not implement signing, transparency logs, in-toto, SLSA, or external
  anchoring.
- V2 does not claim legal admissibility, compliance certification, or forensic
  completeness.
- Compliance mappings are versioned mappings only.
- Any field not populated from V3 or deterministic synthesis must be `null` plus
  `data_unavailable_reason`.
- Replay never calls live systems to verify V2.

## Object Classification

| Object | Classification | V3 data dependency | Verification expectation |
| --- | --- | --- | --- |
| `decision_rationale` | required | accepted findings, evidence refs, verdict, trace summaries | Evidence refs resolve; rationale items cite existing evidence IDs. |
| `false_positive_reasoning` | conditional | rejected findings, benign indicators, analyst overrides if available | Required when verdict is benign or when rejected findings exist. |
| `context_enrichment` | conditional | institutional knowledge, correlation history, threat/context tools | Recorded context refs resolve; live lookup is forbidden during replay. |
| `visibility_gaps` | required | missing telemetry, unavailable fields, trace capture gaps | Gaps are explicit and do not silently imply complete coverage. |
| `approval_record` | required | handoff, governance decision, human review metadata if available | Approval state is consistent with handoff/governance evidence. |
| `blast_radius` | conditional | affected hosts/users/processes, lateral movement, scope evidence | Required when response action or containment recommendation is present. |
| `rollback_plan` | conditional | proposed action, containment, recovery or undo steps | Required when action is proposed; may be `null` for investigation-only packages. |
| `compliance_mapping` | optional | mapped findings, control IDs, framework version | Must be labeled as mapping, not certification. |
| `controls_in_place_at_incident` | customer-supplied | customer control inventory or policy snapshot | Must identify customer-supplied source or mark unavailable. |
| `customer_report_v2` | required | V2 objects plus V1 proof state | Human-readable and bounded; no certification or legal claims. |

## Common Object Envelope

Each V2 object should use a deterministic envelope when serialized in a future
implementation:

| Field | Requirement | Meaning |
| --- | --- | --- |
| `object_type` | required | One of the V2 object names in this contract. |
| `object_version` | required | Version of that object shape. |
| `status` | required | `populated`, `partial`, `unavailable`, or `not_applicable`. |
| `source_refs` | required | Evidence IDs, trace record IDs, capability IDs, or package artifact refs used to populate the object. |
| `data_unavailable_reason` | required when value is `null` or partial | Deterministic reason, such as `not_emitted_by_v3`, `not_captured`, `customer_not_supplied`, or `not_applicable`. |
| `object_hash` | required in future implementation | Canonical hash of the object with `object_hash` blanked or null. |

## Object Definitions

### `decision_rationale`

Purpose: explain why the package verdict and handoff were reached without exposing
raw model chain-of-thought.

Required content:

- `rationale_summary`
- `rationale_items`
- each item must include `evidence_refs`
- each item may include `trace_record_refs` or `capability_refs` when available
- `decision_boundary`, describing what the rationale does and does not prove

Rules:

- Use structured summaries tied to evidence IDs.
- Do not include raw chain-of-thought.
- Do not add claims that are not backed by evidence refs.

### `false_positive_reasoning`

Purpose: record why candidate explanations were rejected or why a benign/no-action
interpretation was or was not accepted.

Required when:

- verdict is benign or low confidence;
- rejected findings exist;
- analyst override or governance review rejects a candidate finding.

Required content:

- `rejected_finding_refs`
- `benign_indicators`
- `contradicting_evidence_refs`
- `reasoning_summary`

If unavailable, use `status: unavailable` and `data_unavailable_reason`.

### `context_enrichment`

Purpose: record context used to understand the alert, such as institutional
knowledge, correlation history, threat enrichment, or asset context.

Required when context influenced findings, verdict, or handoff.

Required content:

- `context_type`
- `context_source`
- `context_hash`
- `evidence_refs`
- `trace_record_refs`

Replay must verify recorded context only. It must not call live enrichment tools.

### `visibility_gaps`

Purpose: make missing data explicit.

Required content:

- `gap_id`
- `gap_type`
- `affected_question`
- `impact_on_confidence`
- `data_unavailable_reason`

Visibility gaps must not be treated as proof that no compromise occurred.

### `approval_record`

Purpose: preserve the human or policy approval path without claiming autonomous
authorization.

Required content:

- `approval_state`
- `governance_decision_ref`
- `handoff_ref`
- `review_required`
- `review_reason`
- `approver_ref` or `data_unavailable_reason`

Governance evidence does not replace Vault authorization.

### `blast_radius`

Purpose: summarize affected or potentially affected scope.

Required when response action, containment, or customer-facing impact language is
present.

Required content:

- `asset_refs`
- `identity_refs`
- `process_refs`
- `network_refs`
- `scope_summary`
- `confidence`
- `data_unavailable_reason` for each unavailable scope dimension

### `rollback_plan`

Purpose: document how a proposed action could be reversed or reviewed safely.

Required when a package proposes or records an action recommendation.

Required content:

- `action_ref`
- `rollback_steps`
- `rollback_owner_ref`
- `preconditions`
- `risks`
- `verification_steps`

If the package is investigation-only, mark this object `not_applicable`.

### `compliance_mapping`

Purpose: map evidence and findings to framework/control references.

Optional content:

- `framework_name`
- `framework_version`
- `mapping_version`
- `control_refs`
- `mapped_evidence_refs`
- `mapping_limitations`

Rules:

- Label mappings as mappings, not certifications.
- Do not claim SOC 2, SEC readiness, SLSA compliance, legal admissibility, or
  forensic completeness.

### `controls_in_place_at_incident`

Purpose: record customer-supplied control state relevant to the incident.

Classification: customer-supplied.

Required content when supplied:

- `control_source_ref`
- `control_snapshot_hash`
- `control_time_scope`
- `control_refs`
- `customer_attestation_ref` when available

If not supplied, use `status: unavailable` and
`data_unavailable_reason: customer_not_supplied`.

### `customer_report_v2`

Purpose: provide a customer-readable summary of V2 package verification and
practitioner-relevant conclusions.

Suggested structure:

- `executive_summary`
- `verified_scope`
- `decision_summary`
- `decision_rationale_summary`
- `false_positive_summary`
- `context_summary`
- `visibility_gaps_summary`
- `approval_summary`
- `blast_radius_summary`
- `rollback_summary`
- `compliance_mapping_summary`
- `limitations`

Rules:

- Keep language bounded and evidence-backed.
- State that V2 verifies exported package consistency only.
- Do not claim legal admissibility, certification readiness, signing, external
  anchoring, or complete upstream evidence collection.

## Compatibility With Current V3 Adapter

As of current main, the V3 adapter writes current V1 proof packages and preserves
available V3 context nested in the existing evidence substrate. It does not emit
first-class Capability Identity objects, Investigation Trace records, or Proof
Package V2 objects.

Proof Package V2 population must therefore be implemented later and tested against
realistic static fixtures before customer outreach uses V2 package claims.
