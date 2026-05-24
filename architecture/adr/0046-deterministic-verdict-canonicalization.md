# ADR-0046: Deterministic Verdict Canonicalization

**Status:** accepted  
**Owner:** architect  
**Established by:** v3.2.4.3  
**Version context:** v3.2.5.0 consolidation extraction from ZOVARK-v3.2.4.3-CLOSURE.md  
**Scope:** architecture decision only; no runtime implementation
**Established by:** v3.2.4.3.
**Related:** INV-004 (deterministic verdict), INV-006 (tamper evident), INV-018 (verdict canonicalization), INV-026 (integer-only numeric precision), INV-039 (canonical verdict input contract), ADR-0019 (mesh agent pool), ADR-0020 (tape recorder), ADR-0027 (verdict determinism canonicalization).

## Context

INV-004 promises byte-identical verdicts across two workers. The strategic review identified six failure vectors: floating-point in scoring, time-based inputs, ordering of LLM call results, ordering of tool execution results, database query result ordering, RLS-induced query plan variance. INV-026 closes the floating-point vector. The other five are not closed by any prior ADR. This ADR closes them, plus pins the audit-chain `row_canonical` definition and the mutation test corpus.

## Decision

`derive_verdict` and every helper it transitively calls obey these binding rules. Violations caught by type-system + runtime tests at M5.

### Forbidden inputs to derive_verdict

- Wall-clock time (`time.time`, `datetime.now`, DB `NOW()`, `CURRENT_TIMESTAMP`).
- Random sources (`random.*`, `secrets.*`, `os.urandom`, UUIDv4).
- Process-local state (PIDs, hostnames, container IDs).
- Iteration order of unordered collections (Python `set`, `dict` pre-3.7 semantics, Go `map`).
- Database query results without an `ORDER BY` clause that produces a total ordering on stable keys.
- File-system metadata (mtime, ctime, inode).
- Network I/O during verdict derivation (any syscall touching network during this function fails closed).

### Required canonical input

`derive_verdict` takes a single `VerdictInput` struct (Pydantic, frozen, extra=forbid) with these fields in this order:

```python
class VerdictInput(BaseModel):
    model_config = {'frozen': True, 'extra': 'forbid'}
    schema_version: str
    tenant_id: TenantId
    investigation_id: str
    logical_clock: int
    alert_envelope: CanonicalAlert
    tenant_config: CanonicalTenantConfig
    tool_catalog_version: str
    tool_results: tuple[ToolResult, ...]
    llm_records: tuple[LLMRecord, ...]
    db_results: tuple[DBResult, ...]
    model_version: str
    decoding_params: CanonicalDecodingParams
    prompt_hash: str
```

### Canonical sorting (closes "DB ordering" + "tool ordering" vectors)

Every `tuple[T, ...]` input is sorted before being passed to `derive_verdict`:
- `tool_results`: sorted by `(tool_call_id, sequence_number)`.
- `llm_records`: sorted by `(call_id, sequence_number)`.
- `db_results`: sorted by `(query_id, row_canonical_hash)` where `row_canonical_hash = sha256(canonical_json(row))`.

The tuple type forbids in-place mutation; sort is performed at construction time and is stable.

### Canonical JSON

All hashing, persistence, comparison uses **Canonical JSON**:
- UTF-8 NFC normalized strings.
- Object keys sorted lexicographically (UTF-8 code-point order).
- No insignificant whitespace.
- Numbers: integers only in deterministic paths (per INV-026); fractional scoring × 10^6 stored as integer.
- No floating-point in any verdict input or output.
- Booleans, null, strings: standard JSON.
- Arrays: order significant; set by canonical sorting above.

### Hash-chain `row_canonical` definition (closes issue #21)

```
row_canonical = canonical_json({
  "schema_version": "schema_version",
  "tenant_id": "tenant_id",
  "logical_clock": 0,
  "event_type": "event_type",
  "actor": "actor",
  "object": "object",
  "action": "action",
  "payload_hash": "sha256_hex",
  "prev_hash": "sha256_hex",
  "sequence_number": 0
})
```

Excluded from `row_canonical` (read-time / replication-time, may differ across replicas): physical row location, page, tuple ID; DB-generated wall-clock timestamps; replication LSNs; index IDs.

### Concurrent inserts (closes issue #21 vector "concurrent inserts")

