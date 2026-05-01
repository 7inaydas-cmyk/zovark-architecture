## Why

Codex review of the rc3 architecture surfaced two related issues in the `investigation-tape` capability, both about how the tape relates to replay:

1. **Lifecycle/immutability tension** — the binding spec says tape state transitions `closed → replaying → closed` AND that the tape "is not mutated" during replay. If `state` participates in the canonical hash chain (per `replay-and-audit` canonicalization), toggling it during replay mutates the hash and breaks immutability.
2. **Drift between binding spec and derived docs** — `architecture/objects/investigation-tape.md` and `architecture/one-page-architecture.md` both list a `replay_state_ref` field on the tape. The binding spec at `openspec/specs/investigation-tape/spec.md` does not list this field. Per the source-of-truth hierarchy, the binding spec wins. The derived docs claim a field the spec does not authorize.

This change resolves both via the cleaner architectural fix: the tape is a one-way artifact (`recording → closed`), and replay status lives only in the `replay_state` object (per `replay-and-audit` capability). The tape-side `replay_available` is derived by querying for replay-state objects with matching `tape_id`, not by storing a back-reference.

## What Changes

- **MODIFIED Requirements** against `investigation-tape`:
  - Tape `state` enum becomes `{recording, closed}`. The `replaying` value is removed — replay status is governed solely by `replay-and-audit`'s `replay_state.state` field.
  - Lifecycle transitions become `recording → closed` (one-way). A tape SHALL NOT transition out of `closed`.
  - Customer-facing surface still derives `replay_available` from "whether a replay-state object referencing this tape exists" — clarified as a tenant-scoped query against the `replay-and-audit` capability, not a tape field lookup.
- Update `architecture/objects/investigation-tape.md` to remove `replay_state_ref` from the field tables and update the lifecycle diagram (`recording → closed`, no `replaying` state).
- Update `architecture/one-page-architecture.md` (line 26) to drop `replay_state_ref` from the Investigation Tape field list and update the lifecycle notation.
- **Out of scope:** changes to `replay-and-audit` (replay state object's own state field unaffected); changes to `edr-handoff` (already references audit/replay correctly); product implementation; new architecture decisions.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `investigation-tape`: collapse tape state enum to `{recording, closed}`; remove `replay_state_ref` from the field set the spec authorizes (it was never there, but this MODIFIED block makes the absence explicit and documents the rationale).

## Impact

- **Documents touched:** `architecture/objects/investigation-tape.md`, `architecture/one-page-architecture.md`.
- **Spec updated:** `openspec/specs/investigation-tape/spec.md` (via archive).
- **Build-planning artifact:** `architecture/one-page-architecture.md` is updated within this change so the build-planning-artifacts spec scenario "field contradicts canonical definition" is no longer violated.
- **Code:** none.
- **Linked items:** closes Codex findings #1 and #2 from the post-rc3 review.
