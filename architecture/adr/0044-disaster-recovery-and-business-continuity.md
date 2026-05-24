# ADR-0044: Disaster Recovery & Business Continuity (SaaS topology)

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** ops  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

The v3.2.4.2 architecture commits to "cloud SaaS first" but has no documented DR posture. ADR-0038 mentions DR in one sentence ("registry data is replicated; loss of the Control Plane DB does not affect customer instances"). Insufficient for Series-B-DD or for the first regulated-buyer questionnaire. RPO, RTO, multi-region failover, point-in-time recovery, and restore-drill cadence must be concrete, measurable, and rehearsed.

## Decision

### Design targets pending implementation

| Subsystem | RPO | RTO | Topology |
|-----------|-----|-----|----------|
| Control Plane registry | ≤5 minutes | ≤4 hours | Multi-AZ synchronous primary + cross-region async replica | [hypothesis:M3-DR-targets]
| Control Plane update catalog | ≤15 minutes | ≤4 hours | Same as registry; bundles in object store with cross-region replication | [hypothesis:M3-DR-targets]
| Update Factory ledger | ≤15 minutes | ≤8 hours | Append-only object store (11-9s durability) + cross-region replication | [hypothesis:M3-DR-targets]
| Research Pipeline corpora | ≤24 hours | ≤24 hours | Daily snapshot; loss recoverable from re-run | [hypothesis:M3-DR-targets]
| Customer Instance (SaaS) | ≤15 minutes | ≤4 hours | Per-tenant; multi-AZ DB primary + read replica; daily PITR snapshot | [hypothesis:M3-DR-targets]
| Customer Instance (Hybrid/air-gap) | Customer-owned | Customer-owned | Reference architecture published; not Zovark-operated |

These are design targets pending PITR runbook, DR drill ledger, failover implementation, and evidence. They are not customer commitments, marketing claims, or contract terms until implemented and tested. INV-033 is the binding invariant for DR drill cadence.

### Backup mechanism design targets

- **PostgreSQL primary target**: continuous WAL streaming to a hot standby in a second AZ within the same region (synchronous_commit=remote_apply for the registry; remote_write for customer-instance per-tenant DBs to keep customer write latency acceptable).
- **PITR design target**: daily base backups + 7-day WAL retention. Tested restore from PITR is planned to run **monthly** in a sandbox region; restore success will be recorded in `ops/dr-drill-ledger.jsonl` once implemented.
- **Cross-region async replica design target**: 15-minute replication target. Intended only for regional disaster failover. Failover runbook in `ops/runbooks/dr-failover.md` lands with the implementation work.
- **Object store target** (bundles, SBOMs, attestations): S3-class with cross-region replication and Object Lock for ledger files (append-only enforced at storage layer).

### Restore drill cadence

- **Monthly target:** PITR restore drill. One per-tenant DB chosen at random; restored to sandbox; verified.
- **Quarterly target:** Regional failover drill. Control Plane registry failed over to cross-region replica; verified; failed back.
- **Annual target:** Full-region loss simulation (region A entirely unavailable; control plane operates from region B). Customer-visible degradation measured; documented; reported in annual SOC 2 evidence.

Once DR drill tooling exists, each drill will produce a record in `ops/dr-drill-ledger.jsonl`. Failure to complete a scheduled drill within 30 days of due date is the planned P1 policy after the drill ledger and incident workflow are implemented. [policy-commitment:ops,quarterly-review]

### Customer reference architecture (Hybrid / air-gap)

Customer instances run on customer infrastructure; DR is the customer's responsibility. Zovark plans to publish a reference architecture (`docs/customer-reference-architectures/dr.md`, lands M3) including:
- Recommended PostgreSQL HA topology (Patroni + 3-node cluster).
- Recommended object-store posture (MinIO with replication, or customer's S3-compatible).
- Recommended audit-chain backup cadence and verification commands.
- A planned `zovark backup verify` CLI command that checks backup integrity offline.

### Customer-visible observability design target (closes issue #34)

Once zvadmin observability is implemented, customers should see:
- Current health status of their own instance (`healthy`/`degraded`/`critical`/`unknown`).
- Last successful audit-chain verification timestamp.
- Last successful replay timestamp.
- Last successful backup timestamp (customer-side).
- For SaaS customers: tenant's RPO/RTO design-target status (whether last recovery point is within target).

The design must not expose:
- Other customers' health.
- Zovark internal infrastructure status (that's the public status page).
- Control Plane's own DR status (also on public status page).

### Public status page design target

`status.zovark.io` is a planned public status-page target, not a live endpoint in this architecture baseline. Once monitoring, incident workflow, operations ownership, and evidence exist, it should publish Control Plane availability, update-distribution availability, and telemetry-receiver availability. Per-tenant data must never appear on the public status page.

## Consequences

- DR drills will be a recurring operational cost (monthly + quarterly + annual). Drift from cadence becomes a P1 incident after drill-ledger and incident-workflow implementation.
- Cross-region replication adds infrastructure cost; budgeted as fixed line item in SaaS cost model.
- Customer instances in air-gap mode have no Zovark-operated DR; reference architecture is the only Zovark deliverable.
- Public status page becomes a customer-trust dependency after implementation; outage reporting within 30 minutes of detection is a design target, not a customer-facing commitment in this baseline. [policy-commitment:ops,incident-review]

## Alternatives Considered

- *No documented DR (status quo)*: rejected; Series-B-DD blocker.
- *RPO=1 hour / RTO=24 hours (looser)*: rejected; regulated buyers expect ≤4 hour RTO. [hypothesis:M3-DR-targets]
- *Three-region active-active*: rejected for v1.0; operationally too complex; revisit M11+.
- *Customer-managed DR for SaaS too*: rejected; SaaS customers paid for managed.
