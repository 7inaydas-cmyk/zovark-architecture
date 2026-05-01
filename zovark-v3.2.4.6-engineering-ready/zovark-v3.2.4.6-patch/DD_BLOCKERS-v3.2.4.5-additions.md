# DD_BLOCKERS additions in v3.2.4.5

These items append to the existing DD_BLOCKERS.md in the v3.2.3.5 baseline.
None are M1-blocking; all are tracked with milestone deadlines. The apply
script does NOT auto-edit DD_BLOCKERS.md — append the block below manually
into the existing file, or via `scripts/apply_v3_2_4_6.py --apply-fragments`
once the team has reviewed.

## M1-DECISION-001 — ADR-0043 founder sign-off (NEW IN v3.2.4.5)

**Established by:** v3.2.4.5.
**Status:** open; tracked.
**Severity:** decision-blocking for ADR-0043 acceptance.
**Deadline:** before tag `v3.2.4.5-bootstrap-baseline`.

### Context

The original Zovark evaluation scope said: "closed-source commercial. No open-source release planned."

ADR-0043 (introduced in v3.2.4.2, refined in v3.2.4.5) proposes a different posture:

- **Tier A — Apache-2.0 open-source** for canonical schemas, standards registry, mapping definitions, bootstrap-acceptance fixtures, ADRs/invariants, verifier scripts, the `zovark update verify` CLI source.
- **Tier B — source-available with product** for the customer-runtime code (read/audit/modify-for-self-hosted-use; no fork-and-redistribute).
- **Tier C — closed-source hosted by Zovark** for control-plane production code, update factory infrastructure, research-pipeline runners, internal tooling.
- **Critical rule:** no closed-source code runs in a customer environment.

This is materially different from the original scope. The schemas were already on a path to public per ADR-0010 (accepted in earlier baselines), but the runtime-code licensing posture and public-GitHub-presence decisions are new.

### Decision required

Founder must explicitly accept, amend, or reject ADR-0043. Acceptable outcomes:

1. **Accept as written.** ADR-0043 status moves from `PROPOSED-STRATEGIC-PIVOT` to `ACCEPTED`. Tier A goes public on the M1 tag. Tier B prep work begins for M2-M5.
2. **Accept with amendments.** Founder narrows or expands scope; ADR-0043 is amended; a new revision is reviewed.
3. **Reject.** ADR-0043 is removed. Zovark ships closed-source binaries with attestations. Schemas remain Apache-2.0 per ADR-0010 (unaffected). The `zovark update verify` CLI may also remain Apache-2.0 if that decision is preserved.

Until decision: M1 work proceeds. The schemas were never going to be closed-source per ADR-0010 anyway. The runtime-code-licensing decision blocks only the public GitHub launch, not internal development.

### Owner

Founder, with input from architect-lead and security-officer.

---

## M3-DEPENDENCY-002 — Vault IPC schemas

**Established by:** architecture review.
**Status:** open; tracked.
**Severity:** medium (not M1-blocking).
**Milestone due:** M3 (production ingest auth + tenant boundary; vault IPC becomes runtime-relevant when the EDR adapter starts requiring per-action vault calls).

### Context

ADR-0028 specifies the vault threat model and ADR-0034 specifies tenant DEK rotation. INV-019 enforces vault per-action authorization. But there is no canonical schema for the IPC envelope between callers (ingest, EDR adapter, audit) and the vault service. Without a schema:

- the per-action authorization payload format is implementation-defined
- audit-log entries for vault accesses cannot be schema-validated
- the vault is harder to fuzz and threat-model
- a future replacement vault would have no contract to match

### What needs to land at M3

- `architecture/blueprint/schemas/vault_request.schema.json`
- `architecture/blueprint/schemas/vault_response.schema.json`
- `architecture/blueprint/schemas/vault_audit_envelope.schema.json`

Each carries the metadata triple. Each has pass/fail fixtures. Each is referenced by `check_vault_ipc_contract.py` (M3 fitness function).

### Why this is M3, not M1

M1's mandate is enforcement-first + first ingest slice. The vault is not on the M1 critical path because the M1 ingest slice does not require credential resolution (synthetic Wazuh fixtures are tenant-pseudonymized). M2 doesn't need it either (control plane holds no credentials). M3 production ingest auth + tenant boundary work is when the vault IPC contract becomes runtime-blocking; landing the schemas with that work keeps the schemas grounded in real consumers.

### Cross-references

- ADR-0028 (vault threat model)
- ADR-0034 (DEK rotation)
- INV-019 (vault per-action authorization, COVERED)
- M3-DEPENDENCY-001 (customer onboarding / first-install trust bootstrap; related because both involve secret material)

### Owner

Architect + security-officer.
