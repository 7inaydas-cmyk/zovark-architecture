# Slice 001 — Requirements

## Overview

Slice 001 is the smallest path that exercises every governing spec in the Zovark
architecture. It takes one static EDR-like JSON sample as input and produces a
complete proof package: an approval-required EDR action card, the evidence ledger,
timeline, findings, deterministic verdict, and a replayable proof bundle.

No network calls. No credentials. No live LLM. No autonomous action.

The completion criterion is the build rule from `architecture/one-page-architecture.md`:

> Does the proof package show the evidence, explain the verdict, record the approval path, and provide a replayable verification?

The internal architecture substrate is the investigation tape. The external hero
artifacts are the **EDR action card** (`edr-handoff.json`) and the **replayable
proof package** (`replay-report.json` + `customer-report.md`).

---

## Hard constraints (non-negotiable)

- No live EDR API calls.
- No autonomous EDR action dispatch.
- No Sigma rule generation.
- No SIEM publication.
- No production credential vault runtime.
- No full web UI.
- No live LLM calls during replay.
- No live LLM calls at all in Slice 001 (rule-driven findings only; `model_contribution: false` everywhere).
- `authorization_record_ref` is the placeholder string `vault://placeholder/bootstrap`.
- `execution_result.status` ends at `pending`.
- `execution_result.reason` is `recommendation_only_no_dispatcher_in_slice_001`.

---

## Requirements

### REQ-001 — Static input ingestion

The system SHALL accept a single static EDR-like JSON file as its only input.

The input file SHALL conform to a documented sample schema (see Design). The system
SHALL NOT make any network call to ingest the input.

**Acceptance criteria:**

- AC-001-1: Given a valid sample JSON file, the system reads it without error.
- AC-001-2: Given a missing or malformed JSON file, the system exits with a clear
  error message and a non-zero exit code.
- AC-001-3: No network socket is opened during ingestion.

---

### REQ-002 — Evidence normalization

The system SHALL normalize the raw input into evidence entries conforming to the
`investigation-tape` spec's `raw_evidence[]` shape.

Each evidence entry SHALL carry:
- `evidence_id` — deterministically derived from the source content (not random).
- `hash` — SHA-256 hex digest of the canonical JSON bytes of the source object.
- `source_type` — mapped from the input (e.g., `edr_alert`, `process_event`).
- `ingested_at` — ISO-8601 UTC timestamp set at processing time.
- `raw_content` — the original source object dict stored inline, so the replay
  engine can recompute the hash without re-reading the input file.

`retention_class` is omitted (post-MVP per the architecture spec).
`raw_content` is a Slice 001 convenience field; post-MVP it is replaced by a
vault retrieval reference.

**Acceptance criteria:**

- AC-002-1: Every evidence entry has a non-empty `evidence_id`.
- AC-002-2: Every evidence entry has a `hash` that is the SHA-256 hex digest of the
  canonical JSON bytes of the source object.
- AC-002-3: Running the same input twice produces byte-identical `evidence_id` and
  `hash` values.
- AC-002-4: Mutating one byte of the source object produces a different `hash`.

---

### REQ-003 — Investigation tape creation

The system SHALL create an investigation tape conforming to the `investigation-tape`
spec.

The tape SHALL carry all MVP-required fields:
- Identity: `tape_id`, `tenant_id`, `created_at`, `schema_version`, `source_alert_ref`.
- `raw_evidence[]` — populated from REQ-002.
- `timeline[]` — populated from REQ-004.
- `findings[]` — populated from REQ-005.
- `verdict` — populated from REQ-006.
- `state` — transitions from `recording` to `closed` exactly once.
- `audit_ref` — set before the tape is written to `closed` state.
- `handoff_ref` and `handoff_summary` — set when a handoff is produced (REQ-007).

`recorded_io` is absent (no models or tools used in Slice 001).

**Acceptance criteria:**

