#!/usr/bin/env python3
from pathlib import Path
import sys

FORBIDDEN = [
    "auto-publish",
    "auto publish",
    "published status",
    "splunk publication",
    "elastic publication",
    "sentinel publication",
    "wazuh publication",
    "generic webhook publication",
    "negative-corpus validation",
    "negative corpus validation",
    "0.1% fp",
    "0.1% false-positive",
]

ALLOWED_CONTEXT = [
    "post-mvp",
    "future",
    "historical",
    "superseded",
    "out of scope",
    "not in mvp",
    "not part of mvp",
]

failures = []

for path in Path(".").rglob("*.md"):
    if ".git" in path.parts:
        continue
    for idx, line in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
        lower = line.lower()
        if "mvp" not in lower:
            continue
        for term in FORBIDDEN:
            if term in lower and not any(ctx in lower for ctx in ALLOWED_CONTEXT):
                failures.append(f"{path}:{idx}: forbidden MVP term '{term}'")

if failures:
    print("\n".join(failures))
    sys.exit(1)

print("MVP scope consistency check passed")
