# ADR-0048: Healer Runtime Defense-in-Depth

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** ops  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

INV-014 says healer is read-only and prohibits DB mutation outside `system_health`, EDR API access, service control, configuration mod, bundle ops, replay record mod, and tenant data access. ADR-0022 enforces this with static AST/import checks. Static checks are necessary but insufficient: indirect imports through `application/`, dynamic imports, reflection, shelling out, and HTTP calls to internal mutating endpoints can bypass static analysis. INV-014 must be enforced by **both** static analysis AND runtime permission isolation.

## Decision

Healer runs under a hardened runtime profile. Five layers, outermost to innermost:

### Layer 1: Static enforcement (existing, ADR-0022)

- AST check: no import from EDR adapter modules, vault modules, tool catalog modules, ingest write paths, audit-chain write paths, replay-record write paths.
- AST check: no dynamic import (`importlib.import_module`, `__import__`).
- AST check: no `subprocess`, `os.system`, `os.exec*`, `os.popen`.
- AST check: no `requests.post/put/delete/patch` calls outside healer-internal allowlist.

These pass at v3.2.4.3 (already shipped). Necessary, not sufficient.

### Layer 2: Process/user isolation

- Healer runs as Linux user `healer`, group `healer`, uid/gid 5001.
- The `healer` user owns no files outside `/var/lib/zovark/healer/`.
- All other Zovark application files are mode 0640 with group `zovark`; the `healer` user is **not** in the `zovark` group.
- Read-only filesystem mount for `/usr/lib/zovark` (the application code).

### Layer 3: Database role

- Healer connects to PostgreSQL as role `zovark_healer_ro`.
- Grants: `SELECT` on `system_health.*` only. No grants on any other schema. No `INSERT/UPDATE/DELETE` anywhere.
- Grant lattice enforced by fixture test in `tests/db/healer-grants.test.sql`.
- Connection string for healer is in healer process environment only; not in any other process's environment.

### Layer 4: Network egress

- Healer container has no outbound network access by default.
- Allowlist: only the healer-internal status endpoint (used to surface findings to zvadmin) and the audit chain read endpoint.
- Denylist (enforced at container network policy): all EDR vendor APIs, all customer SIEM/SOAR endpoints, all LLM provider endpoints, all internal Zovark mutating endpoints.
- Network policy in `ops/k8s/healer-network-policy.yaml` (lands M3); enforced by Cilium / Calico.

### Layer 5: No mounted credentials

- Healer container has no EDR vendor credentials mounted.
- No Zovark signing keys mounted.
- No vault access tokens mounted.
- No customer API keys mounted.
- Container environment audited at startup; any unexpected `*_KEY|*_TOKEN|*_SECRET|*_PASSWORD` env var triggers startup-fail.

### Vault IPC contract (closes issue #32)

Vault IPC pinned in `architecture/blueprint/schemas/vault_request.schema.json` and `vault_response.schema.json` (lands at M3 alongside production ingest auth, not M1; tracked as DD_BLOCKER M3-DEPENDENCY-002 in v3.2.4.3). At M3 they specify:
- Request envelope: `tenant_id`, `action`, `target`, `actor`, `nonce`, `timestamp_logical`, `signature_over_canonical_request`.
- Response envelope: `request_id`, `decision`, `evidence_id`, `expires_at`, `signature_over_canonical_response`.
- Authn: mTLS with per-process cert; healer's cert has no signing-vault grants.
- Authz: per-action allowlist; `healer` cert has zero entries.

Healer cannot pass the vault's authz check at any level even if it could reach the vault (which it cannot at network level). Defense in depth.

### Test fixtures (M3)

`tests/integration/healer-runtime-isolation/` runs a healer with a synthetic compromise (an attacker-controlled module loaded into the healer process) and verifies:
- Compromised module cannot read EDR credentials (no env, no file).
- Compromised module cannot write to audit chain (no DB grant).
- Compromised module cannot reach EDR vendor APIs (network deny).
- Compromised module cannot mutate `system_health` (no INSERT/UPDATE/DELETE grant on any schema).
- Compromised module's findings to zvadmin still flow through audit chain so they appear in customer's audit log.

## Consequences

- Operational complexity: healer becomes its own deployment unit (Pod, Service, NetworkPolicy in Kubernetes). Adds CI/CD lanes.
- Bug class eliminated: an attacker compromising the healer process cannot use it to mutate state because runtime layers prevent it even if static layers were bypassed.
- Onboarding: new engineers must understand healer's restricted environment; "why doesn't this work in healer?" becomes a FAQ. Documentation lands M3.

## Alternatives Considered

- *Static enforcement only*: rejected; the strategic reviewer's exact concern.
- *Healer in-process with the rest of the application*: rejected; cannot isolate at runtime.
- *Healer in separate VM rather than container*: rejected; operationally heavier without proportional security gain.
- *Healer can write to system_health (small exception)*: rejected; INV-014 explicitly forbids it. Healer findings flow via the audit chain (read access to publish through a write-only edge that flows through the audit-chain ingester, not the DB; ingester is a separate process the healer talks to via the vault-IPC pattern).
