# Slice 001 — Tasks

## Status key
- `[ ]` not started
- `[-]` in progress
- `[x]` complete

---

## Task 1 — Project scaffold

- [ ] 1.1 Create `zovark/__init__.py` and `zovark/slice001/__init__.py` with `ZovarkValidationError` exception class.
- [ ] 1.2 Create `pyproject.toml` (or `setup.py`) declaring the package, Python ≥ 3.11, no third-party runtime dependencies.
- [ ] 1.3 Create `samples/edr-sample-001.json` with the static sample defined in Design §1.1.
- [ ] 1.4 Create `tests/__init__.py` and confirm `pytest` discovers the tests directory.

**Done when:** `python -m pytest tests/` runs (with zero tests) and exits 0.

---

## Task 2 — Canonical JSON and SHA-256 utilities

- [ ] 2.1 Implement `zovark/slice001/canonical.py` — `canonical_json(obj) -> bytes` (compact, keys sorted lexicographically, UTF-8, ISO-8601 with Z, no NaN/Inf).
- [ ] 2.2 Implement `zovark/slice001/hashing.py` — `sha256_hex(data)`, `sha256_of_string(s)`, `sha256_of_obj(obj)`.
- [ ] 2.3 Write `tests/test_canonical.py`:
  - Two dicts with same content, different insertion order → byte-identical output.
  - Nested object with array → keys sorted at every level.
  - Timestamp string with `Z` passes through unchanged.
- [ ] 2.4 Write `tests/test_hashing.py`:
  - `sha256_of_string("genesis")` → known golden hex value.
  - `sha256_of_obj({"b": 1, "a": 2})` equals `sha256_of_obj({"a": 2, "b": 1})`.

**Done when:** `pytest tests/test_canonical.py tests/test_hashing.py` passes.

---

## Task 3 — Sample ingestion and evidence normalization

- [ ] 3.1 Implement `zovark/slice001/ingest.py`:
  - `load_sample(path: str) -> dict` — reads and parses JSON; raises `ZovarkValidationError` on missing file or invalid JSON.
  - `normalize_evidence(raw_input: dict) -> list[dict]` — produces evidence entries per Design §1.2; derives `evidence_id` and `hash` deterministically; stores `raw_content` (the original source object dict) inline on each entry.
- [ ] 3.2 Write `tests/test_ingest.py`:
  - Valid sample → correct number of evidence entries (2: one `edr_alert`, one `process_event`).
  - Each entry has `evidence_id`, `hash`, `source_type`, `ingested_at`, `raw_content`.
  - `sha256_of_obj(entry["raw_content"])` equals `entry["hash"]` for every entry.
  - Same input twice → identical `evidence_id` and `hash`.
  - Mutate one byte of source → different `hash`.
  - Missing file → `ZovarkValidationError`.
  - Invalid JSON → `ZovarkValidationError`.

**Done when:** `pytest tests/test_ingest.py` passes.

---

## Task 4 — Investigation tape creation and field assembly

- [ ] 4.1 Implement `zovark/slice001/tape.py`:
  - `create_tape(tenant_id, source_alert_ref) -> dict` — creates tape in `recording` state with identity fields; derives `tape_id` per Design §4.3.
  - `append_evidence(tape, evidence_entries)` — appends entries to `raw_evidence[]`.
  - `attach_handoff(tape, handoff)` — sets `handoff_ref` and `handoff_summary`.
  - `seal_tape(tape, audit_ref) -> dict` — runs pre-close validation checklist (Design §7), sets `state: closed`, sets `audit_ref`; raises `ZovarkValidationError` on any failure.
- [ ] 4.2 Write `tests/test_tape.py`:
  - New tape has `state: recording`.
  - `tape_id` is deterministic given same `tenant_id` + `source_alert_ref`.
  - `seal_tape` sets `state: closed`.
  - `seal_tape` without `verdict.value` raises `ZovarkValidationError`.
  - `seal_tape` without `audit_ref` raises `ZovarkValidationError`.
  - Calling `seal_tape` on an already-closed tape raises `ZovarkValidationError`.
  - Tape does not contain `replay_state_ref` field.
  - Tape does not contain `state: replaying`.

