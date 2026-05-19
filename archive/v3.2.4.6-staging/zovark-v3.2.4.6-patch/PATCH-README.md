# PATCH-README — applying v3.2.4.6 on top of v3.2.3.5

## What you have

- v3.2.3.5 frozen baseline. Stable report hash: `5b3feedf2522d08c02b6f29cba803dd0577d39ef4f0c1a211d56bf7cf3c121a3`.
- This patch zip: `zovark-v3.2.4.6-patch.zip` (with companion `.sha256` file).

## What is in this patch

```
zovark-v3.2.4.6-patch/
  PATCH-README.md
  PATCH-MANIFEST.json                                  (every file + sha256, source of truth for apply_mode)
  ENGINEERING-READY-HANDOFF.md                         (engineering start document)
  ZOVARK-v3.2.4.6-FINAL.md                             (current engineering-ready companion)
  VERSION_METADATA.json                                (corrected counts: 17+1+14=32)
  OWNERS.yaml                                          (with _note_placeholders)
  invariants.md                                        (32 entries, version v3.2.4.5; v3.2.4.6 patch package)
  SECURITY-VULN-DISCLOSURE.md
  DD_BLOCKERS-v3.2.4.5-additions.md                    (M1-DECISION-001 + M3-DEPENDENCY-002)
  architecture/
    source-of-truth.md                                 (conflict-resolution hierarchy)
    adr-index.md                                       (ADR inventory for patch-shipped ADRs)
    mvp-scope.md                                       (product wedge and MVP boundary)
    customer-validation-workflow.md                    (design-partner validation scorecard)
    disaster-recovery-restore-gap.md                   (restore-gap semantics)
    claims/claim-provenance.md                         (claim provenance convention)
    telemetry-justification.md
    adr/
      0038-control-plane-and-customer-instance-authority-boundary.md
      0039-update-factory-and-signed-bundle-distribution.md
      0040-research-pipeline-and-gated-candidate-promotion.md
      0041-telemetry-boundary.md
      0042-cryptographic-key-management.md            (REWRITTEN: key compromise transition)
      0043-open-source-release-strategy.md            (PROPOSED-STRATEGIC-PIVOT marker; stale count removed)
    blueprint/schemas/
      update_candidate.schema.json
      update_bundle_signed.schema.json                (TIGHTENED: distinct signing roles)
      research_experiment_result.schema.json
      control_plane_instance_status.schema.json
      telemetry_envelope.schema.json                  (TIGHTENED: payload_kind→payload binding)
      update_promotion_decision.schema.json           (TIGHTENED: tier role composition + soak)
      examples/
        update_candidate.{pass,fail}.json
        update_bundle_signed.{pass,fail,fail_same_role}.json     (NEW: fail_same_role)
        research_experiment_result.{pass,fail}.json
        control_plane_instance_status.{pass,fail}.json
        telemetry_envelope.{pass,fail,fail_kind_mismatch}.json  (NEW: fail_kind_mismatch)
        update_promotion_decision.{pass,fail,fail_tier3_no_security,fail_tier3_short_soak}.json  (NEW: 2 fail variants)
  scripts/
    apply_v3_2_4_6.py                                  (manifest-driven; no hard-coded internal-file list)
    check_patch_self_test.py
    check_release_metadata_consistency_v3245.py        (verifies invariant arithmetic)
    check_control_plane_schemas_present.py
    check_telemetry_boundary_schema_present.py         (UPDATED: data-shape vs constraint-matcher)
    check_post_apply.py                                (NEW: verifies post-apply state)
    jsonschema_minimal.py                              (UPGRADED: contains/minContains/maxContains)
    run_shiptime_tests.sh
  patches/
    feature-registry.yaml.append_v3_2_4_5              (F-007 + 2 new lifecycle statuses)
    verify-bootstrap.sh.append_v3_2_4_5                (2 new check invocations + 33→35 rewrite)
    zovark.md.append_v3_2_4_5                          (§16 Future Direction)
  tests/bootstrap-fixtures/
    control_plane_schemas_present/{fixture.config, pass.fixture/, fail.fixture/}
    telemetry_boundary_schema_present/{fixture.config, pass.fixture/, fail.fixture/}
  ops/compliance/
    v3.2.4.6-shiptime-transcript.txt                   (regenerated AFTER manifest finalized)
```

## Apply procedure

### Step 1 — Verify baseline

```bash
unzip zovark-v3.2.4.6-patch.zip -d /tmp/

python3 /tmp/zovark-v3.2.4.6-patch/scripts/apply_v3_2_4_6.py \
  --repo-root /path/to/zovark-v1-bootstrap-v3.2.3.5 \
  --patch-root /tmp/zovark-v3.2.4.6-patch \
  --verify-baseline
```

