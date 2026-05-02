# Slice 001 — Build Readiness Review

Review date: 2026-05-02
Reviewer: architecture tutor pass (pre-build)
Spec files reviewed:
- `.kiro/specs/slice-001-investigation-tape/requirements.md`
- `.kiro/specs/slice-001-investigation-tape/design.md`
- `.kiro/specs/slice-001-investigation-tape/tasks.md`

Architecture sources cross-checked:
- `architecture/one-page-architecture.md`
- `openspec/specs/investigation-tape/spec.md`
- `openspec/specs/edr-handoff/spec.md`
- `openspec/specs/replay-and-audit/spec.md`

Patches applied to spec files before this review was written:
1. Added `raw_content` field to evidence entries in design.md §1.2 and requirements.md REQ-002 — required for replay hash recomputation without re-reading the input file.
2. Tightened `signing_tag` derivation in design.md §1.5 — now names the exact fields included in the hash snapshot.
3. Added `handoff_id` derivation to design.md §4.3 derivation table.
4. Added note that `finding_id`, `timeline_event_id`, and `verdict_id` do not exist (correct per architecture spec).
5. Fixed `entry_id` inconsistency — design.md §1.8 said `"audit-entry-001"`, tasks.md §9.2 said `"audit-entry-1"`. Standardised to `"audit-entry-1"` / `"audit-entry-2"` throughout.
6. Added `customer-report.md` as the ninth output artifact in requirements.md REQ-012 and design.md §8, with full structure definition.
7. Updated tasks.md Task 3, 10, 11, 12 to reflect the above.
8. Added audit chain linkage test to tasks.md Task 9 (replay entry `prev_entry_hash` equals close entry `this_entry_hash`).

---

## 1. Requirements → Design → Task → Test traceability matrix

| Requirement | Design section | Task | Test file | AC coverage |
|---|---|---|---|---|
| REQ-001 Static input ingestion | §1.1, §6 | Task 3 | `test_ingest.py` | AC-001-1,2,3 |
| REQ-002 Evidence normalization | §1.2, §4.3 | Task 3 | `test_ingest.py` | AC-002-1,2,3,4 |
| REQ-003 Investigation tape creation | §1.6, §7 | Task 4 | `test_tape.py` | AC-003-1..8 |
| REQ-004 Timeline construction | §1.3 | Task 5 | `test_timeline.py` | AC-004-1..5 |
| REQ-005 Rule-driven findings | §1.4 | Task 6 | `test_findings.py` | AC-005-1..5 |
| REQ-006 Deterministic verdict | §1.5, §4.3 | Task 7 | `test_verdict.py` | AC-006-1..6 |
| REQ-007 Approval-required EDR action card | §1.7, §4.3 | Task 8 | `test_handoff.py` | AC-007-1..13 |
| REQ-008 Tape sealing + audit entry | §1.8, §4.4 | Task 9 | `test_audit.py` | AC-008-1..7 |
| REQ-009 Replay report | §1.9, §1.10, §1.11 | Task 10 | `test_replay.py` | AC-009-1..8 |
| REQ-010 Determinism | §4.1, §4.3 | Task 13 | `test_cli.py` | AC-010-1..4 |
| REQ-011 CLI interface | §3 | Task 12 | `test_cli.py` | AC-011-1..6 |
| REQ-012 Output artifact list | §8 | Task 11, 14 | `test_writer.py`, `test_cli.py` | AC-012-1..7 |

All 12 requirements have design coverage, a task, and a test file. No orphaned
requirements. No orphaned tasks.

---

## 2. Output artifact list

| # | Filename | Type | Producer |
|---|---|---|---|
| 1 | `investigation-tape.json` | JSON | `tape.py` + `writer.py` |
| 2 | `evidence-ledger.json` | JSON | Extracted from tape by `writer.py` |
| 3 | `timeline.json` | JSON | Extracted from tape by `writer.py` |
| 4 | `findings.json` | JSON | Extracted from tape by `writer.py` |
| 5 | `verdict.json` | JSON | Extracted from tape by `writer.py` |
| 6 | `edr-handoff.json` | JSON | `handoff.py` + `writer.py` — approval-required EDR action card |
| 7 | `audit-chain-entry.json` | JSON | `audit.py` + `writer.py` |
| 8 | `replay-report.json` | JSON | `replay.py` + `writer.py` |
| 9 | `customer-report.md` | Markdown | `writer.py` |

