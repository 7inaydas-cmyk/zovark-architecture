## Context

Vault is referenced in three places without being defined here:

- `INV-019` ("Every vault access requires per-action authorization; no broad credentials"), established by baseline `ADR-0028`.
- `edr-handoff` capability's `authorization_record_ref` points at a vault authorization record.
- `replay-and-audit` capability's audit event types `vault_authorization_issued` and `vault_authorization_revoked` reference vault objects.

The baseline ADRs 0001-0037 (including ADR-0028 vault threat model and ADR-0034 tenant DEK rotation) live outside this finalization repo (in the v3.2.3.5 baseline). This change cannot audit those ADR files directly. It produces a spec for the authorization record itself and explicitly defers cross-link verification to `fix-adr-cross-link-verification`.

The patch's `M3-DEPENDENCY-002` blocker names three IPC schemas (`vault_request`, `vault_response`, `vault_audit_envelope`) needed before the EDR adapter can use vault. This change records them as M3 deliverables with acceptance criteria but does not produce the schemas.

The bootstrap package does not implement vault — this is documentation only.

## Goals / Non-Goals

**Goals:**

- Specify the vault authorization record fields and validity rules.
- Specify replay protection semantics (nonces, expiry, single-use).
- Specify compromise-response rules (revocation, key rotation pointer, what happens to in-flight authorizations).
- Lock down which fields the EDR handoff record's `authorization_record_ref` resolves to.
- Document the M3 IPC schema deliverables so build planning is explicit.
- Move finalization criterion #9 from UNAUDITED to PASS-with-tracked-gaps.

**Non-Goals:**

- Implementing the vault.
- Producing the M3 IPC schemas (recorded as deliverables; not built).
- Choosing HSM vs. cloud KMS (implementation per ADR-0042, in-tree).
- Per-tenant key rotation algorithm (lives in baseline ADR-0034).
- Auditing the contents of baseline ADRs (deferred to `fix-adr-cross-link-verification`).
- Defining the wire format of vault calls (M3 deliverable).

## Decisions

### Authorization record fields

```
{
  authorization_id: string,        # unique within tenant
  tenant_id: string,
  action_type: string,             # mirrors edr-handoff.action_type enum
  target: structured,              # mirrors edr-handoff.target shape
  policy_snapshot: string (hash),  # matches edr-handoff.policy_snapshot
  policy_snapshot_version: string,
  approval_ref: string | null,     # null if action_type permitted by policy without per-action approval
  issued_at: ISO-8601,
  expires_at: ISO-8601,            # SHALL be in the future at issuance
  nonce: string,                   # cryptographically random; single-use
  signing_tag: string,             # opaque tag; verifier rebinds against vault root key
  state: enum                      # active | consumed | revoked | expired
}
```

The record SHALL bind action + tenant + target + policy + (approval when required) + expiry + nonce. Verification SHALL re-check every binding.

**Rationale.** Per INV-019: "every vault access requires per-action authorization; no broad credentials." The field set captures what "per-action" means concretely. Alternative considered: minimal record with just an opaque token. Rejected — leaves the verifier no information to enforce against; defeats the audit story.

### Verification rules

To use an authorization record (i.e., to dispatch a handoff or perform a vault op):

1. The record SHALL be `state: active`.
2. The current time SHALL be ≤ `expires_at`.
3. The action_type, tenant_id, target SHALL match the requested operation exactly.
4. The policy_snapshot SHALL match the policy in effect at use time, OR the verifier SHALL reject (policy drift between issuance and use is failure-closed).
5. When `approval_ref` is non-null, it SHALL resolve to an approval record from a human authorizer.
6. The signing_tag SHALL verify against the tenant's vault root key (per ADR-0042).
7. The nonce SHALL not have been previously used for any operation under this tenant.

If any check fails → operation rejected, audit chain entry of `vault_authorization_issued` SHALL NOT be amended (keep the issuance record), and a new audit entry of type `vault_authorization_use_rejected` (added in this change) records the failure with reason.

**Rationale.** Failure-closed at every check is the architecture's posture (per `INV-001`). Alternative considered: time-bound only, no per-use re-verification. Rejected — leaves a window for replay.

### Replay protection

`nonce` is the primary replay-protection mechanism:

- Cryptographically random; ≥ 128 bits of entropy.
- Single-use within tenant scope. Once `state` transitions from `active` to `consumed`, the nonce SHALL NOT be re-presented.
- Vault SHALL reject any operation whose presented `nonce` is already in `consumed` or `revoked` state.

