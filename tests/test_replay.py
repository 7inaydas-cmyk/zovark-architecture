"""Tests for Slice 001 deterministic replay report construction."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.audit import (
    GENESIS_HASH,
    attach_audit_entry,
    compute_this_entry_hash,
    derive_audit_entry,
)
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.handoff import attach_handoff, derive_handoff
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.replay import (
    attach_replay_report,
    build_replay_report,
    derive_replay_report,
    set_replay_report,
)
from zovark.slice001.tape import create_tape
from zovark.slice001.timeline import attach_timeline, build_initial_timeline
from zovark.slice001.verdict import attach_verdict, derive_verdict


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
DEMO_TIMELINE_PATH = Path("demo/zovark-proof-package/out/tape-001/timeline.json")
DEMO_REPLAY_PATH = Path("demo/zovark-proof-package/out/tape-001/replay-report.json")
REPLAY_REPORT_FIELDS = {"audit_chain_entry", "replay_state"}
REPLAY_STATE_FIELDS = {
    "completed_at",
    "evidence_hashes_verified",
    "mismatch_details",
    "mode",
    "model_versions_pin",
    "no_live_edr_call",
    "no_live_llm_call",
    "replay_id",
    "replay_status",
    "schema_pin",
    "started_at",
    "state",
    "tape_ref",
    "tenant_id",
    "tool_catalog_pin",
    "unsigned_tail_replay",
    "verdict_match",
    "verdict_recomputed",
    "verification_detail",
}
VERIFICATION_DETAIL_FIELDS = {
    "evidence_entries_checked",
    "evidence_entries_failed",
    "evidence_entries_passed",
    "verdict_matched",
    "verdict_recomputed_value",
    "verdict_stored",
}
AUDIT_ENTRY_FIELDS = {
    "created_at",
    "entry_id",
    "event_type",
    "payload",
    "prev_entry_hash",
    "sequence",
    "signed_root",
    "tenant_id",
    "this_entry_hash",
}
REPLAY_PAYLOAD_FIELDS = {
    "evidence_hashes_verified",
    "replay_id",
    "replay_state",
    "tape_id",
    "verdict_matched",
    "verdict_recomputed",
}


def _sample_sealed_tape() -> dict:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    tape = create_tape(raw, evidence)
    timeline = build_initial_timeline(tape)
    tape = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    tape["audit_ref"] = "audit-entry-1"
    handoff = derive_handoff(tape)
    tape = attach_handoff(tape, handoff)
    audit_entry = derive_audit_entry(tape)
    return attach_audit_entry(tape, audit_entry)


def _demo_sealed_tape() -> dict:
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))
    committed_timeline = json.loads(DEMO_TIMELINE_PATH.read_text(encoding="utf-8"))
    tape = create_tape(raw, evidence, tenant_id=committed_tape["tenant_id"])
    tape["tape_id"] = committed_tape["tape_id"]
    tape["audit_ref"] = committed_tape["audit_ref"]
    tape["timeline"] = committed_timeline
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    handoff = derive_handoff(tape)
    tape = attach_handoff(tape, handoff)
    audit_entry = derive_audit_entry(tape)
    return attach_audit_entry(tape, audit_entry)


def _fields_hash_snapshot(tape: dict) -> dict:
    return {
        "findings": tape["findings"],
        "raw_evidence": tape["raw_evidence"],
        "schema_version": tape["schema_version"],
        "source_alert_ref": tape["source_alert_ref"],
        "tape_id": tape["tape_id"],
        "tenant_id": tape["tenant_id"],
        "verdict_value": tape["verdict"]["value"],
    }


def _with_forged_verdict(tape: dict, value: str) -> dict:
    forged = deepcopy(tape)
    forged["verdict"] = deepcopy(tape["verdict"])
    forged["verdict"]["value"] = value
    forged["verdict"]["signing_tag"] = "sig-" + sha256_of_obj(
        _fields_hash_snapshot(forged)
    )
    return forged


def _self_consistent_wrong_replay_report(tape: dict) -> dict:
    report = derive_replay_report(tape)
    report["replay_state"]["state"] = "failed"
    report["replay_state"]["replay_status"] = "failed"
    report["audit_chain_entry"]["payload"]["replay_state"] = "failed"
    report["audit_chain_entry"]["this_entry_hash"] = compute_this_entry_hash(
        report["audit_chain_entry"]
    )
    return report


def test_demo_pipeline_replay_report_matches_committed_contract():
    committed_replay = json.loads(DEMO_REPLAY_PATH.read_text(encoding="utf-8"))

    replay_report = derive_replay_report(_demo_sealed_tape())

    assert replay_report == committed_replay


def test_replay_report_is_deterministic_across_repeated_runs():
    tape = _sample_sealed_tape()

    first = derive_replay_report(tape)
    second = derive_replay_report(tape)

    assert first == second
    assert (
        first["audit_chain_entry"]["this_entry_hash"]
        == second["audit_chain_entry"]["this_entry_hash"]
    )


def test_build_replay_report_alias_matches_derive_replay_report():
    tape = _sample_sealed_tape()

    assert build_replay_report(tape) == derive_replay_report(tape)


def test_replay_report_schema_is_exact():
    replay_report = derive_replay_report(_sample_sealed_tape())

    assert set(replay_report) == REPLAY_REPORT_FIELDS
    assert set(replay_report["replay_state"]) == REPLAY_STATE_FIELDS
    assert (
        set(replay_report["replay_state"]["verification_detail"])
        == VERIFICATION_DETAIL_FIELDS
    )
    assert set(replay_report["audit_chain_entry"]) == AUDIT_ENTRY_FIELDS
    assert set(replay_report["audit_chain_entry"]["payload"]) == REPLAY_PAYLOAD_FIELDS


def test_replay_state_verification_values_are_deterministic():
    tape = _sample_sealed_tape()

    replay_report = derive_replay_report(tape)

    assert replay_report["replay_state"] == {
        "completed_at": replay_report["audit_chain_entry"]["created_at"],
        "evidence_hashes_verified": True,
        "mismatch_details": None,
        "mode": "recorded_output",
        "model_versions_pin": [],
        "no_live_edr_call": True,
        "no_live_llm_call": True,
        "replay_id": "replay-001",
        "replay_status": "succeeded",
        "schema_pin": "tape/1.0",
        "started_at": replay_report["audit_chain_entry"]["created_at"],
        "state": "succeeded",
        "tape_ref": tape["tape_id"],
        "tenant_id": tape["tenant_id"],
        "tool_catalog_pin": "none-slice-001",
        "unsigned_tail_replay": True,
        "verdict_match": True,
        "verdict_recomputed": True,
        "verification_detail": {
            "evidence_entries_checked": len(tape["raw_evidence"]),
            "evidence_entries_failed": 0,
            "evidence_entries_passed": len(tape["raw_evidence"]),
            "verdict_matched": True,
            "verdict_recomputed_value": tape["verdict"]["value"],
            "verdict_stored": tape["verdict"]["value"],
        },
    }


def test_replay_audit_entry_values_are_recomputable():
    tape = _sample_sealed_tape()

    replay_entry = derive_replay_report(tape)["audit_chain_entry"]

    assert replay_entry["entry_id"] == "audit-entry-2"
    assert replay_entry["event_type"] == "tape_replayed"
    assert replay_entry["sequence"] == 2
    assert replay_entry["prev_entry_hash"] == tape["audit_entry"]["this_entry_hash"]
    assert replay_entry["signed_root"] is None
    assert replay_entry["this_entry_hash"] == compute_this_entry_hash(replay_entry)


@pytest.mark.parametrize(
    "missing_key",
    ["raw_evidence", "timeline", "findings", "verdict", "handoff", "audit_entry"],
)
def test_missing_required_tape_fields_are_rejected(missing_key):
    tape = _sample_sealed_tape()
    tape.pop(missing_key)

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_malformed_raw_evidence_entries_are_rejected():
    tape = _sample_sealed_tape()
    tape["raw_evidence"][0].pop("raw_content")

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_timeline_refs_absent_from_raw_evidence_are_rejected():
    tape = _sample_sealed_tape()
    tape["timeline"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_finding_refs_absent_from_raw_evidence_are_rejected():
    tape = _sample_sealed_tape()
    tape["findings"][0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_forged_verdict_is_rejected_before_replay_report():
    tape = _sample_sealed_tape()
    forged = _with_forged_verdict(tape, "benign")

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(forged)


def test_forged_handoff_is_rejected_before_replay_report():
    tape = _sample_sealed_tape()
    tape["handoff"]["execution_result"]["status"] = "succeeded"

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_forged_audit_entry_is_rejected_before_replay_report():
    tape = _sample_sealed_tape()
    tape["audit_entry"]["payload"]["verdict_value"] = "benign"
    tape["audit_entry"]["this_entry_hash"] = compute_this_entry_hash(
        tape["audit_entry"]
    )

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_evidence_raw_content_change_without_hash_update_fails_closed():
    tape = _sample_sealed_tape()
    tape["raw_evidence"][0]["raw_content"]["host"] = "CHANGED"

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_audit_sequence_one_requires_genesis_predecessor():
    tape = _sample_sealed_tape()
    tape["audit_entry"]["prev_entry_hash"] = sha256_of_string("not-genesis")
    tape["audit_entry"]["this_entry_hash"] = compute_this_entry_hash(
        tape["audit_entry"]
    )

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)
    assert GENESIS_HASH == sha256_of_string("genesis")


def test_replay_rejects_unsealed_tape():
    tape = _sample_sealed_tape()
    tape["state"] = "recording"

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_attach_replay_report_returns_copied_tape_and_preserves_state():
    tape = _sample_sealed_tape()
    original = deepcopy(tape)
    replay_report = derive_replay_report(tape)

    updated = attach_replay_report(tape, replay_report)

    assert updated is not tape
    assert tape == original
    assert updated["replay_report"] == replay_report
    assert updated["raw_evidence"] == original["raw_evidence"]
    assert updated["timeline"] == original["timeline"]
    assert updated["findings"] == original["findings"]
    assert updated["verdict"] == original["verdict"]
    assert updated["handoff"] == original["handoff"]
    assert updated["audit_entry"] == original["audit_entry"]
    assert updated["audit_ref"] == original["audit_ref"]
    assert updated["state"] == "closed"


def test_set_replay_report_alias_matches_attach_replay_report():
    tape = _sample_sealed_tape()
    replay_report = derive_replay_report(tape)

    assert set_replay_report(tape, replay_report) == attach_replay_report(
        tape, replay_report
    )


def test_mutating_caller_replay_report_after_attach_does_not_mutate_tape():
    tape = _sample_sealed_tape()
    replay_report = derive_replay_report(tape)

    updated = attach_replay_report(tape, replay_report)
    replay_report["replay_state"]["state"] = "failed"
    replay_report["audit_chain_entry"]["payload"]["replay_state"] = "failed"

    assert updated["replay_report"] == derive_replay_report(tape)


def test_mutating_original_tape_after_derivation_does_not_change_replay_report():
    tape = _sample_sealed_tape()

    replay_report = derive_replay_report(tape)
    tape["raw_evidence"][0]["raw_content"]["host"] = "CHANGED"
    tape["verdict"]["value"] = "benign"
    tape["handoff"]["action_type"] = "notify_only"
    tape["audit_entry"]["payload"]["verdict_value"] = "benign"

    assert replay_report == derive_replay_report(_sample_sealed_tape())


def test_attach_rejects_self_consistent_but_non_derived_replay_report():
    tape = _sample_sealed_tape()
    forged_report = _self_consistent_wrong_replay_report(tape)

    with pytest.raises(ZovarkValidationError):
        attach_replay_report(tape, forged_report)


def test_attach_rejects_malformed_replay_report_shape():
    tape = _sample_sealed_tape()
    replay_report = derive_replay_report(tape)
    replay_report["unexpected"] = "extra"

    with pytest.raises(ZovarkValidationError):
        attach_replay_report(tape, replay_report)


def test_no_forbidden_imports_or_scope_creep_in_replay_module():
    source = Path("zovark/slice001/replay.py").read_text(encoding="utf-8")

    forbidden = [
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "openai",
        "ramalama",
        "temporalio",
        "redis",
        "psycopg2",
        "sqlalchemy",
        "boto3",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "uuid.uuid4",
        "random",
        "writer.py",
        "cli.py",
        "__main__",
        "sentry",
    ]
    for token in forbidden:
        assert token not in source