**Done when:** `pytest tests/test_tape.py` passes.

---

## Task 5 — Timeline construction

- [ ] 5.1 Implement `zovark/slice001/timeline.py`:
  - `build_timeline(evidence_entries, findings, verdict_value) -> list[dict]` — produces the six event types defined in REQ-004 in non-decreasing timestamp order; all actors `"system"`.
  - `append_timeline(tape, events)` — appends events to `tape["timeline"]`.
- [ ] 5.2 Write `tests/test_timeline.py`:
  - Output contains all six required event types.
  - Events are in non-decreasing `at` order.
  - Every `evidence_added` event references the correct `evidence_id`.
  - `verdict_set` event has `decision_contribution: true`.
  - All actors are `"system"`.

**Done when:** `pytest tests/test_timeline.py` passes.

---

## Task 6 — Rule-driven findings

- [ ] 6.1 Implement `zovark/slice001/findings.py`:
  - `RULES` — static list of rule dicts (RULE-001, RULE-002, RULE-003 per REQ-005).
  - `derive_findings(evidence_entries: list[dict]) -> tuple[list[dict], bool]` — returns `(findings, no_findings_flag)`.
  - Each finding has `title`, `severity`, `evidence_refs`, `model_contribution: false`.
  - `append_findings(tape, findings, no_findings_flag)` — appends to `tape["findings"]`; sets `tape["no_findings_flag"]` if flag is true.
- [ ] 6.2 Write `tests/test_findings.py`:
  - `edr_alert` evidence → RULE-001 fires → finding with `severity: medium`.
  - `process_event` evidence → RULE-002 fires → finding with `severity: high`.
  - Both evidence types → both rules fire → two findings.
  - Empty evidence → RULE-003 fires → `no_findings_flag: true`.
  - Every finding has `model_contribution: false`.
  - Every finding's `evidence_refs` entries exist in the input evidence list.

**Done when:** `pytest tests/test_findings.py` passes.

---

## Task 7 — Deterministic verdict

- [ ] 7.1 Implement `zovark/slice001/verdict.py`:
  - `compute_verdict(findings: list[dict], evidence_entries: list[dict], tape: dict) -> dict` — applies the derivation table from REQ-006; derives `signing_tag` per Design §4.3.
  - `set_verdict(tape, verdict)` — sets `tape["verdict"]`.
- [ ] 7.2 Write `tests/test_verdict.py`:
  - High-severity finding → `confirmed_malicious`.
  - Medium-severity finding only → `suspicious_unconfirmed`.
  - Info/low findings only → `benign`.
  - `no_findings_flag: true` → `inconclusive_insufficient_evidence`.
  - `model_contribution` is `false`.
  - `evidence_refs` is non-empty when findings exist.
  - Same input twice → identical `value` and `signing_tag`.
  - Value outside fixed enum raises `ZovarkValidationError`.

**Done when:** `pytest tests/test_verdict.py` passes.

---

## Task 8 — Approval-required EDR action card

- [ ] 8.1 Implement `zovark/slice001/handoff.py`:
  - `build_handoff(tape: dict, verdict: dict) -> dict` — constructs the 14-field action card per Design §1.7 and REQ-007.
  - Action selection: `isolate_host` if any finding severity `high`/`critical`; else `notify_only`.
  - `policy_snapshot` derived from `sha256_of_string("slice-001-bootstrap-policy")`.
  - `idempotency_key` derived per Design §4.3.
  - `rollback_plan.reversibility_class` uses the three-value enum:
    - `isolate_host` → `reversible_by_edr`, `vendor_reversal_action: release_isolation`
    - `notify_only` → `reversible_by_edr`, `vendor_reversal_action: none`
  - `authorization_record_ref: "vault://placeholder/bootstrap"`.
  - `execution_result.status: "pending"`, `reason: "recommendation_only_no_dispatcher_in_slice_001"`.
