## Why

The `vault-authorization` capability landed in `fix-vault-authorization-audit` introduces a new audit event type `vault_authorization_use_rejected`. Decision-log TR-004 explicitly tracked this as a deferred follow-up to keep `fix-vault-authorization-audit` scoped to one capability. This change picks up that follow-up: extend `replay-and-audit`'s fixed event-type enum to include the new type so cross-capability references are coherent.

Documentation only. No runtime impact.

## What Changes

- `MODIFIED Requirements` against `replay-and-audit` capability: extend the `event_type` enum on the "Audit chain entry SHALL have canonical fields and ordering" requirement to include `vault_authorization_use_rejected`.
- Update `architecture/objects/replay-and-audit.md` to mirror the spec change.
- **Out of scope:** any other event-type additions; any runtime change.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `replay-and-audit`: extend the fixed `event_type` enum to include `vault_authorization_use_rejected`.

## Impact

- **Documents touched:** `architecture/objects/replay-and-audit.md` — adds the new enum value to the event-type list.
- **Code:** none.
- **Linked items:** closes the deferred follow-up tracked in decision-log TR-004 (`fix-vault-authorization-audit`).
