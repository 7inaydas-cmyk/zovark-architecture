# EDR Handoff — Object Architecture

The EDR handoff is the closing bookend of Zovark's product wedge. The canonical
core flow is:

> **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

This document defines the EDR handoff record at the architectural level: required
fields, approval modes, idempotency semantics, rollback/reversal structure, and the
linkage between handoff, investigation tape, vault authorization, and audit chain.

The binding spec is `openspec/specs/edr-handoff/spec.md`. Direct edits to this file
without a corresponding `MODIFIED Requirements` change against the `edr-handoff`
capability SHALL be rejected at review.

## The 14 fields

Every EDR handoff record carries 14 fields: the 10 canonical fields named in the
finalization checklist plus 4 architecturally-necessary extras.

### Identity (3)

| Field | Type | Notes |
|---|---|---|
| `handoff_id` | string | Unique within tenant. |
| `tenant_id` | string | Never crossed. |
| `tape_ref` | string | References source tape's `tape_id` (see `investigation-tape`). |

### Action and target (2)

| Field | Type | Notes |
|---|---|---|
| `action_type` | enum | `isolate_host`, `kill_process`, `quarantine_file`, `block_hash`, `block_network_indicator`, `revoke_session`, `disable_account`, `notify_only`, `custom`. |
| `target` | structured | `{kind, identifier, validated_at}`. Kinds: `host`, `process`, `file_hash`, `network_ip`, `network_domain`, `session_id`, `account_id`, `custom`. |

`target.kind` SHALL be consistent with `action_type` (e.g., `isolate_host` ↔ `kind:host`).

`action_type: custom` SHALL include a free-form `custom_action_descriptor` declaring
what the custom action does.

### Evidence and policy (3)

| Field | Type | Notes |
|---|---|---|
| `evidence_refs` | list[string] | Non-empty; `evidence_id`s drawn from the source tape's `raw_evidence`. |
| `policy_snapshot` | string (hash) | Content hash of the tenant policy in effect at authorization. |
| `policy_snapshot_version` | string | Identifier (semver-ish). |

### Authorization (2)

| Field | Type | Notes |
|---|---|---|
| `approval_mode` | enum | `approval_required` or `autonomous`. MVP allows only `approval_required`. |
| `authorization_record_ref` | string | References a `vault-authorization` record (placeholder pre-vault-runtime). |

### Execution (1)

`execution_result` — structured:

```
{
  status: "pending" | "dispatched" | "succeeded" | "failed" | "partial" | "rolled_back",
  started_at: ISO-8601,
  completed_at: ISO-8601,
  vendor_response_ref: string,    # opaque reference to vendor adapter response, tenant-scoped
  error: { code, message, retryable } # populated when status is failed/partial
}
```

State transitions: `pending → dispatched → {succeeded | failed | partial} → rolled_back`.

### Idempotency (1)

| Field | Type | Notes |
|---|---|---|
| `idempotency_key` | string | Same key + same target + same tenant + same action_type → no-op on second dispatch. |

Idempotency key SHOULD be derived as `tape_id` + content hash of `action_type + target.identifier`.

### Rollback (1)

`rollback_plan` — structured:

```
{
  reversibility_class: "automatic" | "manual_documented" | "irreversible",
  vendor_reversal_action: enum (release_isolation | restore_file | unblock_hash | unblock_indicator | restore_session | re_enable_account | none),
  vendor_reversal_target: structured  # mirrors `target`
  manual_steps: [string]              # populated when class is manual_documented
  reversal_window: duration           # informational
  idempotency_key: string             # rollback's own key
}
```

Class rules:

- `automatic` — vendor exposes a reversal API; build team implements it.
- `manual_documented` — `manual_steps` lists what an operator must do; build team
  surfaces the steps in the rollback UI.
- `irreversible` — `vendor_reversal_action` SHALL be `none`; `manual_steps` lists
  remediation guidance (e.g., for `disable_account`: "operator manually re-enables
  via IdP admin").

### Linkage (2)

| Field | Type | Notes |
|---|---|---|
| `audit_ref` | string | Reference to the audit chain entry recording dispatch + execution + rollback (see `replay-and-audit`). |
| `replay_linkage` | list[string] | References to recorded I/O entries on the source tape that informed the dispatch decision. May be empty. |

## Approval modes

- `approval_required` — dispatch SHALL occur only after a human approval is recorded
  in `authorization_record_ref`. Default and only allowed mode in design-partner MVP.
- `autonomous` — dispatch MAY occur without per-action human approval; the policy
  snapshot MUST authorize the `action_type` for autonomous execution. Reserved for
  post-MVP; rejected by current MVP policy.

The mode is set at creation and SHALL NOT change after dispatch.

## Idempotency

Same `idempotency_key + tenant_id + target + action_type`:

- Second dispatch is a no-op at vendor level.
- Existing record is re-fetched, not re-created.
- Audit chain records both attempts; second is marked `idempotent_replay: true`.

This protects against duplicate isolations, duplicate account locks, etc. The
recommended derivation (tape_id + hash of action+target) gives natural
deduplication without explicit key management.

## Linkage table

| Reference field | Target capability | Defined in |
|---|---|---|
| `tape_ref` | `investigation-tape` | `architecture/objects/investigation-tape.md` |
| `evidence_refs[]` | `investigation-tape` (raw_evidence entries) | same |
| `authorization_record_ref` | `vault-authorization` | `architecture/objects/vault-authorization.md` (forthcoming) |
| `audit_ref` | `replay-and-audit` (audit chain entry) | `architecture/objects/replay-and-audit.md` (forthcoming) |
| `replay_linkage[]` | `investigation-tape` (recorded_io entries) | same |

## Build planning

This spec gives the build team enough to scope:

- **Adapter interfaces:** dispatch, status poll, reversal. Per-vendor implementation
  in M1+.
- **Idempotency:** record-level (not vendor-adapter-level). Same idempotency_key
  → fetch existing record.
- **Rollback UI:** three classes; class drives whether the UI offers a reverse
  button vs. shows manual steps vs. shows remediation guidance.
- **Approval flow:** vault authorization + UI approval prompt. Autonomous mode is
  documented but disallowed by MVP policy.
- **Tests:** every requirement scenario in `openspec/specs/edr-handoff/spec.md`
  is a candidate test case.

## What this document does not define

- Per-vendor adapter implementations.
- Per-vendor reversal API specifics.
- HTTP transport / wire format / signing details.
- Per-tenant policy on which actions require approval (that is policy, not record).
- The shape of `vault-authorization` records (that is its own capability).
- The shape of audit chain entries (that is `replay-and-audit`).
