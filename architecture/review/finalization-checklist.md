# Architecture Finalization Checklist

This is the frozen rubric for finalizing the architecture. Reviewers and AI agents may propose issues only against these categories.

## 1. Product wedge clarity

Acceptance:
- Zovark is consistently described as the tape recorder for cybersecurity investigations.
- The core flow is EDR alerts → investigation tape → replayable evidence → verdict → EDR handoff.
- The architecture does not drift into a generic AI SOC platform.
- EDR handoff and replayability are central.

## 2. MVP scope consistency

Acceptance:
- M0, design-partner MVP, post-MVP, GA, and future scope are clearly separated.
- No post-MVP feature is described as MVP behavior.
- Sigma scope, EDR adapter scope, SIEM publication, and autonomous action scope are consistent.
- Customer-facing docs do not imply unshipped capabilities.

## 3. ADR inventory and supersession

Acceptance:
- Every ADR is indexed in `architecture/adr-index.md`.
- Every ADR has a status.
- Superseded ADRs are clearly marked.
- Active ADRs do not contradict each other.
- Active ADRs do not reference superseded ADRs as current guidance.

## 4. Claim provenance

Acceptance:
- Every quantified claim has one of:
  - `[hypothesis]`
  - `[measured:<artifact-id>,<date>]`
  - `[vendor-cited:<citation-id>]`
  - `[policy-commitment:<owner>,<review-cadence>]`
- Customer-facing docs contain no `[hypothesis]` claims.
- Measured claims point to real evidence artifacts.
- Policy commitments name an owner and review cadence.

## 5. Investigation tape object

Acceptance:
- The investigation tape is defined as the core product object.
- Tape includes raw evidence, timeline, campaign grouping, evidence-backed findings, verdict, EDR handoff, replay state, and audit references.
- Customer can inspect what Zovark saw, concluded, and handed off.

## 6. Replay correctness

Acceptance:
- Recorded-output replay does not call live LLMs.
- Replay uses recorded model I/O.
- Replay uses historical schema/tool/catalog versions.
- Replay verifies raw evidence hashes.
- Replay recomputes deterministic verdicts where claimed.
- Replay distinguishes recorded-output replay from forensic re-execution.

## 7. EDR handoff correctness

Acceptance:
- Every EDR handoff records action type, target, tenant, evidence links, policy snapshot, approval mode, authorization record, idempotency key, execution result, and rollback/reversal plan.
- Handoff is replayable and auditable.
- Approval-required and autonomous modes are clearly distinguished.

## 8. Audit, DR, and tenant lifecycle

Acceptance:
- Audit-chain canonicalization, concurrent insert behavior, root signatures, unsigned-tail behavior, and restore-gap semantics are defined.
- Same-region HA is not described as cross-region DR.
- Terminate-retain, crypto-shred, legal hold, and identity erasure are distinct.
- Historical audit rows are not mutated for erasure.

## 9. Vault / authorization

Acceptance:
- Signing and verification model is cryptographically coherent.
- Worker and adapter cannot mint authorization.
- Vault verifies action, tenant, target, expiry, nonce, policy, and authorization record.
- Replay protection and compromise scenarios are documented.

## 10. Evidence status

Acceptance:
- Existing scripts/tests/runbooks are real.
- Missing scripts/tests/runbooks are marked M0/future deliverables.
- No document claims non-existent enforcement exists.

## 11. Schedule realism

Acceptance:
- M0 and MVP schedules are separate if M0 is used.
- Old schedules are superseded.
- Planning envelope is explicit.
- Scope-cut rules exist.
- Schedule claims have provenance tags.

## 12. Customer validation workflow

Acceptance:
- Design-partner workflow exists.
- Customer scorecard exists.
- Workflow tests whether replayability increases trust in EDR response.
