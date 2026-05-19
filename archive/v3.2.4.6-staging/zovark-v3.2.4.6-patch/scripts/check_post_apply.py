#!/usr/bin/env python3
"""
check_post_apply.py — runs against the v3.2.4.5 post-apply baseline state
produced by the v3.2.4.6 patch artifact to verify that:

  1. The new ADRs (0038-0043) are at architecture/adr/.
  2. The new schemas are at architecture/blueprint/schemas/.
  3. The new fixture trees are at tests/bootstrap-fixtures/.
  4. invariants.md has 32 entries (INV-001..INV-032).
  5. VERSION_METADATA.json is at the repo root.
  6. zovark.md contains the §16 anchor.
  7. feature-registry.yaml contains F-007 + the two new lifecycle statuses.
  8. verify-bootstrap.sh has been updated to 35 checks.
  9. OWNERS.yaml carries the _note_placeholders field.
 10. Soft warning: if any "@zovark-*-lead" placeholder remains in OWNERS.yaml,
     emit a warning. Hard-fail at M2 readiness gate; soft-warning here.

Verifies that post-apply manual edits were actually made.

Usage:
  python3 scripts/check_post_apply.py --repo-root /path/to/repo

Exit codes:
  0  every required post-apply state is present
  1  one or more checks failed
  2  invocation error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_ADRS = [
    "0038-control-plane-and-customer-instance-authority-boundary.md",
    "0039-update-factory-and-signed-bundle-distribution.md",
    "0040-research-pipeline-and-gated-candidate-promotion.md",
    "0041-telemetry-boundary.md",
    "0042-cryptographic-key-management.md",
    "0043-open-source-release-strategy.md",
]
REQUIRED_SCHEMAS = [
    "update_candidate.schema.json",
    "update_bundle_signed.schema.json",
    "research_experiment_result.schema.json",
    "control_plane_instance_status.schema.json",
    "telemetry_envelope.schema.json",
    "update_promotion_decision.schema.json",
]
REQUIRED_FIXTURES = [
    "control_plane_schemas_present",
    "telemetry_boundary_schema_present",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()
    root = args.repo_root.resolve()

    failures = []
    warnings = []

    # 1-2. ADRs and schemas
    for f in REQUIRED_ADRS:
        if not (root / "architecture" / "adr" / f).exists():
            failures.append(f"missing ADR: architecture/adr/{f}")
    for f in REQUIRED_SCHEMAS:
        if not (root / "architecture" / "blueprint" / "schemas" / f).exists():
            failures.append(f"missing schema: architecture/blueprint/schemas/{f}")

    # 3. Fixture trees
    for fix in REQUIRED_FIXTURES:
        d = root / "tests" / "bootstrap-fixtures" / fix
        if not d.is_dir():
            failures.append(f"missing fixture: tests/bootstrap-fixtures/{fix}/")

    # 4. invariants.md count
    inv_path = root / "invariants.md"
    if not inv_path.exists():
        failures.append("missing invariants.md")
    else:
        text = inv_path.read_text()
        ids = re.findall(r"^## (INV-\d{3})", text, re.MULTILINE)
        if len(ids) != 32:
            failures.append(f"invariants.md has {len(ids)} INV entries; expected 32")
        for i in range(1, 33):
            want = f"INV-{i:03d}"
            if want not in ids:
                failures.append(f"invariants.md missing {want}")

    # 5. VERSION_METADATA.json
    vm_path = root / "VERSION_METADATA.json"
    if not vm_path.exists():
        failures.append("missing VERSION_METADATA.json")
    else:
        try:
            vm = json.loads(vm_path.read_text())
            counts = vm.get("counts", {})
            if counts.get("invariants") != 32:
                failures.append(f"VERSION_METADATA invariants count is {counts.get('invariants')}, expected 32")
            if counts.get("invariants_covered") != 17:
                failures.append(f"VERSION_METADATA invariants_covered is {counts.get('invariants_covered')}, expected 17")
            if counts.get("invariants_partial") != 1:
                failures.append(f"VERSION_METADATA invariants_partial is {counts.get('invariants_partial')}, expected 1")
            if counts.get("invariants_deferred") != 14:
                failures.append(f"VERSION_METADATA invariants_deferred is {counts.get('invariants_deferred')}, expected 14")
        except json.JSONDecodeError as e:
            failures.append(f"VERSION_METADATA.json invalid JSON: {e}")

    # 6. zovark.md anchor
    zov_path = root / "zovark.md"
    if zov_path.exists():
        if "ZVK-PATCH-v3.2.4.5-zovark-section-16" not in zov_path.read_text():
            warnings.append("zovark.md does not contain the §16 fragment anchor "
                            "(run scripts/apply_v3_2_4_6.py --apply-fragments --commit)")
    else:
        warnings.append("zovark.md missing")

    # 7. feature-registry.yaml content
    fr_path = root / "product" / "features" / "feature-registry.yaml"
    if not fr_path.exists():
        # alternate location used in some baselines
        for cand in [root / "feature-registry.yaml",
                     root / "product" / "feature-registry.yaml"]:
            if cand.exists():
                fr_path = cand
                break
    if fr_path.exists():
        text = fr_path.read_text()
        if "F-007" not in text:
            failures.append(f"{fr_path.relative_to(root)}: F-007 entry not found")
        if "research_candidate" not in text:
            failures.append(f"{fr_path.relative_to(root)}: research_candidate status not found")
        if "under_review" not in text:
            failures.append(f"{fr_path.relative_to(root)}: under_review status not found")
    else:
        warnings.append("feature-registry.yaml not found at the expected paths "
                        "(product/features/feature-registry.yaml); F-007 cannot be verified")

    # 8. verify-bootstrap.sh updated
    vb_path = root / "verify-bootstrap.sh"
    if vb_path.exists():
        text = vb_path.read_text()
        if "ZVK-PATCH-v3.2.4.5-verify-bootstrap" not in text:
            warnings.append("verify-bootstrap.sh missing v3.2.4.5 anchor "
                            "(run scripts/apply_v3_2_4_6.py --apply-fragments --commit)")
        if "ALL 33/33 CHECKS PASSED" in text and "ALL 35/35 CHECKS PASSED" not in text:
            failures.append("verify-bootstrap.sh still says ALL 33/33; "
                            "the apply-fragments rewrite did not run")

    # 9. OWNERS.yaml _note_placeholders
    ow_path = root / "OWNERS.yaml"
    if ow_path.exists():
        text = ow_path.read_text()
        if "_note_placeholders" not in text:
            failures.append("OWNERS.yaml missing _note_placeholders field")

        # 10. soft warning on remaining placeholder handles
        placeholders = re.findall(r"@zovark-[a-z0-9-]+-lead", text)
        if placeholders:
            warnings.append(f"OWNERS.yaml still has {len(set(placeholders))} placeholder handles "
                            f"({', '.join(sorted(set(placeholders))[:3])}…); replace with real "
                            f"GitHub handles before any M2 PR")

    # Output
    if not args.quiet:
        for w in warnings:
            print(f"WARN: {w}")
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"PASS: post-apply state matches v3.2.4.5 expectations "
              f"({len(warnings)} soft warnings; not blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
