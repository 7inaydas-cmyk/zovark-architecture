# Slice 001 — Design

## Overview

This document defines the implementation design for Slice 001. It covers data object
shapes, module layout, the CLI command, canonical JSON / deterministic hashing
approach, the no-network/no-LLM boundary, and the output artifact list.

The governing architecture specs are:
- `openspec/specs/investigation-tape/spec.md`
- `openspec/specs/edr-handoff/spec.md`
- `openspec/specs/replay-and-audit/spec.md`

This design does not modify any architecture document.

---

## 1. Data object shapes

### 1.1 Sample input — `edr-sample-001.json`

```json
{
  "alert_id": "alert-20260501-001",
  "alert_type": "edr_alert",
  "host": "workstation-42.corp.example",
  "timestamp": "2026-05-01T10:00:00Z",
  "severity": "high",
  "description": "Suspicious PowerShell execution detected",
  "process_events": [
    {
      "event_id": "pe-001",
      "event_type": "process_event",
      "process_name": "powershell.exe",
      "command_line": "powershell.exe -EncodedCommand <base64>",
      "pid": 4812,
      "parent_pid": 1024,
      "timestamp": "2026-05-01T10:00:01Z"
    }
  ]
}
```

The sample is the only input. It is committed to `samples/edr-sample-001.json`.

---

### 1.2 Evidence entry (element of `raw_evidence[]`)

```json
{
  "evidence_id": "<sha256-of-source-type-colon-canonical-json>",
  "hash": "<sha256-hex-of-canonical-json-bytes-of-source-object>",
  "source_type": "edr_alert",
  "ingested_at": "2026-05-01T10:05:00Z",
  "raw_content": { /* the original source object, verbatim */ }
}
```

`evidence_id` derivation: `sha256(source_type + ":" + canonical_json(source_object))`,
hex-encoded, prefixed with `ev-`. This makes it deterministic and content-addressed.

`hash` derivation: `sha256(canonical_json(source_object))`, hex-encoded.

`raw_content`: the original source object dict stored inline. This is required so
the replay engine can recompute `sha256_of_obj(entry["raw_content"])` and compare
against the stored `hash` without re-reading the input file. In Slice 001 (single
static file, no network, no vault) this is the correct approach. Post-MVP, raw
content moves to a tenant-scoped vault and `raw_content` is replaced by a vault
retrieval reference.

The top-level alert object produces one evidence entry with `source_type: edr_alert`.
Each element of `process_events` produces one evidence entry with
`source_type: process_event`.

---

### 1.3 Timeline event (element of `timeline[]`)

```json
{
  "event_type": "evidence_added",
  "at": "2026-05-01T10:05:00Z",
  "actor": "system",
  "evidence_refs": ["ev-<hash>"],
  "decision_contribution": false
}
```

All actors in Slice 001 are `"system"`. `decision_contribution` is `true` only on
`verdict_set` and `finding_recorded` events.

---

### 1.4 Finding (element of `findings[]`)

```json
{
  "title": "EDR alert detected",
  "severity": "medium",
  "evidence_refs": ["ev-<hash>"],
  "model_contribution": false
}
```

`confidence_band` is omitted (post-MVP per architecture spec).

---

### 1.5 Verdict

```json
{
  "value": "confirmed_malicious",
  "evidence_refs": ["ev-<hash-1>", "ev-<hash-2>"],
  "model_contribution": false,
  "signing_tag": "<sha256-of-canonical-tape-bytes-at-verdict-time>",
  "set_at": "2026-05-01T10:05:01Z"
}
```

`signing_tag` derivation: `sha256(canonical_json(tape_snapshot))`, hex-encoded,
prefixed with `sig-`. `tape_snapshot` is the tape dict at the moment the verdict
value is determined, containing exactly: `tape_id`, `tenant_id`, `schema_version`,
`source_alert_ref`, `raw_evidence`, `findings`, and `verdict.value`. It does NOT
include `timeline`, `handoff_ref`, `handoff_summary`, `audit_ref`, or `state`,
because those fields are set after the verdict. This makes `signing_tag` stable and
deterministic across runs with the same input.

