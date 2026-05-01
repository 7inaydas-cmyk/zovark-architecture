## 1. Update the architecture object document

- [ ] 1.1 In `architecture/objects/replay-and-audit.md`, add `vault_authorization_use_rejected` to the event-type enum list.

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-replay-and-audit-event-type-extension`.
- [ ] 2.2 Run `openspec archive fix-replay-and-audit-event-type-extension --yes`.

## 3. Commit and push

- [ ] 3.1 Stage `architecture/objects/replay-and-audit.md` and the change archive.
- [ ] 3.2 Commit: "Extend replay-and-audit event-type enum with vault_authorization_use_rejected".
- [ ] 3.3 Push.