Expect:
- `PASS: baseline stable report hash matches v3.2.3.5`
- `=== ALL 33/33 CHECKS PASSED ===`
- `Total: 53  Passed: 53  Failed: 0`

### Step 2 — Verify the patch itself

```bash
python3 /tmp/zovark-v3.2.4.6-patch/scripts/apply_v3_2_4_6.py \
  --patch-root /tmp/zovark-v3.2.4.6-patch \
  --verify-patch-tree-hash
```

Expect: `PASS: <N> files in tree, <N> files in manifest, all hashes match`.

### Step 3 — Dry-run

```bash
python3 /tmp/zovark-v3.2.4.6-patch/scripts/apply_v3_2_4_6.py \
  --repo-root /path/to/zovark-v1-bootstrap-v3.2.3.5 \
  --patch-root /tmp/zovark-v3.2.4.6-patch \
  --apply
```

This prints what would happen. No files are written.

### Step 4 — Commit (copy files)

```bash
python3 /tmp/zovark-v3.2.4.6-patch/scripts/apply_v3_2_4_6.py \
  --repo-root /path/to/zovark-v1-bootstrap-v3.2.3.5 \
  --patch-root /tmp/zovark-v3.2.4.6-patch \
  --apply --commit
```

Files with `apply_mode: copy` in the manifest are copied. Files with `apply_mode: patch-internal` (manifest, FIXES doc, apply script itself, transcript, etc.) stay inside the patch. **There is no hard-coded list — the manifest is the source of truth.**

### Step 5 — Apply anchored fragments

```bash
python3 /tmp/zovark-v3.2.4.6-patch/scripts/apply_v3_2_4_6.py \
  --repo-root /path/to/zovark-v1-bootstrap-v3.2.3.5 \
  --patch-root /tmp/zovark-v3.2.4.6-patch \
  --apply-fragments --commit
```

This idempotently appends fragments to `zovark.md`, `verify-bootstrap.sh`, and `feature-registry.yaml`, anchored on tags like `ZVK-PATCH-v3.2.4.5-zovark-section-16`. Re-running is safe; if the anchor is already present, the fragment is skipped.

### Step 6 — Remaining manual edits

Three remaining manual edits (small, deterministic):

1. Append the body of `DD_BLOCKERS-v3.2.4.5-additions.md` into your repo's `DD_BLOCKERS.md` under a new heading. (M1-DECISION-001 + M3-DEPENDENCY-002.)
2. Update `MANIFEST.md` and `README.md` version strings from `v3.2.3.5` to `v3.2.4.5`.
3. Regenerate `adrs.md` using your baseline's `adr-splitter` tool.

These edits remain explicit because the affected files live in the predecessor baseline.

### Step 7 — Post-apply verification

```bash
python3 /tmp/zovark-v3.2.4.6-patch/scripts/check_post_apply.py \
  --repo-root /path/to/zovark-v1-bootstrap-v3.2.3.5
```

Expect: `PASS: post-apply state matches v3.2.4.5 expectations`. Soft warnings on `@zovark-*-lead` placeholder handles in `OWNERS.yaml` are not blocking; replace before any M2 PR.

### Step 8 — Run gates from post-apply repo

```bash
cd /path/to/zovark-v1-bootstrap-v3.2.3.5
bash verify-bootstrap.sh                              # expect 35/35 PASS
bash scripts/bootstrap-acceptance.sh                  # expect 55/55 PASS
```

Capture both outputs to `ops/compliance/v3.2.4.5-clean-rerun-transcript.txt` and commit. The `v3.2.4.6` transcript in this patch covers the patch artifact before apply; the `v3.2.4.5` transcript covers the post-apply baseline state.

### Step 9 — Tag (DO NOT skip)

Before tagging `v3.2.4.5-bootstrap-baseline`:

1. Step 8 transcript is committed.
2. M1-DECISION-001 (founder sign-off on ADR-0043) is resolved.
3. The new stable report hash is recorded in `M1-COMPLETION-CRITERIA.md`.

Then:

```bash
git tag v3.2.4.5-bootstrap-baseline
```

Until those conditions hold, v3.2.3.5 remains the working baseline.

## Verification of this patch zip

```bash
sha256sum zovark-v3.2.4.6-patch.zip
# compare to zovark-v3.2.4.6-patch.zip.sha256
```

## What this patch does NOT do

- Does not introduce new ADRs (still ADR-0038 through ADR-0043).
- Does not introduce new invariants (still INV-001 through INV-032).
- Does not introduce ADR-0044..0051.
- Does not require pip dependencies (validator is in-tree pure stdlib).
- Does not auto-modify your existing v3.2.3.5 files except via the explicit `--apply-fragments` mode that uses anchored idempotent appends.