---

## 3. Per-artifact detail

### 3.1 `investigation-tape.json`

**Producer module:** `tape.py` (construction, sealing), `writer.py` (serialization)

**Required fields:**
- Identity: `tape_id`, `tenant_id`, `created_at`, `schema_version`, `source_alert_ref`
- `state: "closed"`
- `raw_evidence[]` — each entry: `evidence_id`, `hash`, `source_type`, `ingested_at`, `raw_content`
- `timeline[]` — each event: `event_type`, `at`, `actor`, `evidence_refs`, `decision_contribution`
- `findings[]` — each finding: `title`, `severity`, `evidence_refs`, `model_contribution`
- `verdict` — `value`, `evidence_refs`, `model_contribution`, `signing_tag`, `set_at`
- `handoff_ref`, `handoff_summary`
- `audit_ref`

**Forbidden fields:** `replay_state_ref`, `state: "replaying"`, `recorded_io` (absent when no models used)

**Validation rule:** `seal_tape()` pre-close checklist in design.md §7. Raises `ZovarkValidationError` on any missing required field or invalid enum value.

**Test coverage:** `test_tape.py` (unit), `test_cli.py` (end-to-end)

---

### 3.2 `evidence-ledger.json`

**Producer module:** `writer.py` (extracts `tape["raw_evidence"]`)

**Required fields:** Same as `raw_evidence[]` entries above. Each entry must have `evidence_id`, `hash`, `source_type`, `ingested_at`, `raw_content`.

**Validation rule:** Content must be byte-identical to `investigation-tape.json`'s `raw_evidence` field (AC-012-3).

**Test coverage:** `test_writer.py`, `test_cli.py`

---

### 3.3 `timeline.json`

**Producer module:** `timeline.py` (construction), `writer.py` (extraction)

**Required fields:** Array of timeline events. Each: `event_type`, `at`, `actor`, `evidence_refs`, `decision_contribution`. Must contain at minimum: `alert_received`, `evidence_added` (×N), `finding_recorded` (×M), `verdict_set`, `handoff_dispatched`, `audit_signed`. Events in non-decreasing `at` order.

**Validation rule:** Non-decreasing timestamp order enforced in `timeline.py`. Content must match tape's `timeline` field (AC-012-4).

**Test coverage:** `test_timeline.py`, `test_writer.py`

---

### 3.4 `findings.json`

**Producer module:** `findings.py` (derivation), `writer.py` (extraction)

**Required fields:** Array of findings. Each: `title`, `severity`, `evidence_refs` (non-empty), `model_contribution: false`. `confidence_band` omitted (post-MVP).

**Validation rule:** Every `evidence_id` in `evidence_refs` must exist in `raw_evidence`. `model_contribution` must be `false`. Content must match tape's `findings` field (AC-012-5).

**Test coverage:** `test_findings.py`, `test_writer.py`

---

### 3.5 `verdict.json`

**Producer module:** `verdict.py` (computation), `writer.py` (extraction)

**Required fields:** `value` (fixed enum), `evidence_refs` (non-empty when findings exist), `model_contribution: false`, `signing_tag`, `set_at`.

**Validation rule:** `value` must be one of `benign`, `suspicious_unconfirmed`, `confirmed_malicious`, `inconclusive_insufficient_evidence`. `signing_tag` is deterministic (same input → same tag). Content must match tape's `verdict` field (AC-012-6).

**Test coverage:** `test_verdict.py`, `test_writer.py`

---

### 3.6 `edr-handoff.json` — Approval-required EDR action card

**Producer module:** `handoff.py`, `writer.py`

