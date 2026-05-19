# ADR-0045: Customer Offboarding, GDPR Article 17, and Legal Hold

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** audit-owner  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

The v3.2.4.2 architecture has no documented customer-offboarding workflow. INV-020 ("immutable audit erasure boundary") is deferred to M5 with no operational specification. GDPR Article 17 (right to erasure) exposure is real for any customer with EU data subjects. The first regulated-buyer DPA negotiation surfaces this; cannot be improvised under contract pressure.

## Decision

### The two paths

1. **Customer offboarding** (contract end). 30-day target window from contract-end for customer-controlled data and tenant-scoped operational data that is not legally or regulatorily retained audit-chain material — alerts, evidence, replay records, vault material, telemetry buffers, and non-retained identity-resolution mappings. Deletion is intended to use cryptographic key shred (per-tenant DEK destroyed per ADR-0034; encrypted blobs become unreadable) once the offboarding jobs and key-ledger workflow exist. Audit-chain entries, audit hashes, legal-hold records, and required retention metadata follow the audit-retention rules in "Audit-chain interaction" below.
2. **Article 17 deletion request** (in-contract). 30-day target window from verified request. Specific data subject's records are targeted for destruction when they are not required audit-chain material. Customer (data controller) verifies the request; Zovark (data processor) will execute against the planned DSAR API once implemented.

### Cryptographic deletion mechanism

The planned SaaS deletion mechanism uses a top-level tenant DEK held in HSM-backed key storage, with customer data at rest encrypted under subordinate keys derived from that tenant DEK. At scale, customer-data deletion is intended to destroy the tenant DEK so encrypted blobs become unreadable. This is a future design target pending HSM procurement, key-ledger implementation, offboarding deletion jobs, and DSAR API implementation; it is not current runtime behavior or a customer/legal compliance claim. INV-034 is the binding invariant for customer-data deletion via DEK destruction, and ADR-0042 records the HSM/key-management design constraints.

For per-data-subject Article 17 deletion (smaller scope), the target design re-encrypts affected subject records under a new DEK that excludes the deleted records, then destroys the old DEK. This remains implementation-pending with the DSAR API and offboarding job.

### Audit-chain interaction

INV-020 says audit-event erasure can occur only via the legal-hold-honoring retention process. We satisfy by:
- Audit-chain entries encrypted with a separate audit DEK (`audit-DEK`), not the tenant data DEK.
- On customer offboarding: audit DEK retained for the regulatory minimum (default 7 years for SOC 2 / ISO 27001 evidence; configurable per customer contract up to 10 years [policy-commitment:audit-owner,annual-review]).
- After regulatory minimum: audit DEK destroyed; audit chain becomes unreadable; chain integrity records (head hash, sequence numbers) retained as anonymized evidence forever.
- Article 17 requests do **not** delete audit chain entries (audit logs are explicitly excluded from Article 17 in most regulator guidance because they are required for regulatory compliance — lawful basis under Article 17(3)(b)).

### Legal hold

When Zovark or a customer is served a legal preservation notice, deletion is **paused** for affected scope. Planned mechanism:
- `ops/legal-hold-ledger.jsonl` (append-only, hash-chained) will record every legal-hold event: scope, reason, served-by, served-at, expected-duration, lifted-at.
- An active legal-hold entry will block the offboarding-deletion job and the Article-17-deletion job for matching scope.
- Operations on a held tenant will produce an audit event recording the hold.
- Lifting a hold will require two-party authorization: legal-counsel + security-officer.

### DSAR API

The DSAR surface is a planned implementation target, not current runtime behavior. Once the DSAR API, offboarding job, authorization checks, audit logging, and validation are implemented, customers should be able to issue Article-17 / Article-15 requests via:
- `zovark dsar request --subject {subject_id} --type {article15|article17}` (planned CLI; logged to audit chain).
- `zvadmin → DSAR` UI (planned Web surface; same audit logging).
- A documented support channel for paper requests once the support workflow exists.

Article 15 export within 30 days is a design target pending DSAR API and export validation. Article 17 signed deletion receipts within 30 days are likewise a design target pending HSM/key-ledger flow, offboarding deletion jobs, and validation. INV-034 remains the binding invariant for customer-data deletion via DEK destruction.

### Stop conditions

- Any audit chain entry mutated or missing without a matching legal-hold-ledger entry is intended to trigger P0 incident handling, a full audit-chain integrity check, and customer notification after incident/customer-notification workflow exists; this is not a current customer notification commitment. [policy-commitment:audit-owner,incident-review]
- Any tenant DEK destroyed before its 30-day offboarding window completes is intended to trigger P0 incident handling and executive escalation after offboarding jobs and incident workflow exist.

### Test fixtures

`tests/integration/offboarding-deletion-drill/` runs nightly in M5+:
- Creates synthetic tenant.
- Populates with synthetic data.
- Runs offboarding flow.
- Verifies: data unreadable post-DEK-destruction; audit chain still intact; legal-hold integrations work; Article-17 path works.

## Consequences

- Audit-chain encryption decision means audit logs survive customer offboarding for the regulatory window; this is a customer-contract negotiation point and must be communicated upfront.
- Cryptographic deletion is faster than per-blob deletion but requires robust DEK management (ADR-0034 + ADR-0042).
- DSAR API adds a new customer-facing surface that must be authn'd, audited, and rate-limited.
- Legal hold will become a real-time operational concern; ledger must be highly available once implemented.

## Alternatives Considered

- *Per-blob deletion across all replicas*: rejected; impossible to verify completeness across cross-region replication and PITR-snapshots.
- *Retain customer data forever (anonymized)*: rejected; Article 17 violation; defeats deletion right.
- *No legal hold in v1.0*: rejected; first enterprise customer asks; cannot be improvised.
- *Audit-chain retention < regulatory minimum*: rejected; SOC 2 evidence requires it.
