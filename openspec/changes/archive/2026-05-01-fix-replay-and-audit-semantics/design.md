## Context

Two distinct concerns are bundled in one capability because their semantics cross-reference at every step:

1. **Replay** — read a closed tape, rebind recorded I/O, recompute the verdict, and arrive at the same value. Replay reads audit chain entries to verify evidence hashes and verdict signatures.

2. **Audit chain** — append-only log of architecturally-relevant events (tape close, handoff dispatch, replay completion, restore completion). The audit chain anchors trust: every closed tape signs an audit entry and every reviewer can verify the chain.

The patch tree has `disaster-recovery-restore-gap.md` defining the `DISASTER_RECOVERY_RESTORE_COMPLETED` event and the verifier state `VALID_AFTER_RESTORE_WITH_DECLARED_GAP`. This is preserved verbatim in spec form. Other audit semantics (canonicalization, concurrent-insert, unsigned-tail) are referenced in invariants but not consolidated. This change consolidates without altering existing rules.

The bootstrap package (v3.2.4.6) does not implement replay or audit chain runtime — this is documentation only.

## Goals / Non-Goals

**Goals:**

- Specify replay state object, lifecycle, and determinism rules.
- Specify what replay rebinds (recorded I/O, schema version, tool/catalog version).
- Specify audit chain entry shape — canonical fields, ordering, signature anchor.
- Specify canonicalization rules so two implementations of audit-chain serialization produce identical bytes.
- Specify concurrent-insert behavior (deterministic ordering by sequence number).
- Specify root signature semantics — what "the root" means, how often it's signed.
- Specify unsigned-tail behavior (what happens during a window between events and the next root signature).
- Specify the `DISASTER_RECOVERY_RESTORE_COMPLETED` event and `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` verifier state, preserving the patch tree's existing semantics.

**Non-Goals:**

- Choosing a hash algorithm (SHA-256 vs. SHA-3 vs. BLAKE3) — that is an implementation choice.
- Choosing a signature scheme (RSA vs. Ed25519) — implementation.
- Audit chain storage layout (Merkle tree vs. linked list vs. append log) — implementation.
- DR runbook / restore-drill cadence (deferred to ARCH-P2-002 sketch and a future ADR).
- Per-tenant key rotation (lives in `vault-authorization`).
- Picking signature roots' hardware (HSM vs. cloud KMS) — implementation per ADR-0042.

## Decisions

### Replay state object

`replay_state` carries:

- `replay_id` — string, unique within tenant.
- `tape_ref` — references the source `tape_id`.
- `tenant_id` — same as the tape.
- `schema_pin` — string; the `schema_version` of the tape at recording time. Replay SHALL use this pinned version.
- `tool_catalog_pin` — string; the tool catalog version at recording time. Replay rebinds tool calls against this version, not the current catalog.
- `model_versions_pin` — list of `(model_id, version)` pinned at recording time, derived from the tape's `recorded_io`.
- `state` — enum: `pending`, `running`, `succeeded`, `mismatch`, `failed`.
- `mismatch_details` — populated when state = `mismatch`; lists which fields differed (verdict, finding, timeline event).
- `started_at`, `completed_at` — ISO-8601.

Replay determinism rules:

1. Replay SHALL NOT call live LLMs or live tools. All model/tool I/O comes from the tape's `recorded_io`.
2. Replay SHALL verify every `raw_evidence` entry's `hash` against the stored content. Hash mismatch → `state: failed` with reason `evidence_corruption`.
3. Replay SHALL recompute the verdict from the recorded inputs. If the recomputed verdict differs from the tape's stored verdict → `state: mismatch` with `mismatch_details` listing the fields.
4. Replay SHALL produce a new audit chain entry (`event_type: replay_completed`) recording the result.

**Rationale.** Mirrors the patch's `mvp-scope.md` distinction: "Recorded-output replay that uses stored records and does not call live inference." Pinning schema/tool/model versions is the only way to make replay deterministic across catalog updates. Alternative considered: replay against the current catalog. Rejected — defeats the audit purpose; a finding could disappear because a tool was retired.

### Forensic re-execution vs. recorded-output replay

Two replay modes, both governed by this capability:

- **Recorded-output replay** (default) — uses recorded I/O; deterministic; what the tape recorded is what replay sees.
- **Forensic re-execution** — re-runs models/tools live against the current catalog. Used when a security investigation needs to re-evaluate against newer signatures. Requires explicit reviewer initiation, generates a *new* tape rather than mutating the original. Out of MVP per `mvp-scope.md`; specified here for completeness.

The two modes are distinguished by the `replay_state.mode` field: `recorded_output` (default) or `forensic_reexecution`.

**Rationale.** Both are real workflows; surfacing the distinction in spec prevents the build team from conflating them. Alternative considered: only specify recorded-output replay in this version. Rejected — the EDR handoff spec needs to know forensic re-execution exists (because rolling back an action might prompt a re-investigation).

### Audit chain entry shape

Every audit chain entry:

```
{
  entry_id: string,                # unique within tenant; monotonically assigned
  tenant_id: string,
  sequence: integer,               # tenant-scoped, monotonically increasing, no gaps
  event_type: enum,                # see below
  payload: structured,             # event-specific
  created_at: ISO-8601,
  prev_entry_hash: string,         # hash of the canonical bytes of the previous entry
  this_entry_hash: string,         # hash of this entry's canonical bytes
  signed_root: { ref: string, signed_at: ISO-8601 } | null   # null until next root signature lands
}
```

Event types:

