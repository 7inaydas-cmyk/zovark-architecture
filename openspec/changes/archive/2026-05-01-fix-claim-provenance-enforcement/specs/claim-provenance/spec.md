## MODIFIED Requirements

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
