#!/usr/bin/env python3
"""
apply_v3_2_4_6.py — external apply script for the Zovark v3.2.4.6 patch.

External patch model: this script lives in the patch package, NOT in the
repo. It takes --repo-root and --patch-root as explicit arguments.

The apply script reads the apply_mode field from PATCH-MANIFEST.json for
every file. There is NO hard-coded internal-file list. The manifest is the
single source of truth for copy, fragment, and patch-internal behavior.

apply_mode values supported:

  copy            : copy the file from patch-root to repo-root at the same
                    relative path (overwrites if present)
  patch-internal  : do NOT copy; this file lives only inside the patch
                    package (manifests, apply scripts, FIXES docs, etc.)
  fragment        : this file is a fragment under patches/; apply via
                    --apply-fragments mode using anchor markers (idempotent)

Hash domain discipline. Two domains are tracked, never mixed:

  REPORT_HASH:  sha256(ops/compliance/bootstrap-acceptance-report.stable.json)
                Verified via --verify-baseline-report-hash.
                Frozen value for v3.2.3.5:
                  5b3feedf2522d08c02b6f29cba803dd0577d39ef4f0c1a211d56bf7cf3c121a3

  TREE_HASH:    sha256 chain of (relpath|sha256) lines for the patch tree.
                Verified via --verify-patch-tree-hash.
                Computed at ship time, recorded in PATCH-MANIFEST.json.

Modes:
  --verify-baseline-report-hash    : verifies REPORT_HASH only
  --verify-baseline-gates          : runs verify-bootstrap.sh + bootstrap-acceptance.sh
  --verify-baseline                : runs both of the above
  --verify-patch-tree-hash         : runs check_patch_self_test on the patch
  --apply                          : copies patch files into repo (dry-run by default;
                                     pass --commit to actually write)
  --apply-fragments                : applies anchored append fragments from patches/
                                     into existing repo files (idempotent)
  --status                         : prints what would happen, doesn't change repo

Exit codes:
  0   action succeeded
  1   verification failed
  2   invocation error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


V3_2_3_5_REPORT_HASH = "5b3feedf2522d08c02b6f29cba803dd0577d39ef4f0c1a211d56bf7cf3c121a3"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(patch_root: Path) -> dict:
    p = patch_root / "PATCH-MANIFEST.json"
    if not p.exists():
        raise FileNotFoundError(f"PATCH-MANIFEST.json missing at {p}")
    return json.loads(p.read_text())


def verify_baseline_report_hash(repo_root: Path) -> bool:
    rep = repo_root / "ops" / "compliance" / "bootstrap-acceptance-report.stable.json"
    if not rep.exists():
        print(f"FAIL: stable report not found at {rep}", file=sys.stderr)
        print("      (have you run scripts/bootstrap-acceptance.sh against v3.2.3.5?)",
              file=sys.stderr)
        return False
    actual = sha256_file(rep)
    if actual != V3_2_3_5_REPORT_HASH:
        print("FAIL: stable report hash drift", file=sys.stderr)
        print(f"      expected: {V3_2_3_5_REPORT_HASH}", file=sys.stderr)
        print(f"      actual:   {actual}", file=sys.stderr)
        print("      Domain: sha256(ops/compliance/bootstrap-acceptance-report.stable.json)",
              file=sys.stderr)
        return False
    print(f"PASS: baseline stable report hash matches v3.2.3.5")
    return True


def verify_baseline_gates(repo_root: Path) -> bool:
    okay = True
    for cmd, label in [
        (["bash", str(repo_root / "verify-bootstrap.sh")], "verify-bootstrap.sh"),
        (["bash", str(repo_root / "scripts" / "bootstrap-acceptance.sh")], "bootstrap-acceptance.sh"),
    ]:
        print(f"--- running {label} ---")
        r = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL: {label} exited {r.returncode}", file=sys.stderr)
            sys.stderr.write(r.stdout[-2000:])
            sys.stderr.write(r.stderr[-2000:])
            okay = False
        else:
            for line in r.stdout.splitlines()[-3:]:
                print(line)
    return okay


def verify_patch_tree_hash(patch_root: Path) -> bool:
    cmd = [sys.executable, str(patch_root / "scripts" / "check_patch_self_test.py"),
           "--patch-root", str(patch_root)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    return r.returncode == 0


def files_to_copy(manifest: dict) -> list[dict]:
    """Returns manifest entries with apply_mode == 'copy'."""
    return [e for e in manifest.get("files", []) if e.get("apply_mode") == "copy"]


def fragments(manifest: dict) -> list[dict]:
    """Returns manifest entries with apply_mode == 'fragment'."""
    return [e for e in manifest.get("files", []) if e.get("apply_mode") == "fragment"]


def apply_patch(repo_root: Path, patch_root: Path, manifest: dict, commit: bool) -> bool:
    files = files_to_copy(manifest)
    print(f"--- applying {len(files)} files (apply_mode=copy) {'(COMMIT)' if commit else '(DRY-RUN)'} ---")
    for entry in files:
        rel = entry["path"]
        src = patch_root / rel
        dst = repo_root / rel
        action = "WRITE" if not dst.exists() else "OVERWRITE"
        print(f"  [{action}] {rel}")
        if commit:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    if not commit:
        print("--- dry-run only; pass --commit to actually write files ---")
    else:
        print(f"--- {len(files)} files written; next: bash verify-bootstrap.sh from {repo_root} ---")
    return True


def apply_fragments(repo_root: Path, patch_root: Path, manifest: dict, commit: bool) -> bool:
    """Applies anchored append fragments idempotently."""
    frags = fragments(manifest)
    print(f"--- applying {len(frags)} fragments {'(COMMIT)' if commit else '(DRY-RUN)'} ---")
    okay = True
    for entry in frags:
        rel = entry["path"]
        src = patch_root / rel
        # Each fragment carries a target_file and anchor in its declared metadata
        target_rel = entry.get("target_file")
        anchor = entry.get("anchor")
        if not target_rel or not anchor:
            print(f"  [SKIP] {rel}: missing target_file or anchor in manifest", file=sys.stderr)
            okay = False
            continue
        target = repo_root / target_rel
        if not target.exists():
            print(f"  [SKIP] {rel}: target {target_rel} does not exist in repo", file=sys.stderr)
            okay = False
            continue
        target_text = target.read_text()
        if anchor in target_text:
            print(f"  [IDEMPOTENT] {rel}: anchor {anchor!r} already in {target_rel}; skipping")
            continue
        fragment_text = src.read_text()
        new_text = target_text.rstrip() + "\n\n" + fragment_text
        # Optional: handle the verify-bootstrap.sh count-string rewrite
        rewrite = entry.get("rewrite")
        if rewrite:
            old, new = rewrite.get("from"), rewrite.get("to")
            if old in new_text:
                new_text = new_text.replace(old, new, 1)
        print(f"  [APPEND] {rel} -> {target_rel} (anchor: {anchor})")
        if commit:
            target.write_text(new_text)
    if not commit:
        print("--- dry-run only; pass --commit to actually write files ---")
    return okay


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-root", type=Path, default=None)
    p.add_argument("--patch-root", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--verify-baseline-report-hash", action="store_true")
    p.add_argument("--verify-baseline-gates", action="store_true")
    p.add_argument("--verify-baseline", action="store_true")
    p.add_argument("--verify-patch-tree-hash", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--apply-fragments", action="store_true")
    p.add_argument("--commit", action="store_true")
    p.add_argument("--status", action="store_true")
    args = p.parse_args()

    requested = [args.verify_baseline_report_hash, args.verify_baseline_gates,
                 args.verify_baseline, args.verify_patch_tree_hash,
                 args.apply, args.apply_fragments, args.status]
    if not any(requested):
        p.print_help()
        return 2

    patch_root = args.patch_root.resolve()
    manifest = load_manifest(patch_root)

    if args.verify_baseline_report_hash or args.verify_baseline:
        if not args.repo_root:
            print("FAIL: --repo-root required", file=sys.stderr); return 2
        if not verify_baseline_report_hash(args.repo_root.resolve()):
            return 1

    if args.verify_baseline_gates or args.verify_baseline:
        if not args.repo_root:
            print("FAIL: --repo-root required", file=sys.stderr); return 2
        if not verify_baseline_gates(args.repo_root.resolve()):
            return 1

    if args.verify_patch_tree_hash:
        if not verify_patch_tree_hash(patch_root):
            return 1

    if args.status:
        copy_files = files_to_copy(manifest)
        frags = fragments(manifest)
        print(f"patch root:    {patch_root}")
        print(f"repo root:     {args.repo_root.resolve() if args.repo_root else '(not specified)'}")
        print(f"copy files:    {len(copy_files)}")
        print(f"fragments:     {len(frags)}")
        print(f"manifest hash: {manifest.get('patch_tree_hash')}")
        return 0

    if args.apply:
        if not args.repo_root:
            print("FAIL: --repo-root required for --apply", file=sys.stderr); return 2
        if not apply_patch(args.repo_root.resolve(), patch_root, manifest, args.commit):
            return 1

    if args.apply_fragments:
        if not args.repo_root:
            print("FAIL: --repo-root required for --apply-fragments", file=sys.stderr); return 2
        if not apply_fragments(args.repo_root.resolve(), patch_root, manifest, args.commit):
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
