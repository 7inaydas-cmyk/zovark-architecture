# Current Implementation Map

Status: implementation map. This document describes current code paths and test
coverage only. It does not change runtime code, adapter behavior, verifier
behavior, proof-package schema, or test fixtures.

## End-To-End Static Path

Current implemented flow:

```text
V3-like fixture/input
-> zovark.slice001.v3_adapter
-> Slice 001 tape construction
-> Proof Package V1 or explicit Proof Package V2 generation
-> zovark.slice001.package_verifier Replay verification
```

The implemented path is fixture-driven. It is not connected to a live V3 product
runtime, AlertForge runtime, SIEM, EDR, LLM, DB, or network service.

## V3 Fixture/Input

Representative V3-like input is a Python dictionary or JSON fixture with:

- `alert` fields such as `alert_id`, deterministic timestamp, host, severity,
  alert type, and optional process labels.
- `execution` fields such as `execution_mode`, `source`, `path_taken`,
  `plan_executed`, tool names/results, verdict, governance decision, and optional
  V2 practitioner fields.
- event arrays such as `process_events`, `network_events`,
  `credential_access_events`, and `lateral_movement_events`.

Real files:

- `tests/test_v3_adapter.py`
- `tests/test_v3_generated_package_verification.py`
- `tests/fixtures/v3-realistic-scenarios/alertforge-style-ransomware-containment.json`

## V3 Adapter

Primary module:

- `zovark/slice001/v3_adapter.py`

Primary entry points:

- `adapt_v3_fixture_to_slice_input(fixture)`
- `build_tape_from_v3_fixture(fixture, tenant_id=None)`
- `build_proof_package_from_v3_fixture(fixture, tenant_id=None, proof_package_version=...)`
- `write_proof_package_from_v3_fixture(fixture, output_dir, tenant_id=None, proof_package_version=...)`

Version behavior:

- Default path uses `V1_PACKAGE_CONTRACT = "slice-001-proof-package/1.0"`.
- Explicit V2 path uses `V2_PACKAGE_CONTRACT = "proof-package-v2/0.1"`.
- V1 output remains the nine-file package only.
- V2 output emits the nine V1 files plus `proof-package-v2.json`.

Important adapter behavior:

- Validates fixture shape and supported execution modes.
- Preserves deterministic path distinction:
  - deterministic tools
  - LLM-selected tools
  - explicit sandbox
  - sandbox fallback
- Builds Slice-compatible static input from the V3-like fixture.
- Preserves safe V2-only trace/context metadata only on the explicit V2 path.
- Sanitizes prompt transformation logs, tool-call summaries, and allowlisted
  V2 trace values.
- Populates currently supported V2 objects from recorded evidence only.

## Slice 001 Tape And V1 Package Generation

Primary modules:

- `zovark/slice001/cli.py`
- `zovark/slice001/ingest.py`
- `zovark/slice001/tape.py`
- `zovark/slice001/timeline.py`
- `zovark/slice001/findings.py`
- `zovark/slice001/verdict.py`
- `zovark/slice001/handoff.py`
- `zovark/slice001/audit.py`
- `zovark/slice001/replay.py`
- `zovark/slice001/writer.py`

Package files emitted by V1:

- `investigation-tape.json`
- `evidence-ledger.json`
- `timeline.json`
- `findings.json`
- `verdict.json`
- `edr-handoff.json`
- `audit-chain-entry.json`
- `replay-report.json`
- `customer-report.md`

CLI path:

```bash
python -m zovark.slice001 --input samples/edr-sample-001.json --output out/ --tenant-id tenant-001
```

Verifier path:

```bash
python -m zovark.slice001 verify --package out/
```

## Proof Package V2 Generation

V2 is generated only through the explicit adapter path:

```python
from zovark.slice001.package_verifier import V2_PACKAGE_CONTRACT
from zovark.slice001.v3_adapter import write_proof_package_from_v3_fixture

write_proof_package_from_v3_fixture(
    fixture,
    output_dir,
    proof_package_version=V2_PACKAGE_CONTRACT,
)
```

V2 marker file:

- `proof-package-v2.json`

V2 object population currently includes:

- `decision_rationale`
- `false_positive_reasoning`
- `context_enrichment`
- `visibility_gaps`
- `approval_record`
- `blast_radius`
- `rollback_plan`
- `compliance_mapping`
- `controls_in_place_at_incident`
- `customer_report_v2`

Current V2 safety properties:

- Source refs resolve through verified V1 evidence.
- Conditions are derived from verified evidence by the verifier.
- Required objects are source-backed.
- Prompt and tool summaries are sanitized.
- Raw prompt text, raw tool args, raw tool outputs, payloads, messages, notes,
  hidden reasoning, and chain-of-thought are not emitted by the tested V2 path.

## Replay Verification

Primary module:

- `zovark/slice001/package_verifier.py`

Public functions:

- `load_proof_package(package_dir)`
- `validate_loaded_proof_package(package)`
- `verify_proof_package(package_dir)`

V1 verifier behavior:

- Verifies exact file set.
- Parses JSON artifacts.
- Reconstructs the verified tape.
- Checks extracted views against `investigation-tape.json`.
- Re-derives handoff, audit entry, replay report, and customer report.
- Fails closed on tampering or malformed packages.

V2 verifier behavior:

- Recognizes V2 only when `proof-package-v2.json` is present.
- Runs V1 verification first.
- Derives V2 conditions from verified V1 package evidence.
- Builds a trusted reference index from verified evidence, trace/context refs
  preserved in the V1 evidence substrate, handoff refs, audit refs, replay refs,
  and artifact refs.
- Validates V2 marker shape, required objects, conditional objects, object
  envelopes, source refs, and unavailable/null handling.

## Test Coverage Map

| Test file | Coverage |
| --- | --- |
| `tests/test_package_verifier.py` | V1 verifier compatibility, V2 verifier skeleton, static V2 fixture, fail-closed behavior, condition derivation, source-ref resolution. |
| `tests/test_v3_adapter.py` | V3 adapter shape validation, V1/V2 generation, V2 object population, V1/V2 projection separation, sanitizer regressions. |
| `tests/test_v3_generated_package_verification.py` | V3-generated V1 package verifies with Replay V2 and CLI verification path remains valid. |
| `tests/test_v2_realistic_scenario_validation.py` | AlertForge-style static realistic scenario generates a V2 package, verifies, checks source refs, checks determinism, and checks sensitive-data leakage. |
| `tests/fixtures/proof-package-v2/response-action/` | Committed static V2 package fixture. |
| `tests/fixtures/v3-realistic-scenarios/` | Committed static V3-like realistic scenario fixture. |

## Not Yet Implemented

- First-class Capability Identity objects in generated proof packages.
- First-class Investigation Trace V1 record export.
- A command-line wrapper for V3 fixture -> V2 proof package generation.
- AlertForge input parser or integration runner.
- Live V3 runtime ingestion from `Zovark_final`.
- Live SIEM/EDR connectors.
- Live LLM/tool execution.
- DB-backed workflow.
- Dashboard/API workflow.
- Product-level local testbed command.
- Benchmarks or scale measurement scripts for the V3/V2 path.
- Customer-readiness package.
- Signing, anchoring, provenance manifest, SLSA, or in-toto.
