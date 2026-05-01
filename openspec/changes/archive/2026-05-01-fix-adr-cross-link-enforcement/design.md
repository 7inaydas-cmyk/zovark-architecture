## Context

The rc2 spec `adr-cross-link-verification` describes post-apply verification: walk the full ADR set, check existence, status, and INV-ID non-contradiction for the 8 enumerated baseline ADRs (0011, 0024, 0025, 0027, 0028, 0030, 0031, 0034). The bootstrap repo doesn't contain those baseline ADRs (they're in v3.2.3.5). Without a documented mode for "pre-apply state," running the script in this repo would always fail.

This change adds an explicit **bootstrap mode** to the script's behavior and codifies it in the spec via a `MODIFIED Requirements` block.

## Goals / Non-Goals

**Goals:**

- Auto-detect mode based on whether `architecture/adr/` at the repo root contains baseline ADRs (numeric prefix < 38).
- Bootstrap mode passes when the index has the right placeholder section + IDs and the patch ADRs 0038-0043 are present.
- Post-apply mode runs the full verification per the existing spec.
- The same script binary works in both modes — operators don't pick a flag.

**Non-Goals:**

- Producing baseline ADRs in this tree.
- Semantic-level contradiction detection (still future work).
- Wiring into CI.
- Cross-version baseline pinning (separate concern).

## Decisions

### Mode detection

```
post-apply  if `architecture/adr/` exists at repo root and contains
            at least one ADR file with a numeric prefix < 38
bootstrap   otherwise
```

**Rationale.** Numeric prefix < 38 is the unambiguous signal that the baseline (0001-0037) has been merged. Alternative considered: a CLI flag `--mode`. Rejected — operators forget flags; auto-detection from filesystem state is robust.

### Bootstrap-mode checks

Four structural checks:

1. `architecture/adr-index.md` exists.
2. The string `"Baseline ADRs (post-apply verified)"` appears in the index.
3. All 8 enumerated baseline ADR IDs appear somewhere in the index.
4. Patch ADRs 0038-0043 each have a file under
   `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/adr/`.

If all four pass, exit 0 with a summary banner. The bootstrap-mode message explicitly lists the baseline ADRs awaiting verification — reviewers see exactly what the post-apply step still needs to confirm.

**Rationale.** Bootstrap-mode is verifying that "we did the right pre-apply preparation." The four checks correspond to the deliverables that fix-adr-cross-link-verification (rc2) was supposed to produce. Anyone removing the placeholder section or the patch ADRs trips the check immediately.

### Post-apply-mode checks

Mirrors the existing spec's contract verbatim:

1. For each enumerated baseline ADR ID: file present, status valid, status not in `{superseded, rejected, historical}`.
2. INV-ID gathering across patch + baseline ADRs (informational at this stage; same-INV-ID multi-ADR references logged but not auto-failure — semantic contradiction detection is a future enhancement).
3. Write `architecture/adr-index.draft.md` enriched with status from each verified baseline ADR.

**Rationale.** The post-apply behavior is what the existing spec required. This change does NOT modify it; it only adds the bootstrap-mode counterpart.

### No third-party deps

The script uses only stdlib. Mirrors `check_mvp_scope_consistency.py` and `check_claim_provenance.py` in style.

**Rationale.** Architecture-tooling scripts shouldn't pull in dependencies. Spec parsing uses regex; YAML parsing isn't needed.

## Risks / Trade-offs

- **Risk:** an operator pulls a partial baseline (some 0001-0037 ADRs missing) and the script flips to post-apply mode and reports many missing ADRs as failures. → **Acceptable.** This is exactly what the script should do — partial baseline is broken. The failure list shows them which ADRs are missing.
- **Risk:** the bootstrap-mode banner gives a false sense of completeness. → **Mitigation:** the banner explicitly says "awaiting post-apply verification" and lists the IDs.
- **Trade-off:** semantic contradiction detection deferred. Accepted per the spec's open question.

## Migration Plan

1. Add `scripts/check_adr_cross_links.py`.
2. Run it in current state; verify bootstrap-mode pass.
3. Update spec via this change's `MODIFIED Requirements`.
4. Archive.

**Rollback:** revert.

## Open Questions

(none — bootstrap-mode is the only new addition)
