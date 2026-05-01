## Why

The EDR handoff is one bookend of Zovark's product wedge: the core flow ends with "verified EDR handoff → rollback/reversal record." The `investigation-tape` capability references the handoff but does not define it. The rc1 finalization-checklist criterion #7 (EDR handoff correctness) is PARTIAL because the canonical 10-field handoff record is signposted but not specified anywhere. Without a documented record, neither build planning nor adapter scoping can proceed.

This change defines the EDR handoff record at the spec level — required fields, approval modes, idempotency semantics, replay linkage, and rollback/reversal — without implementing any vendor adapter.

## What Changes

- Land `architecture/objects/edr-handoff.md` defining the EDR handoff record: action types, target spec, evidence linkage, policy snapshot, approval modes, authorization record, idempotency key, execution result, rollback/reversal plan, and replay linkage to the investigation tape.
- Capture the requirements as `openspec/specs/edr-handoff/spec.md` after archive.
- Reference the new doc from `architecture/objects/investigation-tape.md` (already forward-references the handoff record by name; no rewrites needed).
- **Out of scope:** vendor adapter implementations (CrowdStrike/SentinelOne/etc. integration); HTTP transport details; tenant-key signing implementation; autonomous-mode policy decisions (approval-required vs autonomous remains a per-tenant policy, not specified here in detail beyond the mode enumeration).

## Capabilities

### New Capabilities

- `edr-handoff`: EDR handoff record spec — fields required on every handoff, approval modes, idempotency semantics, replay/audit linkage, rollback/reversal plan structure.

### Modified Capabilities

(none — `investigation-tape` already forward-references `edr-handoff`)

## Impact

- **Documents added:** `architecture/objects/edr-handoff.md`, `openspec/specs/edr-handoff/spec.md` (after archive).
- **Documents touched:** none (cross-references in `investigation-tape.md` already in place).
- **Code:** none.
- **Linked issue:** drives finalization-checklist #7 from PARTIAL → PASS in rc2 scorecard.
