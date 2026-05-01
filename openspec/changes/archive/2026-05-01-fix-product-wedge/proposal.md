## Why

The architecture's source-of-truth hierarchy declares Zovark as "the tape recorder for cybersecurity investigations" with a canonical EDR-bookended flow, but the actual architecture content (mvp-scope, ZOVARK-FINAL, ENGINEERING-READY-HANDOFF) uses different vocabulary and treats EDR as one adapter among many. This wedge mismatch is freeze-blocking under finalization checklist criterion #1 (`Product wedge clarity`) and tracked as ARCH-P0-001 / GitHub issue #1.

## What Changes

- Introduce a single canonical product-wedge statement and apply it consistently across architecture content. The statement is: **Zovark is the tape recorder for cybersecurity investigations.**
- Define the canonical core flow: **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.** This flow appears in every top-level architecture and customer-facing doc.
- Rewrite the product-wedge / overview sections of: `mvp-scope.md`, `ZOVARK-v3.2.4.6-FINAL.md`, `ENGINEERING-READY-HANDOFF.md`. Keep MVP scope details, technical scope, and engineering deliverables intact — only the framing/positioning changes.
- Subordinate generic "AI SOC platform" framing where it appears. The architecture remains a tape-recorder product; AI capabilities are the mechanism, not the wedge.
- Surface the investigation tape and EDR handoff as central concepts in architecture overviews. Do not redefine them — point at existing object definitions where they exist, mark gaps as future work otherwise.
- Keep the existing `OWNERS.yaml` component name "Replay engine and tape recorder" (F-002) and the telemetry envelope schema enum value `tape-recorder`. These now align with the wedge instead of being orphan nouns.
- **Out of scope:** adding new product capabilities, EDR vendor expansion, post-MVP platform claims, building the investigation-tape object schema, or any implementation work. This is a documentation-coherence change.

## Capabilities

### New Capabilities

- `product-wedge`: Single source of truth for Zovark's product positioning, core flow, and the relationship between investigation tape, replay, verdict, and EDR handoff. Defines what statements about Zovark must say and how they must compose. All architecture and customer-facing docs cite this capability rather than restating positioning.

### Modified Capabilities

(none — no existing OpenSpec specs in this repo yet; `openspec/specs/` is empty)

## Impact

- **Documents touched:** `architecture/source-of-truth.md` (already governance-aligned, lightly clarified if needed), `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/mvp-scope.md`, `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ZOVARK-v3.2.4.6-FINAL.md`, `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/ENGINEERING-READY-HANDOFF.md`.
- **Documents not touched:** ADRs (status quo), invariants, schemas, scripts, OWNERS.yaml component descriptions (already aligned), claim-provenance.md (separate change).
- **Code/APIs:** none — no runtime impact.
- **Dependencies:** none.
- **Linked issue:** ARCH-P0-001 / GitHub #1. Closes on apply + verify.
