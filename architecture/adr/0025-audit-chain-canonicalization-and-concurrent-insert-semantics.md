# ADR-0025: Audit chain canonicalization and concurrent-insert semantics

**Status:** accepted  
**Date:** 2026-04-28  
**Owner:** audit-owner  
**Version context:** v3.2.5.0 consolidation promotion from zovark-v1-bootstrap-v3.2.3.2-final.zip  
**Source classification:** bootstrap predecessor ADR, mechanically normalized for current ADR format
## Context

ADR-0020 and INV-006 require hash-chained audit events: `chain_hash = sha256(prev_hash || row_canonical)`, with `verify_audit_chain.sh` walking the chain. The original specification leaves three load-bearing details undefined:

1. **What is `row_canonical`?** Tenant ID inclusion, timestamp precision, JSON field ordering, nullable handling, encoding (UTF-8 normalization), and chain root signature inputs all materially affect chain semantics. Two implementations of `row_canonical` will produce different chains for the same logical events; chain mismatch under replay is then unidentifiable as canonicalization drift versus tampering.
2. **Concurrent inserts.** Two simultaneous events in the same tenant could read the same `prev_hash` if the insert trigger does not serialize per-tenant. The chain forks; one event's `chain_hash` is correct, the other is not — and which is which depends on commit order.
3. **Mutation testing corpus.** ADR-0020 names "mutation testing on hash-chain code paths" but does not enumerate the mutants. Without an explicit corpus, the test passes vacuously.

This ADR specifies all three. It is not a supersession of ADR-0020; it is a correctness extension.

## Decision

**Canonicalization.** `row_canonical` is computed via RFC 8785 JSON Canonicalization Scheme (JCS) over a fixed field set:

```
{
  "event_id": "uuid",
  "tenant_id": "uuid",
  "event_type": "enum-string",
  "actor_id": "uuid",
  "subject_id": "uuid-or-null",
  "occurred_at_ns": 0,
  "occurred_seq": 0,
  "payload": { ... canonicalized inner JSON ... }
}
```

Excluded fields: `chain_hash`, `prev_hash`, `chain_root_signature`, `inserted_at` (database arrival timestamp, distinct from `occurred_at_ns`). These are chain-derived or operationally observed; including them would make the chain self-referential.

Field-level rules:
- Strings are NFC-normalized UTF-8.
- Numbers are integer or RFC 8785 `Number` form; floats are forbidden in canonicalized payloads.
- Object keys are lexicographically ordered (JCS default).
- Arrays preserve insertion order; insertion order itself must be canonical (see ADR-0027 for verdict-side ordering).
- `null` is permitted only on fields explicitly typed nullable in `schemas/audit_event.schema.json`.

**Audit row immutability.** Once an `audit_events` row is committed it is never mutated. A database trigger rejects `UPDATE` and `DELETE` on `audit_events`. Erasure is achieved by destroying the identity-resolution mapping or the per-tenant DEK (per ADR-0024); the audit chain itself is append-only forever. INV-020 binds this rule.

**Per-tenant serialization.** Concurrent inserts in the same tenant are serialized via a per-tenant lock row, not a hashed advisory lock. The v2 design used `pg_advisory_xact_lock(hashtext('audit:' || tenant_id::text))`; `hashtext` is not collision-resistant and a collision would cause unexpected cross-tenant contention or — in pathological deployments — confused locking. v3 uses a dedicated table:

```sql
CREATE TABLE tenant_audit_locks (
  tenant_id    uuid    PRIMARY KEY,
  next_seq     bigint  NOT NULL DEFAULT 1
);

-- Inside the audit_events insert trigger, for the current tenant_id:
SELECT next_seq
FROM tenant_audit_locks
WHERE tenant_id = $1
FOR UPDATE;
-- Read prev_hash for this tenant under the lock.
-- Compute row_canonical, chain_hash.
-- INSERT into audit_events.
-- UPDATE tenant_audit_locks SET next_seq = next_seq + 1 WHERE tenant_id = $1.
-- Commit releases the row lock.
```

`occurred_seq` is the value read at `SELECT ... FOR UPDATE` time. The row lock is per-tenant; cross-tenant inserts run in parallel without contention. Rolled-back transactions release the lock without consuming the sequence (since the `UPDATE` rolls back too); sequence holes are not tolerated under this scheme — the chain is dense per tenant.

