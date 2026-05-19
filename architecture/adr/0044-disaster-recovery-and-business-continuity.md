# ADR-0044: Disaster Recovery & Business Continuity (SaaS topology)

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** ops  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

The v3.2.4.2 architecture commits to "cloud SaaS first" but has no documented DR posture. ADR-0038 mentions DR in one sentence ("registry data is replicated; loss of the Control Plane DB does not affect customer instances"). Insufficient for Series-B-DD or for the first regulated-buyer questionnaire. RPO, RTO, multi-region failover, point-in-time recovery, and restore-drill cadence must be concrete, measurable, and rehearsed.

## Decision

### Targets (binding customer commitments)

| Subsystem | RPO | RTO | Topology |
|-----------|-----|-----|----------|
| Control Plane registry | ≤5 minutes | ≤4 hours | Multi-AZ synchronous primary + cross-region async replica | [hypothesis:M3-DR-targets]
| Control Plane update catalog | ≤15 minutes | ≤4 hours | Same as registry; bundles in object store with cross-region replication | [hypothesis:M3-DR-targets]
| Update Factory ledger | ≤15 minutes | ≤8 hours | Append-only object store (11-9s durability) + cross-region replication | [hypothesis:M3-DR-targets]
| Research Pipeline corpora | ≤24 hours | ≤24 hours | Daily snapshot; loss recoverable from re-run | [hypothesis:M3-DR-targets]
| Customer Instance (SaaS) | ≤15 minutes | ≤4 hours | Per-tenant; multi-AZ DB primary + read replica; daily PITR snapshot | [hypothesis:M3-DR-targets]
| Customer Instance (Hybrid/air-gap) | Customer-owned | Customer-owned | Reference architecture published; not Zovark-operated |

These are **customer commitments**, not internal SLOs. Marketing and contracts use these numbers without modification.

### Backup mechanisms

- **PostgreSQL primary**: continuous WAL streaming to a hot standby in a second AZ within the same region (synchronous_commit=remote_apply for the registry; remote_write for customer-instance per-tenant DBs to keep customer write latency acceptable).
- **PITR**: daily base backups + 7-day WAL retention. Tested restore from PITR runs **monthly** in a sandbox region; restore success recorded in `ops/dr-drill-ledger.jsonl` (append-only, hash-chained).
- **Cross-region async replica**: 15-minute replication target. Used only for regional disaster failover. Failover runbook in `ops/runbooks/dr-failover.md` (lands at M3 alongside production ingest auth).
- **Object store** (bundles, SBOMs, attestations): S3-class with cross-region replication and Object Lock for ledger files (append-only enforced at storage layer).

### Restore drill cadence

- **Monthly:** PITR restore drill. One per-tenant DB chosen at random; restored to sandbox; verified.
- **Quarterly:** Regional failover drill. Control Plane registry failed over to cross-region replica; verified; failed back.
- **Annually:** Full-region loss simulation (region A entirely unavailable; control plane operates from region B). Customer-visible degradation measured; documented; reported in annual SOC 2 evidence.

Each drill produces a record in `ops/dr-drill-ledger.jsonl`. Failure to complete a scheduled drill within 30 days of due date → P1 incident. [policy-commitment:ops,quarterly-review]

### Customer reference architecture (Hybrid / air-gap)

Customer instances run on customer infrastructure; DR is the customer's responsibility. Zovark publishes a reference architecture (`docs/customer-reference-architectures/dr.md`, lands M3) including:
- Recommended PostgreSQL HA topology (Patroni + 3-node cluster).
- Recommended object-store posture (MinIO with replication, or customer's S3-compatible).
- Recommended audit-chain backup cadence and verification commands.
- A `zovark backup verify` CLI command that checks backup integrity offline.

### Customer-visible observability (closes issue #34)

Customers see (via zvadmin):
- Current health status of their own instance (`healthy`/`degraded`/`critical`/`unknown`).
- Last successful audit-chain verification timestamp.
- Last successful replay timestamp.
- Last successful backup timestamp (customer-side).
- For SaaS customers: tenant's RPO/RTO compliance status (whether last recovery point is within target).

Customers do NOT see:
- Other customers' health.
- Zovark internal infrastructure status (that's the public status page).
- Control Plane's own DR status (also on public status page).

### Public status page

`status.zovark.io` publishes Control Plane availability, update-distribution availability, telemetry-receiver availability. Per-tenant data never appears on the public status page.

## Consequences

- DR drills are recurring operational cost (monthly + quarterly + annual). Drift from cadence is P1 incident.
- Cross-region replication adds infrastructure cost; budgeted as fixed line item in SaaS cost model.
- Customer instances in air-gap mode have no Zovark-operated DR; reference architecture is the only Zovark deliverable.
- Public status page becomes a customer-trust dependency; outages must be reported within 30 minutes of detection. [policy-commitment:ops,incident-review]

## Alternatives Considered

- *No documented DR (status quo)*: rejected; Series-B-DD blocker.
- *RPO=1 hour / RTO=24 hours (looser)*: rejected; regulated buyers expect ≤4 hour RTO. [hypothesis:M3-DR-targets]
- *Three-region active-active*: rejected for v1.0; operationally too complex; revisit M11+.
- *Customer-managed DR for SaaS too*: rejected; SaaS customers paid for managed.
