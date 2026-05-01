## 1. Land the architecture object document

- [ ] 1.1 Write `architecture/objects/vault-authorization.md` with: introduction (link to INV-019, ADR-0028, ADR-0042), authorization record fields, verification rules, replay protection, compromise response, audit linkage, M3 IPC schema deliverable list with acceptance criteria, cross-link audit hand-off note.
- [ ] 1.2 Verify the doc names the three M3 IPC schemas verbatim (`vault_request.schema.json`, `vault_response.schema.json`, `vault_audit_envelope.schema.json`).

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-vault-authorization-audit`.
- [ ] 2.2 Run `openspec archive fix-vault-authorization-audit --yes`.

## 3. Note follow-up for replay-and-audit

- [ ] 3.1 Document in `architecture/review/decision-log.md` (TR-004) that `vault_authorization_use_rejected` event-type addition to `replay-and-audit` is a tracked rc2-verification follow-up.

## 4. Commit and push

- [ ] 4.1 Stage `architecture/objects/vault-authorization.md`, the change archive, the new spec, and the decision-log entry.
- [ ] 4.2 Commit: "Define vault authorization spec and M3 IPC schema deliverables".
- [ ] 4.3 Push.