The `tenant_audit_locks` table is created at tenant bootstrap and never deleted; on tenant crypto-shred (ADR-0024 Workflow B), the row is preserved as a chain marker but the tenant DEK is destroyed.

**Chain root signatures — history table, not single signature.** Chain root signatures are stored append-only in `audit_chain_roots`:

```sql
CREATE TABLE audit_chain_roots (
  root_id                       uuid     PRIMARY KEY,
  tenant_id                     uuid     NOT NULL,
  sequence_low                  bigint   NOT NULL,   -- lowest occurred_seq covered (inclusive)
  sequence_high                 bigint   NOT NULL,   -- highest occurred_seq covered (inclusive)
  root_hash                     bytea    NOT NULL,   -- chain_hash at sequence_high
  previous_root_hash            bytea,                -- root_hash of the immediately preceding root for this tenant
  signed_at_ns                  bigint   NOT NULL,
  signing_key_fingerprint       text     NOT NULL,
  signature                     bytea    NOT NULL,
  created_by                    text     NOT NULL    -- "audit-root-signer-job"
);

CREATE INDEX ON audit_chain_roots (tenant_id, sequence_high);
```

A new root row is signed every minute per active tenant covering `(previous_root.sequence_high + 1) .. current_sequence_high_water`. The signature is Ed25519 over the canonical payload `(tenant_id || sequence_low || sequence_high || root_hash || previous_root_hash || signed_at_ns || signing_key_fingerprint)`. Old signatures are never rewritten; regulator export attaches the signature rows whose ranges intersect the export window. Old signing keys are retained for verification of historical signatures and never destroyed.

**Verification states.** `scripts/verify_audit_chain.sh` walks the chain in `(tenant_id, occurred_seq)` order and reports a structured state per tenant:

| State | Meaning |
|---|---|
| `VALID_FULLY_SIGNED` | Every committed event lies within a verified `audit_chain_roots` interval |
| `VALID_WITH_UNSIGNED_TAIL` | Chain valid up through the latest signed range; events newer than the latest root signature are correctly chained but not yet signed (normal under 1-minute signing cadence) |
| `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` | Chain valid post-restore; a `DISASTER_RECOVERY_RESTORE_COMPLETED` event is present declaring a known data-loss window; the post-restore chain is internally consistent but does not prove absence of data loss in the declared window |
| `BROKEN_AT_SEQUENCE` | Recomputed `chain_hash` does not match stored value at a specific `(tenant_id, occurred_seq)`; reports diff |
| `ROOT_SIGNATURE_INVALID` | A `audit_chain_roots` row's signature does not verify against its `signing_key_fingerprint` |
| `ROOT_RANGE_MISSING` | Gap in `audit_chain_roots` ranges for a tenant where events exist (indicates either signing job failure or tampering with `audit_chain_roots`) |
| `ROOT_RANGE_OVERLAP` | Two `audit_chain_roots` rows for the same tenant overlap (corrupted history) |
| `RESTORE_WITHOUT_GAP_MARKER` | Chain shows discontinuity consistent with a restore operation but no `DISASTER_RECOVERY_RESTORE_COMPLETED` event is present; treated as broken until the marker is appended or a `BROKEN_AT_SEQUENCE` diagnosis confirms tampering |

This explicitly distinguishes the normal "events newer than latest root signature" case from the tampering case, and additionally distinguishes a documented restore-with-gap from undocumented chain discontinuity. The v2 design conflated these.

**Restore-gap rule (v3.1 addition).** A valid post-restore audit chain proves internal consistency of the recovered chain. It does not prove absence of data loss. Any PITR, failover, or backup restore that may lose committed events must append a `DISASTER_RECOVERY_RESTORE_COMPLETED` event before reopening the chain to ingest. The event payload conforms to `architecture/blueprint/schemas/dr_restore_completed_event.schema.json` and includes:

```
restore_started_at_ns
restore_completed_at_ns
restored_to_lsn
restored_to_timestamp
pre_restore_latest_root_hash_if_available
post_restore_chain_root
known_data_loss_window_start
known_data_loss_window_end
operator_id
incident_id
```

Verifiers reading the chain after restore report `VALID_AFTER_RESTORE_WITH_DECLARED_GAP` and surface the declared gap to the regulator-export bundle and customer reliability disclosure. A restore without the marker reports `RESTORE_WITHOUT_GAP_MARKER` and the chain is treated as broken. ADR-0024 Workflow D (DR restore) is the operational counterpart and is the only authorized entry point for appending this event.

