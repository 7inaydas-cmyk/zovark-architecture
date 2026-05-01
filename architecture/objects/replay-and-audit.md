# Replay and Audit — Object Architecture

This document defines two tightly-coupled architecture objects: the **replay state**
(used to verify a closed investigation tape) and the **audit chain entry** (the
append-only attestation that anchors trust in tapes, handoffs, and DR events).

The wedge core flow ends with "verified EDR handoff → rollback/reversal record."
"Verified" depends on replay; "verification of verification" depends on the audit
chain. This capability is the spec for both.

The binding spec is `openspec/specs/replay-and-audit/spec.md`. Direct edits to this
file without a corresponding `MODIFIED Requirements` change against the
`replay-and-audit` capability SHALL be rejected at review.

## Replay state object

A `replay_state` represents one execution of replay against a closed tape.

| Field | Type | Notes |
|---|---|---|
| `replay_id` | string | Unique within tenant. |
| `tape_ref` | string | References source tape's `tape_id`. |
| `tenant_id` | string | Same as the tape. |
| `mode` | enum | `recorded_output` (default) or `forensic_reexecution`. |
| `schema_pin` | string | Tape's `schema_version` at recording time. Replay uses this. |
| `tool_catalog_pin` | string | Tool catalog version at recording time. |
| `model_versions_pin` | list[(model_id, version)] | From the tape's `recorded_io`. |
| `state` | enum | `pending`, `running`, `succeeded`, `mismatch`, `failed`. |
| `mismatch_details` | structured | Populated when `state = mismatch`. |
| `unsigned_tail_replay` | bool | Set true if replaying against the unsigned tail. |
| `started_at`, `completed_at` | ISO-8601 | UTC. |

### Replay determinism rules

1. `recorded_output` replays SHALL NOT call live LLMs or tools — all I/O comes from
   the tape's `recorded_io`.
2. Every `raw_evidence` entry's `hash` SHALL be re-verified. Mismatch → `state: failed`
   with reason `evidence_corruption`.
3. The verdict SHALL be recomputed from recorded inputs. Equal → `state: succeeded`.
   Different → `state: mismatch` with `mismatch_details`.
4. Each replay SHALL produce an audit chain entry of `event_type: tape_replayed`.

### Two replay modes

- **`recorded_output`** — default; deterministic; no live calls. The MVP-supported mode.
- **`forensic_reexecution`** — re-runs models/tools live against current catalog;
  produces a *new* tape (does not mutate the source). Out of MVP scope; specified
  here so subsequent capabilities can reference it.

## Audit chain entry

Every architecturally-relevant event lands as an audit chain entry.

| Field | Type | Notes |
|---|---|---|
| `entry_id` | string | Unique within tenant. |
| `tenant_id` | string | Per-tenant chain. |
| `sequence` | integer | Tenant-scoped, monotonic, gap-free. |
| `event_type` | enum | See enum below. |
| `payload` | structured | Event-specific. |
| `created_at` | ISO-8601 | UTC. |
| `prev_entry_hash` | string | Hash of previous entry's canonical bytes. |
| `this_entry_hash` | string | Hash of this entry's canonical bytes. |
| `signed_root` | `{ref, signed_at}` or null | Null until next root signature lands. |

### Event type enum

```
tape_recording_started
tape_recording_closed
tape_replayed
handoff_dispatched
handoff_executed
handoff_rolled_back
vault_authorization_issued
vault_authorization_revoked
disaster_recovery_restore_completed
```

New event types land via a `MODIFIED Requirements` change against this spec. Closed
enum is intentional — it makes the chain auditable.

## Canonicalization

Audit chain entries SHALL be serialized canonically before hashing:

1. Object keys sorted lexicographically.
2. UTF-8 string encoding.
3. Numbers: integers or finite decimals; no NaN, no infinity.
4. Timestamps: ISO-8601 with explicit `Z`.
5. Booleans: lowercase `true`/`false`.
6. Null: `null`.
7. Arrays preserve order.
8. No trailing whitespace.

