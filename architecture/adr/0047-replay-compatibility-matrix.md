# ADR-0047: Replay Compatibility Matrix and Failure Modes

**Status:** accepted  
**Owner:** replay-owner  
**Established by:** v3.2.4.3  
**Version context:** v3.2.5.0 consolidation extraction from ZOVARK-v3.2.4.3-CLOSURE.md  
**Scope:** architecture decision only; no runtime implementation
**Established by:** v3.2.4.3.
**Related:** ADR-0020 (tape recorder), ADR-0026 (replay compatibility), ADR-0046 (verdict canonicalization), INV-005 (replayable), INV-017 (replay fails closed on incompatibility), INV-036 (replay engine never inferences/substitutes/degrades).

## Context

INV-005 says investigations are replayable byte-identically. INV-017 says replay fails closed on incompatibility. ADR-0020 records LLM I/O at investigation time and replays from the record rather than re-inferencing. The strategic review identified three replay failure modes not closed by these statements: (a) recorded LLM output names a tool that no longer exists, (b) replay record is older than current schema, (c) recorded model version is no longer available. This ADR closes all three with explicit fail-closed semantics and a versioned compatibility matrix.

## Decision

### Replay record contents (binding)

```python
class ReplayRecord(BaseModel):
    model_config = {'frozen': True, 'extra': 'forbid'}
    schema_version: str
    record_format_version: str
    investigation_id: str
    tenant_id: TenantId
    captured_logical_clock: int       # logical clock, not wall clock
    replay_compatibility_contract: str # architecture/replay-compatibility.yaml
    failure_policy: str               # fail_closed
    tool_catalog_version: str         # exact version pinned at capture
    model_id: str                     # exact build, not just family
    model_version: str
    decoding_params: CanonicalDecodingParams
    prompt_hashes: tuple[str, ...]
    verdict_input: VerdictInput
    verdict_input_hash: str
    llm_io: tuple[LLMIORecord, ...]   # canonical-sorted
    tool_io: tuple[ToolIORecord, ...] # canonical-sorted
    db_snapshots: tuple[DBSnapshot, ...]
    verdict_envelope_hash: str        # the byte-identical-target
```

The concrete architecture contract artifact for this record is
`architecture/blueprint/schemas/replay_record.schema.json`. It captures the
approved logical clock, the committed replay compatibility contract path, the
recorded `VerdictInput`, model-visible I/O records, provenance, and hashes
needed for deterministic replay proof. This artifact does not add replay-engine
implementation; runtime enforcement remains scheduled under INV-036.

The concrete architecture contract artifact for fail-closed replay reporting is
`architecture/blueprint/schemas/replay_failure_record.schema.json`. It defines
the canonical replay failure-code vocabulary and a bounded failure-record shape
for replay validation outcomes. This artifact does not add replay-engine
implementation or runtime coverage mapping; runtime enforcement remains
scheduled under INV-036.

### Compatibility matrix

`architecture/replay-compatibility.yaml` is the committed architecture replay
compatibility contract:

```yaml
record_format_versions:
  "1.0.0":
    introduced_in: v3.2.4.3
    schema_version_compatible_with: ">=1.0.0,<2.0.0"
    tool_catalog_version_compatible_with: ">=1.0.0,<2.0.0"
    fallback_strategy: fail_closed
```

The replay engine reads this matrix at startup when runtime replay is implemented. Every replay request is checked before any compute.

The matrix also carries `failure_outcome_rows`: stable architecture row IDs that bind canonical replay failure codes to fail-closed compatibility outcomes and bounded runtime evidence requirements. Each canonical replay failure code appears in exactly one outcome row unless a future architecture change introduces an explicit bounded exclusion. These rows are architecture authority for future runtime row-mapping proof; they do not implement replay-engine behavior and do not by themselves claim runtime coverage completion. These architecture rows alone do not establish `REPLAY_COMPATIBILITY_MATRIX_COVERAGE_OK`; that marker is established only by a separate runtime row-equality proof (defined below).

Runtime row-equality coverage marker. A runtime proof MAY assert `REPLAY_COMPATIBILITY_MATRIX_COVERAGE_OK` with the narrow meaning that the canonical failure codes in `failure_outcome_rows` (declared here) are row-for-row equal to the set covered by runtime fail-closed tests and runtime row-mapping (`covered_rows_source` vs `declared_rows_source`). This marker asserts row-equality coverage of the declared failure rows only. It does not assert completeness of the replay-compatibility matrix, replay-engine behavior, or runtime readiness; the three preceding constraints still hold.

