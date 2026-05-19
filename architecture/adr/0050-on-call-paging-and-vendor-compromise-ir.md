# ADR-0050: On-Call, Paging, and Vendor-Compromise Incident Response

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** ops  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

The v3.2.4.2 architecture has no documented on-call rotation, paging policy, escalation matrix, or vendor-compromise incident response. ADR-0035 names an "open-source on-call and paging stack" but the body wasn't supplied; tooling without policy is half a story. The strategic review identified vendor-compromise scenarios specifically: Wasmtime, Temporal, PostgreSQL, EDR vendor APIs, LLM provider, plus our own keys per ADR-0042. Each needs a documented runbook; the team cannot improvise these under outage pressure.

The Wasmtime 14-day Critical/High SLA from INV-011 is single-track and doesn't model air-gap deployment windows. Issue #29 closes here.

## Decision

### Severity tiers and pager response

This response table is a support/operations design target pending on-call rotation, paging configuration, incident/support ledgers, monitoring, and staffing evidence. It is not a current staffing model, customer commitment, marketing claim, or contract term.

| Tier | Examples | Initial response | Escalation |
|------|----------|------------------|-----------|
| **P0** | Customer data exposed; audit chain integrity broken; key compromise; full Control Plane outage; vendor compromise affecting our supply chain | <15 min ack, <1 hour leadership-aware | Founder + security-officer + control-plane-owner immediately |
| **P1** | Single-tenant outage; signed-bundle distribution stalled; non-data-exposing security finding; DR drill failed; vendor security advisory at Critical/High severity | <30 min ack, <4 hour fix-or-mitigate | Subsystem owner + security-officer if security-adjacent |
| **P2** | Performance degradation within tenant's RPO/RTO; non-blocking telemetry-receiver issue; non-customer-facing tooling outage | <2 hour ack during business hours | Subsystem owner | [policy-commitment:ops,incident-review]
| **P3** | Documentation drift; lint failure; non-blocking CI flakiness | Next-business-day | Filed as ticket |

### Rotation

Target rotation: two-engineer primary rotation, weekly hand-off, with a designated secondary.

- **Production rotation target:** at least one ops + one engineer-on-call per shift.
- **Security rotation target:** security-officer or designated alternate available for P0 escalation 24/7.
- **Architect rotation target:** architect-on-call available for cross-subsystem decisions during business hours; not 24/7 in v1.0.

Rotation tooling target: PagerDuty (or open-source equivalent OnCallio/IIRIS per ADR-0035) once cost-budget permits; in v1.0 M1, a manual rotation in `ops/oncall.yaml` plus PagerDuty's free tier is the planned interim path.

### Paging trigger design targets

- Planned synthetic monitoring of every customer-facing surface (status.zovark.io, control-plane API, update-distribution endpoint, telemetry receiver).
- Planned audit-chain integrity check failure on any tenant.
- Planned DR drill cadence breach (per ADR-0044 §restore-drill-cadence).
- Planned key-ledger anomaly (any key event without a corresponding ADR-amendment-or-incident reference).
- Planned customer-reported P0 (via support channel; auto-routed if marked "security" or "data-exposed").

### Vendor-compromise runbooks

Each vendor in the supply chain has a runbook at `ops/runbooks/vendor-{name}.md` (lands M3 except where noted):

- **Wasmtime advisory.** When a Critical/High advisory drops:
  1. Within 4 hours: triage assesses [policy-commitment:ops,incident-review] whether INV-010/INV-011 scope is affected.
  2. If yes: SaaS rollout target = 7 days from advisory; air-gap rollout target = 30 days from advisory + customer's import window. [policy-commitment:ops,incident-review]
  3. The 14-day SaaS SLA in INV-011 applies to "vendor patch incorporated into signed update bundle" — not to "deployed to every air-gap customer." Air-gap deployment is customer-window-bounded.
  4. If a customer's import window pushes past 60 days for a Critical advisory [policy-commitment:ops,incident-review], customer success contacts the customer; if compromise risk is real, Zovark may recommend operational mitigations (capability disablement, monitoring increase) until the customer can import.
