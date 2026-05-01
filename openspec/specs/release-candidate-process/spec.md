# release-candidate-process Specification

## Purpose
TBD - created by archiving change finalize-architecture-rc3-scorecard. Update Purpose after archive.
## Requirements
### Requirement: Release-candidate tags SHALL follow the rc-N progression

Architecture release-candidate tags SHALL follow a numbered progression `architecture-rcN` where each subsequent N marks a meaningful tightening of the architecture state. The progression captured by the rc1/rc2/rc3 cycle is:

- `architecture-rc1` — process established. Source-of-truth hierarchy present, finalization checklist + issue ledger + decision log seeded, baseline ADRs indexed, no open P0.
- `architecture-rc2` — conceptual architecture finalized for review. All checklist categories at PASS or explicitly deferred. Object-level architecture for tape, handoff, replay, audit, vault defined. Documents-only score ≥ 8.0.
- `architecture-rc3` — evidence-backed freeze. M0 architecture enforcement scripts implemented and passing. Documents-only score ≥ 8.5 AND evidence-backed score ≥ 8.5. All categories PASS or explicitly DEFERRED with owner + milestone + acceptance.

Subsequent tags `architecture-rc4`, `architecture-rc5`, etc. SHALL each declare what state they tighten relative to the prior tag. The `architecture-final` tag SHALL be reserved for the freeze that precedes general implementation kickoff.

#### Scenario: rc3 tag requires both scores ≥ 8.5

- **WHEN** preparing to tag `architecture-rc3`
- **THEN** the release-candidate scorecard SHALL show documents-only score ≥ 8.5 AND evidence-backed score ≥ 8.5
- **AND** all 12 finalization-checklist categories SHALL be at PASS or PASS-with-explicit-DEFERRAL

#### Scenario: rc3 tag requires zero open P0 and zero accepted-open P1

- **WHEN** preparing to tag `architecture-rc3`
- **THEN** `gh issue list --label "severity:P0" --state open` SHALL return empty
- **AND** any open `severity:P1` issue SHALL have status `deferred`, never `accepted` (i.e., no accepted-and-unfinished P1 work)

### Requirement: PASS-with-explicit-DEFERRAL annotations SHALL name owner + milestone + acceptance

Every `PASS-with-explicit-DEFERRAL` annotation SHALL name an owner, a target milestone, and acceptance criteria. A finalization-checklist category MAY be at `PASS-with-explicit-DEFERRAL` only when the deferral annotation names:

- An owner (a role from `OWNERS.yaml` or `BOOTSTRAP_PENDING_OWNERS`).
- A target milestone (`M0`, `M1`, `M2`, ..., `MN`, or `GA`).
- Acceptance criteria — what evidence will close the deferral.

Categories at `PASS-with-tracked-gaps` (the rc2 soft form) SHALL NOT remain in that state across an rc-N boundary if N ≥ 3. They SHALL be either upgraded to strict PASS or annotated as `PASS-with-explicit-DEFERRAL`.

#### Scenario: rc3 category cannot remain PASS-with-tracked-gaps

- **WHEN** preparing the rc3 scorecard
- **THEN** every category previously marked `PASS-with-tracked-gaps` SHALL be either upgraded to strict `PASS` or downgraded to `PASS-with-explicit-DEFERRAL` with owner + milestone + acceptance

#### Scenario: A DEFERRED category without acceptance criteria fails review

- **WHEN** the scorecard marks a category `PASS-with-explicit-DEFERRAL` but the deferral annotation lacks an acceptance line
- **THEN** rc-N freeze review SHALL reject the scorecard until the annotation is complete

### Requirement: Each rc-N freeze SHALL produce a decision-log entry

Tagging an `architecture-rcN` SHALL be accompanied by a decision-log entry (e.g., `TR-005` for rc2, `TR-006` for rc3) that records:

- The freeze decision and the date.
- Documents-only and evidence-backed scores.
- The list of archived OpenSpec changes that compose the rc.
- Open issues at freeze time, with severity and status.
- Pointers to the scripts run and their pass/fail status (rc3+).

#### Scenario: Tagging rc3 without a TR-006 decision-log entry fails review

- **WHEN** `architecture-rc3` is tagged but no `TR-006` (or equivalent) entry exists in `architecture/review/decision-log.md`
- **THEN** review SHALL reject the tag and require the entry before pushing

### Requirement: Future release-candidate-process changes go through this spec

Adding new rc tag stages (e.g., `architecture-rc4` semantics), changing the score thresholds, or modifying the deferral-annotation rules SHALL go through a `MODIFIED Requirements` change against `release-candidate-process`. Direct edits to scoring rules in scorecard/checklist docs without a spec change SHALL be rejected at review.

#### Scenario: Lowering the rc3 score threshold requires a spec change

- **WHEN** someone proposes that rc3 should pass at score 7.5 instead of 8.5
- **THEN** they SHALL file a `MODIFIED Requirements` change against `release-candidate-process` first

