# investigation-tape Specification

## Purpose
TBD - created by archiving change fix-investigation-tape-schema. Update Purpose after archive.
## Requirements
### Requirement: Investigation tape SHALL have identity fields

Every investigation tape SHALL carry the following identity fields:

- `tape_id` — string, unique within a tenant.
- `tenant_id` — string, references the tenant scope.
- `created_at` — ISO-8601 timestamp.
- `schema_version` — string, identifies the tape schema version (e.g., `tape/1.0`).
- `source_alert_ref` — reference to the source alert (typically an EDR alert envelope ID + ingestion timestamp).

#### Scenario: Tape without tape_id is invalid

- **WHEN** a tape is created without a `tape_id`
- **THEN** the system SHALL reject the tape and report a missing-field error

#### Scenario: Tape without tenant_id is invalid

- **WHEN** a tape is created without a `tenant_id`
- **THEN** the system SHALL reject the tape and never store it

### Requirement: Investigation tape SHALL carry raw evidence references with hashes

Every investigation tape SHALL include a `raw_evidence` field — an ordered list of evidence references. Each reference includes:

- `evidence_id` — string.
- `hash` — content hash (SHA-256 or stronger).
- `source_type` — enum (e.g., `edr_alert`, `network_flow`, `log_record`, `process_event`).
- `ingested_at` — ISO-8601 timestamp.
- `retention_class` — enum (optional in MVP; required by GA per future ADR).

#### Scenario: Tape with no evidence references is allowed only with explicit no-evidence flag

- **WHEN** a tape has zero entries in `raw_evidence`
- **THEN** the tape SHALL also carry a `no_evidence_flag: true` to make the absence explicit
- **AND** the verdict SHALL acknowledge the absence

#### Scenario: Evidence reference without hash fails

- **WHEN** any entry in `raw_evidence` lacks a `hash`
- **THEN** the tape is invalid

### Requirement: Investigation tape SHALL carry a timeline

Every investigation tape SHALL include a `timeline` field — an ordered list of events. Each event:

- `event_type` — enum (`alert_received`, `evidence_added`, `model_inference`, `tool_call`, `finding_recorded`, `verdict_set`, `handoff_dispatched`, `handoff_executed`, `rollback_recorded`, `audit_signed`).
- `at` — ISO-8601 timestamp.
- `actor` — enum (`system`, `model:<id>`, `tool:<id>`, `human:<role>`).
- `evidence_refs` — list of `evidence_id`s contributing to this event (may be empty).
- `decision_contribution` — boolean: did this event contribute to the verdict?

#### Scenario: Timeline events MUST be in non-decreasing timestamp order

- **WHEN** a tape's `timeline` contains events out of timestamp order
- **THEN** the tape is invalid

#### Scenario: Timeline MAY be empty only on closed tapes with `no_evidence_flag`

- **WHEN** a tape has an empty `timeline`
- **THEN** the tape SHALL also carry `no_evidence_flag: true`

### Requirement: Investigation tape SHALL carry findings

Every investigation tape SHALL include a `findings` field — a list of evidence-backed findings. Each finding:

- `title` — string, human-readable.
- `severity` — enum (`info`, `low`, `medium`, `high`, `critical`).
- `evidence_refs` — list of `evidence_id`s; SHALL contain at least one entry.
- `model_contribution` — boolean: did a model contribute to this finding?
- `confidence_band` — enum (optional in MVP; recommended) (`low`, `medium`, `high`).

A tape MAY have an empty `findings` list ONLY if it carries a `no_findings_flag: true` and the verdict acknowledges absence.

#### Scenario: Finding without evidence_refs fails

- **WHEN** a finding has zero entries in `evidence_refs`
- **THEN** the tape is invalid (every finding must be evidence-backed)

#### Scenario: Empty findings without flag fails

- **WHEN** `findings` is empty and `no_findings_flag` is absent or false
- **THEN** the tape is invalid

### Requirement: Investigation tape SHALL carry a verdict

Every investigation tape SHALL include a `verdict` object with:

- `value` — enum from a fixed set: `benign`, `suspicious_unconfirmed`, `confirmed_malicious`, `inconclusive_insufficient_evidence`. (The set is intentionally small for MVP; expansion goes through a `MODIFIED Requirements` change.)
- `evidence_refs` — list of `evidence_id`s the verdict relies on.
- `model_contribution` — boolean.
- `signing_tag` — opaque tag (the actual signature is stored in the audit chain entry referenced by `audit_ref`).
- `set_at` — ISO-8601 timestamp.

The verdict SHALL be deterministic given the recorded inputs (raw evidence + recorded model/tool I/O + timeline). Replay SHALL be able to recompute the verdict from the recorded inputs and arrive at the same value.

#### Scenario: Tape closed without a verdict is invalid

- **WHEN** a tape transitions from `recording` to `closed` without a `verdict.value` set
- **THEN** the close transition SHALL be rejected

#### Scenario: Verdict outside the fixed enum is invalid

- **WHEN** a verdict is set to a value not in the fixed enum
- **THEN** the tape is invalid

### Requirement: Investigation tape MAY carry recorded model/tool I/O

If models or tools were used during the investigation, the tape SHALL include `recorded_io` — a list of records. Each record:

- `kind` — enum (`model`, `tool`).
- `id` — string identifier of the model or tool.
- `version` — string version identifier.
- `prompt_hash` — content hash of the prompt or tool input (raw prompt may be retained or not, per tenant policy).
- `response_hash` — content hash of the response or tool output.
- `at` — ISO-8601 timestamp.
- `decision_contribution` — boolean: did this I/O record contribute to the verdict?

If no models or tools were used, the field MAY be absent.

#### Scenario: Replay requires recorded_io to recompute

- **WHEN** a tape's verdict has `model_contribution: true`
- **THEN** the tape SHALL have at least one `recorded_io` entry with `decision_contribution: true`

#### Scenario: Tape with model_contribution=true and no recorded_io is invalid

- **WHEN** any of `verdict.model_contribution` or any finding's `model_contribution` is true and `recorded_io` is absent or empty
- **THEN** the tape is invalid

### Requirement: Investigation tape MAY carry an EDR handoff reference

If an EDR handoff occurred, the tape SHALL include `handoff_ref` — a pointer to the EDR handoff record (defined in the `edr-handoff` capability). The tape MAY include an inline `handoff_summary` with: `action_type`, `target`, `approval_mode`, `execution_status`. Inline summary fields SHALL match the referenced handoff record.

If no handoff occurred, both fields are absent.

#### Scenario: Handoff summary that disagrees with the handoff record is invalid

- **WHEN** `handoff_summary.execution_status` differs from the referenced handoff record's status
- **THEN** the tape is invalid

### Requirement: Investigation tape SHALL reference its audit chain entry

Every investigation tape SHALL include `audit_ref` — a reference to the audit chain entry that records the tape's existence, fields hash, and verdict signature. The audit chain entry is defined in the `replay-and-audit` capability.

A tape MAY exist in `recording` state without `audit_ref`, but transitioning to `closed` SHALL require `audit_ref` to be set.

#### Scenario: Closed tape without audit_ref is invalid

- **WHEN** a tape's state is `closed` and `audit_ref` is absent
- **THEN** the tape is invalid

### Requirement: Investigation tape SHALL track lifecycle state

Every investigation tape SHALL carry a `state` field with one of: `recording`, `closed`, `replaying`. State transitions:

- `recording` → `closed`: tape is sealed; no further field appends; audit chain entry is signed; verdict is set.
- `closed` → `replaying`: a replay starts; tape itself is not mutated.
- `replaying` → `closed`: replay finishes; tape returns to closed.

A tape SHALL NOT transition from `closed` back to `recording`. A tape SHALL NOT transition from `replaying` to `recording`.

#### Scenario: Reopen a closed tape for editing fails

- **WHEN** a `closed` tape is requested to transition back to `recording`
- **THEN** the request SHALL fail with a `tape_immutable` error

### Requirement: Investigation tape SHALL define a customer-facing surface

When a customer-side reviewer (design partner, auditor, operator) accesses a tape, they SHALL see:

- All Identity fields.
- All `raw_evidence` entries (hashes + retrievable links via tenant-scoped vault if available).
- The full `timeline`.
- All `findings` with severity, evidence links, and confidence bands when present.
- The `verdict` (full).
- `handoff_summary` (when present).
- A boolean `replay_available` derived from whether a replay state exists.

Reviewers SHALL NOT see:

- Internal authorization records or vault audit (those live in `vault-authorization`).
- Raw model prompts or responses unless the tenant policy explicitly opts in.
- Any cross-tenant data.

#### Scenario: Reviewer cannot see model prompts unless opted in

- **WHEN** a reviewer accesses a tape and the tenant has not opted into raw-prompt visibility
- **THEN** `recorded_io` entries SHALL be presented as redacted (hash + version + decision flag only); raw prompts/responses SHALL NOT be returned

#### Scenario: Reviewer cannot see authorization records

- **WHEN** a reviewer accesses a tape
- **THEN** the tape SHALL NOT include vault authorization records or vault audit lines

### Requirement: MVP-required vs. post-MVP fields

The investigation tape SHALL classify its fields as MVP-required or post-MVP per the lists below.

For the design-partner MVP, the following fields are required on every tape:

- All Identity fields.
- `raw_evidence` (with `no_evidence_flag` if empty).
- `timeline` (may be empty if `no_evidence_flag` is set).
- `findings` (with `no_findings_flag` if empty).
- `verdict` with deterministic enum.
- `audit_ref` on close.

The following are post-MVP / situational:

- `recorded_io` — required only when models or tools contributed to a finding or verdict.
- `handoff_ref` and `handoff_summary` — required only when a handoff occurred.
- `confidence_band` on findings — recommended for MVP, required for GA.
- `retention_class` on `raw_evidence` — optional for MVP, required for GA.

#### Scenario: GA requires retention_class

- **WHEN** the architecture moves to GA (per `mvp-scope.md` GA criteria)
- **THEN** every entry in `raw_evidence` SHALL carry `retention_class` (a `MODIFIED Requirements` spec change moves this from optional to required)

### Requirement: Future tape changes go through this spec

Adding, removing, or renaming tape fields, lifecycle states, or customer-facing surface rules SHALL go through a `MODIFIED Requirements` OpenSpec change against `investigation-tape`. Direct edits to `architecture/objects/investigation-tape.md` SHALL be rejected at review.

#### Scenario: Adding a new field requires a spec change

- **WHEN** someone proposes adding a new tape field (e.g., `tenant_classification`)
- **THEN** they SHALL file a `MODIFIED Requirements` change against `investigation-tape` before editing the architecture doc