- [ ] 8.2 Write `tests/test_handoff.py`:
  - High-severity finding → `action_type: isolate_host`, `target.kind: host`.
  - No high/critical finding → `action_type: notify_only`.
  - `approval_mode` is `approval_required`.
  - `authorization_record_ref` is `vault://placeholder/bootstrap`.
  - `execution_result.status` is `pending`.
  - `execution_result.reason` is `recommendation_only_no_dispatcher_in_slice_001`.
  - `evidence_refs` is non-empty.
  - All `evidence_refs` entries exist in tape's `raw_evidence`.
  - `tape_ref` matches tape's `tape_id`.
  - `tenant_id` matches tape's `tenant_id`.
  - `idempotency_key` is identical across two runs with same input.
  - `isolate_host` → `rollback_plan.reversibility_class: reversible_by_edr`, `vendor_reversal_action: release_isolation`.
  - `notify_only` → `rollback_plan.reversibility_class: reversible_by_edr`, `vendor_reversal_action: none`.
  - `reversibility_class` is one of `reversible_by_edr`, `manual_recovery_required`, `irreversible_requires_compensation` (enum guard).

**Done when:** `pytest tests/test_handoff.py` passes.

---

## Task 9 — Audit chain entry and tape sealing

- [ ] 9.1 Implement `zovark/slice001/audit.py`:
  - `build_close_entry(tape: dict, sequence: int, prev_hash: str) -> dict` — constructs the `tape_recording_closed` audit chain entry per Design §1.8.
  - `compute_this_entry_hash(entry: dict) -> str` — sets `this_entry_hash: ""`, computes `sha256_of_obj(entry)`, returns hex digest.
  - `GENESIS_HASH` constant: `sha256_of_string("genesis")`.
  - `build_replay_entry(tape: dict, replay_state: dict, sequence: int, prev_hash: str) -> dict` — constructs the `tape_replayed` audit chain entry per Design §1.10.
- [ ] 9.2 Write `tests/test_audit.py`:
  - `event_type` is `tape_recording_closed` for close entry.
  - `sequence` is `1` for first entry.
  - `prev_entry_hash` equals `sha256_of_string("genesis")` for first entry.
  - `this_entry_hash` is the SHA-256 of the canonical entry with `this_entry_hash: ""`.
  - `signed_root` is `null`.
  - `entry_id` is `"audit-entry-1"`.
  - Replay entry `event_type` is `tape_replayed`.
  - Replay entry `sequence` is `2`.
  - Replay entry `entry_id` is `"audit-entry-2"`.
  - Replay entry `prev_entry_hash` equals close entry's `this_entry_hash` (chain linkage verified).

**Done when:** `pytest tests/test_audit.py` passes.

---

## Task 10 — Replay engine

- [ ] 10.1 Implement `zovark/slice001/replay.py`:
  - `run_replay(tape: dict, close_audit_entry: dict) -> tuple[dict, dict]` — returns `(replay_state, tape_replayed_audit_entry)`.
  - Step 1: for every entry in `tape["raw_evidence"]`, recompute `sha256_of_obj(entry["raw_content"])` and compare against `entry["hash"]`. On mismatch → `state: failed`, `reason: evidence_corruption`, `affected_evidence_id` named.
  - Step 2: recompute verdict using the same rule set as `verdict.py` applied to `tape["findings"]`. On mismatch → `state: mismatch`, `mismatch_details` populated.
  - Step 3: if both pass → `state: succeeded`.
  - No network calls. No model calls.
  - `unsigned_tail_replay: true` always in Slice 001.
- [ ] 10.2 Write `tests/test_replay.py`:
  - Clean tape → `state: succeeded`.
  - Corrupt one evidence hash in the tape → `state: failed`, reason `evidence_corruption`, affected `evidence_id` named.
  - Patch verdict rule to return different value → `state: mismatch`, `mismatch_details` populated.
  - `mode` is `recorded_output`.
  - `unsigned_tail_replay` is `true`.
  - `model_versions_pin` is `[]`.
  - `tool_catalog_pin` is `"none-slice-001"`.
  - No socket is opened (mock `socket.socket` to raise `OSError`; replay still succeeds).