- `tape_recording_started`, `tape_recording_closed`, `tape_replayed`
- `handoff_dispatched`, `handoff_executed`, `handoff_rolled_back`
- `vault_authorization_issued`, `vault_authorization_revoked`
- `disaster_recovery_restore_completed`

**Rationale.** The list covers the lifecycle events implied by the other capabilities. Alternative considered: open enum (any event_type allowed). Rejected — closed enum makes the audit chain auditable; new event types land via `MODIFIED Requirements`.

### Canonicalization

Audit chain entries SHALL be serialized canonically before hashing. Canonicalization rules:

1. Sort all object keys lexicographically.
2. UTF-8 encode all strings.
3. Numbers SHALL be integers or finite decimals; no NaN or infinity.
4. Timestamps SHALL be ISO-8601 with explicit `Z` for UTC.
5. Boolean SHALL be `true` or `false`, lowercase.
6. Null SHALL be `null`.
7. Arrays preserve order.
8. No trailing whitespace.

Two compliant implementations SHALL produce byte-identical canonical forms.

**Rationale.** Without canonicalization, hash chains are at the mercy of JSON encoder ordering; cross-platform interop fails. Alternative considered: defer to JCS (RFC 8785). Acceptable but a concrete superset; we keep our own minimal rules and can adopt JCS as a `MODIFIED Requirements` change later.

### Concurrent-insert behavior

Audit chain insertions within one tenant SHALL be serialized: a single writer per tenant assigns the next `sequence` number. Concurrent appenders queue. The chain has no gaps.

Cross-tenant inserts are independent (separate chains).

**Rationale.** Tenant-scoped chains are the invariant; per-tenant single-writer eliminates ordering ambiguity. Alternative considered: lock-free concurrent insertion with merge. Rejected — adds reordering complexity not justified by audit-chain throughput needs.

### Root signature semantics

A "root" signature signs a snapshot of the chain head:

- Periodic: at most every N seconds (N is implementation-defined per tenant policy; default 60s).
- Triggered: forced after critical events (`handoff_dispatched`, `disaster_recovery_restore_completed`).

A signed root attests "all entries up to and including `sequence: K` are committed." Entries appended after the most recent root signature are in the **unsigned tail**.

The root signature scheme uses a key issued from the tenant's vault per ADR-0042 (cryptographic key management). Spec does not name the algorithm.

**Rationale.** Periodic + triggered batching is industry-standard for audit chains. Alternative considered: sign every entry. Rejected — too expensive at high throughput; defeats batching benefits.

### Unsigned-tail behavior

The unsigned tail is committed but not yet root-signed. Reviewers SHALL distinguish between signed entries (verifiable) and unsigned-tail entries (committed locally but not yet attested). Replays SHOULD wait until the source tape's audit entries are in the signed range; replays MAY proceed against an unsigned tail with an explicit `unsigned_tail_replay: true` flag in the replay record.

A DR restore SHALL prefer signed-root snapshots over unsigned tails.

**Rationale.** Without this distinction, customers can't tell whether an audit entry is "really committed" or in the unsigned-tail window. Alternative considered: never expose unsigned tail. Rejected — would inflate replay latency to the root signature interval.

### DR restore-gap semantics

Preserved verbatim from `disaster-recovery-restore-gap.md`:

- A valid post-restore audit chain proves internal consistency of the recovered chain. It does not prove that no data loss occurred.

The audit event `disaster_recovery_restore_completed` SHALL include the payload fields named in the patch's DR doc:

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

The verifier SHALL recognize the state `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` for chains that are internally consistent from the restore point forward and explicitly declare the possible loss window.

**Rationale.** Don't relitigate the patch's existing decision. Alternative: rewrite. Rejected — introduces ambiguity and doesn't improve the rule.

### Hook for ARCH-P2-002 (control-plane DR plan)

This spec does not specify the control-plane DR plan (RPO/RTO targets, HA vs. DR posture, restore-drill cadence). Those land in a separate sketch ADR addressing ARCH-P2-002. This spec records the hook so the future DR sketch can reference these audit semantics without redefining them.

**Rationale.** Keep the change scoped. ARCH-P2-002 stays open and tracked as P2.

## Risks / Trade-offs

- **Risk:** specifying canonicalization rules that diverge from JCS (RFC 8785) creates two standards. → **Mitigation:** the rules here are a strict subset of JCS; adopting JCS later is a `MODIFIED Requirements` change with no breaking effect.
- **Risk:** the per-tenant single-writer constraint becomes a throughput bottleneck. → **Mitigation:** per-tenant audit throughput needs are bounded by investigation rate (low). If it becomes an issue, switch to lock-free with a `MODIFIED Requirements` change.
- **Trade-off:** unsigned tail visible to reviewers complicates the UI. Accepted: reviewers need the distinction; UI complexity is the right cost.

## Migration Plan

1. Land `architecture/objects/replay-and-audit.md` consolidating replay state, audit chain entry, canonicalization, concurrent-insert, root signature, unsigned tail, DR restore-gap.
2. Capture as `openspec/specs/replay-and-audit/spec.md` via archive.
3. Cross-references from `investigation-tape` and `edr-handoff` resolve to the new spec.

**Rollback:** revert. Replay/audit go back to scattered references.

## Open Questions

- Should the unsigned-tail window be a configurable per-tenant policy or a system-wide constant? Decision: per-tenant policy default (60s); system-wide minimum (5s) and maximum (5min) bounds. Track as future `MODIFIED Requirements` if the policy grain proves wrong.
- Should `forensic_reexecution` mode require a separate authorization beyond the standard tape-replay permission? Defer — operationalize when forensic re-execution is built (post-MVP).
