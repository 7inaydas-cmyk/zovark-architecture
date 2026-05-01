## 1. Land the architecture object document

- [ ] 1.1 Write `architecture/objects/replay-and-audit.md` with: introduction (link to wedge + tape + handoff), replay state object spec, audit chain entry spec, canonicalization rules, concurrent-insert behavior, root signature semantics, unsigned-tail handling, DR restore-gap semantics, ARCH-P2-002 hook.
- [ ] 1.2 Verify the doc enumerates the audit event_type set and the DR restore event payload fields.

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-replay-and-audit-semantics`.
- [ ] 2.2 Run `openspec archive fix-replay-and-audit-semantics --yes`.

## 3. Commit and push

- [ ] 3.1 Stage `architecture/objects/replay-and-audit.md`, the change archive, and the new spec.
- [ ] 3.2 Commit: "Define replay state and audit chain spec".
- [ ] 3.3 Push.