**Mutation testing corpus.** Mutants required to be killed by the test suite:

1. Drop `tenant_id` from canonicalization.
2. Replace `occurred_at_ns` with `inserted_at`.
3. Reverse JCS object-key ordering.
4. Skip NFC normalization on string fields.
5. Remove the per-tenant lock (allows concurrent prev_hash read).
6. Use `occurred_at_ns` instead of `occurred_seq` for chain ordering (timestamps can collide).
7. Sign chain root without `signing_key_fingerprint`.
8. Allow null `prev_hash` on non-genesis rows.
9. Skip canonicalization on `payload` field.
10. Use SHA-1 instead of SHA-256.
11. (v3 addition) Allow `UPDATE` on a committed `audit_events` row.
12. (v3 addition) Allow overlapping `audit_chain_roots` ranges for the same tenant.

`tests/architecture/audit-chain-mutation.test.py` constructs each mutant explicitly and asserts the production code rejects it.

## Consequences

**Positive.** Chain semantics are unambiguous; two implementations against this spec produce identical chains for identical event streams. Concurrent inserts are correct by construction (lock-table + `FOR UPDATE` is reviewable; no hash-collision concern). Mutation testing has an explicit corpus including the v3-added immutability and signature-overlap mutants. Replay-time chain mismatches are diagnosable as canonicalization drift versus tampering. Regulator export attaches interval-precise signatures, not just the latest. The `VALID_WITH_UNSIGNED_TAIL` state distinguishes normal operation from tampering.

**Negative.** RFC 8785 JCS adds dependency surface (a JCS library per language binding). Lock-table approach is marginally slower than advisory locks under high single-tenant write contention (the worst-case observed in v1.0 alert volumes is well below the contention point; revisit only if a tenant exceeds tens of audit events per second sustained). `audit_chain_roots` grows without bound (one row per minute per active tenant ≈ 525,600 rows/tenant/year); planned for archival to compressed storage after 90 days, retaining cryptographic signature for verification.

**Risks accepted.** RFC 8785 is a stable RFC but the ecosystem of conforming implementations is small; the bindings used in v1.0 are pinned and version-locked per ADR-0014's WASM patch SLA equivalent. If a JCS library bug is found, the patch SLA mirrors Wasmtime's: 14 days for Critical/High advisories. The `tenant_audit_locks` row is a single row per tenant; if it is corrupted, recovery requires DR restore from backup plus re-signing the affected range.

## Alternatives Considered

N/A — original ADR did not address this.

## Fitness functions

- `tests/architecture/audit-canonicalization-vectors.test.py` — for a fixed set of input events, asserts the canonical form matches the spec byte-for-byte across language bindings (Python, Go, Rust, TypeScript).
- `tests/contract/audit-lock-no-fork-concurrent.test.py` — drives 1000 concurrent inserts across multiple tenants; asserts no chain forks, all chains validate, no sequence holes per tenant.
- `tests/architecture/audit-chain-mutation.test.py` — runs the 12-mutant corpus; asserts every mutant is killed.
- `tests/contract/audit-root-range-signature.test.py` — generates `audit_chain_roots` rows over multiple intervals; asserts signatures validate; asserts overlapping or missing intervals rejected.
- `tests/contract/audit-unsigned-tail-status.test.py` — appends events without running the signing job; asserts verification reports `VALID_WITH_UNSIGNED_TAIL` not `BROKEN_AT_SEQUENCE`.
- `tests/contract/audit-row-immutability.test.py` — attempts `UPDATE` on a committed row; asserts trigger rejects.
- `tests/contract/audit-erasure-does-not-mutate-old-rows.test.py` — runs identity-resolution destruction (per ADR-0024); asserts no `audit_events` row was modified.
- `tests/contract/audit-crypto-shred-chain-continuity.test.py` — runs Workflow B crypto-shred; asserts chain still validates as `VALID_FULLY_SIGNED`, tombstone events are present, and pre-shred range remains verifiable via retained signing-key fingerprints.

## References

- INV-006 (tamper-evident), INV-008 (schema-first), INV-016 (audit canonicalization), INV-020 (audit erasure boundary, new)
- ADR-0020 (tape recorder), ADR-0024 (tenant lifecycle workflows)
- `zovark.md` §7