- AC-003-1: The output tape JSON contains all identity fields with non-empty values.
- AC-003-2: `state` is `closed` in the output file.
- AC-003-3: `audit_ref` is present and non-empty in the output file.
- AC-003-4: `schema_version` is `tape/1.0`.
- AC-003-5: A tape without `tape_id` is rejected before writing.
- AC-003-6: A tape without `tenant_id` is rejected before writing.
- AC-003-7: The tape does not contain a `replay_state_ref` field.
- AC-003-8: The tape does not contain a `state` value of `replaying`.

---

### REQ-004 — Timeline construction

The system SHALL build a `timeline[]` on the tape. Events SHALL be appended in
non-decreasing timestamp order.

The following timeline events SHALL be emitted for Slice 001:

| Event type | When emitted |
|---|---|
| `alert_received` | When the source alert is ingested |
| `evidence_added` | Once per evidence entry added to `raw_evidence[]` |
| `finding_recorded` | Once per finding added to `findings[]` |
| `verdict_set` | When the verdict is set |
| `handoff_dispatched` | When the handoff record is created (status `pending`) |
| `audit_signed` | When the audit chain entry is written |

Each event SHALL carry: `event_type`, `at` (ISO-8601 UTC), `actor` (`system` for all
Slice 001 events), `evidence_refs[]` (the relevant evidence IDs, may be empty),
`decision_contribution` (boolean).

**Acceptance criteria:**

- AC-004-1: The output tape contains a `timeline` array with at least the six event
  types listed above.
- AC-004-2: All timeline events are in non-decreasing `at` order.
- AC-004-3: Every `evidence_added` event references the `evidence_id` of the entry
  it records.
- AC-004-4: The `verdict_set` event has `decision_contribution: true`.
- AC-004-5: No timeline event has an `actor` other than `system` in Slice 001.

---

### REQ-005 — Rule-driven findings

The system SHALL derive findings from the evidence using a static rule set. No model
or LLM is involved. `model_contribution` SHALL be `false` on every finding.

The rule set for Slice 001 SHALL include at minimum:

| Rule ID | Trigger condition | Finding title | Severity |
|---|---|---|---|
| RULE-001 | `source_type == edr_alert` | "EDR alert detected" | `medium` |
| RULE-002 | `source_type == process_event` | "Suspicious process event" | `high` |
| RULE-003 | No evidence entries (empty ledger) | "No evidence — inconclusive" | `info` |

Each finding SHALL carry:
- `title` — from the rule.
- `severity` — from the rule.
- `evidence_refs[]` — the `evidence_id`(s) that triggered the rule (at least one,
  unless RULE-003 applies and `no_findings_flag: true` is set).
- `model_contribution: false`.

If no rules fire and the evidence ledger is non-empty, the system SHALL set
`no_findings_flag: true` and produce a verdict of `inconclusive_insufficient_evidence`.

**Acceptance criteria:**

- AC-005-1: Every finding has `model_contribution: false`.
- AC-005-2: Every finding has at least one entry in `evidence_refs[]`, unless
  `no_findings_flag: true` is set.
- AC-005-3: Every `evidence_id` in a finding's `evidence_refs[]` exists in the
  tape's `raw_evidence[]`.
- AC-005-4: Given the standard sample input, at least one finding is produced.
- AC-005-5: An empty evidence ledger produces `no_findings_flag: true` and a verdict
  of `inconclusive_insufficient_evidence`.

---

### REQ-006 — Deterministic verdict

The system SHALL set a verdict deterministically from the findings. The verdict value
SHALL be drawn from the fixed enum:

```
benign | suspicious_unconfirmed | confirmed_malicious | inconclusive_insufficient_evidence
```

The verdict derivation rule for Slice 001:

