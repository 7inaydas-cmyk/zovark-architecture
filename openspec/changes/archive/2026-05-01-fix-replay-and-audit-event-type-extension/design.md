## Context

Cleaning up the deferred follow-up from `fix-vault-authorization-audit`: the new audit event type `vault_authorization_use_rejected` exists in the `vault-authorization` spec but is not yet in `replay-and-audit`'s closed event-type enum. This is documentation-only.

## Goals / Non-Goals

**Goals:**

- Add `vault_authorization_use_rejected` to the `replay-and-audit` event-type enum.
- Update the architecture object document for `replay-and-audit`.

**Non-Goals:**

- Any other event-type additions.
- Any change to canonicalization, root signature, or other audit semantics.

## Decisions

### What changes

The fixed event-type enum gains exactly one value: `vault_authorization_use_rejected`. The closed-enum invariant remains; the spec already requires a `MODIFIED Requirements` change to extend it (which is what this change is).

The corresponding scenario in `replay-and-audit/spec.md` already says "an audit entry with `event_type: random_string` is invalid" — that scenario remains true.

## Risks / Trade-offs

- **Risk:** none. This is the smallest possible spec change.
- **Trade-off:** none.

## Migration Plan

1. Modify `replay-and-audit/spec.md` Requirement "Audit chain entry SHALL have canonical fields and ordering" to include the new event-type value.
2. Update `architecture/objects/replay-and-audit.md` mirror.
3. Archive.

**Rollback:** revert.

## Open Questions

(none)
