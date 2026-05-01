## MODIFIED Requirements

### Requirement: Investigation tape SHALL track lifecycle state

Every investigation tape SHALL carry a `state` field with one of: `recording`, `closed`. The lifecycle is one-way:

- `recording` → `closed`: tape is sealed; no further field appends; audit chain entry is signed; verdict is set.

A `closed` tape SHALL NOT transition to any other state. There is no `replaying` tape state — replay status lives entirely in the `replay-and-audit` capability's `replay_state` object, which has its own state enum (`pending, running, succeeded, mismatch, failed`).

This guarantees the tape is genuinely immutable after `closed`: no field — including `state` — changes during replay. The tape's canonical-bytes hash, anchored in the audit chain, stays stable for the life of the tape.

#### Scenario: Reopen a closed tape for editing fails

- **WHEN** a `closed` tape is requested to transition back to `recording`
- **THEN** the request SHALL fail with a `tape_immutable` error

#### Scenario: Tape state never changes during replay

- **WHEN** a replay starts, runs, or completes against a `closed` tape
- **THEN** the tape's `state` SHALL remain `closed`
- **AND** no other tape field SHALL be modified

#### Scenario: Tape state enum value `replaying` is rejected

- **WHEN** any code path or schema validator encounters a tape with `state: replaying`
- **THEN** the tape is invalid (the value is not in the allowed enum)

### Requirement: Investigation tape SHALL define a customer-facing surface

When a customer-side reviewer (design partner, auditor, operator) accesses a tape, they SHALL see:

- All Identity fields.
- All `raw_evidence` entries (hashes + retrievable links via tenant-scoped vault if available).
- The full `timeline`.
- All `findings` with severity, evidence links, and confidence bands when present.
- The `verdict` (full).
- `handoff_summary` (when present).
- A boolean `replay_available` derived by querying the `replay-and-audit` capability's replay-state store for any `replay_state` object whose `tape_ref` equals this tape's `tape_id`. If at least one such object exists in any state, `replay_available` is `true`.

Reviewers SHALL NOT see:

- Internal authorization records or vault audit (those live in `vault-authorization`).
- Raw model prompts or responses unless the tenant policy explicitly opts in.
- Any cross-tenant data.

The tape SHALL NOT carry a `replay_state_ref` field. Replay status is governed entirely by the `replay-and-audit` capability and is queried, not stored, on the tape side.

#### Scenario: Reviewer cannot see model prompts unless opted in

- **WHEN** a reviewer accesses a tape and the tenant has not opted into raw-prompt visibility
- **THEN** `recorded_io` entries SHALL be presented as redacted (hash + version + decision flag only); raw prompts/responses SHALL NOT be returned

#### Scenario: Reviewer cannot see authorization records

- **WHEN** a reviewer accesses a tape
- **THEN** the tape SHALL NOT include vault authorization records or vault audit lines

#### Scenario: replay_available is true when a replay state exists

- **WHEN** at least one `replay_state` object exists in the `replay-and-audit` store with `tape_ref` matching this tape's `tape_id`
- **THEN** the customer-facing `replay_available` derived value SHALL be `true`

#### Scenario: replay_available is false when no replay state exists

- **WHEN** no `replay_state` object references this tape
- **THEN** the customer-facing `replay_available` derived value SHALL be `false`