The audit chain uses a per-tenant monotonic sequence allocator. Every insert acquires a tenant-scoped advisory lock (PostgreSQL `pg_advisory_xact_lock(tenant_id_hash)`) before reading `prev_hash` and computing `entry_hash`. Serializes inserts within a tenant; cross-tenant concurrency unaffected. Lock held only for canonicalization+hash+insert; not across business logic.

Enforced by:
- Trigger on `audit_event` that fails the insert if the advisory lock is not held.
- Runtime test running 100 concurrent inserts within the same tenant; verifies no duplicate sequence numbers; verifies hash-chain integrity after.

### Mutation test corpus (closes issue #21 vector "mutation testing implicit")

Explicit, not implicit. Lives at `tests/audit-chain/mutations/`. Exactly these mutations:

1. `OMIT_FIELD`: drop one of the `row_canonical` required fields.
2. `REORDER_KEYS`: serialize JSON with non-canonical key order.
3. `SKIP_PREV_HASH`: insert with `prev_hash = "__MISSING_PREV_HASH__"`.
4. `DUPLICATE_SEQUENCE`: two entries with the same `sequence_number`.
5. `CONCURRENT_INSERT_RACE`: two inserts that race for the same `prev_hash` (must be serialized by advisory lock).
6. `WRONG_TENANT_LOCK`: insert under tenant A while holding tenant B's lock.
7. `STALE_PREV_HASH`: insert with `prev_hash` pointing to a non-tip row.
8. `BACKDATE_LOGICAL_CLOCK`: insert with `logical_clock` < tenant's current.
9. `WHITESPACE_DRIFT`: serialize with non-canonical whitespace.
10. `UNICODE_NORMALIZATION_DRIFT`: insert string NFC-different from canonicalized form.

Each mutation must be detected within one verification cycle (typically <100ms) [hypothesis:M5-verdict-canonicalization-budget]. M5 acceptance requires all 10 red-listed in CI.

### Per-stage SLO budgets (closes issue #27)

Six-stage pipeline (INGEST → ANALYZE → EXECUTE → ASSESS → GOVERN → STORE) with explicit per-stage budgets composing to the headline. [hypothesis:M5-saturation-benchmark] budgets at v3.2.4.3, replaced by `[measured]` at the M5 saturation benchmark:

| Stage | p95 budget (hypothesis) | Source |
|-------|------------------------|--------|
| INGEST | 500 ms | normalize + tenant resolution + dedupe |
| ANALYZE | 120 s | LLM tool-loop with continuous batching N=4 |
| EXECUTE | 30 s | tool execution; majority WASM-pure |
| ASSESS | 5 s | scoring + verdict canonicalization |
| GOVERN | 10 s | policy check + EDR action gate |
| STORE | 200 ms | audit chain insert + replay record write |
| **headline** | **≤180 s p95** | sum + queue budget |

The "~50 campaigns/hour" and "~1.2× single-call latency" claims from prior iterations are **provisionally retired**: any document referencing them must add `[hypothesis]` and a benchmark-artifact ID, or be removed by M5. M5 produces measured numbers under the saturation benchmark; we replace this table with `[measured]` values.

### Enforcement

- `tests/architecture/verdict-determinism.test.py` (M1 stub; M5 full): given two workers and same `VerdictInput`, asserts byte-identical `VerdictEnvelope`. Includes randomized DB insertion order, tool-result order, LLM-record order; canonical sorting must absorb the randomization.
- `tests/architecture/forbidden-imports-in-verdict.test.py` (M1): static AST check that `derive_verdict` and callees do not import `time`, `datetime`, `random`, `secrets`, `os.urandom`, or use `set` / unordered `dict` iteration.
- `tests/audit-chain/mutations/` (M5): the 10 mutations above.

## Consequences

- `VerdictInput` Pydantic model becomes binding type. Adding a field is breaking change requiring schema-version bump.
- Every developer touching the verdict path must understand canonical JSON. Onboarding doc lands M5.
- Performance: canonical sorting adds per-investigation overhead proportional to (n_tool_results + n_llm_records + n_db_results). Budgeted; expected <50ms typical [hypothesis:M5-verdict-canonicalization-budget].
- `model_version` field requires inference layer to expose its exact build. ADR-0009 amended in M5 to require this.

## Alternatives Considered

- *Document the rules as policy without enforcement*: rejected; status quo from prior ADRs.
- *Allow floating-point with "small enough delta" tolerance*: rejected; "small enough" cannot be byte-identical.
- *UUIDs for sequence numbers*: rejected; UUIDs do not produce useful order.
- *Timestamps for sequence numbers*: rejected; relies on wall clock.