This is a deterministic content tag, not a cryptographic signature. The architecture
spec notes the actual signature lives in the audit chain entry; in Slice 001 the
audit chain entry's `signed_root` is null, so this tag is the integrity anchor.

---

### 1.6 Investigation tape

```json
{
  "tape_id": "tape-<sha256-of-tenant-id-colon-source-alert-ref>",
  "tenant_id": "tenant-001",
  "created_at": "2026-05-01T10:05:00Z",
  "schema_version": "tape/1.0",
  "source_alert_ref": "alert-20260501-001",
  "state": "closed",
  "raw_evidence": [ /* evidence entries */ ],
  "timeline": [ /* timeline events */ ],
  "findings": [ /* findings */ ],
  "verdict": { /* verdict object */ },
  "handoff_ref": "handoff-<idempotency-key-prefix>",
  "handoff_summary": {
    "action_type": "isolate_host",
    "target": { "kind": "host", "identifier": "workstation-42.corp.example" },
    "approval_mode": "approval_required",
    "execution_status": "pending"
  },
  "audit_ref": "audit-entry-001"
}
```

`tape_id` derivation: `"tape-" + sha256(tenant_id + ":" + source_alert_ref)`,
hex-encoded (first 16 chars for readability). This is deterministic given the same
tenant and alert.

---

### 1.7 Approval-required EDR action card (`edr-handoff.json`)

```json
{
  "handoff_id": "handoff-<first-16-chars-of-idempotency-key>",
  "tenant_id": "tenant-001",
  "tape_ref": "tape-<...>",
  "action_type": "isolate_host",
  "target": {
    "kind": "host",
    "identifier": "workstation-42.corp.example",
    "validated_at": "2026-05-01T10:05:01Z"
  },
  "evidence_refs": ["ev-<hash-1>", "ev-<hash-2>"],
  "policy_snapshot": "<sha256-of-slice-001-bootstrap-policy-string>",
  "policy_snapshot_version": "0.0.1-bootstrap",
  "approval_mode": "approval_required",
  "authorization_record_ref": "vault://placeholder/bootstrap",
  "execution_result": {
    "status": "pending",
    "reason": "recommendation_only_no_dispatcher_in_slice_001",
    "started_at": null,
    "completed_at": null,
    "vendor_response_ref": null,
    "error": null
  },
  "idempotency_key": "<sha256-of-tape-id-colon-action-type-colon-target-identifier>",
  "rollback_plan": {
    "reversibility_class": "reversible_by_edr",
    "vendor_reversal_action": "release_isolation",
    "vendor_reversal_target": {
      "kind": "host",
      "identifier": "workstation-42.corp.example"
    },
    "manual_steps": [],
    "reversal_window": "PT4H",
    "idempotency_key": "<sha256-of-rollback-tape-id-colon-release-isolation-colon-target>"
  },
  "audit_ref": "audit-entry-001",
  "replay_linkage": []
}
```

`reversibility_class` is a first-class field drawn from a three-value enum:

| Value | Meaning | When used |
|---|---|---|
| `reversible_by_edr` | EDR vendor exposes a reversal API; reversal is automatic | `isolate_host` (→ `release_isolation`), `notify_only` (→ `none`) |
| `manual_recovery_required` | No vendor reversal API; operator follows documented steps | e.g., `disable_account` where IdP re-enable is manual |
| `irreversible_requires_compensation` | Action cannot be undone; compensating action required | e.g., permanent file deletion |

For Slice 001:
- `isolate_host` → `reversibility_class: reversible_by_edr`, `vendor_reversal_action: release_isolation`
- `notify_only` → `reversibility_class: reversible_by_edr`, `vendor_reversal_action: none`

`policy_snapshot` derivation: `sha256("slice-001-bootstrap-policy")`, hex-encoded.
This is a stable, deterministic value for the bootstrap policy.

