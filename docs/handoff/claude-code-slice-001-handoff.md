# Claude Code — Slice 001 Handoff

**Date:** 2026-05-02
**Handoff from:** Kiro (spec + Task 2 implementation)
**Handoff to:** Claude Code (Task 3 onward)

---

## 1. Product direction

**Zovark is the audit-grade evidence layer for AI-assisted SOC response.**

Before your SOC isolates a host or disables a user, Zovark shows the evidence,
explains the verdict, records the approval path, and creates a replayable proof
package.

The product hero artifacts are the **approval-required EDR action card**
(`edr-handoff.json`) and the **replayable proof package** (`replay-report.json` +
`customer-report.md`).

---

## 2. Internal architecture metaphor

The **investigation tape** is the internal proof substrate. It is an immutable,
hash-linked record that captures the evidence ledger, timeline, findings, verdict,
and handoff reference. The tape is what makes deterministic replay possible.

The tape is not the external headline — it is the mechanism. The action card and
proof package are what the customer sees.

Internal architecture is frozen at `architecture-rc3`. Do not modify any file under
`architecture/` or `openspec/specs/` unless explicitly instructed.

---

## 3. Slice 001 goal

One command. One static EDR-like JSON sample. No credentials. No network. Produces:

```
static EDR-like JSON
  → investigation tape
  → evidence ledger
  → timeline
  → findings
  → deterministic verdict
  → approval-required EDR action card
  → replay proof package
  → customer-readable proof report
```

Output artifacts (9 files in `out/`):

| File | Description |
|---|---|
| `edr-handoff.json` | Approval-required EDR action card (hero artifact) |
| `replay-report.json` | Replayable proof package (hero artifact) |
| `customer-report.md` | Human-readable proof report |
| `investigation-tape.json` | Internal proof substrate |
| `evidence-ledger.json` | `raw_evidence[]` extracted from tape |
| `timeline.json` | `timeline[]` extracted from tape |
| `findings.json` | `findings[]` extracted from tape |
| `verdict.json` | `verdict` extracted from tape |
| `audit-chain-entry.json` | `tape_recording_closed` audit chain entry |

---

## 4. Current implementation status

### Complete

**Task 2 — Canonical JSON and SHA-256 utilities**

| File | Status |
|---|---|
| `zovark/__init__.py` | ✅ created |
| `zovark/slice001/__init__.py` | ✅ created |
| `zovark/slice001/canonical.py` | ✅ implemented |
| `zovark/slice001/hashing.py` | ✅ implemented |
| `tests/__init__.py` | ✅ created |
| `tests/test_canonical.py` | ✅ 32 tests, all passing |
| `tests/test_hashing.py` | ✅ 19 tests, all passing |
| `pyproject.toml` | ✅ created |

**Test result:** 51/51 passed.

Run tests with:
```bash
uv run --with pytest python3 -m pytest tests/test_canonical.py tests/test_hashing.py -v
```

### Correct genesis hash (verified)

```
sha256_of_string("genesis") = aeebad4a796fcc2e15dc4c6061b45ed9b373f26adfc798ca7d2d8cc58182718e
```

Verified with: `python3 -c "import hashlib; print(hashlib.sha256(b'genesis').hexdigest())"`

The readiness review previously had an incorrect value. It has been patched.

### Remaining

Tasks 3–14. Task 1 scaffold prerequisites are complete: package `__init__` files,
`ZovarkValidationError`, `pyproject.toml`, `samples/edr-sample-001.json`, and
`tests/__init__.py` are present.

---

## 5. Next task for Claude Code

**Task 3 — Sample ingestion and evidence normalization**

From `tasks.md`:

```
3.1 Implement zovark/slice001/ingest.py:
  - load_sample(path: str) -> dict
      reads and parses JSON
      raises ZovarkValidationError on missing file or invalid JSON
  - normalize_evidence(raw_input: dict) -> list[dict]
      produces evidence entries per Design §1.2
      derives evidence_id and hash deterministically
      stores raw_content (the original source object dict) inline on each entry

3.2 Write tests/test_ingest.py:
  - Valid sample → correct number of evidence entries (3: one edr_alert, one process_event, one network_event)
  - Each entry has evidence_id, hash, source_type, ingested_at, raw_content
  - sha256_of_obj(entry["raw_content"]) equals entry["hash"] for every entry
  - Same input twice → identical evidence_id and hash
  - Mutate one byte of source → different hash
  - Missing file → ZovarkValidationError
  - Invalid JSON → ZovarkValidationError
```

Task 1 prerequisites are complete. Task 3 can start directly.

---

## 6. Hard constraints

These are non-negotiable for all of Slice 001:

- No live EDR API calls.
- No autonomous EDR action dispatch.
- No Sigma rule generation.
- No SIEM publication.
- No production credential vault runtime.
- No full web UI.
- No live LLM calls (any phase — findings are rule-driven, `model_contribution: false` everywhere).
- No network calls of any kind.
- No vendor credentials.
- `authorization_record_ref` is always `"vault://placeholder/bootstrap"`.
- `execution_result.status` stays at `"pending"`.
- `execution_result.reason` is `"recommendation_only_no_dispatcher_in_slice_001"`.

---

## 7. Files to read first

Read these before writing any code:

1. `.kiro/specs/slice-001-investigation-tape/requirements.md` — all 12 requirements and acceptance criteria
2. `.kiro/specs/slice-001-investigation-tape/design.md` — data object shapes, module layout, derivation table, canonical JSON rules
3. `.kiro/specs/slice-001-investigation-tape/tasks.md` — task list with sub-tasks and done-when criteria
4. `.kiro/specs/slice-001-investigation-tape/readiness-review.md` — per-artifact field requirements, deterministic ID rules, timestamp rules
5. `docs/demo/slice-001-demo-script.md` — the demo story; understand what the output must look like to a customer
6. `docs/yc/positioning.md` — product framing; understand why the action card leads

Key design sections for Task 3:
- Design §1.1 — sample input shape (`edr-sample-001.json`)
- Design §1.2 — evidence entry shape (including `raw_content`)
- Design §4.3 — `evidence_id` and `hash` derivation formulas

---

## 8. Operating rule

**Implement one task at a time.**

After each task:
1. Run the relevant tests.
2. Confirm all pass.
3. Stop and report.

Do not implement the next task until explicitly asked.

---

## 9. Exact prompt to start Claude Code with Task 3

Copy this prompt verbatim to start Claude Code:

---

```
Read these files first:
- .kiro/specs/slice-001-investigation-tape/requirements.md
- .kiro/specs/slice-001-investigation-tape/design.md
- .kiro/specs/slice-001-investigation-tape/tasks.md
- .kiro/specs/slice-001-investigation-tape/readiness-review.md

Then implement only Task 3 from tasks.md.

Implement:
- zovark/slice001/ingest.py (load_sample and normalize_evidence)
- tests/test_ingest.py (all test cases from Task 3.2)

Hard constraints:
- No live EDR API
- No network calls
- No LLM calls
- No autonomous action
- No Sigma, SIEM, UI, or vault runtime

Run tests with:
  uv run --with pytest python3 -m pytest tests/test_ingest.py -v

After tests pass, stop. Do not implement Task 4.
```

---

## 10. Repository state at handoff

Branch: `yc-wedge-reset`

Recent commits:
```
Correct Slice 001 genesis hash in readiness review
Slice 001: add canonical JSON and hashing utilities
Reposition Slice 001 around audit-grade evidence layer
```

To run all Task 2 tests:
```bash
uv run --with pytest python3 -m pytest tests/test_canonical.py tests/test_hashing.py -v
```

Expected: `51 passed`
