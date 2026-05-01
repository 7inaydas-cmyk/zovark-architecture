## 1. Land the architecture object document

- [ ] 1.1 Write `architecture/objects/edr-handoff.md` with: introduction (link to wedge + investigation tape), the 14 fields (10 canonical + 4 extras), approval-mode rules, idempotency semantics, rollback structure, linkage table to other capabilities.
- [ ] 1.2 Verify the doc enumerates the action_type and target.kind enums.

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-edr-handoff-schema` and confirm pass.
- [ ] 2.2 Run `openspec archive fix-edr-handoff-schema --yes` to promote to `openspec/specs/edr-handoff/spec.md`.

## 3. Commit and push

- [ ] 3.1 Stage `architecture/objects/edr-handoff.md`, the change archive, and the new spec.
- [ ] 3.2 Commit: "Define EDR handoff record spec".
- [ ] 3.3 Push.
