# Investigation Tape — Object Architecture

The investigation tape is the central recorded object of Zovark's product wedge. The
canonical wedge statement is:

> **Zovark is the tape recorder for cybersecurity investigations.**
>
> Core flow: **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

This document defines the tape at the architectural level: what fields it carries,
what lifecycle states it moves through, what subset is visible to a customer-side
reviewer, and which fields are required for the design-partner MVP versus reserved
for post-MVP.

The binding spec is `openspec/specs/investigation-tape/spec.md`. Direct edits to this
file without a corresponding `MODIFIED Requirements` change against the
`investigation-tape` capability SHALL be rejected at review.

## Field categories

The tape is organized into eight field categories:

### 1. Identity

| Field | Type | MVP-required | Notes |
|---|---|---|---|
| `tape_id` | string | yes | Unique within tenant. |
| `tenant_id` | string | yes | Tenant scope; never crossed. |
| `created_at` | ISO-8601 timestamp | yes | UTC. |
| `schema_version` | string | yes | E.g., `tape/1.0`. |
| `source_alert_ref` | string | yes | Reference to the source alert envelope. |

### 2. Raw evidence

A list of evidence references. Each entry:

| Field | Type | MVP-required | Notes |
|---|---|---|---|
| `evidence_id` | string | yes | Tenant-scoped. |
| `hash` | string (SHA-256+) | yes | Content hash. |
| `source_type` | enum | yes | `edr_alert`, `network_flow`, `log_record`, `process_event`, … |
| `ingested_at` | ISO-8601 | yes | UTC. |
| `retention_class` | enum | post-MVP | Required at GA. |

If the list is empty, the tape SHALL also carry `no_evidence_flag: true`, and the
verdict SHALL acknowledge the absence.

### 3. Recorded model / tool I/O

A list of records. Present only when models or tools were used. Each entry:

| Field | Type | Notes |
|---|---|---|
| `kind` | enum | `model` or `tool`. |
| `id` | string | Identifier of the model/tool. |
| `version` | string | Version identifier. |
| `prompt_hash` | string | Content hash of the prompt or input. |
| `response_hash` | string | Content hash of the response or output. |
| `at` | ISO-8601 | UTC. |
| `decision_contribution` | bool | Did this contribute to the verdict? |

If `verdict.model_contribution: true` or any finding has `model_contribution: true`,
the tape SHALL contain at least one `recorded_io` entry with
`decision_contribution: true`.

### 4. Timeline

An ordered list of events. Each:

| Field | Type | Notes |
|---|---|---|
| `event_type` | enum | `alert_received`, `evidence_added`, `model_inference`, `tool_call`, `finding_recorded`, `verdict_set`, `handoff_dispatched`, `handoff_executed`, `rollback_recorded`, `audit_signed`. |
| `at` | ISO-8601 | UTC. |
| `actor` | enum | `system`, `model:<id>`, `tool:<id>`, `human:<role>`. |
| `evidence_refs` | list[`evidence_id`] | May be empty. |
| `decision_contribution` | bool | Did this event contribute to the verdict? |

Events SHALL be ordered by non-decreasing `at`.

### 5. Findings

A list of evidence-backed findings. Each:

| Field | Type | MVP-required | Notes |
|---|---|---|---|
| `title` | string | yes | Human-readable. |
| `severity` | enum | yes | `info`, `low`, `medium`, `high`, `critical`. |
| `evidence_refs` | list[`evidence_id`] | yes | At least one. |
| `model_contribution` | bool | yes | |
| `confidence_band` | enum | post-MVP | `low`, `medium`, `high`. Required at GA. |

Empty findings list requires `no_findings_flag: true` and a verdict that
acknowledges absence.

### 6. Verdict

