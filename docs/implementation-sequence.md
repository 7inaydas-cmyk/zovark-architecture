# Implementation Sequence

Status: implementation sequencing, docs-only. This document does not implement
runtime code, schema changes, fixture capture, adapters, or Replay V2 behavior.

## Current Baseline

Merged baseline before this document:

- Replay V2 package verifier exists.
- Customer-readable verifier output exists.
- V3 ground-truth check exists.
- ADR and architecture-constraint index exists.
- V3 asset inventory and v4.1 domain map exist.
- V3 fixture capture report exists.

The architecture default is Option 2: V3 forward, Slice proof absorbed.

## Track Ownership

| Track | Owner | Work |
| --- | --- | --- |
| Track A | repo/architecture maintainer | Architecture PRs, review gates, proof/replay integration sequence. |
| Track B | founder/architect | Customer discovery and buyer-pain validation. |
| Track C | engineer with V3 runtime access | Scale measurements and bottleneck evidence. |

## Ordered PR Sequence

### PR #29: Capability Identity Contract And Architecture Synthesis

Status: this PR.

Outputs:

- `docs/capability-identity-contract.md`
- `docs/final-architecture-v3-v4-replay.md`
- `docs/implementation-sequence.md`
- `docs/stale-docs-cleanup-plan.md`

Gate:

- Docs-only.
- No runtime code.
- No proof-package schema changes.
- No V3 adapter.
- No Investigation Trace V1 spec.

### PR #30: Investigation Trace V1 Spec

Purpose:

- Define ordered trace events for V3 investigations.
- Tie trace events to Capability Identity Contract records.
- Represent deterministic tools, LLM-selected tools, sandbox fallback, governance,
  institutional context, and correlation context.
- Define candidate findings, accepted findings, rejected findings, and deterministic
  synthesis boundary if fixture evidence supports those fields.

Non-goals:

- No runtime implementation.
- No adapter code.
- No live systems.
- No proof-package schema bump unless explicitly approved by a later design gate.

### PR #31: V3 Fixture To Proof-Package Adapter

Purpose:

- First bridge code that converts captured or synthetic-safe V3 fixture shapes into
  the existing proof-package generation path.
- Preserve path distinctions required by the Capability Identity Contract.

Gate:

- Must not hide LLM-selected or sandbox fallback behavior.
- Must not call live EDR, LLM, DB, network, dispatcher, or external state during
  replay.
- Must not claim production readiness.

### PR #32: Verify Generated V3 Proof Package With Replay V2

Purpose:

- Generate a proof package from V3 fixture-derived input.
- Verify the generated package with the existing Replay V2 verifier.
- Demonstrate end-to-end proof gate for recorded V3 outputs.

Gate:

- Replay remains offline.
- Verifier does not trust the original runtime.
- Tampering still fails closed.

### Later: Controlled Schema Bump If Needed

Purpose:

- Add first-class proof fields only if adapter and trace work show that the existing
  nine-file package cannot distinguish deterministic tools, LLM-selected tools, and
  sandbox fallback without ambiguity.

Gate:

- Requires explicit schema decision.
- Requires tests and proof-package contract update.
- Must preserve backward compatibility or define a versioned migration path.

### Later: Manifest, Provenance, Signing

Purpose:

- Add artifact hashes, package manifest, provenance records, and signing only after
  trace/proof semantics are stable.

Gate:

- Must not retrofit signing claims onto current unsigned packages.
- Must respect ADR-0039 and ADR-0042 constraints.

### Later: Runtime Expansion

Purpose:

- Live EDR/SIEM connectors.
- Harness and Inference Gateway hardening.
- Capability Gateway runtime.
- Vault runtime integration.
- deployment profiles.

Gate:

- Requires customer pull or pilot requirement.
- Requires Track C scale data.

## Parallel Work

Track B customer discovery should continue in parallel with architecture PRs.

Minimum customer signal format:

- role/title:
- company type:
- conversation date:
- key reactions:
- would they use it?
- would they pay?
- where would it live?
- evidence missing:
- strongest objection:
- roadmap impact:

Do not promote buyer-pain hypotheses into roadmap commitments until repeated customer
signals validate them.

Track C scale measurement should produce:

- submission throughput
- completion throughput
- p50/p95/p99 latency if available
- saved-plan hit rate
- LLM-selected path rate
- sandbox fallback rate
- observed bottleneck
- suitable early-customer size range
- explicit gap versus the v4.1 10K alerts/sec target

If measurements are not available, architecture docs must say so directly.

## Hard Sequencing Rules

- Fixture evidence comes before trace fields.
- Capability identity comes before adapter code.
- Trace spec comes before runtime trace implementation.
- V3 adapter comes before end-to-end V3 proof-package verification.
- Replay never calls live systems.
- Governance policy does not replace Vault authorization.
- Proof schema changes require a controlled schema PR.
- Runtime integrations require customer or pilot pull.

## What Not To Do Next

Do not start:

- live EDR/SIEM connector work
- Capability Gateway runtime
- manifest/provenance/signing implementation
- broad runtime rebuild
- proof-package schema bump without fixture-driven need
- Fast Mode or Reasoning Mode productization
- dashboard work
- customer-facing legal/certification claims

## Validation For Docs PRs

Required validation for docs-only architecture PRs:

```bash
git diff --check
python3 scripts/check_adr_cross_links.py
python3 scripts/check_claim_provenance.py
```

Runtime or schema PRs must add focused tests and full validation commands appropriate
to the files changed.
