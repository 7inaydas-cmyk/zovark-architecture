## Context

The runbook §7 (EDR handoff correctness) lists 10 fields every handoff record must contain: action type, target, tenant, evidence links, policy snapshot, approval mode, authorization record, idempotency key, execution result, rollback/reversal plan. The wedge prose mentions that handoffs are "replayable, evidence-linked, and reversible." None of this is currently structured anywhere — the `investigation-tape` capability only signposts the field by name (`handoff_ref` + `handoff_summary`).

The bootstrap package (v3.2.4.6) does not implement EDR adapters. This change defines the record at spec level so build teams can scope adapter work without re-discovering the field set.

## Goals / Non-Goals

**Goals:**

- Specify the 10 canonical fields with conceptual types.
- Distinguish approval-required from autonomous modes at the field level.
- Specify the rollback/reversal plan structure (action class, vendor reversal API contract at the spec level, manual-rollback fallback).
- Specify idempotency semantics: same idempotency key + same target + same tenant SHALL produce the same final state.
- Define the relationship between handoff record, audit chain entry, vault authorization record, and investigation tape.

**Non-Goals:**

- Vendor adapter implementations.
- Per-vendor reversal API specifics.
- HTTP transport / wire format / signing implementation.
- Per-tenant policy on approval mode (which actions require approval is a tenant-level policy, not part of the spec).
- Autonomous execution rules (when autonomous mode is permitted is policy, not record).

## Decisions

### The 10 canonical fields

1. **`handoff_id`** — string, unique within tenant.
2. **`tenant_id`** — string.
3. **`tape_ref`** — reference to the source investigation tape (`tape_id`).
4. **`action_type`** — enum: `isolate_host`, `kill_process`, `quarantine_file`, `block_hash`, `block_network_indicator`, `revoke_session`, `disable_account`, `notify_only`, `custom` (custom requires explicit `custom_action_descriptor`).
5. **`target`** — structured field: `{kind, identifier, validated_at}`. Kind is enum (`host`, `process`, `file_hash`, `network_ip`, `network_domain`, `session_id`, `account_id`, `custom`); identifier is the kind-specific identifier; validated_at is when the target was last verified to exist.
6. **`evidence_refs`** — list of `evidence_id`s from the source tape that justify the handoff. SHALL be non-empty.
7. **`policy_snapshot`** — opaque hash of the tenant policy version that was in effect when the handoff was authorized. Combined with `policy_snapshot_version` (semver-ish string).
8. **`approval_mode`** — enum: `approval_required`, `autonomous`.
9. **`authorization_record_ref`** — reference to a `vault-authorization` record (when M1+ vault is online; placeholder before that).
10. **`execution_result`** — structured: `{status, started_at, completed_at, vendor_response_ref, error}`. Status is enum (`pending`, `dispatched`, `succeeded`, `failed`, `partial`, `rolled_back`).

Plus four additional fields outside the runbook's 10 but architecturally necessary:

- **`idempotency_key`** — string. Same key + same target + same tenant SHALL converge.
- **`rollback_plan`** — structured (see Rollback decisions below).
- **`audit_ref`** — reference to audit chain entry recording dispatch + execution + rollback.
- **`replay_linkage`** — reference to the recorded I/O entries on the source tape that informed the decision.

**Rationale.** The four extras are implied by other architecture invariants (audit, replay, idempotency, rollback) but not stated in runbook §7's bullet list. Surfacing them here prevents implicit coupling in build planning. Alternative considered: keep the spec at the runbook's 10. Rejected — leads to ambiguous adapter contracts (e.g., is rollback part of execution_result or separate? this spec says: separate).

### Approval modes

Two modes:

- **`approval_required`** — handoff is dispatched to vendor only after explicit human approval is recorded in `authorization_record_ref`. Default for MVP.
- **`autonomous`** — handoff is dispatched without per-action human approval. The tenant policy snapshot (`policy_snapshot` + `policy_snapshot_version`) MUST authorize the action_type for autonomous execution. Autonomous mode is not in design-partner MVP per `mvp-scope.md` ("Explicit approval before any external action. No fully autonomous external action is in MVP").