**Required fields (all 14):**
- Identity: `handoff_id`, `tenant_id`, `tape_ref`
- Action: `action_type`, `target` (`kind`, `identifier`, `validated_at`)
- Evidence/policy: `evidence_refs`, `policy_snapshot`, `policy_snapshot_version`
- Authorization: `approval_mode: "approval_required"`, `authorization_record_ref: "vault://placeholder/bootstrap"`
- Execution: `execution_result` (`status: "pending"`, `reason: "recommendation_only_no_dispatcher_in_slice_001"`, `started_at: null`, `completed_at: null`, `vendor_response_ref: null`, `error: null`)
- Idempotency: `idempotency_key`
- Rollback/reversibility: `rollback_plan` with `reversibility_class` ∈ {`reversible_by_edr`, `manual_recovery_required`, `irreversible_requires_compensation`}; `vendor_reversal_action`; `vendor_reversal_target`; `manual_steps`; `reversal_window`; `idempotency_key`
- Linkage: `audit_ref`, `replay_linkage: []`

**Validation rule:** `action_type`/`target.kind` consistency enforced. `evidence_refs` non-empty and all IDs present on tape. `approval_mode` must be `approval_required`. `authorization_record_ref` must be the bootstrap placeholder. `reversibility_class` must be one of the three allowed values.

**Test coverage:** `test_handoff.py`, `test_cli.py`

---

### 3.7 `audit-chain-entry.json`

**Producer module:** `audit.py`, `writer.py`

**Required fields:** `entry_id: "audit-entry-1"`, `tenant_id`, `sequence: 1`, `event_type: "tape_recording_closed"`, `payload` (`tape_id`, `verdict_value`, `fields_hash`), `created_at`, `prev_entry_hash` (= `sha256("genesis")`), `this_entry_hash`, `signed_root: null`.

**Validation rule:** `this_entry_hash` computed by setting field to `""`, hashing canonical JSON, replacing. `prev_entry_hash` is the genesis anchor. `signed_root` is null (root signing deferred to M1+).

**Test coverage:** `test_audit.py`, `test_cli.py`

---

### 3.8 `replay-report.json`

**Producer module:** `replay.py`, `writer.py`

