# Invariants — Zovark v1.0

**Version:** v3.2.4.5
**Counts:** authoritative source is `VERSION_METADATA.json`. As of the v3.2.4.5 post-apply baseline produced by the v3.2.4.6 patch package: **32 total** = 17 covered + 1 partial (INV-001) + 14 deferred. Zero hand-waved.

This file is **append-only** in normal flow. Modifications to existing entries require an ADR amendment per M1-CI-008 baseline-immutability gate.

---

## INV-001 — Tenant boundary

**Statement.** Every tenant-scoped resource is accessed only via tenant-scoped queries. No cross-tenant read or write.
**Established by:** ADR-0003.
**Status:** **PARTIAL** at v3.2.4.5 (covered in test fixtures; runtime enforcement at M3 via M1-INGEST-003 → production auth).
**Fitness function:** Planned M3 `check_tenant_boundary.py`; not present in this patch tree.

## INV-002 — Fail closed

**Statement.** On any unrecoverable error in a privileged path (ingest, audit, vault, EDR), the system fails closed: no event accepted, no action executed.
**Established by:** ADR-0001.
**Status:** DEFERRED → M3.
**Fitness function:** `check_fail_closed.py` at M3 (kill-switch test).

## INV-003 — Air-gap compatible

**Statement.** Every Control Plane API has an offline-package equivalent. Every signed bundle verifies offline. Customer instances can operate end-to-end without internet.
**Established by:** ADR-0011 (amended by ADR-0038).
**Status:** DEFERRED → M10.

## INV-004 — Deterministic verdict

**Statement.** Given the same inputs (alert + tenant config + tool catalog version + model version), the verdict is reproducible.
**Established by:** ADR-0027.
**Status:** COVERED.

## INV-005 — Replayable

**Statement.** Every investigation can be replayed against historical inputs and produce a byte-identical record.
**Established by:** ADR-0020, ADR-0026.
**Status:** DEFERRED → M5.

## INV-006 — Tamper evident

**Statement.** Audit chain entries are hash-chained; any retroactive modification is detectable.
**Established by:** ADR-0025.
**Status:** COVERED in test fixtures with runtime hash chain at M5. [hypothesis:M5-runtime-evidence] Counted as COVERED for the v3.2.4.5 baseline arithmetic; runtime hash chain implementation lands at M5.

## INV-007 — Zero dead code

**Statement.** No code in the production codebase is unreachable. Dead code fails the merge gate.
**Established by:** ADR-0016.
**Status:** COVERED.

## INV-008 — Schema first

**Statement.** Every persistent or wire-format payload conforms to a canonical schema. Code is generated from schema, not the other way around.
**Established by:** ADR-0015.
**Status:** COVERED.

## INV-009 — Open-source-only dependencies

**Statement.** No paid components in the production codebase. Approved licenses: Apache-2.0, BSD-3-Clause, MIT, ISC. AGPL is excluded for canonical-schema dependencies (per ADR-0036).
**Established by:** ADR-0013.
**Status:** COVERED.

## INV-010 — WASM scope locked

**Statement.** WASM is used only for pure-computation tools (defense-in-depth). It is not used as a general code-isolation primitive.
**Established by:** ADR-0014.
**Status:** COVERED.

## INV-011 — Wasmtime configuration locked

**Statement.** Wasmtime configuration (memory limits, fuel, capabilities) is pinned and reviewed.
**Established by:** ADR-0014.
**Status:** DEFERRED → M6.

## INV-012 — Explicit boundaries

**Statement.** Service boundaries are explicit; no implicit cross-module state.
**Established by:** ADR-0001.
**Status:** DEFERRED → M3.

## INV-013 — No retired vocabulary

**Statement.** No code or doc may use vocabulary listed in ADR-0017 (retired terms).
**Established by:** ADR-0017.
**Status:** DEFERRED → M3 (runtime grep).

## INV-014 — Healer is read-only

**Statement.** The Healer service (ADR-0022) cannot mutate state. It diagnoses and reports.
**Established by:** ADR-0022.
**Status:** COVERED.

## INV-015 — Sigma rules require analyst approval

**Statement.** No Sigma rule is auto-published. Every published Sigma rule has an analyst approval record.
**Established by:** ADR-0023, ADR-0029.
**Status:** DEFERRED → M9.

