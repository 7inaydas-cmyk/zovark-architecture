# Claim Provenance

This is the source-of-truth document for tagging quantified claims across Zovark's
architecture and customer-facing documentation. The rules here govern; the predecessor
patch-tree document (`zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/claims/claim-provenance.md`)
is a snapshot and may diverge in future patch versions.

The verification script `scripts/check_claim_provenance.py` is an **M0 deliverable**
and is not yet implemented. Its interface contract is specified below; the spec at
`openspec/specs/claim-provenance/spec.md` is the binding artifact.

## What is a quantified claim

Any statement asserting a numeric value or a numeric bound about:

- **Performance:** latency (p50/p95/p99), throughput, queue depth, capacity, concurrency.
- **Correctness:** false-positive rate, false-negative rate, accuracy, precision.
- **Reliability:** availability, MTBF, MTTR.
- **Operational:** RPO, RTO, support response time, patch response time, retention period.
- **Schedule:** durations expressed in days, weeks, months (e.g., "ships in 8 weeks").
- **Cost:** dollar amounts, license fees, infrastructure cost.
- **Capacity:** number of tenants, alerts/sec, agents, events stored.

A claim that is purely qualitative ("Zovark is fast") is not a quantified claim and
does not require a tag — but reviewers SHOULD flag qualitative claims that smuggle
quantification ("Zovark is significantly faster than incumbents") as either
quantified-needing-tag or as marketing language to be removed.

## Allowed provenance tags

Every quantified claim MUST carry exactly one of the following tags:

### `[hypothesis:evidence-milestone]`

For internal claims that still need evidence. The milestone names when evidence is
expected to land. Examples: `[hypothesis:M5]`, `[hypothesis:M2-soak]`.

**Allowed in:** internal architecture docs, ADRs, internal handoff docs.
**NOT allowed in:** customer-facing docs.

### `[measured:artifact-id,YYYY-MM-DD]`

For claims backed by an artifact present in the repository. The `artifact-id`
identifies a file under `architecture/`, `tests/`, `ops/`, or the patch tree. The
date is the measurement date.

Example: `[measured:audit-chain-soak-2026-04-12,2026-04-12]`.

**Allowed everywhere.** Verification will fail if the artifact does not exist.

### `[vendor-cited:citation-id]`

For claims backed by a real vendor citation (URL, paper, or vendor-published doc).
The `citation-id` identifies an entry in a citations file (e.g.,
`architecture/citations.yaml`, when added).

**Allowed everywhere.** Verification will fail if the citation ID is unknown.

### `[policy-commitment:owner,review-cadence]`

For commitments owned by a role and reviewed on a fixed cadence. The `owner` SHALL
be a role from `OWNERS.yaml` (e.g., `security-officer`, `research-owner`). The
`review-cadence` SHALL be one of: `daily`, `weekly`, `monthly`, `quarterly`,
`semiannual-review`, `annual-review`.

Example: `[policy-commitment:security-officer,semiannual-review]` (used in ADR-0042).

**Allowed everywhere.**

## Customer-facing classification

A document is **customer-facing** if any of:

- It declares `customer_facing: true` in YAML frontmatter.
- Its top-level heading text contains the tokens "Customer", "User", "Operator Guide",
  "Public", or "Onboarding".
- Its path matches `architecture/customer-*.md` or `architecture/handoff/**/*.md`.

A document is **internal** otherwise.

Authors who want to override the heuristic (e.g., classify an internal-looking doc as
customer-facing, or vice versa) SHOULD set `customer_facing:` explicitly in
frontmatter.

## Rules

1. Every quantified claim SHALL carry exactly one provenance tag.
2. Customer-facing documents SHALL NOT contain `[hypothesis:*]` tags.
3. `[measured:*]` artifact IDs SHALL resolve to an existing file.
4. `[vendor-cited:*]` citation IDs SHALL resolve to a known citation entry.
5. `[policy-commitment:*]` owners SHALL be roles listed in `OWNERS.yaml`.
6. `[policy-commitment:*]` cadences SHALL be one of the six allowed values.
7. Tag format SHALL match the grammar exactly — square brackets, lowercase tag
   name, colon-separated payload, no whitespace inside the tag.

## scripts/check_claim_provenance.py — interface contract (M0 deliverable)

The verification script SHALL implement the following interface. The script is an
M0 deliverable; the spec at `openspec/specs/claim-provenance/spec.md` is binding.

### CLI

```
scripts/check_claim_provenance.py [--strict-customer-facing]
```

- `--strict-customer-facing` (optional, default off): also fail if a customer-facing
  doc is missing frontmatter declaring `customer_facing:`.

### Walk

- **Include:** `architecture/**/*.md`, `zovark-v3.2.4.6-engineering-ready/**/*.md`,
  top-level `*.md`.
- **Exclude:** `openspec/changes/archive/**`, `architecture/review/**` (review docs
  describe rules, not assert claims), `.git/**`.

### Detection

Use a category list (the categories above) plus a numeric-with-unit regex (e.g.,
`\d+(\.\d+)?\s*(ms|s|min|h|d|MB|GB|TB|%|alerts/sec|tenants|requests/sec|...)`)
to surface candidate claims. Any candidate within 1 sentence of a category keyword
is a quantified claim.

### Validation

For each quantified claim:

1. Find a tag within the same line OR within the immediately following sentence.
2. If no tag found → **fail** with `<path>:<line>: missing provenance tag`.
3. If multiple tags found → **fail** with `<path>:<line>: multiple tags on one claim`.
4. Validate tag grammar (regex). Bad payload → **fail**.
5. For `[hypothesis:*]` in a customer-facing doc → **fail**.
6. For `[measured:*]` → resolve `artifact-id`. Missing → **fail**.
7. For `[vendor-cited:*]` → resolve against citations source. Missing → **fail**.
8. For `[policy-commitment:*]` → owner in `OWNERS.yaml`? Cadence in allowed list?
   Either failure → **fail**.

### Exit codes

- **0**: all claims pass; print `Claim provenance check passed`.
- **1**: at least one violation; print one line per violation, then exit.

### Implementation hints (non-binding)

- Mirror the structure of `scripts/check_mvp_scope_consistency.py` — the same walk
  and reporting style.
- A YAML or `OWNERS.yaml` parser is required for owner validation; the standard
  library (`yaml` if available, or simple parser) is sufficient.
- The script SHALL NOT make network calls.

## M0 acceptance criteria

The deliverable is accepted when:

1. `scripts/check_claim_provenance.py` exists, is executable, and matches this
   interface.
2. Running the script returns exit 0 against the current repo (i.e., all existing
   quantified claims have valid tags or are removed).
3. The script is exercised in a follow-up commit that adds a CI hook (out of scope
   for this change; tracked as the next M0 follow-up issue).
4. This document (`architecture/claims/claim-provenance.md`) is unchanged from the
   rules established by the OpenSpec change `fix-claim-provenance`.

## Future changes

Adding, removing, or modifying tag formats, claim categories, customer-facing
classification rules, or the script interface SHALL go through a `MODIFIED
Requirements` OpenSpec change against the `claim-provenance` capability. Direct
edits to this file without a corresponding spec change SHALL be rejected at
review.