**Required fields:**
- `replay_state`: `replay_id`, `tape_ref`, `tenant_id`, `mode: "recorded_output"`, `schema_pin: "tape/1.0"`, `tool_catalog_pin: "none-slice-001"`, `model_versions_pin: []`, `state` (succeeded/mismatch/failed), `mismatch_details`, `unsigned_tail_replay: true`, `started_at`, `completed_at`
- `audit_chain_entry`: `entry_id: "audit-entry-2"`, `sequence: 2`, `event_type: "tape_replayed"`, `payload`, `prev_entry_hash` (= `audit-entry-1`'s `this_entry_hash`), `this_entry_hash`, `signed_root: null`

**Validation rule:** `replay_state.state` is `succeeded` on a clean tape. `audit_chain_entry.prev_entry_hash` must equal `audit-chain-entry.json`'s `this_entry_hash` (chain linkage). `unsigned_tail_replay: true` always in Slice 001.

**Test coverage:** `test_replay.py`, `test_audit.py` (chain linkage), `test_cli.py`

---

### 3.9 `customer-report.md`

**Producer module:** `writer.py`

**Required content (in order):** recommended action, target, approval mode, evidence
summary, verdict, reversibility/recovery classification, replay proof status, audit
chain summary, internal proof substrate fields, artifact list. The action decision
section must appear before any internal substrate fields.

**Validation rule:** Must open with the recommended action section. Must contain
action type, target, approval mode, evidence summary, verdict value,
`reversibility_class`, replay result, and all 9 artifact filenames (AC-012-7).

**Test coverage:** `test_writer.py`, `test_cli.py`

---

## 4. Deterministic ID rules

| ID field | Derivation | Stable inputs | Notes |
|---|---|---|---|
| `tape_id` | `"tape-" + sha256(tenant_id + ":" + source_alert_ref)[:16]` | `tenant_id`, `source_alert_ref` | Deterministic given same tenant + alert ref |
| `evidence_id` | `"ev-" + sha256(source_type + ":" + sha256_of_obj(source_object))` | `source_type`, source object content | Content-addressed; changes if source object changes |
| `handoff_id` | `"handoff-" + sha256(tape_id + ":" + action_type + ":" + target.identifier)[:16]` | `tape_id`, `action_type`, `target.identifier` | Derived from tape + action; deterministic |
| `replay_id` | `"replay-" + sha256(tape_id + ":recorded_output")[:16]` | `tape_id` | One replay per tape in Slice 001 |
| `entry_id` (audit) | `"audit-entry-" + str(sequence)` | `sequence` integer | Sequence 1 = close entry, sequence 2 = replay entry |
| `idempotency_key` (handoff) | `sha256(tape_id + ":" + action_type + ":" + target.identifier)` | `tape_id`, `action_type`, `target.identifier` | Full hex; `handoff_id` is the first 16 chars prefixed |
| `idempotency_key` (rollback) | `sha256(tape_id + ":rollback:" + vendor_reversal_action + ":" + target.identifier)` | `tape_id`, `vendor_reversal_action`, `target.identifier` | Separate key from handoff |
| `signing_tag` | `"sig-" + sha256_of_obj(snapshot)` where snapshot = `{tape_id, tenant_id, schema_version, source_alert_ref, raw_evidence, findings, verdict_value}` | All stable fields at verdict time | Does NOT include `timeline`, `handoff_ref`, `audit_ref`, `state` |
| `policy_snapshot` | `sha256("slice-001-bootstrap-policy")` | Literal string constant | Fixed value for all Slice 001 runs |
| `prev_entry_hash` (first) | `sha256("genesis")` | Literal string constant | Bootstrap anchor |
| `this_entry_hash` | `sha256_of_obj(entry_with_this_entry_hash_set_to_"")` | All other entry fields | Circular-dependency-free computation |

**IDs that do not exist (correct per architecture spec):**
- `finding_id` — findings are embedded objects identified by position and `evidence_refs`, not by standalone IDs.
- `timeline_event_id` — timeline events have no ID field.
- `verdict_id` — the verdict is an embedded object on the tape, not a separate record.

---

## 5. Timestamp rules

### 5.1 Timestamps that come from the sample input

| Field | Source | Value in sample |
|---|---|---|
| `source_alert_ref` (alert timestamp component) | `raw_input["timestamp"]` | `"2026-05-01T10:00:00Z"` |
| `process_event.timestamp` | `raw_input["process_events"][0]["timestamp"]` | `"2026-05-01T10:00:01Z"` |
| `target.validated_at` (handoff) | Derived from `raw_input["timestamp"]` | `"2026-05-01T10:00:00Z"` |

These timestamps are fixed by the sample file content and are therefore deterministic across runs.

### 5.2 Generated timestamps that are wall-clock (non-deterministic across runs)

| Field | Set by | Notes |
|---|---|---|
| `tape.created_at` | `cli.py` at tape creation time | Wall-clock UTC |
| `evidence.ingested_at` | `ingest.py` at normalization time | Wall-clock UTC |
| `timeline[*].at` | `timeline.py` at event construction time | Wall-clock UTC; must be non-decreasing |
| `verdict.set_at` | `verdict.py` at verdict computation time | Wall-clock UTC |
| `audit_chain_entry.created_at` | `audit.py` at entry construction time | Wall-clock UTC |
| `replay_state.started_at`, `completed_at` | `replay.py` at replay execution time | Wall-clock UTC |
| `replay audit_chain_entry.created_at` | `audit.py` at replay entry construction time | Wall-clock UTC |

### 5.3 Timestamps that must NOT affect verdict determinism

The following timestamps are present in the tape but are explicitly excluded from the `signing_tag` snapshot and from the verdict derivation logic:

- `tape.created_at`
- `evidence.ingested_at`
- `timeline[*].at`
- `verdict.set_at`
- `audit_chain_entry.created_at`
- `replay_state.started_at`, `completed_at`

The verdict derivation rule (REQ-006) depends only on `findings[*].severity`. The `signing_tag` snapshot (design.md §1.5) includes `raw_evidence`, `findings`, and `verdict.value` but not any timestamp field. This guarantees that two runs on the same input produce the same `verdict.value` and `signing_tag` regardless of when they run.

**Test enforcement:** AC-010-1 through AC-010-4 verify this. `test_cli.py` runs the CLI twice and asserts identical non-timestamp fields.

---

## 6. Canonical JSON and hash rules

### 6.1 Canonical JSON specification

Implemented in `canonical.py`. Rules (matching `replay-and-audit` spec exactly):

1. Object keys sorted lexicographically (Unicode code point order, ascending).
2. Strings UTF-8 encoded.
3. Numbers: integers or finite decimals; NaN and Infinity are rejected.
4. Timestamps: ISO-8601 with explicit `Z` suffix (no `+00:00`).
5. Booleans: lowercase `true` / `false`.
6. Null: `null`.
7. Arrays: insertion order preserved.
8. No trailing whitespace. Compact (no pretty-printing).

Two compliant implementations produce byte-identical output for the same logical object. This is the property that makes `this_entry_hash` independently verifiable.

### 6.2 Hash function

SHA-256, lowercase hex output. Implemented in `hashing.py`. No external dependencies — uses `hashlib` from the Python standard library.

### 6.3 Where canonical JSON is used

| Use | Input to canonical_json() | Output used as |
|---|---|---|
| `evidence.hash` | Source object dict | Hex digest stored in `raw_evidence[].hash` |
| `evidence_id` | `source_type + ":" + sha256_of_obj(source)` | Prefix `ev-` + hex digest |
| `tape_id` | `tenant_id + ":" + source_alert_ref` | Prefix `tape-` + first 16 chars |
| `signing_tag` | Snapshot dict (6 fields) | Prefix `sig-` + hex digest |
| `policy_snapshot` | Literal string | Hex digest |
| `idempotency_key` | Concatenated string | Hex digest |
| `prev_entry_hash` (genesis) | Literal string `"genesis"` | Hex digest |
| `this_entry_hash` | Entry dict with `this_entry_hash: ""` | Hex digest (replaces `""`) |
| `fields_hash` in audit payload | Full tape dict at close time | Hex digest |
| Replay hash verification | `entry["raw_content"]` dict | Compared against `entry["hash"]` |

### 6.4 `this_entry_hash` circular-dependency resolution

```
entry["this_entry_hash"] = ""
digest = sha256_of_obj(entry)          # canonical JSON with this_entry_hash = ""
entry["this_entry_hash"] = digest      # replace placeholder with real digest
```

This is deterministic because canonical JSON sorts keys lexicographically, so `this_entry_hash` always appears at a fixed position in the byte stream regardless of dict insertion order.

### 6.5 Golden value test

`test_hashing.py` includes a golden value test:
- `sha256_of_string("genesis")` must equal `"aeebad4a796fcc2e15dc4c6061b45ed9b373f26adfc798ca7d2d8cc58182718e"` (verified: `hashlib.sha256(b"genesis").hexdigest()`).
- This test will catch any regression in the canonical serializer or hash function.

---

## 7. No-network / no-LLM enforcement strategy

### 7.1 Design-level enforcement

No module in `zovark/slice001/` imports any of:
`requests`, `httpx`, `aiohttp`, `urllib.request`, `openai`, `anthropic`, `boto3`,
`google.cloud`, `cohere`, or any other network or model client library.

This is enforced by:
1. **Import audit** (Task 13.4): a grep/import check confirms no forbidden imports exist.
2. **Socket mock test** (Task 12.3, Task 10.2): `unittest.mock.patch('socket.socket', side_effect=OSError)` is applied during the CLI end-to-end test and the replay test. Both must exit 0 / succeed despite the socket being blocked.
3. **`pyproject.toml` runtime dependencies**: declared as empty (no third-party runtime deps). Any accidental import of a network library will fail at install time in a clean environment.

### 7.2 Replay-specific enforcement

The replay engine (`replay.py`) uses only:
- `tape["raw_evidence"][*]["raw_content"]` — the inline source object stored at ingest time.
- `tape["findings"]` — the recorded findings.
- `findings.py`'s rule set — a static in-process table.

No file I/O beyond what is passed in as arguments. No model client. No tool client.

### 7.3 What "no live LLM" means for Slice 001

`model_contribution: false` on every finding and on the verdict. `recorded_io` is absent from the tape. `model_versions_pin: []` in the replay state. The replay engine has no code path that could invoke a model even if one were installed.

---

## 8. `customer-report.md` structure

The customer report is the human-readable artifact that directly answers the build rule:

> Does the proof package show the evidence, explain the verdict, record the approval path, and provide a replayable verification?

**Section order (required):**

1. **Recommended Action (EDR Action Card)** — action type, target, approval required flag, evidence summary (evidence IDs + count), verdict value, reversibility/recovery classification (`reversible_by_edr` / `manual_recovery_required` / `irreversible_requires_compensation`), authorization ref.
2. **Replay Proof** — replay result, evidence hashes verified, verdict recomputed, replay ID, replay mode.
3. **Evidence and Findings** — findings table (index, title, severity, evidence ID).
4. **Approval Path** — approval mode, status, authorization record.
5. **Audit Chain** — entry 1 (tape_recording_closed), entry 2 (tape_replayed), chain integrity note.
6. **Internal Proof Substrate** — tape ID, tenant, source alert, generated timestamp, schema version.
7. **Artifacts** — list of all 9 filenames, hero artifacts first.

The action decision section (§1) must appear before any internal substrate fields (§6). This is the ordering that answers the customer's first question — "what are you recommending and why?" — before presenting the internal mechanics.

The report is generated by `writer.py` from the in-memory objects. It is not parsed or validated by any downstream system in Slice 001 — it is a read-only human artifact.

---

## 9. Explicit non-goals

The following are explicitly out of scope for Slice 001. Any task or code that touches these areas is out of scope and should be rejected at review.

| Non-goal | Rationale |
|---|---|
| Live EDR API integration | No network; sample input only |
| Autonomous action dispatch | `approval_required` only; `execution_result.status` stays `pending` |
| Sigma rule generation | Out of architecture MVP scope |
| SIEM publication | Out of architecture MVP scope |
| Production credential vault runtime | `authorization_record_ref: "vault://placeholder/bootstrap"` |
| Full web UI | No server, no browser |
| Live LLM calls (any phase) | Rule-driven only; `model_contribution: false` everywhere |
| Forensic re-execution replay mode | `recorded_output` only |
| Multi-tenant operation | Single tenant (`tenant-001`) |
| Concurrent operation | Single-process, single-run |
| `tape_recording_started` audit event | Not emitted; chain starts at `tape_recording_closed` (sequence 1) |
| `retention_class` on evidence entries | Post-MVP / GA field |
| `confidence_band` on findings | Post-MVP / GA field |
| Root signature (non-null `signed_root`) | Deferred to M1+; `signed_root: null` in Slice 001 |
| DR restore events | Deferred to M2+ |
| Vault IPC schemas | Deferred to M3 |
| Per-vendor rollback execution | Rollback plan is documented but not executed |
| `replay_available` boolean on tape | Tape does not carry this field; it is a derived query result |

---

## 10. Unresolved questions

### UQ-001 — `raw_content` field and the architecture spec

The `raw_content` field added to each evidence entry is a Slice 001 convenience
field not present in the architecture spec's `raw_evidence[]` shape. The architecture
spec lists: `evidence_id`, `hash`, `source_type`, `ingested_at`, `retention_class`.

**Status:** Acceptable for Slice 001. The architecture spec says "Each reference
includes" these fields — it does not say the list is exhaustive. `raw_content` is
an implementation detail of the static-file pipeline. Post-MVP, when evidence moves
to a vault, `raw_content` is replaced by a vault retrieval reference and this field
disappears. No architecture spec change is required for Slice 001.

**Action required before M1:** File a `MODIFIED Requirements` change against
`investigation-tape` to formally classify `raw_content` as a Slice 001 bootstrap
field and define its post-MVP replacement.

### UQ-002 — `tape_recording_started` event not emitted

The `replay-and-audit` spec's event enum includes `tape_recording_started` but
Slice 001 never emits it. The audit chain starts at sequence 1 with
`tape_recording_closed`.

**Status:** Acceptable for Slice 001. The spec defines the enum of allowed event
types; it does not require every event type to be emitted. The chain is internally
consistent (genesis → close → replay).

**Action required before M1:** Decide whether `tape_recording_started` should be
emitted as sequence 1 (with `tape_recording_closed` at sequence 2). If yes, update
the spec and tasks before coding begins.

### UQ-003 — `signing_tag` is not a cryptographic signature

The `signing_tag` in Slice 001 is a SHA-256 content tag, not a cryptographic
signature. The architecture spec says "the actual signature is stored in the audit
chain entry referenced by `audit_ref`" — but in Slice 001, `signed_root` is null,
so there is no actual signature anywhere.

**Status:** Acceptable for Slice 001. The architecture explicitly permits stubbing
root signing for the first slice. The `signing_tag` provides integrity evidence
(same input → same tag) without requiring a key management system.

**Action required before M1:** Implement actual signing per ADR-0042 and set
`signed_root` to a non-null value.

### UQ-004 — `handoff.audit_ref` points to `audit-entry-1` (the close entry)

The handoff record's `audit_ref` is set to `"audit-entry-1"` (the
`tape_recording_closed` entry). The `edr-handoff` spec says `audit_ref` references
"the audit chain entry recording dispatch + execution + rollback." In Slice 001
there is no `handoff_dispatched` audit entry because `execution_result.status` stays
`pending`.

