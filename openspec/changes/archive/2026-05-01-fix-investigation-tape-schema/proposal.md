## Why

The investigation tape is named in the `product-wedge` spec as the central recorded object, but no architecture document defines its fields, lifecycle, or the customer-facing surface it exposes. Finalization-checklist criterion #5 (Investigation tape object) is currently PARTIAL on the rc1 scorecard. Without a documented object, build planning for M1+ tape work has nothing to scope against, and `fix-edr-handoff-schema` and `fix-replay-and-audit-semantics` cannot reference tape fields they need to compose with.

This change defines the investigation tape at the spec level — required fields, lifecycle, customer-facing surface, and the object's role in the wedge flow. It does not implement storage, schemas in JSON, or runtime behavior. Documentation only.

## What Changes

- Land `architecture/objects/investigation-tape.md` defining the investigation tape object: required fields, lifecycle states, replay/audit linkage, customer-facing surface, and what is explicitly out of scope.
- Capture the requirements as `openspec/specs/investigation-tape/spec.md` after archive.
- Cross-reference the new doc from `architecture/source-of-truth.md` (under "Current product wedge"), `mvp-scope.md`, and the EDR handoff and replay specs that follow.
- **Out of scope:** JSON Schema or Avro definitions; storage layout; UI/UX; database choice; tenant-scoping implementation. The tape is described at field-and-relationship level, not at serialization or persistence level.

## Capabilities

### New Capabilities

- `investigation-tape`: The investigation tape object spec — required fields, field types at the conceptual level, lifecycle states, the relationship between tape and replay/audit/EDR-handoff sub-objects, and the customer-facing surface (what users can inspect on a tape).

### Modified Capabilities

(none)

## Impact

- **Documents added:** `architecture/objects/investigation-tape.md`, `openspec/specs/investigation-tape/spec.md` (after archive).
- **Documents touched:** none (no patch-tree edits; cross-references added in subsequent rc2 changes if needed).
- **Code:** none.
- **Linked issue:** drives finalization-checklist #5 from PARTIAL → PASS in rc2 scorecard.
