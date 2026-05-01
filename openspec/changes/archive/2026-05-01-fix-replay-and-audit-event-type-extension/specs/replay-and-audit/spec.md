## MODIFIED Requirements

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

The fixed `event_type` enum: `tape_recording_started`, `tape_recording_closed`, `tape_replayed`, `handoff_dispatched`, `handoff_executed`, `handoff_rolled_back`, `vault_authorization_issued`, `vault_authorization_revoked`, `vault_authorization_use_rejected`, `disaster_recovery_restore_completed`.

Adding a new event type requires a `MODIFIED Requirements` change against this spec.

#### Scenario: Audit entry with sequence gap is invalid

- **WHEN** an audit chain has an entry with `sequence: 7` but no entry with `sequence: 6` exists
- **THEN** the chain is invalid

#### Scenario: Audit entry with event_type outside the fixed enum is invalid

- **WHEN** an audit entry has `event_type: random_string`
- **THEN** the entry is invalid
