# Vault Authorization — Object Architecture

This document defines the vault authorization record at the architectural level.
The `edr-handoff` capability already references this object via
`authorization_record_ref`, and the `replay-and-audit` capability emits
`vault_authorization_issued` and `vault_authorization_revoked` events keyed by it.
This is the spec for that object.

The binding spec is `openspec/specs/vault-authorization/spec.md`. Direct edits to
this file without a corresponding `MODIFIED Requirements` change against the
`vault-authorization` capability SHALL be rejected at review.

## Source authority

- `INV-019`: every vault access requires per-action authorization; no broad
  credentials. Established by baseline ADR-0028 (vault threat model).
- `ADR-0042` (in this tree): cryptographic key management, governs the keys used to
  sign authorization records.
- Baseline ADR-0034: tenant DEK rotation, governs the rotation pattern that
  authorization records inherit. Not in this tree; cross-link audit deferred to
  `fix-adr-cross-link-verification`.

## The record

```
{
  authorization_id: string,        # unique within tenant
  tenant_id: string,
  action_type: string,             # mirrors edr-handoff.action_type or a vault-op type
  target: { kind, identifier },    # mirrors edr-handoff.target shape
  policy_snapshot: string (hash),
  policy_snapshot_version: string,
  approval_ref: string | null,     # null when policy permits without per-action approval
  issued_at: ISO-8601,
  expires_at: ISO-8601,            # strictly after issued_at
  nonce: string (≥128 bits entropy),
  signing_tag: string (opaque),    # verifiable against tenant vault root key
  state: "active" | "consumed" | "revoked" | "expired"
}
```

## Verification rules (every use)

When the record is presented for use:

1. `state == active`.
2. Current time `≤ expires_at`.
3. `action_type` matches the requested operation.
4. `tenant_id` matches the requesting tenant.
5. `target` matches the operation's target exactly (kind and identifier).
6. `policy_snapshot` matches the policy in effect at use time. Drift fails closed.
7. When `approval_ref` is non-null, it resolves to a valid human approval record.
8. `signing_tag` verifies against the tenant's vault root key (per ADR-0042).
9. `nonce` has not been previously consumed under this tenant.

Any failure → operation rejected, audit event `vault_authorization_use_rejected`
emitted with the failure reason.

## Replay protection

`nonce` is the primary replay-protection mechanism:

- Cryptographically random; ≥ 128 bits of entropy.
- Single-use within tenant scope. On successful use, `state` transitions
  `active → consumed` and the nonce is added to a tenant-scoped consumed-nonce
  set.
- Vault SHALL reject any operation whose presented `nonce` is in the
  consumed-nonce set.

`expires_at` is a secondary backstop: even if a nonce escapes consumption tracking,
a stale record cannot be used past expiry.

## Compromise response

When a tenant key compromise is declared (per ADR-0042's compromise drill):

1. All `active` records under the compromised key transition to `revoked`.
2. A `vault_authorization_revoked` audit event is emitted for each.
3. New issuances use the new key with new nonces.
4. In-flight EDR handoffs whose `authorization_record_ref` is now revoked abort:
   `execution_result.status: failed` with `error.code: authorization_revoked`.

The drill cadence (scheduled vs. contingency-only) is governed by ARCH-P2-001 /
ADR-0042. This document specifies the response procedure under either
interpretation.

## Audit linkage

| Audit event | Emitted on |
|---|---|
| `vault_authorization_issued` | every issuance |
| `vault_authorization_revoked` | every revocation, with reason |
| `vault_authorization_use_rejected` | every rejected use, with reason |

`vault_authorization_use_rejected` is a new event type. Adding it to the
`replay-and-audit` event-type enum is tracked as a follow-up `MODIFIED Requirements`
change against `replay-and-audit` during rc2 verification.

## M3 IPC schema deliverables

Per the patch's `M3-DEPENDENCY-002` blocker, three IPC schemas are required before
the EDR adapter can use vault. Each is an **M3 deliverable**:

| Schema path | Purpose |
|---|---|
| `architecture/blueprint/schemas/vault_request.schema.json` | Request envelope sent from a caller (ingest, EDR adapter, audit) to vault. |
| `architecture/blueprint/schemas/vault_response.schema.json` | Vault's response envelope. |
| `architecture/blueprint/schemas/vault_audit_envelope.schema.json` | Vault audit log entry shape. |

Acceptance criteria for each schema:

1. Carries the standard metadata triple per the post-apply baseline
   `architecture/blueprint/schemas/` convention.
2. Has a `pass.fixture` and a `fail.fixture` under `tests/bootstrap-fixtures/`
   (per `INV-023`: every fitness function has both fixtures).
3. Is referenced by `scripts/check_vault_ipc_contract.py` (M3 fitness function).
4. Encodes all fields required by this spec's authorization record (action,
   tenant, target, expiry, nonce, policy snapshot, approval reference, signing
   tag, state).

The schemas are not produced as part of this change. They land in M3.

## Cross-link audit hand-off

Baseline ADRs ADR-0028 (vault threat model) and ADR-0034 (tenant DEK rotation) are
not files in this repo; they live in the v3.2.3.5 baseline. The next rc2 change
(`fix-adr-cross-link-verification`) defines the post-apply verification that
confirms these ADRs exist and don't contradict patch ADRs 0038-0043.

Until that verification runs, this spec treats the baseline ADRs as authoritative
for the threat model and rotation algorithm and constrains the authorization record
to be consistent with INV-019.

## Linkage table

| Reference field | Target capability |
|---|---|
| `authorization_id` | Used by `edr-handoff.authorization_record_ref`. |
| `policy_snapshot` | Tenant policy version (out of scope for this spec). |
| `signing_tag` | Tenant vault root key per ADR-0042. |
| `vault_authorization_issued / revoked / use_rejected` events | Emitted to `replay-and-audit` chain. |

## Build planning

This spec gives the build team enough to scope:

- **Authorization issuance:** populate the record, sign it with the tenant's vault
  root key, emit the `_issued` audit event.
- **Verification:** the 9-rule check; fail closed; emit `_use_rejected` on any
  failure.
- **Consumption tracking:** per-tenant consumed-nonce set with monotonic growth;
  expiration sweeps for `state: expired` transitions.
- **Compromise response:** bulk-revoke under a key; emit `_revoked` events;
  surface to EDR handoff abort path.
- **Tests:** every requirement scenario in `openspec/specs/vault-authorization/spec.md`
  is a candidate test case.
- **M3 deliverables:** the three schemas + the M3 fitness function script.

## What this document does not define

- Vault implementation (HSM vs. cloud KMS; storage; replication).
- IPC wire format / transport (M3 schemas above).
- Tenant DEK rotation algorithm (baseline ADR-0034).
- The vault threat model (baseline ADR-0028).
- Drill cadence / compromise-response cadence (ARCH-P2-001 / ADR-0042).
- Per-tenant policy authoring (out of scope).