Two compliant implementations SHALL produce byte-identical canonical forms. (These
rules are a strict subset of JCS / RFC 8785 and can be lifted to JCS via a future
`MODIFIED Requirements` change without breaking existing chains.)

## Concurrent-insert behavior

Audit insertions within one tenant SHALL be serialized: a single writer per tenant
assigns the next `sequence` number. Concurrent appenders queue. The chain has no gaps.

Cross-tenant insertions are independent (separate chains).

This design accepts a per-tenant single-writer constraint as the simplest path to
ordering correctness. Per-tenant audit throughput needs are bounded by investigation
rate (low); if needed, lock-free append lands as a future `MODIFIED Requirements`.

## Root signature semantics

A "root" signature signs a snapshot of the chain head. Roots are produced:

- **Periodically:** at most every 60 seconds (default per-tenant policy; min 5s, max 5min).
- **Triggered:** forced after every entry of type `handoff_dispatched` or
  `disaster_recovery_restore_completed`.

A signed root attests that all entries with `sequence ≤ K` are committed. The
signature scheme uses a key issued from the tenant's vault per ADR-0042; this spec
does not name the algorithm.

## Unsigned tail

Entries appended after the most recent root signature are the **unsigned tail**.

- **Signed range** — verifiable.
- **Unsigned tail** — locally committed, not yet attested.

Reviewers SHALL distinguish the two. Replays SHOULD wait until the source tape's
audit entries are in the signed range; replays MAY proceed against an unsigned tail
only when the replay record carries `unsigned_tail_replay: true`.

DR restores SHALL prefer signed-root snapshots over unsigned tails.

## DR restore-gap semantics

Preserved verbatim from the patch tree's `disaster-recovery-restore-gap.md`:

> A valid post-restore audit chain proves internal consistency of the recovered
> chain. It does NOT prove that no data loss occurred.

The `disaster_recovery_restore_completed` event's payload SHALL include:

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

The verifier SHALL recognize the state `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` for
chains that are internally consistent from the restore point forward and explicitly
declare the loss window.

## Hook for ARCH-P2-002 (control-plane DR plan)

This spec does not specify the control-plane DR plan (RPO/RTO targets, HA vs DR
posture, restore-drill cadence). Those land in a sketch ADR addressing ARCH-P2-002
when scheduled. This capability provides the audit-event semantics the DR sketch
will reference.

## Linkage

| Reference | Target capability |
|---|---|
| `tape_replayed` audit entry's `payload.tape_ref` | `investigation-tape` |
| `handoff_dispatched / handoff_executed / handoff_rolled_back` audit entry's `payload.handoff_id` | `edr-handoff` |
| `vault_authorization_issued / revoked` audit entry's `payload.authorization_record_ref` | `vault-authorization` (forthcoming) |

## Build planning

This spec gives the build team enough to scope:

- **Replay engine:** rebind recorded I/O against pinned versions; verify hashes;
  recompute verdict; compare; emit audit entry.
- **Audit chain store:** per-tenant single-writer queue; sequence assignment;
  canonical-form serializer; hash linker; root signer with periodic + trigger
  schedule; unsigned-tail tracker.
- **Verifier:** chain walker that distinguishes signed range from unsigned tail
  and reports `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` when applicable.
- **Tests:** every requirement scenario in `openspec/specs/replay-and-audit/spec.md`
  is a candidate test case.

## What this document does not define

- Hash algorithm (implementation choice; recommended: SHA-256 minimum).
- Signature scheme (implementation per ADR-0042).
- Audit chain storage layout (Merkle tree vs. append log vs. database).
- DR runbook / restore-drill cadence (future ADR addressing ARCH-P2-002).
- Per-tenant key rotation (lives in `vault-authorization`).
- Vault HSM choice / cloud KMS choice (implementation per ADR-0042).