`expires_at` is a secondary backstop: even if a nonce escapes consumption tracking, a stale record cannot be used past expiry.

**Rationale.** Standard nonce-based replay protection. Alternative considered: per-action sequence number. Rejected — adds ordering complexity without meaningful benefit when nonces are random.

### Compromise-response rules

If a tenant key is compromised (per ADR-0042's compromise drill):

1. All authorization records under the affected key SHALL transition to `state: revoked`.
2. New issuances under the new key SHALL be assigned new nonces.
3. The audit chain SHALL record `vault_authorization_revoked` events for each affected record.
4. In-flight EDR handoffs whose `authorization_record_ref` is now revoked SHALL be aborted (`execution_result.status: failed` with `error.code: authorization_revoked`).

The compromise-drill cadence per ARCH-P2-001 is currently ambiguous (scheduled vs. contingency). This spec does not resolve that ambiguity; it specifies what the response procedure looks like in either interpretation.

**Rationale.** When keys rotate under duress, in-flight authorizations must die. Alternative considered: keep in-flight authorizations valid through grace period. Rejected — a compromised key may have signed authorizations that the attacker controls; the architecture must fail closed.

### Linkage

| Reference field | Target |
|---|---|
| `edr-handoff.authorization_record_ref` | This record's `authorization_id`. |
| `replay-and-audit` audit events `vault_authorization_issued`, `vault_authorization_revoked`, `vault_authorization_use_rejected` (new) | This record's `authorization_id`. |
| `policy_snapshot` | Tenant policy version (out of scope). |
| `signing_tag` | Tenant vault root key per ADR-0042. |

### M3 IPC schemas as named deliverables

The patch's `M3-DEPENDENCY-002` blocker names three schemas needed for vault IPC:

- `architecture/blueprint/schemas/vault_request.schema.json`
- `architecture/blueprint/schemas/vault_response.schema.json`
- `architecture/blueprint/schemas/vault_audit_envelope.schema.json`

Each carries the standard metadata triple, has pass/fail fixtures, and is referenced by `check_vault_ipc_contract.py` (M3 fitness function).

This change documents these as M3 deliverables with acceptance criteria. The schemas themselves are not produced here; they land in M3.

### Cross-link audit hand-off

Baseline ADRs ADR-0028 (vault threat model) and ADR-0034 (tenant DEK rotation) are not files in this repo; they live in the v3.2.3.5 baseline. The next rc2 change (`fix-adr-cross-link-verification`) defines the post-apply verification that confirms these ADRs exist and don't contradict patch ADRs 0038-0043.

This change references those ADRs by ID and treats them as authoritative for the threat model and rotation algorithm.

## Risks / Trade-offs

- **Risk:** the spec assumes ADR-0028's vault threat model without auditing it. → **Mitigation:** ARCH-P2-001 (drill cadence) and ADR-0028 cross-link verification (next rc2 change) cover the audit follow-up.
- **Risk:** the M3 IPC schemas drift from this record's field set when they're produced. → **Mitigation:** the spec's Requirement on field set is binding; the M3 schema fixtures will be checked against the requirement scenarios at archive time.
- **Trade-off:** verifier re-checks every binding on every use, which adds latency. Accepted: vault calls are infrequent (per-handoff, per-vault-op); latency is bounded.

## Migration Plan

1. Land `architecture/objects/vault-authorization.md` with record fields, verification rules, replay protection, compromise response, M3 deliverables.
2. Add the new audit event type `vault_authorization_use_rejected` to the `replay-and-audit` capability via this change's spec (uses ADDED on a new event type *within* this capability, not a MODIFIED of `replay-and-audit` — this change defers that integration to the next rc2 change or the rc2 verification pass).

   Note: cross-capability event-type addition. To keep the change scoped, this spec lists the new event type as part of the `vault-authorization` Requirement on audit events. A subsequent `MODIFIED Requirements` against `replay-and-audit` should pick up the new enum value during rc2 verification.

3. Capture as `openspec/specs/vault-authorization/spec.md` via archive.

**Rollback:** revert. Vault authorization stays UNAUDITED.

## Open Questions

- Should the new audit event `vault_authorization_use_rejected` land as a `MODIFIED Requirements` against `replay-and-audit` in this same change, or in a follow-up? Decision: defer to follow-up cleanup during rc2 verification (Block RC2-V) — keeping this change scoped to the `vault-authorization` capability.
- Should `policy_snapshot` use the same hash algorithm as the audit chain? Defer — both inherit from ADR-0042.
