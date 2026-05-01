# replay-and-audit Specification

## Purpose
TBD - created by archiving change fix-replay-and-audit-semantics. Update Purpose after archive.
## Requirements
### Requirement: Replay state object SHALL pin schema, tools, and models

Every replay SHALL be governed by a `replay_state` object including:

- `replay_id` — string, unique within tenant.
- `tape_ref` — string referencing the source tape's `tape_id`.
- `tenant_id` — same as the tape.
- `mode` — enum: `recorded_output` (default) or `forensic_reexecution`.
- `schema_pin` — string; the tape's `schema_version` at recording time. Replay SHALL use this pinned schema.
- `tool_catalog_pin` — string; the tool catalog version at recording time. Replay SHALL rebind tool calls against this pinned version, not the current catalog.
- `model_versions_pin` — list of `(model_id, version)` from the tape's `recorded_io`.
- `state` — enum: `pending`, `running`, `succeeded`, `mismatch`, `failed`.
- `started_at`, `completed_at` — ISO-8601.
- `mismatch_details` — populated when state = `mismatch`.

#### Scenario: Replay against a different tool catalog version is invalid

- **WHEN** a replay attempts to rebind tool calls against a tool catalog version different from `tool_catalog_pin`
- **THEN** the replay SHALL be rejected with `version_pin_violation`

#### Scenario: Replay without model_versions_pin when the tape used models is invalid

- **WHEN** the source tape has `recorded_io` entries with `kind: model` and the replay's `model_versions_pin` does not include those models and versions
- **THEN** the replay SHALL be rejected

### Requirement: Recorded-output replay SHALL NOT call live LLMs or live tools

Replays in mode `recorded_output` SHALL NOT make any live network call to a model API or tool API. All model and tool I/O SHALL come from the source tape's `recorded_io`.

#### Scenario: Live model call during recorded_output replay fails

- **WHEN** a replay in mode `recorded_output` attempts a live model API call
- **THEN** the replay engine SHALL block the call and transition `state` to `failed` with reason `live_call_attempted`

### Requirement: Replay SHALL verify evidence hashes

For every entry in the source tape's `raw_evidence`, replay SHALL recompute the content hash and compare against the recorded `hash`. Any mismatch SHALL transition `state` to `failed` with reason `evidence_corruption`.

#### Scenario: Tampered evidence is detected

- **WHEN** the recomputed hash of any `raw_evidence` entry differs from the stored hash
- **THEN** replay SHALL fail with `evidence_corruption` and identify the affected `evidence_id`

### Requirement: Replay SHALL recompute the verdict deterministically

Replay SHALL recompute the verdict from the recorded inputs (raw evidence + recorded I/O + timeline) and compare to the tape's stored `verdict.value`. If they differ, `state` SHALL transition to `mismatch` with `mismatch_details` listing the differing fields. If they match, `state` SHALL transition to `succeeded`.

#### Scenario: Verdict matches → succeeded

- **WHEN** the recomputed verdict equals the stored verdict and all evidence hashes verify
- **THEN** `state` SHALL be `succeeded`

#### Scenario: Verdict differs → mismatch

- **WHEN** the recomputed verdict differs from the stored verdict
- **THEN** `state` SHALL be `mismatch` and `mismatch_details` SHALL list the differing fields (verdict, finding, timeline event)

### Requirement: Forensic re-execution SHALL produce a new tape

Replays in mode `forensic_reexecution` re-run models and tools live. They SHALL produce a *new* investigation tape rather than mutating the original. The new tape's `source_alert_ref` MAY reference the original tape's `source_alert_ref` for traceability.

Forensic re-execution is out of design-partner MVP scope per `mvp-scope.md`; specified here for completeness.

#### Scenario: Forensic re-execution does not mutate the source tape

- **WHEN** a replay in mode `forensic_reexecution` completes
- **THEN** the source tape's fields SHALL be unchanged
- **AND** a new tape with its own `tape_id` SHALL be created carrying the re-executed results

### Requirement: Audit chain entry SHALL have canonical fields and ordering

Every audit chain entry SHALL include:

- `entry_id` — string, unique within tenant.
- `tenant_id` — string.
- `sequence` — integer, tenant-scoped, monotonically increasing, no gaps.
- `event_type` — enum from the fixed set (see below).
- `payload` — structured, event-specific.
- `created_at` — ISO-8601.
- `prev_entry_hash` — content hash of the previous entry's canonical bytes.
- `this_entry_hash` — content hash of this entry's canonical bytes.
- `signed_root` — `{ ref, signed_at }` or null until the next root signature lands.

The fixed `event_type` enum: `tape_recording_started`, `tape_recording_closed`, `tape_replayed`, `handoff_dispatched`, `handoff_executed`, `handoff_rolled_back`, `vault_authorization_issued`, `vault_authorization_revoked`, `disaster_recovery_restore_completed`.

Adding a new event type requires a `MODIFIED Requirements` change against this spec.

#### Scenario: Audit entry with sequence gap is invalid

- **WHEN** an audit chain has an entry with `sequence: 7` but no entry with `sequence: 6` exists
- **THEN** the chain is invalid

#### Scenario: Audit entry with event_type outside the fixed enum is invalid

