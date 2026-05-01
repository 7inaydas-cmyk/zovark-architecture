## Why

Replay correctness (finalization-checklist #6) and audit/DR/lifecycle (#8) are PARTIAL on the rc1 scorecard. The wedge spec asserts replayable evidence and the investigation-tape spec asserts deterministic verdict recompute, but no document specifies *how* replay works — how recorded I/O is rebound, which schema/tool/catalog versions are pinned, how evidence hashes are verified. Similarly, audit-chain canonicalization, concurrent-insert behavior, root signatures, unsigned-tail behavior, and the DR restore-gap semantics from `disaster-recovery-restore-gap.md` are scattered across invariants and patch docs. The EDR handoff and investigation tape specs already reference `audit_ref` and replay state by name; this change defines the target.

Closes the architectural gap on replay and audit/DR/lifecycle. Documentation only.

## What Changes

- Land `architecture/objects/replay-and-audit.md` defining: (a) replay state object — what fields, what state transitions, how recorded I/O is rebound during replay, what hash/version pins it enforces; (b) audit chain entry — canonicalization rules, concurrent-insert behavior, root signature scheme at the spec level (without naming the algorithm), unsigned-tail handling, and the restore-gap event from the patch's DR doc.
- Capture as `openspec/specs/replay-and-audit/spec.md`.
- Reference DR sketch hooks for ARCH-P2-002 — the spec records that a control-plane DR plan is the next sketch deliverable but does not produce the sketch in this change.
- **Out of scope:** picking the hash algorithm; picking the signature scheme; storage layout for the audit chain; DR runbook; restore-drill cadence (those land via subsequent ADRs); per-tenant key rotation (that's `vault-authorization`).

## Capabilities

### New Capabilities

- `replay-and-audit`: Combined capability for replay state and audit chain semantics. Defines both objects in one capability because they are tightly coupled (every replay reads audit chain entries; every closed tape signs an audit chain entry). The capability spec covers: replay determinism rules, recorded-I/O rebinding, schema/tool/catalog version pinning, evidence-hash verification, audit chain canonicalization, concurrent-insert behavior, root signature semantics, unsigned-tail handling, DR restore-gap semantics with the `DISASTER_RECOVERY_RESTORE_COMPLETED` event, and verifier state `VALID_AFTER_RESTORE_WITH_DECLARED_GAP`.

### Modified Capabilities

(none — `investigation-tape` and `edr-handoff` forward-reference; this change provides the target)

## Impact

- **Documents added:** `architecture/objects/replay-and-audit.md`, `openspec/specs/replay-and-audit/spec.md`.
- **Documents touched:** none.
- **Code:** none.
- **Linked issues:** drives finalization-checklist #6 and #8 from PARTIAL → PASS in rc2 scorecard. ARCH-P2-002 (control-plane DR plan) is not closed by this change but is referenced; remains tracked as deferred per current triage.