`idempotency_key` derivation: `sha256(tape_id + ":" + action_type + ":" + target.identifier)`,
hex-encoded.

---

### 1.8 Audit chain entry — `tape_recording_closed`

```json
{
  "entry_id": "audit-entry-001",
  "tenant_id": "tenant-001",
  "sequence": 1,
  "event_type": "tape_recording_closed",
  "payload": {
    "tape_id": "tape-<...>",
    "verdict_value": "confirmed_malicious",
    "fields_hash": "<sha256-of-canonical-tape-json>"
  },
  "created_at": "2026-05-01T10:05:02Z",
  "prev_entry_hash": "<sha256-of-string-genesis>",
  "this_entry_hash": "<sha256-of-canonical-entry-json-excluding-this-field>",
  "signed_root": null
}
```

`prev_entry_hash` for the first entry: `sha256("genesis")`, hex-encoded. This is the
bootstrap anchor.

`this_entry_hash` computation: serialize the entry to canonical JSON with
`this_entry_hash` set to the empty string `""`, compute SHA-256, then replace the
empty string with the hex digest. This avoids a circular dependency.

---

### 1.9 Replay state

```json
{
  "replay_id": "replay-<sha256-of-tape-id-colon-replay-suffix>",
  "tape_ref": "tape-<...>",
  "tenant_id": "tenant-001",
  "mode": "recorded_output",
  "schema_pin": "tape/1.0",
  "tool_catalog_pin": "none-slice-001",
  "model_versions_pin": [],
  "state": "succeeded",
  "mismatch_details": null,
  "unsigned_tail_replay": true,
  "started_at": "2026-05-01T10:05:03Z",
  "completed_at": "2026-05-01T10:05:03Z"
}
```

---

### 1.10 Audit chain entry — `tape_replayed`

```json
{
  "entry_id": "audit-entry-002",
  "tenant_id": "tenant-001",
  "sequence": 2,
  "event_type": "tape_replayed",
  "payload": {
    "tape_id": "tape-<...>",
    "replay_id": "replay-<...>",
    "replay_state": "succeeded",
    "evidence_hashes_verified": true,
    "verdict_recomputed": "confirmed_malicious",
    "verdict_matched": true
  },
  "created_at": "2026-05-01T10:05:03Z",
  "prev_entry_hash": "<this_entry_hash-of-entry-001>",
  "this_entry_hash": "<sha256-of-canonical-entry-json-excluding-this-field>",
  "signed_root": null
}
```

---

### 1.11 Replay report — `replay-report.json`

```json
{
  "replay_state": { /* replay state object */ },
  "audit_chain_entry": { /* tape_replayed audit chain entry */ }
}
```

This is the bundle the customer inspects to verify the investigation.

---

## 2. Module layout

```
zovark/
  __init__.py
  slice001/
    __init__.py
    cli.py              # Entry point: argument parsing, orchestration
    ingest.py           # REQ-001, REQ-002: load sample, normalize evidence
    tape.py             # REQ-003: tape creation, field assembly, sealing
    timeline.py         # REQ-004: timeline event construction
    findings.py         # REQ-005: rule-driven finding derivation
    verdict.py          # REQ-006: deterministic verdict computation
    handoff.py          # REQ-007: EDR handoff record construction
    audit.py            # REQ-008: audit chain entry construction and hashing
    replay.py           # REQ-009: replay engine (hash verification + verdict recompute)
    canonical.py        # Canonical JSON serialization (shared utility)
    hashing.py          # SHA-256 helpers (shared utility)
    writer.py           # REQ-012: output artifact writer

samples/
  edr-sample-001.json   # Static sample input

tests/
  test_ingest.py
  test_tape.py
  test_timeline.py
  test_findings.py
  test_verdict.py
  test_handoff.py
  test_audit.py
  test_replay.py
  test_canonical.py
  test_cli.py           # End-to-end: runs CLI, checks all 8 output files
```

No third-party dependencies beyond the Python standard library. Python 3.11+.

---

## 3. CLI command