- **WHEN** an audit entry has `event_type: random_string`
- **THEN** the entry is invalid

### Requirement: Audit chain entries SHALL canonicalize identically across implementations

Audit chain entries SHALL be serialized to canonical form before hashing, using these rules:

1. Object keys are sorted lexicographically.
2. Strings are UTF-8 encoded.
3. Numbers are integers or finite decimals; no NaN, no infinity.
4. Timestamps are ISO-8601 with explicit `Z` for UTC.
5. Booleans are lowercase `true`/`false`.
6. Null is `null`.
7. Arrays preserve order.
8. No trailing whitespace.

Two compliant implementations SHALL produce byte-identical canonical forms.

#### Scenario: Differing key order produces different bytes — invalid

- **WHEN** a serializer emits two entries with the same logical content but different key order
- **THEN** at most one is canonical; the other SHALL be rejected by canonicalization-aware verification

### Requirement: Audit chain insertions SHALL be tenant-scoped and gap-free

Audit chain insertions within one tenant SHALL be serialized: a single writer per tenant assigns the next `sequence`. Concurrent appenders queue. The chain SHALL have no gaps.

Cross-tenant insertions are independent.

#### Scenario: Two concurrent inserts for one tenant get sequential numbers

- **WHEN** two concurrent processes attempt to append to the same tenant's audit chain
- **THEN** they receive distinct, sequential `sequence` numbers; no gap exists

### Requirement: Audit chain SHALL produce signed roots periodically and on triggers

A "root" signature SHALL sign a snapshot of the chain head. Roots SHALL be produced:

- Periodically: at most every 60 seconds (default per-tenant policy; minimum 5s, maximum 5min).
- Triggered: forced after every entry of `event_type` `handoff_dispatched` or `disaster_recovery_restore_completed`.

A signed root attests that all entries with `sequence ≤ K` are committed. The signature scheme uses a key issued from the tenant's vault per ADR-0042; this spec does not name the algorithm.

#### Scenario: handoff_dispatched triggers a root signature

- **WHEN** an entry with `event_type: handoff_dispatched` is appended
- **THEN** a root signature SHALL be triggered before the next periodic interval

### Requirement: Audit chain SHALL distinguish unsigned tail from signed range

Entries appended after the most recent root signature are the **unsigned tail**. Reviewers SHALL distinguish:

- **Signed range**: entries up to and including the most recent signed root's `sequence`. Verifiable.
- **Unsigned tail**: entries after the signed root. Locally committed but not yet attested.

Replays SHOULD wait until the source tape's audit entries are in the signed range. Replays MAY proceed against an unsigned tail only when the replay record carries an explicit `unsigned_tail_replay: true` flag.

DR restores SHALL prefer signed-root snapshots over unsigned tails.

#### Scenario: Replay against unsigned tail without flag fails

- **WHEN** a replay's source tape's `audit_ref` points to an entry in the unsigned tail and the replay record does not carry `unsigned_tail_replay: true`
- **THEN** the replay SHALL be rejected with `unsigned_tail_replay_disallowed`

#### Scenario: Replay against unsigned tail with flag succeeds

- **WHEN** the replay record explicitly sets `unsigned_tail_replay: true`
- **THEN** the replay SHALL proceed and the resulting `tape_replayed` audit entry SHALL also carry the flag

### Requirement: Audit chain SHALL record DR restore completion with declared loss window

The `disaster_recovery_restore_completed` event's `payload` SHALL include:

- `restore_started_at_ns`
- `restore_completed_at_ns`
- `restored_to_lsn`
- `restored_to_timestamp`
- `pre_restore_latest_root_hash_if_available`
- `post_restore_chain_root`
- `known_data_loss_window_start`
- `known_data_loss_window_end`
- `operator_id`
- `incident_id`

A valid post-restore audit chain proves internal consistency of the recovered chain. It does NOT prove that no data loss occurred. Verifiers SHALL recognize the state `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` for chains that are internally consistent from the restore point forward and explicitly declare the loss window.

#### Scenario: Restore event missing loss window fields fails

- **WHEN** a `disaster_recovery_restore_completed` entry omits `known_data_loss_window_start` or `known_data_loss_window_end`
- **THEN** the entry is invalid

#### Scenario: Verifier reports VALID_AFTER_RESTORE_WITH_DECLARED_GAP after a restore

- **WHEN** an audit chain contains a valid `disaster_recovery_restore_completed` entry and all subsequent entries form a consistent chain
- **THEN** verification SHALL report `VALID_AFTER_RESTORE_WITH_DECLARED_GAP`
- **AND** SHALL surface the declared loss window to the reviewer

### Requirement: Future replay/audit changes go through this spec

Adding, removing, or modifying replay state fields, audit chain entry fields, event-type enum values, canonicalization rules, root signature triggers, or DR restore-event payload fields SHALL go through a `MODIFIED Requirements` OpenSpec change against `replay-and-audit`. Direct edits to `architecture/objects/replay-and-audit.md` SHALL be rejected at review.

#### Scenario: Adding a new event_type requires a spec change

- **WHEN** someone proposes adding a new audit event type
- **THEN** they SHALL file a `MODIFIED Requirements` change against `replay-and-audit` first

