## ADDED Requirements

### Requirement: Vault authorization record SHALL bind action+tenant+target+policy+nonce

Every vault authorization record SHALL include:

- `authorization_id` — string, unique within tenant.
- `tenant_id` — string.
- `action_type` — string mirroring `edr-handoff.action_type` enum (or a vault-specific operation type when used outside EDR handoffs).
- `target` — structured `{kind, identifier}` mirroring `edr-handoff.target` shape.
- `policy_snapshot` — opaque content hash of the tenant policy version in effect at issuance.
- `policy_snapshot_version` — string identifier.
- `approval_ref` — string or null. Non-null when the action requires per-action human approval.
- `issued_at` — ISO-8601.
- `expires_at` — ISO-8601, strictly after `issued_at`.
- `nonce` — cryptographically random string with at least 128 bits of entropy, single-use within tenant.
- `signing_tag` — opaque tag verifiable against the tenant's vault root key.
- `state` — enum: `active`, `consumed`, `revoked`, `expired`.

Per `INV-019`, every vault access requires per-action authorization; no broad credentials are permitted. The record's binding fields collectively scope the authorization to exactly one operation.

#### Scenario: Authorization without nonce is invalid

- **WHEN** an authorization record is issued without a `nonce`
- **THEN** the issuance SHALL be rejected

#### Scenario: Authorization with `expires_at` ≤ `issued_at` is invalid

- **WHEN** a record's `expires_at` equals or precedes `issued_at`
- **THEN** the record is invalid

#### Scenario: Authorization without policy_snapshot is invalid

- **WHEN** a record omits `policy_snapshot`
- **THEN** the record is invalid (every authorization is bound to a policy version)

### Requirement: Authorization verification SHALL re-check every binding on every use

When an authorization record is presented for use (e.g., to dispatch an EDR handoff or perform a vault op), the verifier SHALL:

1. Confirm `state = active`.
2. Confirm current time ≤ `expires_at`.
3. Confirm `action_type` matches the requested operation.
4. Confirm `tenant_id` matches the requesting tenant.
5. Confirm `target` matches the operation's target exactly (kind and identifier).
6. Confirm `policy_snapshot` matches the policy in effect at use time. Policy drift between issuance and use SHALL fail closed.
7. Confirm `approval_ref` (when non-null) resolves to a valid approval record from a human authorizer.
8. Confirm `signing_tag` verifies against the tenant's vault root key.
9. Confirm the `nonce` has not been previously consumed under this tenant.

Any check failure SHALL reject the operation. The audit chain SHALL record a `vault_authorization_use_rejected` event with the failure reason.

#### Scenario: Expired authorization is rejected

- **WHEN** an authorization record has `expires_at` in the past
- **THEN** the verifier SHALL reject the use and emit `vault_authorization_use_rejected` with reason `expired`

#### Scenario: Policy drift fails closed

- **WHEN** the policy in effect at use time differs from the record's `policy_snapshot`
- **THEN** the verifier SHALL reject with reason `policy_drift`

#### Scenario: Replayed nonce is rejected

- **WHEN** a `nonce` previously marked `consumed` is re-presented
- **THEN** the verifier SHALL reject with reason `nonce_replay`

#### Scenario: Cross-tenant authorization use is rejected

- **WHEN** tenant A presents an authorization record whose `tenant_id` is tenant B
- **THEN** the verifier SHALL reject with reason `cross_tenant`

### Requirement: Authorization records SHALL be single-use via nonce consumption

On successful use, the record's `state` SHALL transition from `active` to `consumed`, and the `nonce` SHALL be added to the tenant's consumed-nonce set. A `consumed` record SHALL NOT be re-used.

#### Scenario: Successful use transitions state to consumed

- **WHEN** an authorization record passes all verification checks and is used
- **THEN** the record's `state` SHALL be `consumed`
- **AND** the `nonce` SHALL be in the consumed set

#### Scenario: Re-using a consumed record fails

- **WHEN** a record with `state: consumed` is presented again
- **THEN** the verifier SHALL reject with reason `already_consumed`

### Requirement: Compromise response SHALL revoke affected authorizations