- **Temporal compromise** (M3 runbook): assess workflow-history exposure; rotate Temporal API keys; verify no tenant data exfiltrated via Temporal logs; Temporal-side incident report.
- **PostgreSQL CVE** (M3 runbook): triage; SaaS-side patch within standard maintenance window; customer-instance: signed-bundle includes the patched PG; air-gap window same as Wasmtime.
- **EDR vendor API compromise** (M3 runbook): rotate all customer EDR credentials in the vault; revoke pending EDR action authorizations; suspend approval-required EDR handoff for affected tenants/providers; analyst review before re-enabling handoff. Autonomous EDR action is not part of the current architecture and is retired through ADR-0021 in `architecture/source-of-truth.md`.
- **LLM provider compromise** (M3 runbook): pause new investigations on the affected provider; replay continues unaffected (per ADR-0047 — replay does not re-inference); rotate API keys; switch to backup provider per ADR-0009 two-model architecture.
- **Our own keys (per ADR-0042)** runbook is planned for SECURITY-VULN-DISCLOSURE.md §8 and should be rehearsed twice yearly once implemented.

Once incident-ledger implementation exists, each runbook should produce a record in `ops/incident-ledger.jsonl` (append-only, hash-chained) on every drill or real incident.

### Customer-support response targets

- **Tier 1 (P0 customer-reported):** target ack within 1 business hour; engineer engaged within 4 business hours; resolution target within 24 business hours for fixable issues.
- **Tier 2 (P1):** target ack within 4 business hours; engagement within 1 business day; resolution within 5 business days.
- **Tier 3 (P2/P3):** target ack within 1 business day; engagement within 3 business days; resolution per next-release-cycle.

These are design targets for a future paid SaaS support program pending on-call rotation, paging configuration, incident/support ledgers, monitoring, and staffing evidence. They are not customer commitments, marketing claims, or contract terms until implemented and validated. Hybrid and air-gap customers may negotiate different tiers after that support program exists.

### Pen-test / bug-bounty (closes issue #33)

- **Pen-test:** third-party engagement planned before first design-partner onboarding (target: M5 quarter-end). Annual cadence after that. Findings will be tracked in `ops/security/pen-test-ledger.jsonl` once implemented.
- **Bug-bounty:** deferred to M11+; tracked as DD_BLOCKERS M11-DESIGN-004. SECURITY-VULN-DISCLOSURE.md provides the responsible-disclosure interim path.

### Quarterly drills

- **Q1:** Wasmtime advisory drill (synthetic).
- **Q2:** EDR vendor compromise drill.
- **Q3:** PostgreSQL CVE drill + DR full-region failover.
- **Q4:** Our-own-keys compromise drill (per ADR-0042).

Once incident-ledger and on-call workflow exist, each drill should record timing in the incident-ledger [policy-commitment:ops,quarterly-review]; failure to complete a drill within 30 days of due date is the planned P1 policy after that workflow is implemented. [policy-commitment:ops,quarterly-review]

## Consequences

- On-call adds operational headcount cost; budgeted as fixed line item from M3 onwards once the rotation is implemented.
- Customer-support response targets require on-call, paging, incident/support ledger, monitoring, and staffing implementation before they can become contractual commitments.
- Vendor-compromise runbooks (six of them) need to land at M3; that's a real engineering deliverable, not just policy.
- Pen-test scheduling at M5 quarter-end means timeline slip on M5 delays first design-partner.

## Alternatives Considered

- *Reactive on-call only (no rotation; "whoever's available")*: rejected; first P0 will surface the gap.
- *No vendor-compromise runbooks*: rejected; first vendor advisory will surface the gap.
- *24/7 architect rotation*: rejected for v1.0; cost-benefit not there with 4-engineer pod; revisit when team grows.
- *Paid bug-bounty in v1.0*: rejected; deferred to M11+ to manage triage capacity.
