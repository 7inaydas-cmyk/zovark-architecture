## Context

The script's interface contract was locked by `fix-claim-provenance` in rc2 (archived as `2026-05-01-fix-claim-provenance`). This change implements it. While implementing, two pre-existing inconsistencies between the spec and actual patch-tree usage surfaced and need to be codified.

## Goals / Non-Goals

**Goals:**

- A single Python script (`scripts/check_claim_provenance.py`) that runs in the repo, requires no third-party dependencies, mirrors `check_mvp_scope_consistency.py`'s style, and exits 0 against the current state.
- Update the spec to reflect actual cadence and owner usage in the patch tree (this is descriptive, not aspirational — patch-tree tags already use the values).
- Document explicit walk exclusions (`architecture/claims/`, `LICENSE-*`, `architecture/review/`, `openspec/changes/archive/`) so reviewers know why those paths aren't scanned.

**Non-Goals:**

- Wiring the script into CI / pre-commit. Tracked as a separate M0 follow-up.
- Inventing new tag formats or claim categories.
- Re-tagging existing claims. The script passes on existing tags after the spec update — so no re-tagging needed.
- Resolving why `OWNERS.yaml` is missing roles that ADRs reference. The bootstrap-pending allowlist is the explicit accommodation; full registration lands at M2.

## Decisions

### Walk exclusions

The script skips:

- `architecture/claims/` and the patch-tree mirror at
  `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/claims/`. These documents define the rules; their illustrative tags aren't asserted claims.
- `architecture/review/`. Review docs (checklist, scorecard, decision log, ledger) describe and track issues; they don't assert architecture claims.
- `openspec/changes/archive/`. Archived change content has been promoted to specs; re-walking it surfaces duplicates.
- `LICENSE-*`. Legal text that triggers some quantified-claim category words (e.g., "purpose" matches "rpo" via substring without word boundaries) but isn't architecture content.

Word-boundary matching on single-word categories (`\brpo\b` not substring) is used to avoid false positives like "purpose" matching "rpo".

**Rationale.** The exclusions are obvious from a code-reviewer perspective and surface the design intent. Alternative considered: in-document marker like `<!-- claim-provenance:skip -->`. Rejected — adds doc churn for marginal benefit; explicit exclusion list is simpler.

### Cadence allowlist expansion

The spec's original six cadences were: `daily`, `weekly`, `monthly`, `quarterly`, `semiannual-review`, `annual-review`. The patch tree uses an additional eight values:

- Periodic: `quarterly-review` (the patch tree's preferred form vs. bare `quarterly`).
- Event-driven: `release-review`, `milestone-review`, `per-release-review`, `per-promotion-review`, `per-advisory-review`, `per-change-review`, `incident-review`.

This change expands the allowlist via `MODIFIED Requirements`. Adding more cadences in the future requires another `MODIFIED Requirements` change.

**Rationale.** The patch tree's usage is reasonable (event-driven cadences capture "review on every X" semantics). Updating the spec to match is more honest than rejecting half the tags in patch tree. Alternative considered: rewrite patch-tree tags to use the original six. Rejected — that's wholesale doc churn for marginal benefit; the patch tree's vocabulary is sound.

### Bootstrap-pending owner roles

The patch tree references owner roles `product-owner`, `support-owner`, `release-engineering`, and `research-owner`. None are declared in `OWNERS.yaml`'s `roles:` section. `OWNERS.yaml` itself notes that role registration is M2 work.

This change codifies a `BOOTSTRAP_PENDING_OWNERS` allowlist in the script:

```
BOOTSTRAP_PENDING_OWNERS = {
    "product-owner", "support-owner",
    "release-engineering", "research-owner",
}
```

The MODIFIED Requirements update permits owners in this allowlist as well as those in `OWNERS.yaml`. Post-M2, when these roles are registered in `OWNERS.yaml`, the allowlist can collapse to empty — but the script change is a follow-up, not part of this change.

**Rationale.** Modifying patch-tree `OWNERS.yaml` to add the missing roles is an alternative that respects the spec exactly. Rejected for now: `OWNERS.yaml` is part of an immutable bootstrap baseline managed by the M1-CI-009 process, and adding placeholder roles outside that process would diverge the patch from its baseline. The codified allowlist is auditable and time-boxed (M2 closes it).

### Placeholder payload skip

Tags with payloads in a small placeholder set (`<owner>,<review-cadence>`, `artifact-id,YYYY-MM-DD`, etc.) are skipped at validation time. These appear in template / snippet text inside rules docs and aren't asserted claims.

**Rationale.** The exclusions list above (paths) catches most placeholder tags. The payload-set check is a belt-and-suspenders for any straggler that lives in a non-excluded path. Alternative considered: detect "code block" context. Rejected — adds parse complexity for marginal benefit.

### Pass-1 / Pass-2 division

- Pass 1 walks every tag and validates the payload (kind, grammar, owner, cadence, artifact resolution, customer-facing-no-hypothesis).
- Pass 2 walks every line, finds quantified claims (category keyword + unit-bearing number), and confirms a tag is on the same line or the next.

Splitting pass 1 / pass 2 catches malformed tags even on lines that aren't quantified claims, which the spec explicitly requires.

## Risks / Trade-offs

- **Risk:** the cadence allowlist becomes a kitchen sink. → **Mitigation:** the list is enumerated, not regex-permissive; new values require a `MODIFIED Requirements` change.
- **Risk:** `BOOTSTRAP_PENDING_OWNERS` becomes permanent. → **Mitigation:** documented as M2-collapse; rc4 or M2 milestone review re-evaluates.
- **Trade-off:** word-boundary category matching may miss some claim phrasings ("RPOs are tight at 200ms" — plural). Accepted: false negatives are better than false positives in the bootstrap state; the M0 acceptance criterion is "passes against current repo," and the script passes.

## Migration Plan

1. Add `scripts/check_claim_provenance.py`.
2. Run it; confirm clean exit.
3. Update spec via this change's `MODIFIED Requirements`.
4. Archive.
5. Update issue ledger ARCH-P1-001 with implementation note (status remains `fixed`).

**Rollback:** revert. The M0 deliverable is undelivered.

## Open Questions

- Should the script support a `--strict` flag that fails on bootstrap-pending owners? Defer — useful when `OWNERS.yaml` is fully populated.
- Should the script learn frontmatter `customer_facing: false` overrides? Already supported (frontmatter parsing checks for `customer_facing: true`; absent flag is treated as not customer-facing per heuristics).