When a tenant key compromise is declared (per ADR-0042's compromise drill), the system SHALL:

1. Transition all `active` authorization records under the compromised key to `state: revoked`.
2. Emit a `vault_authorization_revoked` audit event for each affected record.
3. Issue new authorization records only under the new key.
4. Abort any in-flight EDR handoff whose `authorization_record_ref` is now revoked, transitioning the handoff's `execution_result.status` to `failed` with `error.code: authorization_revoked`.

The compromise-drill cadence (scheduled vs. contingency-only) is governed by ARCH-P2-001 / ADR-0042; this requirement specifies the response procedure under either interpretation.

#### Scenario: Compromise revokes active records under the compromised key

- **WHEN** a key compromise is declared
- **THEN** all active authorization records signed under that key SHALL transition to `revoked`

#### Scenario: In-flight handoff with revoked authorization aborts

- **WHEN** an EDR handoff has been dispatched against an authorization record that is now `revoked`
- **THEN** the handoff's `execution_result.status` SHALL transition to `failed` with `error.code: authorization_revoked`

### Requirement: Audit chain SHALL record authorization issuance, revocation, and use rejection

Every authorization issuance SHALL emit a `vault_authorization_issued` audit chain entry with the `authorization_id`.

Every authorization revocation SHALL emit a `vault_authorization_revoked` audit chain entry with the `authorization_id` and the reason.

Every rejected use SHALL emit a `vault_authorization_use_rejected` audit chain entry with the `authorization_id` and the failure reason.

Adding `vault_authorization_use_rejected` to the `replay-and-audit` event-type enum is tracked as a follow-up `MODIFIED Requirements` change against `replay-and-audit` during rc2 verification (Block RC2-V).

#### Scenario: Issuance without audit entry is invalid

- **WHEN** an authorization record is created without a corresponding `vault_authorization_issued` audit entry
- **THEN** the issuance is invalid

#### Scenario: Rejected use produces an audit entry

- **WHEN** the verifier rejects a use of an authorization record for any reason
- **THEN** a `vault_authorization_use_rejected` audit entry SHALL be emitted with the reason

### Requirement: Vault IPC schemas SHALL land as M3 deliverables with acceptance criteria

The architecture SHALL track three vault IPC schemas as named M3 deliverables governed by this spec. The patch tree's `M3-DEPENDENCY-002` blocker names them as required before the EDR adapter can use vault:

- `architecture/blueprint/schemas/vault_request.schema.json` — request envelope sent from a caller (ingest, EDR adapter, audit) to vault.
- `architecture/blueprint/schemas/vault_response.schema.json` — vault's response envelope.
- `architecture/blueprint/schemas/vault_audit_envelope.schema.json` — vault audit log entry shape.

Each schema SHALL:

1. Carry the standard metadata triple (whatever the post-apply baseline `architecture/blueprint/schemas/` convention requires).
2. Have a `pass.fixture` and a `fail.fixture` under `tests/bootstrap-fixtures/`.
3. Be referenced by `scripts/check_vault_ipc_contract.py` (M3 fitness function).
4. Encode all fields required by this spec's authorization record (action, tenant, target, expiry, nonce, policy snapshot, approval reference, signing tag, state).

The schemas SHALL NOT be produced as part of this change. They are M3 deliverables.

#### Scenario: M3 deliverable schema missing a required field fails contract check

- **WHEN** the M3 vault IPC schemas are produced and one omits a field required by this spec (e.g., `nonce`)
- **THEN** `check_vault_ipc_contract.py` SHALL fail the M3 gate

#### Scenario: M3 deliverable without fixtures fails check

- **WHEN** any of the three schemas lacks a pass.fixture or fail.fixture
- **THEN** the M3 gate SHALL fail per `INV-023` (every fitness function has both fixtures)

### Requirement: Future vault authorization changes go through this spec

Adding, removing, or modifying authorization record fields, verification rules, compromise-response steps, or M3 schema acceptance criteria SHALL go through a `MODIFIED Requirements` OpenSpec change against `vault-authorization`. Direct edits to `architecture/objects/vault-authorization.md` SHALL be rejected at review.

#### Scenario: Adding a new verification rule requires a spec change

- **WHEN** someone proposes adding a new vault verification rule (e.g., geo-restriction)
- **THEN** they SHALL file a `MODIFIED Requirements` change against `vault-authorization` first