| Condition | Verdict value |
|---|---|
| Any finding with severity `critical` or `high` | `confirmed_malicious` |
| Any finding with severity `medium` and none `high`/`critical` | `suspicious_unconfirmed` |
| All findings severity `low` or `info` | `benign` |
| `no_findings_flag: true` | `inconclusive_insufficient_evidence` |

The verdict SHALL carry:
- `value` — from the table above.
- `evidence_refs[]` — union of all finding `evidence_refs[]`.
- `model_contribution: false`.
- `signing_tag` — a deterministic tag derived from the tape's canonical bytes (see
  Design for derivation).
- `set_at` — ISO-8601 UTC timestamp.

**Acceptance criteria:**

- AC-006-1: The verdict `value` is one of the four allowed enum values.
- AC-006-2: `model_contribution` is `false`.
- AC-006-3: `evidence_refs[]` is non-empty when findings exist.
- AC-006-4: Given the same input, the same verdict value is produced on every run.
- AC-006-5: A verdict value outside the fixed enum is rejected.
- AC-006-6: The tape cannot be closed without a `verdict.value` set.

---

### REQ-007 — Approval-required EDR action card

The system SHALL produce an approval-required EDR action card conforming to the
`edr-handoff` spec. The output file is `edr-handoff.json`. The card is the primary
decision artifact: it names the recommended action, the evidence basis, the approval
gate, and the reversibility/recovery classification before any action is dispatched.

The action card SHALL carry all 14 required fields:

**Identity (3):** `handoff_id`, `tenant_id`, `tape_ref`.

**Action and target (2):** `action_type` and `target` derived from the findings.
For Slice 001, the default action is `notify_only` with `target.kind: custom` and
`target.identifier: "slice-001-static-sample"`. If a finding with severity `high` or
`critical` is present, the action is `isolate_host` with `target.kind: host` and
`target.identifier` taken from the sample input's host field.

**Evidence and policy (3):** `evidence_refs[]` (from verdict evidence refs),
`policy_snapshot` (SHA-256 of the literal string `slice-001-bootstrap-policy`),
`policy_snapshot_version: "0.0.1-bootstrap"`.

**Authorization (2):** `approval_mode: approval_required`,
`authorization_record_ref: "vault://placeholder/bootstrap"`.

**Execution (1):** `execution_result` with `status: pending` and
`reason: "recommendation_only_no_dispatcher_in_slice_001"`.

**Idempotency (1):** `idempotency_key` derived as SHA-256 of
`tape_id + ":" + action_type + ":" + target.identifier`.

**Rollback / reversibility (1):** `rollback_plan` with a first-class
`reversibility_class` drawn from the following three-value enum:

| `reversibility_class` | Meaning | Slice 001 mapping |
|---|---|---|
| `reversible_by_edr` | EDR vendor exposes a reversal API; reversal is automatic | `isolate_host` → `release_isolation` |
| `manual_recovery_required` | No vendor reversal API; operator must follow documented steps | (not triggered in Slice 001 sample) |
| `irreversible_requires_compensation` | Action cannot be undone; compensating action required | (not triggered in Slice 001 sample) |

For Slice 001:
- `notify_only` → `reversibility_class: reversible_by_edr`, `vendor_reversal_action: none`.
- `isolate_host` → `reversibility_class: reversible_by_edr`, `vendor_reversal_action: release_isolation`.

**Linkage (2):** `audit_ref` (set after the audit chain entry is written),
`replay_linkage: []` (no recorded I/O in Slice 001).

The tape SHALL carry `handoff_ref` (the `handoff_id`) and `handoff_summary`
(`action_type`, `target`, `approval_mode`, `execution_status: pending`).

**Acceptance criteria:**

