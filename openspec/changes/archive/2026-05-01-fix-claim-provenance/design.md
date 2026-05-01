## Context

`invariants.md` INV-022 and `ENGINEERING-READY-HANDOFF.md` reference `scripts/check_claim_provenance.py` as an M0 deliverable. The patch-tree `claim-provenance.md` documents the four allowed provenance tags and rules. The root `architecture/claims/claim-provenance.md` is empty. Without consolidating rules in the root and specifying the script's contract, the M0 deliverable is under-defined and the rc2 finalization category stays FAIL.

This change is a documentation-only consolidation. It creates the source-of-truth rules document, locks in the script's interface, and writes formal acceptance criteria — but does not implement the script.

## Goals / Non-Goals

**Goals:**

- One authoritative claim-provenance rules document at `architecture/claims/claim-provenance.md`.
- A spec capturing the rules and the script interface so future changes are traceable.
- M0 acceptance criteria precise enough that an engineer can implement the script in a single sitting without further design questions.
- Cover the full doc set: architecture/, zovark-v3.2.4.6-engineering-ready/, ADRs, customer-facing docs.

**Non-Goals:**

- Implementing the checker.
- Adding new tag formats beyond the four already documented in the patch tree.
- Inventing new "customer-facing" categories — the existing classification is preserved.
- Changing claim coverage (which claim categories are required to carry tags) — the existing list is preserved.
- Wiring the checker into CI.

## Decisions

### Source-of-truth location

The root `architecture/claims/claim-provenance.md` is the single source of truth. The patch-tree `claim-provenance.md` becomes a snapshot/predecessor and may diverge in future patch versions, but the root rules govern.

**Rationale.** The finalization repo is the canonical authority per `architecture/source-of-truth.md`'s hierarchy. Future patches should be expected to reference the root rules, not to maintain their own copy. Alternative considered: leave rules only in the patch tree. Rejected — would force every future change to know which patch version to consult.

### Tag grammar

The four tag formats are preserved verbatim:

- `[hypothesis:evidence-milestone]`
- `[measured:artifact-id,YYYY-MM-DD]`
- `[vendor-cited:citation-id]`
- `[policy-commitment:owner,review-cadence]`

**Rationale.** Tags already appear in the patch tree's ADRs (e.g., ADR-0042 uses `[policy-commitment:security-officer,semiannual-review]`). Changing the grammar would require sweeping rewrites across ADRs and break existing tag usage. Alternative considered: simplify to two tag types. Rejected — the four-way distinction (hypothesis vs. measured vs. vendor-cited vs. policy-commitment) carries meaningful semantics for review.

### What counts as a "quantified claim"

Any claim about: latency, throughput, capacity, queue depth, false-positive rate, RPO, RTO, support response time, patch response time, retention period, schedule duration, cost, reliability, availability, accuracy, or precision. The full enumeration is in the rules document.

**Rationale.** Enumeration is concrete and auditable. Alternative considered: detect via regex (numeric + unit). Rejected — produces too many false positives on non-claim content (e.g., "12-column table"). Enumeration of categories paired with regex of numeric tokens within those categories is the script's job.

### Script interface

`scripts/check_claim_provenance.py` is specified to:

- Walk: `architecture/**/*.md`, `zovark-v3.2.4.6-engineering-ready/**/*.md`, top-level `*.md`.
- Skip: `openspec/changes/archive/**`, `architecture/review/**` (the review docs themselves describe the rule, not assert claims).
- For each document, partition lines into "customer-facing" or "internal" based on a frontmatter or heading marker.
- Find quantified claims using a category list + numeric/unit regex.
- For each claim, verify exactly one tag appears within the same line or the immediately following sentence.
- Reject `[hypothesis:*]` in customer-facing docs.
- Verify `[measured:*]` artifact IDs exist as files under `architecture/`, `tests/`, or `ops/`.
- Verify `[policy-commitment:*]` owner is a known role from `OWNERS.yaml`.
- Exit 0 if clean; exit 1 with a failure list otherwise.

**Rationale.** This interface mirrors `scripts/check_mvp_scope_consistency.py` (already in the repo) — same walk-and-grep style, same exit-code convention. Alternative considered: structured-AST parsing of markdown. Rejected — adds dependency surface (`mistune`/`commonmark`) without enough payoff for the M0 scope.

### Customer-facing classification

A document is "customer-facing" if either:

- It declares `customer_facing: true` in YAML frontmatter, OR
- Its top-level heading text contains "Customer", "User", "Operator Guide", "Public", or "Onboarding" tokens, OR
- Its path matches `architecture/customer-*.md` or `architecture/handoff/**/*.md`.

A document is "internal" otherwise.

**Rationale.** Frontmatter is the canonical signal; the heuristics catch existing docs that don't yet have frontmatter. Alternative considered: a manifest file listing customer-facing docs. Rejected — requires manual maintenance and gets stale.

### M0 acceptance criteria

The deliverable is accepted when:

1. `scripts/check_claim_provenance.py` exists, is executable, and matches the interface in this spec.
2. Running the script returns exit 0 against the current repo (i.e., all existing claims have tags or are removed).
3. The script is wired into a pre-commit or CI step (out of scope for this change but tracked as the next M0 follow-up).
4. `architecture/claims/claim-provenance.md` is unchanged from the rules established by this change.

## Risks / Trade-offs

- **Risk:** the four-tag grammar is rigid and might not fit a future claim category. → **Mitigation:** new tag formats land via a `MODIFIED Requirements` change against `claim-provenance` spec; rejection mode is explicit, not silent.
- **Risk:** the enumeration of "quantified claim categories" misses something. → **Mitigation:** misses surface as missing tags during M0 implementation; tracked as follow-up issues against the spec.
- **Trade-off:** the customer-facing heuristic catches existing docs but may over-classify. Accepted: false positives produce a tag prompt, not a runtime failure. Reviewer can override per-doc with frontmatter.

## Migration Plan

1. Write `architecture/claims/claim-provenance.md` with the rules + script interface contract.
2. Capture as `openspec/specs/claim-provenance/spec.md` via change archive.
3. Update the issue ledger: ARCH-P1-001 status `fixed` (rules + spec); add a follow-up note that `scripts/check_claim_provenance.py` remains the M0 deliverable.
4. Close GitHub #2.

**Rollback:** revert the commit. The rules go back to patch-tree-only.

## Open Questions

- Where does the customer-facing manifest live if the heuristic is too coarse? Defer: not blocking until the M0 implementation surfaces concrete cases.
- Does `[measured:*]` need to verify artifact freshness (i.e., `YYYY-MM-DD` not older than N months)? Defer: out of scope for M0; track as a possible enhancement.
