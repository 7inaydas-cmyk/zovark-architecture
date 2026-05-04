# Kiro Coding-Agent Session — Zovark YC Demo (Short Version)

**Branch:** `mvp/slice-001-claude-implementation` · **Date:** 2026-05-04

---

## What this session produced

A static YC demo proof package showing what Zovark produces before a SOC analyst
approves host isolation. The scenario: phishing document → encoded PowerShell →
C2 contact → LSASS credential dump → lateral movement attempt.

**Output artifacts** (`demo/zovark-proof-package/`):

| Artifact | Description |
|---|---|
| `samples/edr/phishing-powershell.json` | Synthetic EDR alert input |
| `out/tape-001/evidence-ledger.json` | 5 entries, SHA-256 hashed |
| `out/tape-001/findings.json` | 4 rule-driven findings, no model |
| `out/tape-001/verdict.json` | Deterministic: `confirmed_malicious` |
| `out/tape-001/edr-handoff.json` | Approval-required action card |
| `out/tape-001/replay-report.json` | Replay state + audit chain entry |
| `out/tape-001/customer-report.md` | 8-question human-readable report |
| `demo-recording.html` | 7-scene founder walkthrough for Loom |
| `scripts/validate_yc_demo.py` | 30-check validator |

---

## Hard constraints given to the agent

No live EDR. No autonomous response. No network calls. No LLM calls. No Sigma.
No SIEM. Artifacts must be deterministic. Use canonical JSON + SHA-256. Validate
before commit. `execution_result.status` stays `pending`.

---

## How the agent worked

1. Computed all SHA-256 hashes before writing any file — evidence hashes, evidence
   IDs, signing tag, idempotency key, audit chain `this_entry_hash` values.
2. Wrote all 9 output artifacts with internally consistent hashes.
3. Wrote `scripts/validate_yc_demo.py` with 30 checks: JSON parse, hash
   recomputation, audit chain linkage, replay assertions, handoff assertions.
4. Ran the validator. **30/30 passed.**
5. After visual review, applied targeted fixes: softened reversal language that
   implied live EDR capability, changed red ❌ to green ✅ for positive constraints,
   created `demo-recording.html` as a 7-scene walkthrough for recording.

---

## Validation output

```
VALIDATION PASSED — all checks OK.
30/30 checks passed.
```

Checks included: JSON parse (8), evidence hash recomputation (10), audit chain
linkage (2), replay-report assertions (8), EDR handoff assertions (10).

---

## Commits

| Hash | Description |
|---|---|
| `03b928e` | Add YC demo proof package — phishing/PowerShell scenario |
| `e2239af` | Add YC demo generator, validator, and demo.html |
| `1af43c3` | Patch: update IP, new positioning, soften reversal language |
| `d4ec4d2` | Add demo-recording.html, fix reversal language, fix red X |
| `6d5dd4c` | demo-recording.html: 3 copy edits |

---

## Why I am proud of this session

The agent was not given a blank canvas. It was given a spec, a constraint list,
and a validation requirement. It computed real hashes, linked a real audit chain,
and stopped when the task was done. When it produced language that implied a
capability that does not exist yet, I caught it in review and gave a precise
correction. The agent applied the fix and re-validated.

This is the workflow I want to use to build Zovark: spec → artifact → validation →
commit. The demo package is not the product. It is evidence that the workflow is real.

---

## What this is not

Not a production product. Not a live EDR integration. Not autonomous response.
A static Slice 001 proof-package walkthrough showing the intended output shape of
the Zovark pipeline currently under construction.
