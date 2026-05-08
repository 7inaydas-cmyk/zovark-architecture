# Zovark

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

In product terms, Zovark is the AI-native proof layer for high-stakes security
response. Before a SOC isolates a host or disables a user, Zovark shows the
evidence, explains the verdict, records the approval path, and creates a
replayable proof package. EDR detects. AI investigates. SOC approves. Zovark
proves.

Slice 001 is a deterministic local proof-package pipeline. It takes one static
EDR-style JSON sample and writes a 9-file proof package. Slice 001 uses no live
EDR, no LLM calls, and no network calls.

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

## Local Files

Do not commit local editor or generated files such as `.vscode/`, `uv.lock`, or
`zovark-yc-demo.zip` unless the project deliberately changes that policy.
