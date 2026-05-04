# Kiro Coding-Agent Session — Zovark YC Demo Proof Package

**Branch:** `mvp/slice-001-claude-implementation`
**Date:** 2026-05-04
**Commits covered:** `03b928e` → `e2239af` → `1af43c3` → `d4ec4d2` → `6d5dd4c`

---

## 1. Why this session matters

The goal was to create a static YC demo proof package for Zovark — a concrete,
inspectable artifact that shows what the product produces before a SOC analyst
approves a high-risk response action.

The demo scenario: a synthetic phishing incident on HOST-12 — Word spawns encoded
PowerShell, PowerShell contacts an external IP, reads LSASS memory, and attempts
lateral movement. Zovark processes this into:

```
EDR-style alert
  → evidence ledger (5 entries, SHA-256 hashed)
  → timeline (13 events)
  → findings (4 rule-driven, no model)
  → deterministic verdict (confirmed_malicious)
  → approval-required EDR action card
  → replay proof package
  → customer-readable proof report
```

This was not a live EDR integration. It was not autonomous response. No network
calls were made. No AI model ran during the session or during replay.

The value of the session is what it demonstrates about how I use AI coding tools:
tight constraints, deterministic artifacts, validation before commit, and a clear
stop condition. The agent was not given a blank canvas — it was given a spec and
told exactly what it could and could not do.

---

## 2. Starting prompt / task constraints

The agent was given this task:

> Create a static demo package under `demo/zovark-proof-package/`. The demo should
> show Zovark as the AI-native proof layer for high-stakes security response. Core
> demo question: Should a SOC approve host isolation?

With these hard constraints, stated explicitly and non-negotiably:

- Do not change architecture docs.
- Do not add product scope.
- Do not add live EDR integration.
- Do not add autonomous response.
- Do not add Sigma.
- Do not add SIEM publication.
- Do not add network calls.
- Do not add LLM calls.
- Keep artifacts deterministic — same input, same output, every run.
- Use canonical JSON serialization (keys sorted lexicographically, compact, UTF-8).
- Use SHA-256 for all content hashes.
- Validate all artifacts before committing.
- `authorization_record_ref` must be `vault://placeholder/bootstrap`.
- `execution_result.status` must be `pending`.
- `execution_result.reason` must be `recommendation_only_no_dispatcher_in_slice_001`.

A second pass added:

- Replace scenario IP `192.168.1.100` with `203.0.113.50` (documentation-safe range).
- Soften EDR reversal language — do not imply live EDR API capability exists.
- Fix visual issues in `demo.html` (red ❌ for positive constraints → green ✅).
- Create a 7-scene founder walkthrough page (`demo-recording.html`).

---

## 3. What the agent built

### Commit `03b928e` — initial proof package (11 files)

| File | Description |
|---|---|
| `samples/edr/phishing-powershell.json` | Synthetic EDR alert input |
| `out/tape-001/evidence-ledger.json` | 5 evidence entries with SHA-256 hashes |
| `out/tape-001/timeline.json` | 13 timeline events |
| `out/tape-001/findings.json` | 4 rule-driven findings (no model) |
| `out/tape-001/verdict.json` | Deterministic verdict object |
| `out/tape-001/edr-handoff.json` | Approval-required EDR action card |
| `out/tape-001/replay-report.json` | Replay state + audit chain entry |
| `out/tape-001/investigation-tape.json` | Full internal proof substrate |
| `out/tape-001/customer-report.md` | Human-readable proof report |
| `README.md` | Package overview with honesty disclaimer |
| `demo-script.md` | 90-second screen recording script |

### Commit `e2239af` — generator, validator, demo.html (13 files changed)

| File | Description |
|---|---|
| `scripts/generate_yc_demo.py` | Deterministic generator — produces all artifacts from source objects |
| `scripts/validate_yc_demo.py` | Validator — 30 checks across 5 categories |
| `demo/zovark-proof-package/demo.html` | Static HTML reference walkthrough |
| All `out/tape-001/*.json` | Regenerated with consistent hashes from the generator |

### Commit `1af43c3` — IP patch and positioning update (12 files)

All artifacts regenerated after changing `destination_ip` from `192.168.1.100` to
`203.0.113.50`. All hashes recomputed. Validator re-run to confirm consistency.

### Commit `d4ec4d2` — demo-recording.html and final fixes (4 files)

| File | Change |
|---|---|
| `demo-recording.html` | New — 7-scene full-screen founder walkthrough |
| `demo-script.md` | Removed "automatic release available" language |
| `demo.html` | ❌ → ✅ for no-live-LLM and no-live-EDR indicators |
| `README.md` | "How to regenerate" → honest "Validation" section |

### Commit `6d5dd4c` — 3 copy edits to demo-recording.html

- Banner: "AI-native" → "deterministic proof layer"
- Scene 1: added muted lead-in line above the headline
- Scene 7: added closing line "Zovark is not another alert summary. It is proof before response."

---

## 4. Deterministic proof work

The core technical requirement was that every hash in the package be a real,
independently verifiable SHA-256 digest — not a placeholder.