**Status:** Acceptable for Slice 001. The handoff is a recommendation only; no
dispatch occurs. Pointing `audit_ref` at the close entry is the closest available
anchor. The `reason` field makes this explicit.

**Action required before M1:** When dispatch is implemented, emit a
`handoff_dispatched` audit entry and update `handoff.audit_ref` to point to it.

---

## 11. Final decision

**READY_WITH_NOTES**

The spec is ready to build. All requirements have design coverage, tasks, and test
files. The four patches applied above resolved the only blocking gaps (replay hash
recomputation, `signing_tag` ambiguity, `entry_id` inconsistency, missing
`customer-report.md`).

The four unresolved questions (UQ-001 through UQ-004) are all acceptable for Slice
001 and do not block coding. They are pre-M1 action items, not pre-build blockers.

**Notes for the builder:**

1. Start with Task 2 (canonical JSON + hashing). Every other module depends on it.
   Get the golden value test passing first — it will catch any serializer regression
   immediately.

2. The `raw_content` field on evidence entries is the key to replay correctness.
   `replay.py` must use `entry["raw_content"]` as the input to `sha256_of_obj()`,
   not re-read the input file.

3. The `signing_tag` snapshot includes exactly six fields: `tape_id`, `tenant_id`,
   `schema_version`, `source_alert_ref`, `raw_evidence`, `findings`, and
   `verdict_value`. Do not include `timeline`, `handoff_ref`, `handoff_summary`,
   `audit_ref`, or `state`. Including any of those would make `signing_tag`
   non-deterministic across runs (because `audit_ref` is set after the tag is
   computed).

4. The audit chain has exactly two entries in Slice 001: `audit-entry-1`
   (`tape_recording_closed`, sequence 1) and `audit-entry-2` (`tape_replayed`,
   sequence 2). The `prev_entry_hash` of entry 2 must equal the `this_entry_hash`
   of entry 1. Test this explicitly (Task 9.2).

5. `customer-report.md` is the artifact a design partner will actually read. Make
   it clear and complete. The build rule question — "Can a customer inspect and
   replay why Zovark recommended an EDR action?" — should be answerable by reading
   only that file.
