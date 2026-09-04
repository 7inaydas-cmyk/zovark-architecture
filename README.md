# Zovark

[![checks](https://github.com/7inaydas-cmyk/zovark-architecture/actions/workflows/checks.yml/badge.svg)](https://github.com/7inaydas-cmyk/zovark-architecture/actions/workflows/checks.yml)

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

Before a security team isolates a host or disables a user account, Zovark shows the
evidence behind the decision, explains the verdict, records the approval path, and
writes a proof package that can be replayed afterwards and checked byte for byte.
EDR detects. AI investigates. The security operations team approves. Zovark proves
what happened.

The people this is built for are security operations teams who have to answer for an
action after it was taken, and who cannot answer with an opaque model summary.

## Status, stated plainly

Pre-revenue. Not launched. No users.

Slice 001 is built and it runs. It is a deterministic local pipeline: one static
EDR-style JSON sample in, a 9-file proof package out. Slice 001 uses no live EDR, no
LLM calls, and no network calls.

Everything past Slice 001 is designed and written down rather than built.
`architecture/invariants.md` tracks 39 invariants and labels each one covered,
partial, or deferred, so the gap between what runs and what is planned is on the
record instead of in a pitch.

## Prerequisites

- Python 3.11+
- No runtime dependencies beyond the Python standard library

The test command below uses `pytest`. The repository validation workflow runs it
through `uv run --with pytest` so the test dependency does not need to be added
to the runtime package.

## Run Slice 001

From the repository root:

```bash
python -m zovark.slice001 --input samples/edr-sample-001.json --output out/ --tenant-id tenant-001
```

The input sample is `samples/edr-sample-001.json`. It is synthetic and contains:

- one top-level EDR alert object
- one process event
- one network event

It does not contain real customer data or secrets.

## Expected Output

The command writes exactly 9 proof-package files: 8 JSON files and 1 Markdown
file. The input sample is not copied into the output directory.

Hero artifacts:

- `edr-handoff.json`
- `replay-report.json`
- `customer-report.md`

Full output file set:

- `edr-handoff.json`
- `replay-report.json`
- `customer-report.md`
- `investigation-tape.json`
- `evidence-ledger.json`
- `timeline.json`
- `findings.json`
- `verdict.json`
- `audit-chain-entry.json`

### What the analyst actually reads

`customer-report.md` opens with the action card. The action is recommended, not
taken:

```
## Recommended Action (EDR Action Card)

**Action:** ISOLATE_HOST
**Target:** workstation-42.corp.example
**Approval required:** YES - no action has been dispatched
**Evidence basis:** 3 evidence items (see below)
**Verdict:** CONFIRMED_MALICIOUS
**Reversibility:** automatic - `release_isolation` available
```

`verdict.json` carries the rule that produced the verdict and the evidence it was
derived from, so the verdict can be argued with rather than trusted:

```json
{
  "derivation_rule": "Any finding with severity critical or high -> confirmed_malicious",
  "value": "confirmed_malicious",
  "model_contribution": false,
  "evidence_refs": ["ev-1dbe5270...", "ev-6c297d89...", "ev-921f44c7..."]
}
```

A live demo package, including an HTML recording of a replay, is in
`demo/zovark-proof-package/`.

## Replay And Verification

Slice 001 is deterministic and repeatable within the exported proof-package
contract. Replay verifies that the exported artifacts are consistent with the
static input and local deterministic pipeline:

- evidence hashes are recomputed from `raw_content`
- timeline and finding references resolve to exported evidence IDs
- findings are rule-based and evidence-backed
- the verdict is derived from findings
- the EDR handoff remains approval-required with pending execution
- the audit entry seals the deterministic close snapshot
- the replay report fails closed when required evidence or hashes are corrupted

This makes the proof package auditor-verifiable within the Slice 001 export
contract. It is not a legal, certification, or complete-evidence claim.

The verifier re-derives the whole chain from the evidence rather than reading the
findings it was handed. That change is written up in
`DESIGN_verifier_rederivation.md` and `AUDIT_verifier_rederivation.md`, and it
closed a hole where a forged findings file would have been accepted.

## Run Tests

```bash
pytest tests/
```

The full repository validation command used during Slice 001 development is:

```bash
uv run --with pytest python3 -m pytest tests/ -q
python3 scripts/validate_yc_demo.py
python3 scripts/check_mvp_scope_consistency.py
python3 scripts/check_claim_provenance.py
python3 scripts/check_adr_cross_links.py
```

## How this repository keeps itself honest

The interesting part of this repository is not the pipeline. It is that the
documentation is under test alongside the code. Every push runs six gates in CI,
and a red gate blocks the merge.

| Gate | What it refuses to let through |
|---|---|
| Tests | `tests/` fails, including `tests/test_readme.py`, which asserts this README still documents the real command and the real 9-file output, and which holds a blocklist of overreaching legal and certification phrases that this file is not allowed to contain |
| Schema contracts | A contract in `contracts/` drifts away from the payloads that are actually produced |
| Claim provenance | A number with a unit appears next to a category word such as latency or throughput without a provenance tag saying who measured it, how, and when. An unsourced performance figure fails the build |
| MVP scope consistency | A document quietly widens the shipped scope past what Slice 001 does |
| ADR cross-links | An architecture decision record points at a decision that does not exist |
| Demo validation | The committed demo package stops matching what the pipeline produces |

The claim-provenance gate is the one worth reading the source of. It exists
because the easiest thing to do in an early-stage architecture document is to
write a confident number nobody measured. `scripts/check_claim_provenance.py`
makes that fail the build.

## Repository map

| Path | What is there |
|---|---|
| `zovark/slice001/` | The pipeline: ingest, canonical form, hashing, tape, timeline, findings, verdict, handoff, audit chain, replay, verifier |
| `tests/` | The test suite, plus recorded proof-package fixtures used to catch contract drift |
| `architecture/` | 27 architecture decision records, the invariants register, the object model, and the one-page architecture map |
| `openspec/` | Specification changes tracked as reviewable records rather than as edits to prose |
| `contracts/` | JSON Schema contracts enforced by CI |
| `docs/` | Working documents: current implementation map, roadmap after Slice 001, positioning, review-gate policy |
| `demo/` | A runnable proof package and an HTML recording of the replay |
| `scripts/` | The CI gate scripts described above |
| `archive/` | Superseded design bundles, kept so the decision history stays readable |

## Scope and limits

- Slice 001 is the only built path. Treat the rest of `architecture/` as design intent.
- There is no live EDR integration, no model in the loop, and no multi-tenant runtime.
- The proof package is verifiable against its own export contract. It is not a legal or certification artifact.
- Licensing is not settled. ADR-0043 gates the source-available terms and it has not been accepted, so a draft license lives in `archive/` and no license file is published at the repository root yet.

## Local Files

Do not commit local editor or generated files such as `.vscode/`, `uv.lock`, or
`zovark-yc-demo.zip` unless the project deliberately changes that policy.