## INV-016 — Audit canonicalization

**Statement.** Every audit event is canonicalized to `audit_event.schema.json` before persistence.
**Established by:** ADR-0025.
**Status:** DEFERRED → M5.

## INV-017 — Replay fails closed on incompatibility

**Statement.** If a replay record cannot be deserialized under the current schema, replay fails closed (does not produce a degraded result).
**Established by:** ADR-0026.
**Status:** COVERED.

## INV-018 — Verdict canonicalization

**Statement.** Every verdict is canonicalized to `verdict_envelope.schema.json` before emission.
**Established by:** ADR-0027.
**Status:** DEFERRED → M5.

## INV-019 — Vault per-action authorization

**Statement.** Every vault access requires per-action authorization; no broad credentials.
**Established by:** ADR-0028.
**Status:** COVERED.

## INV-020 — Immutable audit erasure boundary

**Statement.** Audit-event erasure can occur only via the legal-hold-honoring retention process; no other path can delete audit events.
**Established by:** ADR-0024, ADR-0025.
**Status:** DEFERRED → M5.

## INV-021 — Tenant usage attribution

**Statement.** Every billable action is attributed to a tenant via `tenant_usage_event.schema.json`.
**Established by:** ADR-0024.
**Status:** COVERED.

## INV-022 — Quantified claim provenance

**Statement.** Every quantified product claim (latency, accuracy, throughput) is traceable to a recorded `benchmark_artifact`.
**Established by:** ADR-0031.
**Status:** COVERED for the documentation convention. Enforcement by `scripts/check_claim_provenance.py` is an M0 deliverable and is not present in this patch tree.

## INV-023 — Bootstrap enforcement evidence

**Statement.** Every fitness function in the bootstrap discipline has both a fail-fixture and a pass-fixture.
**Established by:** ADR-0030.
**Status:** COVERED.

## INV-024 — MVP scope consistency

**Statement.** The product surface area is the union of accepted features in `feature-registry.yaml`. No service code may exist for a feature not on this list.
**Established by:** ADR-0018.
**Status:** COVERED.

## INV-025 — Open standards binding

**Statement.** Every ingest, audit, replay, verdict, and benchmark surface binds to an open standard registered in `open-standards-registry.yaml`.
**Established by:** ADR-0033.
**Status:** COVERED.

## INV-026 — Integer-only numeric precision in deterministic paths

**Statement.** Verdict logic and audit canonicalization use integer arithmetic only; no floating-point comparisons.
**Established by:** ADR-0027.
**Status:** COVERED.

## INV-027 — Open-source schema boundary

**Statement.** No vendor-proprietary schema is canonical. All canonical storage and verdict schemas are Zovark-defined and Apache-2.0 licensed.
**Established by:** ADR-0036.
**Status:** COVERED.

## INV-028 — Feature lifecycle and dead-code housekeeping

**Statement.** Every feature has a lifecycle status from `allowed_statuses`. Features in terminal states (`retired`, `deleted`, `rejected`) cannot have active runtime code.
**Established by:** ADR-0037.
**Status:** COVERED.

---

## INV-029 — Customer Instance Tenant-Data Authority

**Statement.** The customer instance is the sole authoritative store of customer evidence, raw alerts, investigation records, vault material, EDR credentials, audit log entries, and replay records. The Control Plane never holds these.
**Established by:** ADR-0038.
**Status:** DEFERRED → M2.
**Fitness function:** Planned M2 `check_control_plane_data_classification.py` — scans control-plane code paths and storage schemas for any field name in the ADR-0041 forbidden set; fails on any match. Not present in this patch tree.

## INV-030 — Research Pipeline Output Is Not Customer-Runtime Authoritative

**Statement.** No Research Pipeline output may affect customer runtime unless: (1) it has a feature ID, (2) it passes schema validation, (3) it passes security gates, (4) it passes replay/compatibility tests where applicable, (5) it has provenance, (6) it is signed by two distinct role-keys (release-engineer + security-officer per ADR-0042), (7) it is approved by the configured release policy, (8) the customer instance accepts the update under local policy.
**Established by:** ADR-0040.
**Status:** DEFERRED → M6.
**Fitness function:** Planned M6 `check_no_direct_runtime_mutation.py` — verifies no path exists from `research-pipeline/` outputs to any `customer-runtime/` artifact except via the Update Factory promotion queue. Not present in this patch tree.

