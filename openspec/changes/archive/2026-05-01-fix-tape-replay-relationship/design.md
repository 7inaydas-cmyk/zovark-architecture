## Context

Two issues, one root cause: the relationship between the tape and replays was loosely worded.

**The contradiction.** The investigation-tape spec requirement "Investigation tape SHALL track lifecycle state" lists three states (`recording, closed, replaying`) and the transitions between them. But it also says, in the same requirement, "tape itself is not mutated" during replay. If `state` is one of the canonical fields whose canonical-bytes hash anchors the audit chain (per `replay-and-audit` canonicalization rules), then `closed → replaying → closed` mutates the canonical bytes and the chain hash. That breaks the immutability story.

**The drift.** Separately, `architecture/objects/investigation-tape.md` (the architecture object doc) and `architecture/one-page-architecture.md` (the one-pager) both list a `replay_state_ref` field on the tape. The binding spec doesn't list it. The intent in those derived docs was "the tape can know which replay is currently active," but the spec itself doesn't authorize that — and the customer-facing surface in the spec describes `replay_available` as derived "from whether a replay state exists," not from a tape field.

## Goals / Non-Goals

**Goals:**

- Tape state becomes a true one-way lifecycle: `recording → closed`. No `replaying` state.
- Tape is genuinely immutable after `closed`. No fields toggle during replay.
- Replay status is fully governed by the `replay_state` object's own state field (`pending, running, succeeded, mismatch, failed`).
- Derived docs (object doc + one-pager) align with the binding spec — no `replay_state_ref` field.
- Build-planning-artifacts spec scenario "field contradicts canonical definition" is no longer triggered.

**Non-Goals:**

- Modifying `replay-and-audit`'s replay-state object spec (it already supports the model where replay status lives entirely in that object).
- Modifying `edr-handoff` (already correctly linked).
- Adding back-references from tape to anything outside the tape's own data.
- Implementing how `replay_available` is derived at runtime — the spec already says "derived from whether a replay state exists," and the implementation can query the `replay-and-audit` store for replay-state objects with matching `tape_id`.

## Decisions

### Tape state becomes `{recording, closed}` only

Removing `replaying` from the enum has three benefits:

1. **Immutability is real.** Once `closed`, no field changes. Canonical hash is stable.
2. **Single source of truth for replay status.** The `replay_state` object already has a state field that tracks `pending → running → {succeeded | mismatch | failed}`. There's no value in duplicating "is replaying" on the tape side.
3. **Cleaner tenant-scoped queries.** "Show me all replays of tape X" becomes a query against the `replay-and-audit` store, not a join.

**Rationale.** Alternative considered: keep `replaying` but exclude `state` from the canonical hash. Rejected — the canonicalization rules are deliberately strict (every field hashes), and adding per-field opt-out would create ongoing decision burden. The simpler architectural move is to remove the offending state value.

### Customer-facing `replay_available` is derived from `replay-and-audit` queries

The spec already defines `replay_available` as a derived value. We clarify that "derivation" means: query the `replay-and-audit` capability's replay-state index for any object with `tape_ref == this.tape_id`. If at least one exists in any state (including `pending`/`running`), `replay_available` is `true`. Otherwise `false`.

The implementation may cache this for performance, but the cache is not part of the tape's canonical fields.

**Rationale.** Keeps the tape immutable. Replay state can change asynchronously without invalidating the tape's audit-chain hash.

### Removing `replay_state_ref` from derived docs

Two derived docs claim a `replay_state_ref` field on the tape that the binding spec doesn't authorize:

- `architecture/objects/investigation-tape.md` line 123 (table row)
- `architecture/one-page-architecture.md` line 26 (field list)

Both are updated within this change to remove the field. The lifecycle notation in both docs is updated from `recording → closed → replaying → closed` to `recording → closed` (one-way).

**Rationale.** Per the source-of-truth hierarchy, the binding spec wins. Derived docs must follow.

### What this change does NOT do

- It does NOT delete the `replaying` concept entirely — the `replay_state.state` enum still has `pending, running` as transient states inside the `replay-and-audit` capability. We're only removing the *tape*-side state value.
- It does NOT change canonical hash semantics or audit-chain rules.
- It does NOT touch the `Reopen a closed tape for editing fails` scenario — that scenario remains valid (a `closed` tape stays `closed`).

## Risks / Trade-offs

- **Risk:** an implementation needs a fast lookup of "is this tape currently being replayed?" and the absence of `replay_state_ref` adds a query. → **Mitigation:** the runtime can index the replay-state store by `tape_ref`; the lookup is O(1). The spec doesn't require a tape-side back-reference.
- **Trade-off:** removing the `replaying` tape state means the tape's `state` field is binary. Some readers may find this less expressive. Accepted: expressiveness through duplicate state representation was the source of the immutability problem in the first place.

## Migration Plan

1. MODIFY the binding spec via this change's `MODIFIED Requirements` block.
2. Edit `architecture/objects/investigation-tape.md` to remove `replay_state_ref` and update the lifecycle section.
3. Edit `architecture/one-page-architecture.md` (line 26) to remove `replay_state_ref` and update the lifecycle notation.
4. Archive.
5. Re-run `scripts/check_mvp_scope_consistency.py`, `scripts/check_claim_provenance.py`, `scripts/check_adr_cross_links.py` — confirm all pass.

**Rollback:** revert. The tape state goes back to three values; the immutability tension returns.

## Open Questions

(none — both issues have a clean joint fix)
