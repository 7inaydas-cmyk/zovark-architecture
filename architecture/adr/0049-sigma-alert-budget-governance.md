# ADR-0049: Sigma Alert-Budget Governance

**Status:** active
**Date:** 2026-05-19
**Owner:** detection-owner
**Source:** rewritten from v3.2.4.3 ADR-0049 for the v3.2.5.0 consolidation baseline

## Context

INV-015 requires analyst approval before a Sigma rule is published. ADR-0023
defines how rule drafts are generated, and ADR-0029 limits the initial scope to
review and manual export. Publication governance still needs a separate safety
gate so approved rules do not overwhelm a tenant's SOC.

The historical source used exact percentage and event-count examples. Those
examples are not carried forward as binding claims. This ADR keeps the current
architecture rule: Sigma publication must be governed by tenant-specific alert
budgets, corpus freshness, drift status, and analyst approval.

## Decision

Before a Sigma rule can be published by any system-side path, it must satisfy a
per-tenant alert-budget review. The review record binds:

- the rule identity and rule version;
- the tenant and severity tier;
- the corpus version used for evaluation;
- corpus freshness status;
- corpus drift status;
- the tenant's configured alert budget for the severity tier;
- the observed alert volume against the evaluation corpus;
- the analyst approval record required by INV-015; and
- the tenant policy authorizing publication for that rule class.

The alert budget is tenant-scoped and severity-aware. A tenant may configure
different budgets for different severity tiers, but every override must be
recorded in tenant policy and surfaced in the rule lifecycle record.

Corpus governance is mandatory for publication review. The corpus must be
tenant-specific, versioned, refreshable, drift-checked, and auditable. If the
corpus is stale, drifted, missing provenance, or below the tenant's governance
bar, publication fails closed.

Analyst approval is necessary but not sufficient. A rule with analyst approval
still cannot be published if alert-budget, corpus, drift, tenant-policy, or
audit-linkage checks fail.

When post-publication monitoring shows that a rule exceeds its configured
budget, the rule is quarantined for analyst review rather than continuing to
send unrestricted customer alerts.

This ADR does not implement publication adapters, SIEM integrations, corpus
collection, or customer deployment automation. It defines the governance
contract those later implementations must satisfy.

## Consequences

- Sigma publication governance becomes operationally meaningful instead of
  relying on an abstract false-positive percentage.
- The review record gives auditors a concrete explanation for why a rule was
  allowed or blocked.
- Tenants can align detection noise with local SOC capacity without making
  Zovark's defaults universal.
- Publication paths become more complex because corpus and budget state are now
  part of the approval boundary.
- ADR-0023 and ADR-0029 remain generation and scope decisions; this ADR owns
  publication governance.

## Alternatives Considered

- **Use a universal percentage threshold.** Rejected because it does not map to
  tenant SOC capacity or severity.
- **Rely on analyst approval alone.** Rejected because automated budget checks
  are a necessary guardrail before customer alerting.
- **Use a fixed budget for all tenants.** Rejected because tenant size and
  staffing differ.
- **Allow publication when budget passes without analyst approval.** Rejected
  because INV-015 is binding.