**Done when:** `pytest tests/test_replay.py` passes.

---

## Task 11 — Output writer

- [ ] 11.1 Implement `zovark/slice001/writer.py`:
  - `write_artifacts(output_dir, tape, handoff, close_audit_entry, replay_report) -> dict[str, str]` — writes all 8 files; returns `{filename: path}` map.
  - Creates `output_dir` if it does not exist.
  - All files written with `json.dumps(obj, indent=2, ensure_ascii=False)`.
  - Extracts `evidence-ledger.json`, `timeline.json`, `findings.json`, `verdict.json` from the tape object.
  - Generates `customer-report.md` from the tape, handoff, and replay report per Design §8.
- [ ] 11.2 Write `tests/test_writer.py`:
  - All 9 files are present after `write_artifacts`.
  - All 8 JSON files are valid JSON.
  - `evidence-ledger.json` content matches tape's `raw_evidence`.
  - `timeline.json` content matches tape's `timeline`.
  - `findings.json` content matches tape's `findings`.
  - `verdict.json` content matches tape's `verdict`.
  - `customer-report.md` opens with the recommended action section (action type, target, approval mode, evidence summary, verdict, reversibility class, replay proof status) before any internal substrate fields.

**Done when:** `pytest tests/test_writer.py` passes.

---

## Task 12 — CLI entry point

- [ ] 12.1 Implement `zovark/slice001/cli.py`:
  - `main()` function using `argparse`: `--input`, `--output`, `--tenant-id`.
  - Orchestrates the full pipeline: ingest → tape → timeline → findings → verdict → handoff → audit → seal → replay → write.
  - Exits 0 on success; exits with appropriate code (1–4) on error.
  - Prints artifact summary to stdout on success.
- [ ] 12.2 Add `__main__.py` to `zovark/slice001/` so `python -m zovark.slice001` works.
- [ ] 12.3 Write `tests/test_cli.py`:
  - End-to-end: run CLI on `samples/edr-sample-001.json` → all 9 output files present.
  - All 8 JSON output files are valid JSON.
  - `customer-report.md` is present and non-empty.
  - Exit code 0 on success.
  - Exit code 1 on missing input file.
  - Exit code 2 on invalid JSON input.
  - `replay-report.json` has `replay_state.state: succeeded`.
  - Run twice on same input → identical `verdict.value`, `idempotency_key`, `signing_tag`, `this_entry_hash` in audit entry (timestamps may differ).
  - Mock `socket.socket` to raise `OSError` → CLI still exits 0 (no network dependency).

**Done when:** `pytest tests/test_cli.py` passes.

---

## Task 13 — Full test suite and determinism verification

- [ ] 13.1 Run `pytest tests/` — all tests pass, zero failures.
- [ ] 13.2 Run the CLI twice on `samples/edr-sample-001.json` with the same `--tenant-id`; diff the two output directories on non-timestamp fields; confirm zero diffs.
- [ ] 13.3 Manually corrupt one `hash` value in `investigation-tape.json` and run replay directly; confirm `replay_state.state` is `failed`.
- [ ] 13.4 Confirm no file in `zovark/slice001/` imports `requests`, `httpx`, `aiohttp`, `openai`, `anthropic`, `boto3`, or `urllib.request`.

**Done when:** all four checks pass.

---

## Task 14 — Sample and README

- [ ] 14.1 Confirm `samples/edr-sample-001.json` is committed and matches the schema in Design §1.1.
- [ ] 14.2 Write `README.md` at the repo root with:
  - One-sentence product description (external canonical wedge: "Zovark is the audit-grade evidence layer for AI-assisted SOC response.").
  - Prerequisites (Python 3.11+, no other dependencies).
  - How to run: `python -m zovark.slice001 --input samples/edr-sample-001.json --output out/ --tenant-id tenant-001`.
  - Expected output artifact list (hero artifacts first: `edr-handoff.json`, `replay-report.json`, `customer-report.md`).
  - How to run tests: `pytest tests/`.

**Done when:** a new developer can clone the repo, run the command, and see all 9 output files without reading any other document.
