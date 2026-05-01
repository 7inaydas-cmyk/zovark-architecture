# edr-handoff Specification

## Purpose
Defines the EDR handoff record — the structured action recommendation produced from an investigation tape — including required fields, approval modes, idempotency rules, rollback classes, and the linkage to investigation tape, vault authorization, and audit chain.
## Requirements
### Requirement: EDR handoff record SHALL carry a unique handoff_id and tenant scope

Every EDR handoff record SHALL include:

- `handoff_id` — string, unique within tenant.
- `tenant_id` — string.
- `tape_ref` — string referencing the source investigation tape's `tape_id` (defined in `investigation-tape`).

#### Scenario: Handoff without tape_ref is invalid

- **WHEN** a handoff is created without a `tape_ref`
- **THEN** the system SHALL reject the handoff

#### Scenario: Handoff cross-tenant is invalid

- **WHEN** a handoff's `tenant_id` does not match the source tape's `tenant_id`
- **THEN** the handoff is invalid and SHALL be rejected

### Requirement: EDR handoff SHALL have a typed action and a structured target

Every handoff SHALL include:

- `action_type` — enum from a fixed set: `isolate_host`, `kill_process`, `quarantine_file`, `block_hash`, `block_network_indicator`, `revoke_session`, `disable_account`, `notify_only`, `custom`. The `custom` value SHALL include a `custom_action_descriptor` (free-form string) declaring what the custom action does.
- `target` — structured `{kind, identifier, validated_at}` where `kind` is one of `host`, `process`, `file_hash`, `network_ip`, `network_domain`, `session_id`, `account_id`, `custom`; `identifier` is the kind-specific identifier; `validated_at` is the ISO-8601 timestamp when the target was last verified to exist.

The `target.kind` SHALL be consistent with the `action_type` (e.g., `isolate_host` requires `target.kind = host`).

#### Scenario: action_type without compatible target.kind fails

- **WHEN** a handoff has `action_type: isolate_host` and `target.kind: file_hash`
- **THEN** the handoff is invalid

#### Scenario: action_type custom without descriptor fails

- **WHEN** a handoff has `action_type: custom` and no `custom_action_descriptor`
- **THEN** the handoff is invalid

### Requirement: EDR handoff SHALL link to evidence

Every handoff SHALL include `evidence_refs` — a non-empty list of `evidence_id`s drawn from the source tape's `raw_evidence`. These IDs SHALL exist on the referenced tape.

#### Scenario: Handoff with empty evidence_refs is invalid

- **WHEN** `evidence_refs` is empty
- **THEN** the handoff is invalid (every action must be evidence-linked)

#### Scenario: Handoff with evidence_id not present on the tape is invalid

- **WHEN** any `evidence_id` in `evidence_refs` does not appear in the referenced tape's `raw_evidence`
- **THEN** the handoff is invalid

### Requirement: EDR handoff SHALL capture a policy snapshot

Every handoff SHALL include:

- `policy_snapshot` — opaque content hash of the tenant policy version in effect at authorization time.
- `policy_snapshot_version` — string identifier (e.g., semver-ish).

The `policy_snapshot` SHALL match the policy referenced by the `authorization_record_ref` (vault authorization record).

#### Scenario: Mismatched policy_snapshot fails

- **WHEN** the handoff's `policy_snapshot` does not match the authorization record's policy hash
- **THEN** the handoff is invalid and SHALL be rejected

### Requirement: EDR handoff SHALL declare an approval mode

Every handoff SHALL include `approval_mode` — enum: `approval_required` or `autonomous`.

- `approval_required`: dispatch SHALL occur only after a human approval is recorded in `authorization_record_ref`.
- `autonomous`: dispatch MAY occur without per-action human approval; the policy snapshot MUST authorize the `action_type` for autonomous execution.

The `approval_mode` SHALL be set at handoff creation and SHALL NOT change after dispatch.

For the design-partner MVP, the only allowed `approval_mode` is `approval_required` (per `mvp-scope.md`). The `autonomous` mode is reserved for post-MVP and is rejected by MVP policy.

#### Scenario: Autonomous handoff in MVP is rejected by policy

- **WHEN** a handoff is created with `approval_mode: autonomous` under the design-partner MVP policy
- **THEN** the handoff SHALL be rejected (MVP policy disallows autonomous execution)

#### Scenario: Approval mode change after dispatch fails

- **WHEN** a handoff's `approval_mode` is changed after `execution_result.status` reaches `dispatched` or beyond
- **THEN** the modification SHALL be rejected

### Requirement: EDR handoff SHALL reference a vault authorization record

Every handoff SHALL include `authorization_record_ref` — a reference to a `vault-authorization` record (capability defined separately). The vault authorization record SHALL bind the action, tenant, target, expiry, nonce, policy, and approval (when `approval_required`).

For pre-vault-runtime (bootstrap) handoffs, the field MAY be a placeholder string identifying that vault is not yet online; build-time enforcement comes when vault lands per ADR-0028 / ADR-0034.