```
python -m zovark.slice001 \
  --input  samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

Options:

| Flag | Required | Default | Description |
|---|---|---|---|
| `--input` | yes | — | Path to the EDR-like JSON sample file |
| `--output` | yes | — | Directory to write output artifacts |
| `--tenant-id` | no | `tenant-001` | Tenant identifier |

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Success — all artifacts written |
| 1 | Input file not found or unreadable |
| 2 | Input file is not valid JSON |
| 3 | Validation error (missing required field, invalid enum, etc.) |
| 4 | Output directory cannot be created or written |

On success, stdout prints:

```
Slice 001 complete.
  investigation-tape.json   → out/investigation-tape.json
  evidence-ledger.json      → out/evidence-ledger.json
  timeline.json             → out/timeline.json
  findings.json             → out/findings.json
  verdict.json              → out/verdict.json
  edr-handoff.json          → out/edr-handoff.json
  audit-chain-entry.json    → out/audit-chain-entry.json
  replay-report.json        → out/replay-report.json
  customer-report.md        → out/customer-report.md
Replay: succeeded
```

---

## 4. Canonical JSON and deterministic hashing

### 4.1 Canonical JSON rules

All hashing in Slice 001 uses canonical JSON. The rules match the `replay-and-audit`
spec exactly:

1. Object keys sorted lexicographically (Unicode code point order).
2. Strings UTF-8 encoded.
3. Numbers: integers or finite decimals; no NaN, no infinity.
4. Timestamps: ISO-8601 with explicit `Z` suffix.
5. Booleans: lowercase `true` / `false`.
6. Null: `null`.
7. Arrays preserve insertion order.
8. No trailing whitespace. No pretty-printing in the canonical form (compact).

Implementation: `canonical.py` exposes a single function `canonical_json(obj: Any) -> bytes`
that returns compact, key-sorted UTF-8 bytes. This is the only serialization used
for hashing. Output files are pretty-printed separately (2-space indent) for
human readability.

### 4.2 SHA-256 helper

`hashing.py` exposes:

```python
def sha256_hex(data: bytes) -> str:
    """Return lowercase hex SHA-256 digest of data."""

def sha256_of_string(s: str) -> str:
    """Return sha256_hex(s.encode('utf-8'))."""

def sha256_of_obj(obj: Any) -> str:
    """Return sha256_hex(canonical_json(obj))."""
