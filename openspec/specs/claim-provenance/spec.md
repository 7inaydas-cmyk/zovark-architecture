# claim-provenance Specification

## Purpose
Defines the four allowed provenance tags for quantified claims, the customer-facing classification rules, and the interface contract for the M0 verification script `scripts/check_claim_provenance.py`.
## Requirements
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

A `[policy-commitment:owner,review-cadence]` tag's `owner` SHALL be a role listed in `OWNERS.yaml` OR a role declared in the implementation script's `BOOTSTRAP_PENDING_OWNERS` allowlist. The bootstrap allowlist is finite, documented in `scripts/check_claim_provenance.py`, and exists to accommodate roles referenced by patch-tree tags that are not yet declared in `OWNERS.yaml`'s `roles:` section. The allowlist collapses to empty post-M2 OWNERS.yaml registration.

The `review-cadence` SHALL be one of:

- Periodic: `daily`, `weekly`, `monthly`, `quarterly`, `quarterly-review`, `semiannual-review`, `annual-review`.
- Event-driven: `release-review`, `milestone-review`, `per-release-review`, `per-promotion-review`, `per-advisory-review`, `per-change-review`, `incident-review`.

Other cadences require a `MODIFIED Requirements` spec change.

#### Scenario: Unknown owner fails

- **WHEN** a `[policy-commitment:fred,annual-review]` tag references "fred" who is not in `OWNERS.yaml` and not in `BOOTSTRAP_PENDING_OWNERS`
- **THEN** verification SHALL fail and report "owner not in OWNERS.yaml or bootstrap-pending"

#### Scenario: Bootstrap-pending owner passes

- **WHEN** a `[policy-commitment:product-owner,release-review]` tag references a role in `BOOTSTRAP_PENDING_OWNERS` and the cadence is in the allowed list
- **THEN** verification SHALL pass

#### Scenario: Free-form cadence fails

- **WHEN** a `[policy-commitment:security-officer,sometimes]` tag uses a cadence outside the allowed list
- **THEN** verification SHALL fail and report "cadence not in allowed list"

#### Scenario: Event-driven cadence passes

- **WHEN** a `[policy-commitment:release-engineering,per-release-review]` tag uses an event-driven cadence in the allowed list
- **THEN** verification SHALL pass

### Requirement: scripts/check_claim_provenance.py SHALL implement the verification interface

The verification script SHALL:

- Walk: `architecture/**/*.md`, `zovark-v3.2.4.6-engineering-ready/**/*.md`, top-level `*.md`.
- Skip: `openspec/changes/archive/**`, `architecture/review/**`, `architecture/claims/**` (the rules-of-the-rules document and its patch-tree mirror), `LICENSE-*` (legal text, not architecture content).
- Detect quantified claims using a category list (word-boundary match for single-word categories) + numeric-with-unit regex.
- Validate each tag in two passes: (1) every tag's payload is well-formed (kind, grammar, owner, cadence, measured-artifact resolves, hypothesis only outside customer-facing); (2) every quantified claim has a tag on the same line or the immediately following line.
- Skip illustrative placeholder payloads (`<owner>,<review-cadence>`, `artifact-id,YYYY-MM-DD`, etc.) at validation time.
- Exit 0 if all checks pass; exit non-zero with a failure list (one line per failure: `path:line: <reason>`) otherwise.

The script implementation lands in the rc3 change `fix-claim-provenance-enforcement`. Subsequent updates to the walk pattern, category list, or placeholder allowlist SHALL go through a `MODIFIED Requirements` change against this spec.

#### Scenario: Clean run on a tagged repo

- **WHEN** every quantified claim in scope carries a valid provenance tag
- **THEN** the script SHALL exit 0 with output "Claim provenance check passed"

#### Scenario: Failure run

- **WHEN** at least one claim violates a rule
- **THEN** the script SHALL print one failure line per violation and exit non-zero

#### Scenario: Walk excludes architecture/claims/

- **WHEN** the verifier encounters a tag inside `architecture/claims/claim-provenance.md` that is illustrative (e.g., the literal string `[measured:artifact-id,YYYY-MM-DD]` shown as a syntax example)
- **THEN** the verifier SHALL NOT report a failure for that tag (the path is excluded from the walk)

### Requirement: Future tag changes go through this spec

Adding, removing, or modifying tag formats, claim categories, customer-facing classification rules, or the script interface SHALL be filed as a `MODIFIED Requirements` OpenSpec change against `claim-provenance`. Ad-hoc edits to `architecture/claims/claim-provenance.md` SHALL be rejected at review.

#### Scenario: Direct edit without spec change is rejected

- **WHEN** someone edits `architecture/claims/claim-provenance.md` without a corresponding `MODIFIED Requirements` change
- **THEN** review SHALL reject the change and ask for a spec proposal first

