#!/usr/bin/env python3
"""
check_control_plane_schemas_present.py

Verifies that the six v3.2.4.4 control-plane / update / research schemas are
present at architecture/blueprint/schemas/ and parse as valid JSON Schema
documents carrying the metadata triple (x-zovark-license,
x-zovark-open-source, x-zovark-publication).

Fixture mode (--fixture-root <dir>): operates against the fixture tree
rather than the repo root. The fixture tree must reproduce the failing or
passing state under test. There is NO marker that short-circuits the check;
it inspects actual files.

Exit codes:
  0  all six schemas present and well-formed
  1  one or more schemas missing, malformed, or missing metadata
  2  invocation error
"""
from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

EXPECTED_SCHEMAS = [
    "update_candidate.schema.json",
    "update_bundle_signed.schema.json",
    "research_experiment_result.schema.json",
    "control_plane_instance_status.schema.json",
    "telemetry_envelope.schema.json",
    "update_promotion_decision.schema.json",
]

REQUIRED_METADATA = ("x-zovark-license", "x-zovark-open-source", "x-zovark-publication")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture-root", type=Path, default=None,
                   help="Path to fixture root (overrides repo root).")
    p.add_argument("--repo-root", type=Path, default=Path("."),
                   help="Repo root (default: cwd).")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    root = args.fixture_root if args.fixture_root else args.repo_root
    schema_dir = root / "architecture" / "blueprint" / "schemas"

    if not schema_dir.is_dir():
        print(f"FAIL: schema dir does not exist: {schema_dir}", file=sys.stderr)
        return 1

    failures = []
    for name in EXPECTED_SCHEMAS:
        path = schema_dir / name
        if not path.exists():
            failures.append(f"missing: {name}")
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            failures.append(f"invalid JSON: {name}: {e}")
            continue
        if not isinstance(doc, dict):
            failures.append(f"not an object: {name}")
            continue
        if doc.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(f"wrong $schema: {name} (expected draft 2020-12)")
        for key in REQUIRED_METADATA:
            if key not in doc:
                failures.append(f"missing metadata {key}: {name}")
        if doc.get("additionalProperties") is not False:
            failures.append(f"missing additionalProperties: false at root: {name}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"PASS: all {len(EXPECTED_SCHEMAS)} schemas present, well-formed, with metadata triple")
    return 0


if __name__ == "__main__":
    sys.exit(main())