```

### 4.3 Derived field derivations (summary)

| Field | Derivation |
|---|---|
| `evidence_id` | `"ev-" + sha256_of_string(source_type + ":" + sha256_of_obj(source_object))` |
| `hash` (evidence) | `sha256_of_obj(source_object)` |
| `tape_id` | `"tape-" + sha256_of_string(tenant_id + ":" + source_alert_ref)[:16]` |
| `signing_tag` | `"sig-" + sha256_of_obj({"tape_id":…, "tenant_id":…, "schema_version":…, "source_alert_ref":…, "raw_evidence":…, "findings":…, "verdict_value":…})` |
| `policy_snapshot` | `sha256_of_string("slice-001-bootstrap-policy")` |
| `handoff_id` | `"handoff-" + sha256_of_string(tape_id + ":" + action_type + ":" + target_identifier)[:16]` |
| `idempotency_key` (handoff) | `sha256_of_string(tape_id + ":" + action_type + ":" + target_identifier)` |
| `idempotency_key` (rollback) | `sha256_of_string(tape_id + ":rollback:" + vendor_reversal_action + ":" + target_identifier)` |
| `prev_entry_hash` (first entry) | `sha256_of_string("genesis")` |
| `this_entry_hash` | `sha256_of_obj(entry_with_this_entry_hash_set_to_empty_string)` |
| `replay_id` | `"replay-" + sha256_of_string(tape_id + ":recorded_output")[:16]` |
| `entry_id` (audit) | `"audit-entry-" + str(sequence)` (e.g., `"audit-entry-1"`, `"audit-entry-2"`) |

Note: `finding_id`, `timeline_event_id`, and `verdict_id` do not exist. Findings,
timeline events, and the verdict are embedded objects identified by their position
and `evidence_refs`, not by standalone IDs. This is correct per the architecture
specs.

### 4.4 `this_entry_hash` computation detail

To avoid a circular dependency when computing `this_entry_hash`:

1. Build the full entry dict with `"this_entry_hash": ""`.
2. Compute `sha256_of_obj(entry_dict)`.
3. Set `entry_dict["this_entry_hash"]` to the hex digest.

This is deterministic because the canonical serializer sorts keys, so the position
of `this_entry_hash` in the byte stream is fixed regardless of insertion order.

---

## 5. No-network / no-LLM boundary

The following is enforced by design, not just convention:

- `ingest.py` reads only from the local filesystem. No `urllib`, `requests`,
  `httpx`, or socket calls.
- `findings.py` uses only a static in-process rule table. No model client imports.
- `verdict.py` uses only the findings list. No model client imports.
- `replay.py` uses only the tape's `recorded_io` (empty in Slice 001) and the
  local rule set. No model client imports.
- No module in `zovark/slice001/` imports `openai`, `anthropic`, `boto3`,
  `requests`, `httpx`, `aiohttp`, or any other network library.

A test in `test_cli.py` verifies that running the CLI with network access blocked
(via `unittest.mock.patch('socket.socket', side_effect=OSError)`) still exits 0.

---

## 6. Processing flow

```
cli.py
  │
  ├─ ingest.py
  │    load_sample(path) → raw_input dict
  │    normalize_evidence(raw_input) → list[EvidenceEntry]
  │
  ├─ tape.py
  │    create_tape(tenant_id, source_alert_ref) → Tape (state: recording)
  │    append_evidence(tape, evidence_entries)
  │
  ├─ timeline.py
  │    build_timeline(tape, evidence_entries) → list[TimelineEvent]
  │    append_timeline(tape, events)
  │
  ├─ findings.py
  │    derive_findings(evidence_entries) → list[Finding]
  │    append_findings(tape, findings)
  │
  ├─ verdict.py
  │    compute_verdict(findings, evidence_entries) → Verdict
  │    set_verdict(tape, verdict)
  │
  ├─ handoff.py
  │    build_handoff(tape, verdict) → HandoffRecord
  │    attach_handoff(tape, handoff)
  │
  ├─ audit.py
  │    build_close_entry(tape, prev_hash) → AuditChainEntry
  │    seal_tape(tape, audit_entry) → closed Tape
  │
  ├─ replay.py
  │    run_replay(tape, audit_entry) → (ReplayState, AuditChainEntry)
  │
  └─ writer.py
       write_artifacts(output_dir, tape, handoff, audit_entry, replay_report)
```

Each module is stateless and pure (given the same inputs, produces the same
outputs). Side effects (filesystem writes, timestamp reads) are isolated to
`cli.py` and `writer.py`.

---

## 7. Validation approach

Validation is performed at two points:

**At construction time** — each builder function validates its inputs before
returning. Invalid inputs raise a `ZovarkValidationError` (a custom exception in
`zovark/slice001/__init__.py`) with a descriptive message.

**At seal time** — `seal_tape()` performs a final pre-close validation checklist:
- `tape_id` present.
- `tenant_id` present.
- `raw_evidence` non-empty or `no_evidence_flag: true`.
- `findings` non-empty or `no_findings_flag: true`.
- `verdict.value` set and in the fixed enum.
- `audit_ref` set.
- `state` is `recording` (cannot re-seal a closed tape).

Any failure raises `ZovarkValidationError` and the tape is not written.

---

## 8. Output artifact list

| File | Source | Notes |
|---|---|---|
| `investigation-tape.json` | `tape.py` | Full closed tape; pretty-printed |
| `evidence-ledger.json` | Extracted from tape | `raw_evidence[]` array |
| `timeline.json` | Extracted from tape | `timeline[]` array |
| `findings.json` | Extracted from tape | `findings[]` array |
| `verdict.json` | Extracted from tape | `verdict` object |
| `edr-handoff.json` | `handoff.py` | Approval-required EDR action card; pretty-printed |
| `audit-chain-entry.json` | `audit.py` | `tape_recording_closed` entry |
| `replay-report.json` | `replay.py` | `{replay_state, audit_chain_entry}` bundle |
| `customer-report.md` | `writer.py` | Human-readable summary for design-partner review |

All JSON files written by `writer.py` using `json.dumps(obj, indent=2, ensure_ascii=False)`.

### customer-report.md structure

The customer report is a Markdown file that is the primary human-readable artifact
for design-partner review. It leads with the **EDR action card** — the recommended
action, evidence basis, approval status, and reversibility — then provides the
replayable proof. It answers the external build rule directly:

> Does the proof package show the evidence, explain the verdict, record the approval path, and provide a replayable verification?

```markdown
# Zovark Proof Package

