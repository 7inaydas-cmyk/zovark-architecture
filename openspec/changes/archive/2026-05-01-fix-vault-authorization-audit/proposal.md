## Why

Finalization-checklist criterion #9 (Vault / authorization) is currently UNAUDITED on the rc1 scorecard. The patch tree references `INV-019` ("Every vault access requires per-action authorization; no broad credentials") established by ADR-0028 (vault threat model, in baseline ADR set 0001-0037 not present here). DD-blocker `M3-DEPENDENCY-002` flags missing IPC schemas (`vault_request`, `vault_response`, `vault_audit_envelope`) needed before the EDR adapter can use vault. The `edr-handoff` capability already references `authorization_record_ref` to a `vault-authorization` record without that capability being defined.

This change does not implement vault, does not produce IPC schemas, and does not audit baseline ADRs whose files are not in this repository. It produces a spec-level definition of the vault authorization record and a documented audit posture that lets rc2 move criterion #9 from UNAUDITED to PASS-with-tracked-gaps. It explicitly hands off the missing IPC schemas as M3 deliverables with acceptance criteria, mirroring what `fix-claim-provenance` did for the M0 claim-provenance script.

## What Changes

- Land `architecture/objects/vault-authorization.md` defining the vault authorization record at the spec level: required fields (action, tenant, target, expiry, nonce, policy reference, approval reference when approval-required, signing tag), authorization issuance and verification rules, replay protection, compromise-response rules, and the relationship to EDR handoff and audit chain.
- Capture as `openspec/specs/vault-authorization/spec.md`.
- Document the audit posture: which baseline ADRs (0028, 0034, etc.) need to be cross-link verified post-apply (deferred to `fix-adr-cross-link-verification` rc2 change). What scope of vault behavior the architecture commits to without naming an implementation.
- Document the M3 IPC schemas (`vault_request.schema.json`, `vault_response.schema.json`, `vault_audit_envelope.schema.json`) as deliverables with acceptance criteria, drawn from the patch's `M3-DEPENDENCY-002` blocker.
- **Out of scope:** implementing vault; implementing IPC schemas; auditing baseline ADRs (file content not in this repo); choosing HSM vs. cloud KMS; per-tenant key rotation algorithm details (those are ADR-0034).

## Capabilities

### New Capabilities

- `vault-authorization`: Spec for the vault authorization record (the object referenced by `edr-handoff.authorization_record_ref`), authorization issuance/verification rules, replay protection, and compromise-response semantics. Defines what the record contains, how it binds action+tenant+target+policy+approval, what makes it valid, and what makes it invalid.

### Modified Capabilities

(none)

## Impact

- **Documents added:** `architecture/objects/vault-authorization.md`, `openspec/specs/vault-authorization/spec.md`.
- **Documents touched:** none.
- **Code:** none.
- **Linked items:**
  - Drives finalization-checklist criterion #9 from UNAUDITED → PASS-with-tracked-gaps in rc2 scorecard.
  - References baseline ADR-0028 and ADR-0034 (out-of-tree) as referenced sources; cross-link audit deferred to `fix-adr-cross-link-verification`.
  - Captures `M3-DEPENDENCY-002` IPC schemas as named M3 deliverables with acceptance criteria.
