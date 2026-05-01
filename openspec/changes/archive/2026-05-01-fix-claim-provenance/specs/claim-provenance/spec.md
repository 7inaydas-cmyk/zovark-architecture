## ADDED Requirements

### Requirement: Quantified claims SHALL carry exactly one provenance tag

Every quantified claim in architecture and customer-facing documentation SHALL be tagged with exactly one of the four allowed provenance tags. Tag formats:

- `[hypothesis:evidence-milestone]` — internal claims that still need evidence; the milestone (e.g., `M2`, `M5`) is named explicitly.
- `[measured:artifact-id,YYYY-MM-DD]` — claims backed by an artifact present in the repository; the artifact ID and measurement date are named.
- `[vendor-cited:citation-id]` — claims backed by a real vendor citation file or URL; the citation ID is named.
- `[policy-commitment:owner,review-cadence]` — commitments owned by a role and reviewed on a fixed cadence; both fields are required.

Quantified claims include statements about: latency, throughput, capacity, queue depth, false-positive rate, RPO, RTO, support response time, patch response time, retention period, schedule duration, cost, reliability, availability, accuracy, and precision.

#### Scenario: Untagged quantified claim is a violation

- **WHEN** a document contains a quantified claim (e.g., "p99 latency is under 200ms") without any provenance tag
- **THEN** verification SHALL fail and report the file:line and claim text

#### Scenario: Multiple tags on the same claim is a violation

- **WHEN** a single quantified claim carries more than one provenance tag
- **THEN** verification SHALL fail (exactly one tag is required)

#### Scenario: Tag with malformed payload is a violation

- **WHEN** a tag of one of the four types appears with a missing or malformed payload (e.g., `[measured:artifact-id]` without a date, `[policy-commitment:owner]` without a cadence)
- **THEN** verification SHALL fail and report the malformed payload

### Requirement: Customer-facing documents SHALL NOT contain hypothesis tags

Documents classified as customer-facing SHALL NOT contain `[hypothesis:*]` tags. Customer-facing claims must be backed by `[measured:*]`, `[vendor-cited:*]`, or `[policy-commitment:*]`.

A document is classified as customer-facing if any of the following are true:

- It declares `customer_facing: true` in YAML frontmatter; OR
- Its top-level heading text contains the tokens "Customer", "User", "Operator Guide", "Public", or "Onboarding"; OR
- Its path matches `architecture/customer-*.md` or `architecture/handoff/**/*.md`.

#### Scenario: Hypothesis claim in a customer-facing doc fails

- **WHEN** a customer-facing document contains a `[hypothesis:*]` tag
- **THEN** verification SHALL fail and report the file:line

#### Scenario: Hypothesis claim in an internal doc passes

- **WHEN** a non-customer-facing document contains a `[hypothesis:milestone]` tag with a valid milestone name
- **THEN** verification SHALL pass for that claim

### Requirement: Measured tags SHALL point to artifacts that exist

A `[measured:artifact-id,YYYY-MM-DD]` tag's `artifact-id` SHALL identify a file present under `architecture/`, `tests/`, `ops/`, or the patch tree. Verification SHALL resolve the artifact ID against actual files and fail if no match is found.

#### Scenario: Measured claim with missing artifact fails

- **WHEN** a `[measured:nonexistent-id,2026-01-01]` tag references an artifact that does not exist
- **THEN** verification SHALL fail and report "artifact not found"

### Requirement: Policy-commitment tags SHALL name a known owner

A `[policy-commitment:owner,review-cadence]` tag's `owner` SHALL be a role listed in `OWNERS.yaml` (or the patch-tree equivalent). Free-form names that are not in `OWNERS.yaml` SHALL fail verification.

The `review-cadence` SHALL be one of: `daily`, `weekly`, `monthly`, `quarterly`, `semiannual-review`, `annual-review`. Other cadences require a `MODIFIED Requirements` spec change.

#### Scenario: Unknown owner fails

- **WHEN** a `[policy-commitment:fred,annual-review]` tag references "fred" who is not in `OWNERS.yaml`
- **THEN** verification SHALL fail and report "owner not found in OWNERS.yaml"

#### Scenario: Free-form cadence fails

- **WHEN** a `[policy-commitment:security-officer,sometimes]` tag uses a cadence outside the allowed list
- **THEN** verification SHALL fail and report "cadence not in allowed list"

### Requirement: scripts/check_claim_provenance.py SHALL implement the verification interface

The verification script SHALL:

- Walk: `architecture/**/*.md`, `zovark-v3.2.4.6-engineering-ready/**/*.md`, top-level `*.md`.
- Skip: `openspec/changes/archive/**`, `architecture/review/**`.
- Detect quantified claims using a category list + numeric-with-unit regex.
- Validate each claim against the rules above.
- Exit 0 if all claims pass; exit non-zero with a failure list (one line per failure: `path:line: <reason>`) otherwise.

The script implementation is an M0 deliverable; this spec defines its contract. The script SHALL NOT be implemented as part of this change.

#### Scenario: Clean run on a tagged repo

- **WHEN** every quantified claim in scope carries a valid provenance tag
- **THEN** the script SHALL exit 0 with output "Claim provenance check passed"

#### Scenario: Failure run

- **WHEN** at least one claim violates a rule
- **THEN** the script SHALL print one failure line per violation and exit non-zero

### Requirement: Future tag changes go through this spec

Adding, removing, or modifying tag formats, claim categories, customer-facing classification rules, or the script interface SHALL be filed as a `MODIFIED Requirements` OpenSpec change against `claim-provenance`. Ad-hoc edits to `architecture/claims/claim-provenance.md` SHALL be rejected at review.

#### Scenario: Direct edit without spec change is rejected

- **WHEN** someone edits `architecture/claims/claim-provenance.md` without a corresponding `MODIFIED Requirements` change
- **THEN** review SHALL reject the change and ask for a spec proposal first
