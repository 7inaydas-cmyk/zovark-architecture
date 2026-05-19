#!/usr/bin/env python3
"""
check_patch_self_test.py

Verifies that every file shipped in the patch tree matches its declared
SHA-256 hash in PATCH-MANIFEST.json. This is the structural defense against:

  * file-extraction-format bugs
  * silent file omission
  * silent file modification
  * incomplete manifest claims

The manifest must list EVERY file under the patch root (excluding the
manifest itself and the rerun transcript). Any file present in the tree
but absent from the manifest is a failure. Any manifest entry whose
on-disk SHA-256 does not match is a failure.

Usage:
    python3 scripts/check_patch_self_test.py --patch-root <dir>

Exit codes:
  0  every file in the tree matches the manifest, and vice versa
  1  any drift, missing, or mismatch
  2  invocation error
"""
from __future__ import annotations

import hashlib
import json
import sys
import argparse
from pathlib import Path

# Files excluded from manifest coverage because they wrap the manifest itself.
SELF_EXCLUSIONS = {
    "PATCH-MANIFEST.json",  # contains the hashes; can't self-hash
    "PATCH-MANIFEST.json.sha256",  # informational
}

# Path components that are NEVER part of the patch contents — e.g., Python
# bytecode caches generated at runtime by any of the scripts. Added in
# v3.2.4.6 because run_shiptime_tests.sh on a second run created
# scripts/__pycache__/, which then failed the self-test (files on disk but
# not in PATCH-MANIFEST.json). The runner now also exports
# PYTHONDONTWRITEBYTECODE=1, but this is defense-in-depth: any future caller
# that doesn't set that variable still gets a clean self-test.
IGNORED_PATH_COMPONENTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--patch-root", type=Path, default=Path("."),
                   help="Path to the patch root (default: cwd).")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    root = args.patch_root.resolve()
    manifest_path = root / "PATCH-MANIFEST.json"
    if not manifest_path.exists():
        print(f"FAIL: PATCH-MANIFEST.json missing at {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: PATCH-MANIFEST.json is invalid JSON: {e}", file=sys.stderr)
        return 1

    manifest_files = manifest.get("files", [])
    by_path = {entry["path"]: entry for entry in manifest_files}

    # Walk the patch root and compute hashes for every file.
    actual_files: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORED_PATH_COMPONENTS for part in rel_parts):
            continue
        rel = str(path.relative_to(root))
        if rel in SELF_EXCLUSIONS:
            continue
        actual_files[rel] = sha256_file(path)

    failures = []

    # Manifest claims must all hash-match the on-disk file.
    for rel, entry in by_path.items():
        if rel in SELF_EXCLUSIONS:
            failures.append(f"manifest entry {rel} must not list a self-excluded file")
            continue
        if rel not in actual_files:
            failures.append(f"manifest claims {rel} but file is not present on disk")
            continue
        expected_hash = entry.get("sha256")
        if not expected_hash:
            failures.append(f"manifest entry {rel} has no sha256 field")
            continue
        actual_hash = actual_files[rel]
        if actual_hash != expected_hash:
            failures.append(f"hash drift on {rel}: manifest={expected_hash[:16]}…  actual={actual_hash[:16]}…")

    # Tree files not in manifest are also failures.
    for rel in actual_files:
        if rel not in by_path:
            failures.append(f"file {rel} present in tree but not declared in PATCH-MANIFEST.json")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"PASS: {len(actual_files)} files in tree, {len(by_path)} files in manifest, all hashes match")

    # Echo the patch_tree_hash (sha256 of sorted "path|sha256" lines)
    lines = sorted(f"{rel}|{h}" for rel, h in actual_files.items())
    tree_hash = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    if not args.quiet:
        print(f"patch_tree_hash: {tree_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