| Field | Type | Notes |
|---|---|---|
| `value` | enum | `benign`, `suspicious_unconfirmed`, `confirmed_malicious`, `inconclusive_insufficient_evidence`. Fixed set; expansion via `MODIFIED Requirements`. |
| `evidence_refs` | list[`evidence_id`] | Evidence the verdict relies on. |
| `model_contribution` | bool | |
| `signing_tag` | opaque string | Signature lives in `audit_ref` entry. |
| `set_at` | ISO-8601 | UTC. |

The verdict SHALL be deterministic given the recorded inputs (raw evidence +
recorded I/O + timeline). Replay (per the `replay-and-audit` capability) MUST
recompute the same value.

### 7. Handoff

Present only when an EDR handoff occurred:

| Field | Type | Notes |
|---|---|---|
| `handoff_ref` | string | Reference to the EDR handoff record (defined in `edr-handoff` capability). |
| `handoff_summary` | object | Inline subset: `action_type`, `target`, `approval_mode`, `execution_status`. MUST match the referenced record. |

### 8. Audit and replay

| Field | Type | Notes |
|---|---|---|
| `audit_ref` | string | Reference to audit chain entry (defined in `replay-and-audit` capability). Required when state is `closed`. |
| `replay_state_ref` | string | Optional. Present only while `replaying`. |

## Lifecycle

Three states with explicit transitions:

```
recording  ──seal──▶  closed  ──replay-start──▶  replaying  ──replay-end──▶  closed
```

- `recording` → `closed`: tape sealed, audit chain entry signed, verdict set,
  no further field appends.
- `closed` → `replaying`: a replay starts; tape is read-only.
- `replaying` → `closed`: replay finishes.

A tape SHALL NOT transition from `closed` back to `recording`. A tape SHALL NOT
transition from `replaying` back to `recording`.

## Customer-facing surface

When a design partner / auditor / operator accesses a tape, they SEE:

- All Identity fields.
- `raw_evidence` entries (hashes + retrievable links via tenant-scoped vault, when M1+ vault is online).
- Full `timeline`.
- All `findings` with severity, evidence links, and (when present) confidence bands.
- The full `verdict`.
- `handoff_summary` (when present).
- `replay_available` boolean (derived from `replay_state_ref`).

They DO NOT SEE:

- Internal authorization records (those live in the `vault-authorization` capability).
- Raw model prompts/responses unless the tenant policy explicitly opts in
  (default: redacted to hash + version + decision flag).
- Cross-tenant data of any kind.

## MVP-required vs. post-MVP

**Required for design-partner MVP:**

- All Identity fields.
- `raw_evidence` (with `no_evidence_flag` if empty).
- `timeline` (may be empty if `no_evidence_flag`).
- `findings` (with `no_findings_flag` if empty).
- `verdict` with deterministic enum.
- `audit_ref` on close.

**Post-MVP / situational:**

- `recorded_io` — required only when models/tools contributed to a finding or verdict.
- `handoff_ref` / `handoff_summary` — required only when a handoff occurred.
- `confidence_band` on findings — recommended for MVP, required for GA.
- `retention_class` on `raw_evidence` — required for GA.

## What this document does not define

- JSON Schema, Avro, Protobuf, or any serialization. Implementation chooses.
- Storage: object store vs. database vs. blob; encryption at rest;
  per-tenant replication.
- Tenant-scoping mechanism (tenant scope is an invariant; mechanism is M1+).
- UI/UX for the reviewer surface.
- The full content of forward-referenced objects (EDR handoff record, audit
  chain entry, replay state) — defined in their own capabilities.

## Build planning

This spec gives the build team enough to scope:

- Storage: 8 categories, with raw evidence and recorded I/O the heaviest payloads.
- API: a tape is created, fields appended during `recording`, sealed at `closed`,
  read-only thereafter.
- UI: customer-facing surface excludes 3 categories of data
  (authorization records, raw model I/O, cross-tenant); the rest is rendered
  by a relatively small set of widgets.
- Tests: every requirement scenario in `openspec/specs/investigation-tape/spec.md`
  is a candidate test case.