- AC-007-1: The action card contains all 14 fields.
- AC-007-2: `approval_mode` is `approval_required`.
- AC-007-3: `authorization_record_ref` is `vault://placeholder/bootstrap`.
- AC-007-4: `execution_result.status` is `pending`.
- AC-007-5: `execution_result.reason` is `recommendation_only_no_dispatcher_in_slice_001`.
- AC-007-6: `evidence_refs[]` is non-empty.
- AC-007-7: Every `evidence_id` in `evidence_refs[]` exists in the tape's `raw_evidence[]`.
- AC-007-8: `tape_ref` matches the tape's `tape_id`.
- AC-007-9: `tenant_id` matches the tape's `tenant_id`.
- AC-007-10: `idempotency_key` is deterministic — same input produces same key.
- AC-007-11: `rollback_plan.reversibility_class` is one of `reversible_by_edr`,
  `manual_recovery_required`, or `irreversible_requires_compensation`.
- AC-007-12: `isolate_host` action produces `reversibility_class: reversible_by_edr`
  and `vendor_reversal_action: release_isolation`.
- AC-007-13: `handoff_summary.execution_status` matches `execution_result.status`.

---

### REQ-008 — Tape sealing and audit chain entry

The system SHALL seal the tape (transition `state: recording → closed`) and write an
audit chain entry.

