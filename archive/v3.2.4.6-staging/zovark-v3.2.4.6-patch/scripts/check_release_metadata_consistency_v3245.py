#!/usr/bin/env python3
"""
check_release_metadata_consistency_v3245.py

Verifies that VERSION_METADATA.json's claimed counts match the actual patch
contents, the v3.2.3.5 baseline counts, AND its own internal arithmetic.

Specifically:
  * counts.invariants == covered + partial + deferred
  * counts.invariants_deferred == len(deferred_invariants list)

Plus version-domain cross-checks:
  * VERSION_METADATA.json says current_version is "v3.2.4.6"
  * invariants.md heading says "Version: v3.2.4.5" because it describes
    the post-apply baseline state produced by this patch artifact

Plus structural checks:
  * patch tree has exactly 6 ADRs and 6 schemas (this patch's additions)
  * baseline hash claim matches v3.2.3.5 frozen value

Counts checked (post-apply state):
  ADRs                 = 37 (baseline) + 6 (patch new) = 43
  Invariants           = 28 (baseline) + 4 (patch new) = 32
    Covered            = 17
    Partial            = 1   (INV-001)
    Deferred           = 14
  Schemas              = 17 (baseline) + 6 (patch new) = 23
  Features             = 6 (baseline) + 1 (patch new) = 7
  Lifecycle statuses   = 8
  Verify checks        = 33 (baseline) + 2 (patch smoke gates) = 35
  Bootstrap fixtures   = 53 (baseline) + 2 (patch fixture pairs) = 55

Exit codes:
  0  all consistent
  1  one or more drift conditions
  2  invocation error
"""
from __future__ import annotations

import json
import re
import sys
import argparse
from pathlib import Path


V3_2_3_5_BASELINE = {
    "adrs": 37,
    "invariants": 28,
    "schemas": 17,
    "features": 6,
    "verify_checks": 33,
    "bootstrap_fixtures": 53,
    "stable_report_hash": "5b3feedf2522d08c02b6f29cba803dd0577d39ef4f0c1a211d56bf7cf3c121a3",
}

V3_2_4_5_ADDS = {
    "adrs": 6,
    "invariants": 4,
    "schemas": 6,
    "features": 1,
    "verify_checks": 2,
    "bootstrap_fixtures": 2,
}

EXPECTED = {k: V3_2_3_5_BASELINE[k] + V3_2_4_5_ADDS[k] for k in V3_2_4_5_ADDS}
EXPECTED["lifecycle_statuses"] = 8
EXPECTED_PARTIAL = 1     # INV-001
EXPECTED_COVERED = 17
EXPECTED_DEFERRED = 14


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--patch-root", type=Path, default=Path("."))
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    vm_path = args.patch_root / "VERSION_METADATA.json"
    if not vm_path.exists():
        print(f"FAIL: VERSION_METADATA.json missing at {vm_path}", file=sys.stderr)
        return 1
    try:
        vm = json.loads(vm_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: VERSION_METADATA.json is not valid JSON: {e}", file=sys.stderr)
        return 1

    failures = []
    counts = vm.get("counts", {})
    for k, expected in EXPECTED.items():
        got = counts.get(k)
        if got != expected:
            failures.append(f"counts.{k}: got {got!r}, expected {expected}")

    # Internal-arithmetic check.
    if counts.get("invariants_covered") != EXPECTED_COVERED:
        failures.append(f"counts.invariants_covered: got {counts.get('invariants_covered')!r}, expected {EXPECTED_COVERED}")
    if counts.get("invariants_partial") != EXPECTED_PARTIAL:
        failures.append(f"counts.invariants_partial: got {counts.get('invariants_partial')!r}, expected {EXPECTED_PARTIAL}")
    if counts.get("invariants_deferred") != EXPECTED_DEFERRED:
        failures.append(f"counts.invariants_deferred: got {counts.get('invariants_deferred')!r}, expected {EXPECTED_DEFERRED}")

    arithmetic = (counts.get("invariants_covered", 0)
                  + counts.get("invariants_partial", 0)
                  + counts.get("invariants_deferred", 0))
    if arithmetic != counts.get("invariants"):
        failures.append(
            f"invariants arithmetic: covered + partial + deferred = "
            f"{counts.get('invariants_covered',0)} + {counts.get('invariants_partial',0)} + "
            f"{counts.get('invariants_deferred',0)} = {arithmetic}, but counts.invariants is "
            f"{counts.get('invariants')!r}"
        )

    # deferred list length must match
    deferred_list = vm.get("deferred_invariants", [])
    if len(deferred_list) != counts.get("invariants_deferred"):
        failures.append(
            f"deferred_invariants list has {len(deferred_list)} entries; "
            f"counts.invariants_deferred says {counts.get('invariants_deferred')}"
        )

    # Cross-check version string
    if vm.get("current_version") != "v3.2.4.6":
        failures.append(f"current_version: got {vm.get('current_version')!r}, expected 'v3.2.4.6'")

    # Cross-check invariants.md
    inv_path = args.patch_root / "invariants.md"
    if inv_path.exists():
        text = inv_path.read_text()
        if "Version:** v3.2.4.5" not in text and "Version: v3.2.4.5" not in text:
            failures.append("invariants.md does not declare Version: v3.2.4.5")
        ids = re.findall(r"^## (INV-\d{3})", text, re.MULTILINE)
        if len(ids) != 32:
            failures.append(f"invariants.md has {len(ids)} INV-* entries; expected 32")

    # Patch-tree contents
    schema_dir = args.patch_root / "architecture" / "blueprint" / "schemas"
    if schema_dir.is_dir():
        actual = sorted(p.name for p in schema_dir.glob("*.schema.json"))
        if len(actual) != V3_2_4_5_ADDS["schemas"]:
            failures.append(f"patch schemas tree has {len(actual)}, want {V3_2_4_5_ADDS['schemas']}")
    adr_dir = args.patch_root / "architecture" / "adr"
    if adr_dir.is_dir():
        actual = sorted(p.name for p in adr_dir.glob("*.md"))
        if len(actual) != V3_2_4_5_ADDS["adrs"]:
            failures.append(f"patch ADRs tree has {len(actual)}, want {V3_2_4_5_ADDS['adrs']}")

    # Baseline hash claim
    if vm.get("previous_baseline_stable_report_hash") != V3_2_3_5_BASELINE["stable_report_hash"]:
        failures.append(
            "previous_baseline_stable_report_hash mismatch: "
            f"got {vm.get('previous_baseline_stable_report_hash')!r}, "
            f"expected {V3_2_3_5_BASELINE['stable_report_hash']!r}"
        )

    # No approximation language
    text = vm_path.read_text()
    for bw in ("approximately", "about ~", "~40", "~55", "~ "):
        if bw in text:
            failures.append(f"VERSION_METADATA.json contains approximate language: {bw!r}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    if not args.quiet:
        for k, v in EXPECTED.items():
            print(f"  {k}: {v}")
        print(f"  invariants_covered: {EXPECTED_COVERED}")
        print(f"  invariants_partial: {EXPECTED_PARTIAL}")
        print(f"  invariants_deferred: {EXPECTED_DEFERRED}")
        print(f"  arithmetic: {EXPECTED_COVERED} + {EXPECTED_PARTIAL} + {EXPECTED_DEFERRED} = {EXPECTED['invariants']}")
        print("PASS: VERSION_METADATA.json consistent with v3.2.3.5 baseline + v3.2.4.6 patch package and self-arithmetic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