### Failure mode 1: recorded tool name no longer in catalog

When the replay record references a tool that exists in the recorded `tool_catalog_version` but not in the current catalog (the tool was retired), replay fails closed:

```
REPLAY_TOOL_RETIRED: tool={tool_name} recorded_version={recorded_version} current_version={current_version}
```

The machine-readable authority for this failure mode is
`architecture/blueprint/schemas/replay_tool_catalog.schema.json` plus the
versioned catalog artifacts under `architecture/replay/catalogs/`.
`architecture/replay-compatibility.yaml` names the current tool catalog version
and the catalog artifact path for each replay catalog version. A replay tool
identity is the pair `(tool_name, tool_version)`, matching
`ReplayToolIORecord`.

The deterministic retirement rule is: if a replay record references a tool
identity that exists in the recorded catalog artifact, is absent from the active
tools in the current catalog artifact, and appears in the current catalog's
`retired_tools` ledger with `failure_code: REPLAY_TOOL_RETIRED` and
`row_id: tool_compatibility.tool_retired`, replay may fail closed with
`REPLAY_TOOL_RETIRED`. This rule defines architecture authority only; it does
not implement runtime replay-engine behavior and does not claim runtime
coverage completion.

Replay does NOT attempt successor mapping. Does NOT silently downgrade. Does NOT inference. The investigation's verdict cannot be re-derived; replay produces a typed error.

Customer remediation: pin the customer instance to the recorded `tool_catalog_version` (read-only; for replay only). Customer instances run multiple historical catalogs side-by-side for replay; only the current catalog is used for new investigations.

### Failure mode 2: replay record older than current schema

If the record's `schema_version` is outside the matrix range, replay fails closed:

```
REPLAY_SCHEMA_INCOMPATIBLE: record_schema={record_schema_version} compatible_range={compatible_range}
```

Every major schema bump ships a **golden replay corpus**: a fixed set of replay records under the old schema that the new replay engine must verify byte-identically. If it cannot, the schema bump is invalid and rolled back.

The corpus will be stored at `tests/replay-corpus/{schema_version}/` and will run in CI on every PR (planned, M5; not yet built).

### Failure mode 3: recorded model version no longer available

The replay engine does NOT re-inference. It uses the recorded LLM output from `llm_io`. Model version availability is therefore irrelevant to byte-identical replay.

Model version is recorded for **provenance and audit explanation** purposes only. If a customer or auditor asks "what model produced this output?", the replay record answers. If that model build is no longer available, replay still produces byte-identical results.

### Tool catalog retirement policy

A tool may be retired only via:
1. ADR amendment naming the retirement.
2. 30-day deprecation window (tool present but flagged `deprecated`).
3. Tool removed from new investigations after deprecation window.
4. Tool catalog version bumped (minor: `1.5.0 → 1.6.0`).
5. Replay against records using the retired tool fails closed per Failure mode 1.

### Test fixtures (M5)

Planned, not yet built. These fixtures will live under `tests/replay/`:
- `tool-retired/`: replay record references retired tool; expects `REPLAY_TOOL_RETIRED`.
- `schema-incompatible/`: replay record schema outside matrix range; expects `REPLAY_SCHEMA_INCOMPATIBLE`.
- `model-unavailable/`: replay record references unavailable model; expects byte-identical replay (model unavailability is not an error).
- `byte-identical/`: replay record + current state; expects byte-identical verdict envelope.

### Replay-engine invariants (NEW: INV-036)

INV-036: "Replay engine never inferences; never silently substitutes; never produces a degraded result."

## Consequences

- Customer instances must support running multiple `tool_catalog_version`s side-by-side (read-only, for replay). Adds storage and inventory complexity.
- Major schema version bumps require golden-replay-corpus production. Adds release engineering work.
- Audit queries that need "the verdict for this old investigation" always work; queries that need "re-derive the verdict under current rules" fail closed and require explicit re-investigation.
- Customer-facing message when replay fails-closed must be clear, actionable, and not blame the customer for our retirement decisions.

## Alternatives Considered

- *Best-effort replay with degraded results*: rejected; INV-017 says fail closed.
- *Automatic tool successor mapping*: rejected; semantic drift unpredictable; mapping creates non-determinism.
- *Re-inference on model unavailability*: rejected; defeats the entire ADR-0020 record-and-replay model.
- *Discard old replay records on schema bump*: rejected; auditors and customers expect old records to remain queryable.