The mode selection happens at handoff creation. Mode SHALL NOT change after dispatch.

**Rationale.** Both modes need the same record fields; the mode flag only changes the authorization path. Alternative considered: separate record types per mode. Rejected — duplicates fields and complicates audit.

### Rollback / reversal plan structure

`rollback_plan` is structured:

```
{
  reversibility_class: enum,         # automatic | manual_documented | irreversible
  vendor_reversal_action: enum,      # release_isolation | restore_file | unblock_hash | unblock_indicator | restore_session | re-enable_account | none
  vendor_reversal_target: structured # mirrors `target` shape; what the reversal acts on
  manual_steps: list[string]         # populated when reversibility_class is manual_documented
  reversal_window: duration          # how long after dispatch reversal is reasonable; informational
  idempotency_key: string            # rollback's own idempotency key
}
```

**Rationale.** Some EDR actions are automatically reversible (host isolation), some require documented manual steps (restoring a quarantined file may need IT support), and some are functionally irreversible within reasonable time (account password rotation). Spec captures the class so build teams know which adapter ops to implement and which to document. Alternative considered: leave rollback as free text. Rejected — ambiguous; build planning needs the class enum.

### Idempotency semantics

Same `idempotency_key` + same `target` + same `tenant_id` + same `action_type`:

- Second dispatch with identical inputs SHALL be a no-op at the vendor level.
- The handoff record SHALL be re-fetched, not re-created.
- The audit chain SHALL record both attempts but mark the second as `idempotent_replay`.

The idempotency key SHOULD be derived from the source tape's `tape_id` plus a content hash of the action+target — this gives natural deduplication without explicit key management.

**Rationale.** Idempotency is a hard architecture invariant: the customer cannot tolerate duplicate isolations or duplicate account locks. Alternative considered: idempotency at vendor adapter level only. Rejected — different vendors have different semantics; the record-level idempotency anchors the contract.

### Linkage to other capabilities

- **Tape:** `tape_ref` and `evidence_refs` (which point at `evidence_id`s on the tape).
- **Vault:** `authorization_record_ref` points at `vault-authorization` records.
- **Audit:** `audit_ref` points at `replay-and-audit` chain entries.

These cross-spec references are normal; each capability spec defines its own record shape.

## Risks / Trade-offs

- **Risk:** the `action_type` enum is too narrow and a real customer needs an action not enumerated. → **Mitigation:** the `custom` value with `custom_action_descriptor` allows extension; new common actions land via `MODIFIED Requirements`.
- **Risk:** rollback class lock-in: an action initially classified as `manual_documented` may later get an automatic vendor reversal. → **Mitigation:** rollback class is per-record at dispatch time; class can change in subsequent records without churn on existing tapes.
- **Trade-off:** the record is somewhat large (10+ fields). Accepted: handoffs are infrequent relative to evidence ingestion; record size is not a hot path.

## Migration Plan

1. Land `architecture/objects/edr-handoff.md` with the 10 + 4 fields, approval-mode enum, rollback structure, idempotency rules, and linkage.
2. Capture as `openspec/specs/edr-handoff/spec.md` via archive.
3. The subsequent `fix-replay-and-audit-semantics` will define `audit_ref` target shape; the subsequent `fix-vault-authorization-audit` will define `authorization_record_ref` target shape.

**Rollback:** revert. The record goes back to being signposted only.

## Open Questions

- Should `notify_only` be a separate enum value or a subset of `custom`? Decision: separate. Notify-only is common enough to warrant first-class handling and the audit semantics differ slightly (no vendor side-effect to track).
- Should `approval_mode: autonomous` be allowed at all in v1 of the spec given MVP forbids it? Decision: yes, document the mode, with a spec-level note that current MVP policy disallows it. Removing the mode would require a `MODIFIED Requirements` change later when policies change.