### Canonical JSON

All hashing used a strict canonical serialization:
- Object keys sorted lexicographically (Unicode code point order)
- Compact (no whitespace)
- UTF-8 encoding
- Booleans: `true`/`false` (not `1`/`0`)
- Null: `null`
- Arrays: insertion order preserved

This matches the `replay-and-audit` architecture spec exactly, so the demo hashes
are compatible with the real pipeline when it is built.

### Evidence hash derivation

Each evidence entry's `hash` is `sha256(canonical_json(source_object))`.

Each `evidence_id` is `"ev-" + sha256(source_type + ":" + sha256(canonical_json(source_object)))`.

Both are deterministic — same source object always produces the same ID and hash.

### Audit chain linkage

The audit chain has two entries:

- Entry 1 (`tape_recording_closed`, sequence 1): `prev_entry_hash = sha256("genesis")`
- Entry 2 (`tape_replayed`, sequence 2): `prev_entry_hash = entry1.this_entry_hash`

Each `this_entry_hash` is computed by setting the field to `""`, hashing the
canonical JSON of the entry, then replacing `""` with the digest. This avoids a
circular dependency while remaining deterministic.

### Replay constraints

The replay report asserts:
- `evidence_hashes_verified: true` — all 5 hashes recomputed and matched
- `verdict_recomputed: true` — same rule set, same verdict
- `verdict_match: true`
- `no_live_llm_call: true`
- `no_live_edr_call: true`

These are not claims about a running system. They are assertions about the static
package that the validator checks independently.

---

## 5. Validation results

`scripts/validate_yc_demo.py` runs 30 checks across 5 categories:

```
[1] JSON parse check
  OK: evidence-ledger.json parses
  OK: findings.json parses
  OK: verdict.json parses
  OK: timeline.json parses
  OK: edr-handoff.json parses
  OK: replay-report.json parses
  OK: investigation-tape.json parses
  OK: phishing-powershell.json parses

[2] Evidence hash recomputation
  OK: entry[0] (edr_alert) hash matches
  OK: entry[0] (edr_alert) evidence_id matches
  OK: entry[1] (process_event) hash matches
  OK: entry[1] (process_event) evidence_id matches
  OK: entry[2] (network_event) hash matches
  OK: entry[2] (network_event) evidence_id matches
  OK: entry[3] (credential_access) hash matches
  OK: entry[3] (credential_access) evidence_id matches
  OK: entry[4] (lateral_movement_attempt) hash matches
  OK: entry[4] (lateral_movement_attempt) evidence_id matches

[3] Audit chain linkage
  OK: audit chain linkage: entry2.prev_entry_hash == entry1.this_entry_hash
  OK: entry2.this_entry_hash is correct

[4] replay-report.json assertions
  OK: replay_state: evidence_hashes_verified = True
  OK: replay_state: verdict_recomputed = True
  OK: replay_state: verdict_match = True
  OK: replay_state: no_live_llm_call = True
  OK: replay_state: no_live_edr_call = True
  OK: replay_state: state = 'succeeded'
  OK: replay_state: replay_status = 'succeeded'
  OK: replay_state: mode = 'recorded_output'

[5] edr-handoff.json assertions
  OK: action_type = 'isolate_host'
  OK: approval_mode = 'approval_required'
  OK: authorization_record_ref = 'vault://placeholder/bootstrap'
  OK: target.identifier = 'HOST-12'
  OK: execution_result: status = 'pending'
  OK: execution_result: reason = 'recommendation_only_no_dispatcher_in_slice_001'
  OK: evidence_refs has 5 entries
  OK: blast_radius field present
  OK: reversal_or_recovery_plan field present
  OK: reversibility_class = 'reversible_by_edr'

VALIDATION PASSED — all checks OK.
```

**30/30 checks passed.**

---

## 6. Demo refinement pass

After the initial package was committed and validated, a visual review pass
identified four issues that needed fixing before the demo was YC-ready:

**Issue 1 — Reversal language implied live EDR capability.**
`demo-script.md` said "automatic release available." This was changed to: "expected
EDR reversal action is `release_isolation`. In this Slice 001 demo, no EDR action
is dispatched." The same language was updated in `edr-handoff.json`'s
`recovery_notes` field.

**Issue 2 — Red ❌ for positive constraints looked like failures.**
`demo.html` showed `❌ No live LLM call during replay` and `❌ No live EDR call
during replay`. A red X visually signals failure. Changed to `✅` with green
styling — these are positive constraints, not errors.

**Issue 3 — README referenced regeneration scripts without context.**
The README had bare `python scripts/generate_yc_demo.py` commands with no
explanation. Replaced with a "Validation" section that explains the artifacts were
validated before commit and the scripts are available for re-validation.

**Issue 4 — No founder-friendly walkthrough page.**
`demo.html` was a full reference document, not a recording-friendly walkthrough.
`demo-recording.html` was created as a 7-scene full-screen page designed for a
60–90 second Loom recording. Each scene fits 1920×1080, has a progress indicator,
and supports keyboard navigation (arrow keys / spacebar).

