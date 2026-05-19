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

1. **Customer offboarding** (contract end). 30-day window from contract-end. All customer data — alerts, evidence, replay records, vault material, audit log entries, telemetry buffers — destroyed via cryptographic key shred (per-tenant DEK destroyed per ADR-0034; encrypted blobs become unreadable).
2. **Article 17 deletion request** (in-contract). 30-day window from verified request. Specific data subject's records destroyed. Customer (data controller) verifies the request; Zovark (data processor) executes against a documented DSAR API.

### Cryptographic deletion mechanism

Each tenant has a top-level DEK held in HSM-backed key storage. Customer data at rest is encrypted with subordinate keys derived from the tenant DEK. To "delete" customer data at scale, we destroy the tenant DEK; encrypted blobs are mathematically unrecoverable. This is the **only** customer-data deletion path in SaaS topology. We do not depend on per-blob deletion completing on every replica; we depend on DEK destruction propagating, which is small and atomic.

For per-data-subject Article 17 deletion (smaller scope), the affected subject's records are re-encrypted under a new DEK that excludes the deleted records. The old DEK is destroyed. Operationally heavier but allows targeted deletion without affecting the rest of the tenant's data.

### Audit-chain interaction

INV-020 says audit-event erasure can occur only via the legal-hold-honoring retention process. We satisfy by:
- Audit-chain entries encrypted with a separate audit DEK (`audit-DEK`), not the tenant data DEK.
- On customer offboarding: audit DEK retained for the regulatory minimum (default 7 years for SOC 2 / ISO 27001 evidence; configurable per customer contract up to 10 years [policy-commitment:audit-owner,annual-review]).
- After regulatory minimum: audit DEK destroyed; audit chain becomes unreadable; chain integrity records (head hash, sequence numbers) retained as anonymized evidence forever.
- Article 17 requests do **not** delete audit chain entries (audit logs are explicitly excluded from Article 17 in most regulator guidance because they are required for regulatory compliance — lawful basis under Article 17(3)(b)).

### Legal hold

When Zovark or a customer is served a legal preservation notice, deletion is **paused** for affected scope. Mechanism:
- `ops/legal-hold-ledger.jsonl` (append-only, hash-chained) records every legal-hold event: scope, reason, served-by, served-at, expected-duration, lifted-at.
- An active legal-hold entry blocks the offboarding-deletion job and the Article-17-deletion job for matching scope.
- Operations on a held tenant produce an audit event recording the hold.
- Lifting a hold requires two-party authorization: legal-counsel + security-officer.

### DSAR API

Customers can issue Article-17 / Article-15 (subject access) requests via:
- `zovark dsar request --subject {subject_id} --type {article15|article17}` (CLI; logged to audit chain).
- `zvadmin → DSAR` UI (Web; same audit logging).
- A documented support channel for paper requests (1-business-day acknowledgment SLA per ADR-0050).

Article 15 requests produce a tarball of subject's data in OCSF + JSON formats within 30 days. [policy-commitment:audit-owner,quarterly-review]
Article 17 requests produce a deletion-confirmation receipt (signed, hash-chained) within 30 days; actual cryptographic deletion performed in that window.

### Stop conditions

- Any audit chain entry mutated or missing without a matching legal-hold-ledger entry → P0 incident, full audit-chain integrity check, customer notification within 24 hours. [policy-commitment:audit-owner,incident-review]
- Any tenant DEK destroyed before its 30-day offboarding window completes → P0 incident, executive escalation.

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
- Legal hold becomes real-time operational concern; ledger must be highly available.

## Alternatives Considered

- *Per-blob deletion across all replicas*: rejected; impossible to verify completeness across cross-region replication and PITR-snapshots.
- *Retain customer data forever (anonymized)*: rejected; Article 17 violation; defeats deletion right.
- *No legal hold in v1.0*: rejected; first enterprise customer asks; cannot be improvised.
- *Audit-chain retention < regulatory minimum*: rejected; SOC 2 evidence requires it.
