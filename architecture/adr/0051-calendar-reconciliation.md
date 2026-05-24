# ADR-0051: Calendar Reconciliation

**Status:** accepted  
**Date:** 2026-05-01  
**Owner:** architect  
**Version context:** v3.2.5.0 consolidation promotion  
**Source classification:** v3.2.4.3 patch ADR, mechanically normalized for current ADR format
## Context

The v3.2.4.2 contract carries three contradictory calendar statements:
- ADR-0012 (still listed as "SUPERSEDED by 0032"): 28 days. [hypothesis:calendar-reconciliation]
- The original prompt to which the v3.2.4.2 review was responding: 32-35 days for design-partner MVP [hypothesis:calendar-reconciliation] with 4-engineer pod. [hypothesis:calendar-reconciliation]
- The strategic review's referenced handover.md §2.3: 55-65 days (revised after schedule-math review). [hypothesis:calendar-reconciliation]
- The v3.2.4.2 FINAL doc §12.3: M1 alone is 3-7 weeks (best/expected/worst), with one FT engineer + half-time architect. [hypothesis:calendar-reconciliation]

Three sources, three numbers, no single authoritative figure. Series-B-DD will surface this immediately; engineering execution depends on a single calendar.

## Decision

### Authoritative calendars (binding)

**M1 (mechanical baseline + first vertical slice):**
- **Target:** 5 weeks calendar / 25 working days [hypothesis:calendar-reconciliation]
- **Team:** 1 FT engineer + 0.5 architect
- **Best case:** 3 weeks (2 FT engineers + 0.5 architect) [hypothesis:calendar-reconciliation]
- **Worst case:** 7 weeks (single FT, environment friction) [hypothesis:calendar-reconciliation]
- **Scope:** the 28 M1 tasks from v3.2.4.2 §12.2 plus the v3.2.4.3 mechanical-closure tasks (apply script, new check scripts, new fixtures).

**MVP (design-partner ready):**
- **Target:** 60 working days / 12 calendar weeks from M1 commit
- **Team:** 4 FT engineers + 0.5 architect + 0.25 security-officer
- **Best case:** 50 working days (highly experienced team, no environment friction)
- **Worst case:** 80 working days (single attrition + HSM procurement delay)
- **Scope:** M1-M5 milestones (mechanical baseline + control-plane local + production ingest auth + Update Factory proof + audit chain runtime). DR, customer offboarding, healer runtime hardening also land in this window.

**Note on the prompt's "32-35 days for design-partner MVP [hypothesis:calendar-reconciliation]":** that calendar is achievable only if MVP scope is narrowed to M1+M2 (mechanical baseline + control-plane local protocol with telemetry boundary enforcement, no Update Factory proof, no real audit chain runtime). v3.2.4.3 does not commit to that scope as the design-partner-ready definition; ADR-0032's "schedule realism" rule applies and we keep MVP scope at M1-M5 with a 60-working-day target.

### Math, explicit

Using the prompt's assumptions: S=4h, M=12h, L=32h; 4 engineers × 8h/day × 80% pure-engineering = 25.6 hours/day team capacity. [hypothesis:calendar-reconciliation]

If MVP requires 80 OpenSpec changes averaging M (12h):
- Total work: 80 × 12 = 960 hours. [hypothesis:calendar-reconciliation]
- At team capacity 25.6 h/day with full parallelism: 38 working days.
- Add critical-path drag (sequential dependencies M1→M2→M3→M4→M5): +30%.
- Realistic MVP: ~50 working days. Adding HSM procurement risk + integration friction: 60 working days.

If 65 changes are M and 15 are L (32h each):
- Total: 65×12 + 15×32 = 780 + 480 = 1,260 hours. [hypothesis:calendar-reconciliation]
- 49 working days at full parallelism + critical-path drag: 64 working days.

The 60-working-day target sits inside this envelope. The 32-35-day target sits outside it for full MVP scope; it sits inside for narrowed scope.

### What slips first if scope must compress

In order from first-to-slip to last-to-slip:
1. F-005 Sigma candidate learning publication path (defer to M9 as already planned).
2. Additional EDR adapters beyond Wazuh (defer to M11+ per existing scope).
3. zvadmin UI polish (functional UI sufficient for design-partner; polish at M11+).
4. Air-gap operational proof (defer to M10 as already planned).
5. Research Pipeline runner (defer to M6 as already planned).
6. Update Factory production hardening (M4 lands proof; production at M11+).

What does **not** slip:
- Audit chain integrity (M5 requirement; this is the wedge).
- Replay engine (M5 requirement; this is the wedge).
- Vault per-action authz (already covered as INV-019).
- Tenancy boundary runtime (M3 requirement).
- Schema-first generated bindings (M1 requirement).
- DR cadence (ADR-0044 binding from contract).

### Stop conditions (added)

- Any document in the repository asserts a calendar number not matching this ADR's targets without an explicit `[supersedes ADR-0051]` marker → P1.
- Any customer-facing material claims an MVP timeline shorter than the 50-working-day best case → marketing-language stop condition.

### Supersedence

- ADR-0012 ("Engineering team builds in compressed timeframe", 28 days): superseded.
- ADR-0032 ("Schedule realism supersedes ADR-0012", referenced in v3.2.4.2 inventory): superseded by this ADR. ADR-0032's principle (schedule realism > optimism) is preserved here.

Both prior ADRs remain in repository history for audit purposes; no document outside that history may cite them as authoritative.

## Consequences

- A single source of truth for calendar across all repository documents.
- Calendar realism is now an architectural commitment, not a planning aspiration.
- Marketing materials must reference these numbers; sales conversations cannot promise the 32-35-day MVP without explicit scope narrowing.
- Series-B-DD has one number to evaluate.

## Alternatives Considered

- *Keep 32-35 days as authoritative*: rejected; math doesn't compose for full MVP scope; prior schedule-math review caught this.
- *Keep ADR-0032 but re-derive numbers*: rejected; cleaner to have one calendar ADR superseding both prior ones.
- *No calendar in architecture; calendar is a project-management concern*: rejected; investors and customers ask; architecture team is asked first.