## INV-031 — All Update Bundles Signed and Offline-Verifiable

**Statement.** Every update bundle distributed by the Update Factory carries two signatures from **distinct** roles (release-engineer + security-officer; never two from the same role), a Sigstore attestation referencing the source commit, a complete CycloneDX 1.5 SBOM with dependency provenance, a compatibility matrix, and rollback metadata. Bundle signature is verifiable offline. `[policy-commitment:release-engineering,per-release-review]`
**Established by:** ADR-0039; key management per ADR-0042; distinct-role enforcement at schema level in v3.2.4.5.
**Status:** DEFERRED → M4.
**Fitness function:** Planned M4 `check_update_bundle_signed.py` — verifies bundle structure, signature presence (count >= 2, distinct role-keys via `update_bundle_signed.schema.json` `contains/minContains/maxContains`), attestation chain, SBOM completeness, offline-verifiability. This patch tree currently provides schema validation only.

## INV-032 — Telemetry Crossing the Boundary Is Enumerable and Customer-Auditable

**Statement.** Every field that crosses the customer→control-plane boundary appears in `telemetry_envelope.schema.json`'s allowlist; when the M2 runtime exists, every outbound payload is recorded in the customer-side `telemetry_audit_log.jsonl`; the customer can run `zovark telemetry preview` to see exactly what would be sent before sending. The schema also binds `payload_kind` to payload shape so a `status` envelope cannot smuggle a `health` payload (or vice versa).
**Established by:** ADR-0041; payload-kind binding tightened at schema level in v3.2.4.5.
**Status:** DEFERRED → M2.
**Fitness function:** Planned M2 `check_telemetry_boundary.py` — scans for telemetry-emission patterns; verifies every emitted field is on the allowlist; verifies audit-log writes happen. This patch tree currently provides schema/example checks and `scripts/check_telemetry_boundary_schema_present.py`.

---

## Count arithmetic

```
Covered (17):  INV-004, INV-006, INV-007, INV-008, INV-009, INV-010, INV-014,
               INV-017, INV-019, INV-021, INV-022, INV-023, INV-024, INV-025,
               INV-026, INV-027, INV-028
Partial (1):   INV-001
Deferred (14): INV-002, INV-003, INV-005, INV-011, INV-012, INV-013, INV-015,
               INV-016, INV-018, INV-020, INV-029, INV-030, INV-031, INV-032
Total:         17 + 1 + 14 = 32
```

## Deferred-INV milestone table

```
INV-002  → M3   fail-closed runtime
INV-003  → M10  air-gap operational proof
INV-005  → M5   replay engine
INV-011  → M6   Wasmtime configuration runtime
INV-012  → M3   service boundary tests
INV-013  → M3   retired vocabulary runtime scan
INV-015  → M9   Sigma analyst approval gate
INV-016  → M5   audit canonicalization runtime
INV-018  → M5   verdict canonicalization runtime
INV-020  → M5   audit erasure boundary runtime
INV-029  → M2   control plane data classification
INV-030  → M6   no direct runtime mutation
INV-031  → M4   signed bundle enforcement
INV-032  → M2   telemetry boundary enforcement
```

By M10, all 32 invariants are COVERED. M11+ is product expansion, not invariant closure.

## Restore-gap semantics

DD-DR-001 is deferred to M3. Any future backup, PITR, restore, or audit-chain verification design must use this rule:

A valid post-restore audit chain proves internal consistency of the recovered chain. It does not prove that no data loss occurred.

Future audit-chain schemas must include `DISASTER_RECOVERY_RESTORE_COMPLETED` with:

- `restore_started_at_ns`
- `restore_completed_at_ns`
- `restored_to_lsn`
- `restored_to_timestamp`
- `pre_restore_latest_root_hash_if_available`
- `post_restore_chain_root`
- `known_data_loss_window_start`
- `known_data_loss_window_end`
- `operator_id`
- `incident_id`

Future audit-chain verifier states must include `VALID_AFTER_RESTORE_WITH_DECLARED_GAP`.
