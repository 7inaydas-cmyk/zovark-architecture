#!/usr/bin/env python3
"""
check_claim_provenance.py — verify quantified-claim provenance tags.

Implements the M0 deliverable contract specified in
architecture/claims/claim-provenance.md and openspec/specs/claim-provenance/spec.md.

Two validation passes:
  1. Every tag occurrence (anywhere in scope) must be syntactically valid:
     known tag kind, well-formed payload, known owner, known cadence,
     measured-artifact resolves, hypothesis only outside customer-facing.
  2. Every quantified claim (a category keyword on a line that also carries a
     unit-bearing number) must have a tag on the same line or the immediately
     following line.

Walks: architecture/**/*.md, zovark-v3.2.4.6-engineering-ready/**/*.md, *.md.
Skips: openspec/changes/archive/**, architecture/review/** (rules describe,
not assert), .git/**, node_modules/, __pycache__/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Quantified-claim detection
# ---------------------------------------------------------------------------

# Category keywords. A line is a candidate quantified claim only if it contains
# at least one of these (word-boundary match, case-insensitive) AND a
# unit-bearing number (NUMERIC_RE). Multi-word categories use exact substring
# match because they are unambiguous.
SINGLE_WORD_CATEGORIES = (
    "latency", "throughput", "concurrency",
    "accuracy", "precision",
    "availability", "uptime", "mtbf", "mttr",
    "rpo", "rto",
)
MULTIWORD_CATEGORIES = (
    "queue depth",
    "false-positive", "false positive",
    "false-negative", "false negative",
    "support response", "patch response",
    "retention period",
    "ships in", "delivers in", "ship time",
    "license fee",
)
SINGLE_WORD_CATEGORY_RE = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in SINGLE_WORD_CATEGORIES) + r")\b",
    re.IGNORECASE,
)

# Unit-bearing numeric regex. Conservative — we want category+number, not any
# number anywhere. Units cover time, percent, and capacity-rate descriptors
# typical of product claims.
NUMERIC_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*"
    r"(?:ms|seconds?|minutes?|hours?|days?|weeks?|months?|years?|"
    r"%|percent|"
    r"alerts?/sec|requests?/sec|events?/sec|tenants?|agents?|hosts?)"
    r"\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Tag grammar and validation
# ---------------------------------------------------------------------------

TAG_RE = re.compile(
    r"\[(hypothesis|measured|vendor-cited|policy-commitment):([^\]]+)\]"
)

# Allowed review cadences. The base set is from claim-provenance/spec.md
# (daily, weekly, monthly, quarterly, semiannual-review, annual-review).
# Patch-tree usage drives the additions below. The rc3 MODIFIED Requirements
# change fix-claim-provenance-enforcement updates the spec to match.
ALLOWED_CADENCES = {
    # Periodic
    "daily", "weekly", "monthly", "quarterly",
    "quarterly-review", "semiannual-review", "annual-review",
    # Event-driven (each occurrence triggers a review)
    "release-review", "milestone-review",
    "per-release-review", "per-promotion-review",
    "per-advisory-review", "per-change-review",
    "incident-review",
}

# Bootstrap-pending owner roles. These appear in patch-tree tags but are not
# yet declared in OWNERS.yaml's roles: section. M2 will register them in
# OWNERS.yaml directly and this list collapses to empty. Documented in the
# fix-claim-provenance-enforcement change design.md.
BOOTSTRAP_PENDING_OWNERS = {
    "product-owner", "support-owner",
    "release-engineering", "research-owner",
}

# Tag payloads that are obviously illustrative placeholders inside the rules
# documentation itself or template snippets. Validation skips these.
PLACEHOLDER_PAYLOADS = {
    "<owner>,<review-cadence>",
    "owner,review-cadence",
    "artifact-id,YYYY-MM-DD",
    "citation-id",
    "evidence-milestone",
    "*",
    "owner",
    "review-cadence",
}

# Date pattern for [measured:artifact,DATE]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# OWNERS.yaml roles parsing — each role is a top-level key under "roles:".
# Indentation is exactly two spaces in the patch-tree convention.
ROLE_KEY_RE = re.compile(r"^  ([a-z][a-z0-9-]+):\s*$")

# ---------------------------------------------------------------------------
# Customer-facing classification
# ---------------------------------------------------------------------------

CF_PATH_TOKENS = ("customer-", "/handoff/", "customer_")
CF_HEADING_TOKENS = ("Customer", "User", "Operator Guide", "Public", "Onboarding")

# ---------------------------------------------------------------------------
# Walk include / exclude
# ---------------------------------------------------------------------------

WALK_ROOTS = ("architecture", "zovark-v3.2.4.6-engineering-ready")
EXCLUDE_TOKENS = (
    ".git/",
    "openspec/changes/archive/",
    "architecture/review/",
    "architecture/claims/",
    # Patch-tree mirror of the rules doc (illustrative tags, not asserted claims).
    "zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/architecture/claims/",
    # License/legal text is not architecture content.
    "LICENSE-",
    "node_modules/",
    "__pycache__/",
)


def is_excluded(path: Path, repo_root: Path) -> bool:
    rel = str(path.relative_to(repo_root))
    return any(token in rel for token in EXCLUDE_TOKENS)


def collect_files(repo_root: Path) -> list[Path]:
    out: set[Path] = set()
    for root in WALK_ROOTS:
        out.update((repo_root / root).rglob("*.md"))
    out.update(repo_root.glob("*.md"))
    return sorted(p for p in out if not is_excluded(p, repo_root))


# ---------------------------------------------------------------------------
# OWNERS.yaml parsing
# ---------------------------------------------------------------------------


def load_owners(repo_root: Path) -> set[str]:
    """Extract role names from any OWNERS.yaml under the repo (excludes archive)."""
    owners: set[str] = set()
    for path in repo_root.rglob("OWNERS.yaml"):
        if is_excluded(path, repo_root):
            continue
        in_roles = False
        for line in path.read_text(errors="ignore").splitlines():
            stripped_no_space = line.lstrip()
            if line.strip() == "roles:":
                in_roles = True
                continue
            if not in_roles:
                continue
            # End of roles block: a new top-level key with no leading whitespace.
            if line and not line[0].isspace() and not line.startswith("#"):
                in_roles = False
                continue
            m = ROLE_KEY_RE.match(line)
            if m:
                owners.add(m.group(1))
    return owners


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def is_customer_facing(path: Path, content: str, repo_root: Path) -> bool:
    rel = str(path.relative_to(repo_root))
    if any(token in rel for token in CF_PATH_TOKENS):
        return True
    # YAML frontmatter
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end > 0 and "customer_facing: true" in content[4:end]:
            return True
    # First H1 in the first ~10 lines
    for line in content.splitlines()[:10]:
        if line.startswith("# "):
            heading = line[2:]
            if any(tok in heading for tok in CF_HEADING_TOKENS):
                return True
            break
    return False


def find_quantified_claim_categories(line: str) -> list[str]:
    if not NUMERIC_RE.search(line):
        return []
    found = [m.group(1).lower() for m in SINGLE_WORD_CATEGORY_RE.finditer(line)]
    lower = line.lower()
    found.extend(cat for cat in MULTIWORD_CATEGORIES if cat in lower)
    return found


def validate_tag_payload(kind: str, payload: str, owners: set[str], repo_root: Path) -> str | None:
    """Return error string if tag payload is invalid, else None."""
    # Skip illustrative placeholder tags found in template / rules-of-the-rules text.
    if payload.strip() in PLACEHOLDER_PAYLOADS:
        return None
    if kind == "hypothesis":
        if not payload.strip():
            return "[hypothesis:] tag has empty milestone"
        return None

    if kind == "measured":
        parts = [p.strip() for p in payload.split(",")]
        if len(parts) != 2:
            return f"[measured:] tag malformed (expected artifact-id,YYYY-MM-DD): {payload!r}"
        artifact_id, date = parts
        if not DATE_RE.match(date):
            return f"[measured:] tag date malformed: {date!r}"
        # Resolve the artifact: any path containing the artifact_id substring.
        # Conservative — caller can use a precise artifact ID. Skip if path
        # contains the archive/review tokens.
        matches = [
            p for p in repo_root.rglob(f"*{artifact_id}*")
            if not is_excluded(p, repo_root)
        ]
        if not matches:
            return f"[measured:] artifact not found in tree: {artifact_id!r}"
        return None

    if kind == "vendor-cited":
        if not payload.strip():
            return "[vendor-cited:] tag has empty citation-id"
        return None

    if kind == "policy-commitment":
        parts = [p.strip() for p in payload.split(",")]
        if len(parts) != 2:
            return f"[policy-commitment:] tag malformed (expected owner,review-cadence): {payload!r}"
        owner, cadence = parts
        if owner not in owners and owner not in BOOTSTRAP_PENDING_OWNERS:
            return (
                f"[policy-commitment:] owner {owner!r} not in OWNERS.yaml roles "
                f"and not in BOOTSTRAP_PENDING_OWNERS"
            )
        if cadence not in ALLOWED_CADENCES:
            return f"[policy-commitment:] cadence {cadence!r} not in allowed list"
        return None

    return f"unknown tag kind: {kind!r}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    repo_root = Path.cwd()
    owners = load_owners(repo_root)
    failures: list[str] = []

    files = collect_files(repo_root)

    # Pass 1 — validate every tag in every file.
    for path in files:
        try:
            content = path.read_text(errors="ignore")
        except OSError:
            continue
        cf = is_customer_facing(path, content, repo_root)
        rel = path.relative_to(repo_root)
        for line_no, line in enumerate(content.splitlines(), start=1):
            for tag_m in TAG_RE.finditer(line):
                kind = tag_m.group(1)
                payload = tag_m.group(2)
                if cf and kind == "hypothesis":
                    failures.append(
                        f"{rel}:{line_no}: [hypothesis:*] not allowed in customer-facing doc"
                    )
                    continue
                err = validate_tag_payload(kind, payload, owners, repo_root)
                if err:
                    failures.append(f"{rel}:{line_no}: {err}")

    # Pass 2 — every quantified claim has a tag on this line or the next.
    for path in files:
        try:
            content = path.read_text(errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(repo_root)
        lines = content.splitlines()
        for line_no, line in enumerate(lines, start=1):
            cats = find_quantified_claim_categories(line)
            if not cats:
                continue
            tags_here = list(TAG_RE.finditer(line))
            tags_next = (
                list(TAG_RE.finditer(lines[line_no])) if line_no < len(lines) else []
            )
            tags = tags_here + tags_next
            if not tags:
                failures.append(
                    f"{rel}:{line_no}: missing provenance tag (categories: {', '.join(cats)})"
                )
                continue
            if len(tags) > 1 and len(tags_here) > 1:
                # Multiple tags on the *same* line for a quantified claim — ambiguous.
                failures.append(
                    f"{rel}:{line_no}: multiple tags on the same quantified-claim line"
                )

    if failures:
        for f in failures:
            print(f)
        return 1

    print("Claim provenance check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