#### Scenario: Dispatch without authorization_record_ref fails

- **WHEN** a handoff with `approval_mode: approval_required` attempts to advance to `execution_result.status: dispatched` and `authorization_record_ref` is absent or unresolved
- **THEN** dispatch SHALL be blocked

### Requirement: EDR handoff SHALL be idempotent

Every handoff SHALL include `idempotency_key` — a string. Same `idempotency_key` + same `tenant_id` + same `target` + same `action_type` SHALL be treated as the same handoff: a second dispatch SHALL be a no-op at the vendor level, and the existing record SHALL be re-fetched, not re-created.

The idempotency key SHOULD be derived from the source tape's `tape_id` plus a content hash of `action_type + target.identifier`, so duplicate dispatches naturally collide.

#### Scenario: Duplicate dispatch is a no-op

- **WHEN** a handoff is dispatched and a second dispatch with the same idempotency key + same target + same tenant + same action_type occurs
- **THEN** the second dispatch SHALL not call the vendor a second time
- **AND** the audit chain SHALL record the second attempt with `idempotent_replay: true`

#### Scenario: Different idempotency key triggers a new handoff

- **WHEN** a second handoff has a different `idempotency_key` even if other fields match
- **THEN** the second handoff is a new dispatch and SHALL run normally

### Requirement: EDR handoff SHALL track execution result

Every handoff SHALL include `execution_result`:

- `status` — enum: `pending`, `dispatched`, `succeeded`, `failed`, `partial`, `rolled_back`.
- `started_at` — ISO-8601 (set when status becomes `dispatched`).
- `completed_at` — ISO-8601 (set when status reaches a terminal state: `succeeded`, `failed`, `partial`, `rolled_back`).
- `vendor_response_ref` — opaque reference to the vendor adapter's response payload (stored under tenant scope).
- `error` — structured error info if `status = failed` or `partial`.

State transitions SHALL be: `pending → dispatched → {succeeded | failed | partial}`. From any terminal state, a rollback transitions to `rolled_back`.

#### Scenario: Direct pending → succeeded fails

- **WHEN** a handoff transitions from `pending` to `succeeded` without going through `dispatched`
- **THEN** the transition is invalid

#### Scenario: Rollback after a terminal state succeeds

- **WHEN** a handoff with `status: succeeded` undergoes a rollback per `rollback_plan`
- **THEN** the status SHALL transition to `rolled_back`
- **AND** the audit chain entry SHALL record both the original execution and the rollback

### Requirement: EDR handoff SHALL include a rollback plan

Every handoff SHALL include `rollback_plan`:

- `reversibility_class` — enum: `automatic`, `manual_documented`, `irreversible`.
- `vendor_reversal_action` — enum: `release_isolation`, `restore_file`, `unblock_hash`, `unblock_indicator`, `restore_session`, `re_enable_account`, `none`.
- `vendor_reversal_target` — structured (mirrors `target`).
- `manual_steps` — list of strings; populated when `reversibility_class = manual_documented`; empty otherwise.
- `reversal_window` — duration; informational; how long after dispatch reversal is operationally reasonable.
- `idempotency_key` — rollback's own key (separate from handoff's idempotency_key).

When `reversibility_class = irreversible`, `vendor_reversal_action` SHALL be `none` and `manual_steps` SHALL list manual remediation (e.g., for `disable_account`: "operator manually re-enables account via IdP admin console").

#### Scenario: manual_documented requires manual_steps

- **WHEN** `reversibility_class = manual_documented` and `manual_steps` is empty
- **THEN** the handoff is invalid

#### Scenario: irreversible class with vendor_reversal_action != none fails

- **WHEN** `reversibility_class = irreversible` and `vendor_reversal_action` is anything other than `none`
- **THEN** the handoff is invalid (irreversible by definition has no vendor reversal)

### Requirement: EDR handoff SHALL link to audit chain and replay

Every handoff SHALL include:

- `audit_ref` — reference to the audit chain entry recording dispatch + execution + rollback (defined in `replay-and-audit`).
- `replay_linkage` — list of references to the recorded I/O entries on the source tape that informed the decision to dispatch (when models or tools contributed). May be empty for pure-rule-based handoffs.

#### Scenario: Closed handoff without audit_ref fails

- **WHEN** a handoff reaches a terminal `execution_result.status` and `audit_ref` is absent
- **THEN** the handoff is invalid

### Requirement: Future handoff schema changes go through this spec

Adding, removing, or renaming handoff fields, action types, target kinds, approval modes, or rollback classes SHALL go through a `MODIFIED Requirements` OpenSpec change against `edr-handoff`. Direct edits to `architecture/objects/edr-handoff.md` SHALL be rejected at review.

#### Scenario: Adding a new action_type requires a spec change

- **WHEN** someone proposes adding a new `action_type` value (e.g., `kill_container`)
- **THEN** they SHALL file a `MODIFIED Requirements` change against `edr-handoff` first

