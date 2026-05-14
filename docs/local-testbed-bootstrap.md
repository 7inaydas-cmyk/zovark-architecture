# Local Zovark Testbed Bootstrap

Status: local proof/Replay bootstrap. This workflow runs only static or sanitized
V3-like input through the existing adapter, proof-package writer, and offline
Replay verifier.

## Feature Lifecycle

ADR-0037 requires durable feature lifecycle discipline before adding new CLI,
testbed, AlertForge, benchmark, service, or schema work. No current applied/root
`product/features/feature-registry.yaml` file is present in this repo snapshot.
The only discovered feature-registry material is recovered patch-tree material,
including:

```text
zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/patches/feature-registry.yaml.append_v3_2_4_5
```

That recovered material was inspected for lifecycle context. This runner is
scoped as workflow plumbing for the existing `F-002` Replay engine and tape
recorder feature referenced in recovered ownership metadata, not as a new
product feature. No new feature ID is introduced and no root feature-registry
entry is changed in this PR.

The local runner remains a narrow static proof/Replay workflow. Any future
product component, standalone testbed feature, AlertForge ingest path, benchmark
harness, service, feature flag, or customer-facing workflow must add or update
the feature registry according to ADR-0037 before implementation claims are
made.

## Prerequisites

- Python 3.11 or newer.
- Run commands from the repository root.
- No network, database, Vault, EDR, SIEM, LLM, control plane, or AlertForge
  service is required.

## Input Fixture

Sample fixture:

```text
samples/v3-local-proof-fixture.json
```

The sample is static and sanitized. It is not customer data and does not contain
raw prompts, raw tool arguments, raw tool outputs, payload bodies, chat messages,
analyst notes, or hidden reasoning.

## Generate And Verify V2

```bash
python3 -m zovark.slice001.local_testbed \
  --input samples/v3-local-proof-fixture.json \
  --output .tmp/local-testbed-v2 \
  --package-version v2
```

The command generates the current nine V1 proof-package files plus
`proof-package-v2.json`, then runs offline Replay verification.

Run verification again:

```bash
python3 -m zovark.slice001 verify --package .tmp/local-testbed-v2
```

## Generate And Verify V1

```bash
python3 -m zovark.slice001.local_testbed \
  --input samples/v3-local-proof-fixture.json \
  --output .tmp/local-testbed-v1 \
  --package-version v1
```

The V1 output remains the existing nine-file package. It does not emit
`proof-package-v2.json` or V2-only trace/context fields.

## What Is Real

- V3-like fixture loading from a local JSON file.
- Existing `zovark.slice001.v3_adapter` package generation.
- Explicit V1 or V2 package selection.
- Existing proof-package writer output.
- Offline Replay verification through `zovark.slice001.package_verifier`.

## What Is Static Or Mocked

- The input is a static local fixture.
- The alert, execution metadata, governance evidence, control snapshot, and
  response details are recorded fixture values.
- There is no live collection from EDR, SIEM, CMDB, ticketing, IAM, LLM, Vault,
  network, or control-plane systems.

## Not Included Yet

- AlertForge output contract.
- AlertForge ingest/importer.
- End-to-end synthetic alert validation outside static fixtures.
- Benchmarks or capacity claims.
- Customer-readiness bundle or outreach material.
- Signing, anchoring, SLSA, in-toto, legal admissibility, compliance
  certification, or full implementation compliance claims for recovered
  ADR-0044 through ADR-0051.

ADR-0036 remains a schema boundary constraint: local proof-package and export
work must not make vendor/proprietary schemas canonical dependencies for Replay,
audit, storage, verdict, or customer evidence.

Context Compaction Memory is not part of this local runner. The current testbed
uses sanitized static fixtures and existing proof/Replay code only. Future
runtime work that produces high-volume tool output must apply the
`docs/context-compaction-memory.md` and `docs/investigation-memory-contract.md`
contracts before placing tool output into model context.