The audit chain entry SHALL conform to the `replay-and-audit` spec and carry:
- `entry_id` — deterministically derived.
- `tenant_id` — matches the tape.
- `sequence: 1` (first and only entry in Slice 001).
- `event_type: tape_recording_closed`.
- `payload` — includes `tape_id`, `verdict_value`, `fields_hash` (SHA-256 of the
  tape's canonical JSON bytes at close time).
- `created_at` — ISO-8601 UTC.
- `prev_entry_hash` — SHA-256 of the literal string `genesis` (no prior entry in
  Slice 001).
- `this_entry_hash` — SHA-256 of the canonical JSON bytes of this entry.
- `signed_root: null` (root signing is stubbed in Slice 001; the field is present
  but null).

**Acceptance criteria:**

- AC-008-1: The audit chain entry JSON file is written to the output directory.
- AC-008-2: `event_type` is `tape_recording_closed`.
- AC-008-3: `sequence` is `1`.
- AC-008-4: `this_entry_hash` is the SHA-256 of the canonical JSON bytes of the entry
  (excluding the `this_entry_hash` field itself during computation — see Design).
- AC-008-5: `signed_root` is `null`.
- AC-008-6: The tape's `audit_ref` matches the audit chain entry's `entry_id`.
- AC-008-7: The tape's `state` is `closed` after sealing.

---

### REQ-009 — Replay report

The system SHALL run a replay against the closed tape and produce a replay report.

The replay SHALL:
1. Verify the SHA-256 hash of every `raw_evidence` entry against the stored `hash`.
2. Recompute the verdict from the recorded inputs using the same rule set as REQ-006.
3. Compare the recomputed verdict to the stored `verdict.value`.
4. Emit a `tape_replayed` audit chain entry.

The replay report SHALL bundle:
- `replay_state` — conforming to the `replay-and-audit` spec, with:
  - `replay_id` — deterministically derived.
  - `tape_ref` — the tape's `tape_id`.
  - `tenant_id` — matches the tape.
  - `mode: recorded_output`.
  - `schema_pin: "tape/1.0"`.
  - `tool_catalog_pin: "none-slice-001"`.
  - `model_versions_pin: []`.
  - `state` — `succeeded` if hashes verify and verdict matches; `mismatch` if verdict
    differs; `failed` if any hash fails.
  - `mismatch_details` — populated when `state: mismatch`.
  - `unsigned_tail_replay: true` (the audit entry is in the unsigned tail in Slice 001).
  - `started_at`, `completed_at`.
- `audit_chain_entry` — the `tape_replayed` audit chain entry produced by this replay.

The replay SHALL make no network calls and invoke no LLM.

**Acceptance criteria:**

- AC-009-1: The replay report JSON file is written to the output directory.
- AC-009-2: `replay_state.mode` is `recorded_output`.
- AC-009-3: `replay_state.state` is `succeeded` when the same input is processed twice.
- AC-009-4: If any `raw_evidence` entry's hash is manually corrupted before replay,
  `replay_state.state` is `failed` with reason `evidence_corruption`.
- AC-009-5: If the verdict derivation rule is changed to produce a different value,
  `replay_state.state` is `mismatch` and `mismatch_details` names the differing field.
- AC-009-6: No network socket is opened during replay.
- AC-009-7: The `tape_replayed` audit chain entry is present in the replay report.
- AC-009-8: `unsigned_tail_replay` is `true`.

---

### REQ-010 — Determinism and byte-identical output

The system SHALL produce byte-identical output for the same input.

Specifically:
- Same input JSON → same `evidence_id` values.
- Same input JSON → same `hash` values.
- Same input JSON → same `verdict.value`.
- Same input JSON → same `idempotency_key`.
- Same input JSON → same `signing_tag`.
- Same input JSON → same `this_entry_hash` on the audit chain entry.

Timestamps (`created_at`, `ingested_at`, `set_at`, etc.) are the only fields that
may differ between runs, as they record wall-clock time. All derived/computed fields
must be deterministic.

**Acceptance criteria:**

- AC-010-1: Running the CLI twice on the same input produces identical values for all
  non-timestamp fields.
- AC-010-2: The `verdict.value` is identical across runs.
- AC-010-3: The `idempotency_key` is identical across runs.
- AC-010-4: The `signing_tag` is identical across runs.

---

### REQ-011 — CLI interface

The system SHALL expose a single CLI command that processes the static sample and
writes all output artifacts to a specified output directory.

```
python -m zovark.slice001 \
  --input samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

The command SHALL exit 0 on success and non-zero on any error. It SHALL print a
summary of produced artifacts to stdout on success.

**Acceptance criteria:**

- AC-011-1: The command exits 0 on a valid input.
- AC-011-2: The command exits non-zero on a missing input file.
- AC-011-3: The command exits non-zero on a malformed input file.
- AC-011-4: All output artifacts are written to the specified output directory.
- AC-011-5: The command prints the paths of all produced artifacts on success.
- AC-011-6: No credentials, API keys, or environment variables are required to run
  the command.

---

### REQ-012 — Output artifact list

The system SHALL produce the following artifacts in the output directory:

| Filename | Contents |
|---|---|
| `investigation-tape.json` | The complete closed investigation tape |
| `evidence-ledger.json` | The `raw_evidence[]` array extracted from the tape |
| `timeline.json` | The `timeline[]` array extracted from the tape |
| `findings.json` | The `findings[]` array extracted from the tape |
| `verdict.json` | The `verdict` object extracted from the tape |
| `edr-handoff.json` | The approval-required EDR action card (recommended action, evidence basis, approval gate, reversibility class) |
| `audit-chain-entry.json` | The `tape_recording_closed` audit chain entry |
| `replay-report.json` | The replay state + `tape_replayed` audit chain entry bundle |
| `customer-report.md` | Human-readable summary answering the build rule question |

All JSON files SHALL be valid JSON. All JSON files SHALL be human-readable
(pretty-printed, 2-space indent). `customer-report.md` SHALL be valid Markdown.

**Acceptance criteria:**

- AC-012-1: All nine files are present in the output directory after a successful run.
- AC-012-2: All eight JSON files are valid JSON.
- AC-012-3: `evidence-ledger.json` content matches `investigation-tape.json`'s
  `raw_evidence` field.
- AC-012-4: `timeline.json` content matches `investigation-tape.json`'s `timeline` field.
- AC-012-5: `findings.json` content matches `investigation-tape.json`'s `findings` field.
- AC-012-6: `verdict.json` content matches `investigation-tape.json`'s `verdict` field.
- AC-012-7: `customer-report.md` opens with the recommended action, target, approval
  mode, evidence summary, verdict, reversibility/recovery classification, and replay
  proof status — in that order — before any internal substrate fields.