**Final scene flow:**

| Scene | Title |
|---|---|
| 1 | The Question — "Should we approve host isolation?" |
| 2 | Raw Incident — the EDR-style alert |
| 3 | Action Card — approval-required, blast radius, reversal plan |
| 4 | Evidence — 5 hashed entries |
| 5 | Verdict — deterministic, confirmed_malicious |
| 6 | Replay Proof — 5/5 hashes verified, verdict recomputed |
| 7 | Proof Package — 8 questions answered, closing line |

---

## 7. Commits

| Hash | Date | Description |
|---|---|---|
| `03b928e` | 2026-05-04 | Add YC demo proof package — phishing/PowerShell scenario |
| `e2239af` | 2026-05-04 | Add YC demo generator, validator, and demo.html |
| `1af43c3` | 2026-05-04 | Patch YC demo: update IP to 203.0.113.50, new positioning, soften reversal language |
| `d4ec4d2` | 2026-05-04 | Add demo-recording.html, fix reversal language, fix red X, fix README |
| `6d5dd4c` | 2026-05-04 | demo-recording.html: 3 copy edits — banner, Scene 1 lead-in, Scene 7 closing line |

All commits on branch `mvp/slice-001-claude-implementation`.

---

## 8. Why I am proud of this session

I am proud of this session because it shows how I use AI coding tools under
constraints. The agent was not allowed to invent product scope, call external
services, or produce non-deterministic output. It had to compute real SHA-256
hashes, link an audit chain, validate 30 assertions, and stop after the defined
task.

Every constraint was stated explicitly before the agent started. When the agent
produced something that implied a capability that does not exist yet — live EDR
reversal — I caught it in review and gave a precise correction. The agent applied
the fix, re-ran validation, and confirmed the output was clean.

This is the same workflow I want to use to build Zovark: spec → artifact →
validation → commit. The demo package is not the product. It is evidence that the
workflow is real.

---

## 9. What this is not

- This is not a production product.
- This is not a live EDR integration.
- This is not autonomous response.
- No EDR vendor API was called at any point.
- No AI model ran during the demo or during replay.
- This is a static Slice 001 proof-package walkthrough, hand-crafted to show the
  intended output shape of the Zovark pipeline currently under construction.

---

## 10. Appendix: trimmed transcript highlights

### Task prompt (condensed)

> Create a static demo package under `demo/zovark-proof-package/`. Scenario: user
> opens phishing document → winword.exe spawns powershell.exe → PowerShell runs
> encoded command → external IP contacted → credential-access behavior → lateral
> movement attempt. The proof package must emphasize evidence links, deterministic
> verdict, approval-required action card, blast radius, reversal/recovery plan, and
> replay verification. Do not add live EDR. Do not add autonomous response. Do not
> add network calls. Keep hashes internally consistent.

### Agent plan (before writing any files)

The agent computed all SHA-256 values before writing a single file:

```python
# Evidence source objects → canonical JSON → SHA-256
alert_hash:  794e31dac2f14f5df1c802dd9bbf57dd56bdbba75e301bb972b2c3609d72e45d
pe_001_hash: c65c0ef3f6dad53569a930b7260d503f146f89656759d76472c8875d4bac4f0d
ne_001_hash: d8d1a7ef1e4f9bf578c6b27ad842880852b1b5280957f9e55768bf218df73649
ca_001_hash: f4a832d60d5598ed46ac4b72cc8f69ed2a030373ddfbaafd4ebbde8d9043c224
lm_001_hash: a825d1974ff6e43f372428db972c99a27d86c3fd1222708b1395e791999a127d

signing_tag: sig-9d97f0257f869f0cb5c84dfb81e968dc3c7f2f73961718d29454a124a238adc5
idempotency_key: 9f71c494eb9924ec832e347350f7643e71cdbcda7bcb7d568c2350ebf853271c
entry1_this_entry_hash: af0c6d7a6edd3b5c7db612e42be72fffaac2918086fcbcf76aa3a002c6193728
entry2_this_entry_hash: c14ff0b3c3e4be6feb077813088f6e493ee9523b2c9df8823a031e21b0145c16
```

These values were computed first, then used consistently across all 9 output files.

### File creation summary

```
Commit 03b928e — 11 files, 935 insertions
Commit e2239af — 13 files changed, 2406 insertions (generator + validator + demo.html)
Commit 1af43c3 — 12 files, IP patch + hash recomputation
Commit d4ec4d2 — 4 files, demo-recording.html + 3 fixes
Commit 6d5dd4c — 1 file, 3 copy edits
```

### Validation output (final run)

```
VALIDATION PASSED — all checks OK.
30/30 checks passed.
```

### Final commit summary

```
6d5dd4c  demo-recording.html: 3 copy edits
d4ec4d2  Add demo-recording.html, fix reversal language, fix red X, fix README
1af43c3  Patch YC demo: update IP, new positioning, soften reversal language
e2239af  Add YC demo generator, validator, and demo.html
03b928e  Add YC demo proof package — phishing/PowerShell scenario
```
