## 1. Land the architecture object document

- [ ] 1.1 Write `architecture/objects/investigation-tape.md` with: introduction (link to wedge), categorized field list, lifecycle states, customer-facing surface, MVP-required vs. post-MVP classification, and forward-references to `edr-handoff`, `replay-and-audit`, and `vault-authorization` capabilities.
- [ ] 1.2 Verify the doc enumerates all 8 field categories (Identity, Raw evidence, Recorded model/tool I/O, Timeline, Findings, Verdict, Handoff, Audit and replay).
- [ ] 1.3 Verify the doc includes the verdict's deterministic enum (`benign`, `suspicious_unconfirmed`, `confirmed_malicious`, `inconclusive_insufficient_evidence`).

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-investigation-tape-schema` and confirm pass.
- [ ] 2.2 Run `openspec archive fix-investigation-tape-schema --yes` to promote to `openspec/specs/investigation-tape/spec.md`.

## 3. Commit and push

- [ ] 3.1 Stage `architecture/objects/investigation-tape.md`, the change archive, and the new spec.
- [ ] 3.2 Commit: "Define investigation tape object spec".
- [ ] 3.3 Push.