**Zovark is the audit-grade evidence layer for AI-assisted SOC response.**

---

## Recommended Action (EDR Action Card)

**Action:** ISOLATE_HOST
**Target:** workstation-42.corp.example (host)
**Approval required:** YES — no action has been dispatched
**Evidence basis:** ev-<...>, ev-<...> (2 evidence items)
**Verdict:** CONFIRMED_MALICIOUS
**Reversibility:** reversible_by_edr — automatic release_isolation available
**Authorization:** vault://placeholder/bootstrap (bootstrap mode)

> No action has been dispatched. Human approval is required before any EDR action.

---

## Replay Proof

**Replay result:** succeeded
**Evidence hashes verified:** yes
**Verdict recomputed:** CONFIRMED_MALICIOUS (matches recorded verdict)
**Replay ID:** replay-<...>
**Replay mode:** recorded_output (no live LLM or tool calls)

---

## Evidence and Findings

| # | Finding | Severity | Evidence ID |
|---|---|---|---|
| 1 | EDR alert detected | medium | ev-<...> |
| 2 | Suspicious process event | high | ev-<...> |

---

## Approval Path

Approval mode: approval_required
Status: pending — awaiting human approval before any dispatch
Authorization record: vault://placeholder/bootstrap

---

## Audit Chain

Entry 1 — tape_recording_closed (audit-entry-1)
Entry 2 — tape_replayed (audit-entry-2)
Chain: hash-linked, unsigned tail (root signing deferred to M1+)

---

## Internal Proof Substrate

Tape ID: tape-<...>
Tenant: tenant-001
Source alert: alert-20260501-001
Generated: 2026-05-01T10:05:00Z
Schema: tape/1.0

---

## Artifacts

- edr-handoff.json          ← EDR action card (hero artifact)
- replay-report.json        ← Replayable proof package (hero artifact)
- customer-report.md        ← This document
- investigation-tape.json   ← Internal proof substrate
- evidence-ledger.json
- timeline.json
- findings.json
- verdict.json
- audit-chain-entry.json
```

---

## 9. Test strategy

Each module has a corresponding unit test file. Tests use only `pytest` and the
Python standard library.

Key test cases (beyond the per-requirement acceptance criteria):

- `test_canonical.py`: two dicts with same content but different key insertion order
  produce byte-identical canonical JSON.
- `test_hashing.py`: known input → known SHA-256 output (golden value test).
- `test_replay.py`: corrupt one evidence hash → `state: failed`. Change verdict rule
  → `state: mismatch`.
- `test_cli.py`: end-to-end run produces all 9 files; re-run produces identical
  non-timestamp fields.

No test requires network access. No test requires credentials.

---

## 10. What this design does not define

- Serialization format beyond JSON (no Avro, Protobuf, MessagePack).
- Storage backend (files only in Slice 001).
- Tenant isolation mechanism (single tenant in Slice 001).
- Vault runtime (placeholder string only).
- Root signature algorithm (stubbed as `null` in Slice 001).
- Per-vendor EDR adapter (no live EDR in Slice 001).
- Web UI or API server.
- Multi-tenant or concurrent operation.
