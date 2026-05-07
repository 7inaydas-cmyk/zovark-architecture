"""Tests for Slice 001 approval-required EDR handoff construction."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.handoff import (
    APPROVAL_MODE,
    AUTHORIZATION_RECORD_REF,
    build_handoff,
    attach_handoff,
    derive_handoff,
    set_handoff,
)
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.tape import create_tape
from zovark.slice001.timeline import attach_timeline, build_initial_timeline
from zovark.slice001.verdict import attach_verdict, derive_verdict


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
DEMO_HANDOFF_PATH = Path("demo/zovark-proof-package/out/tape-001/edr-handoff.json")
ALLOWED_ROLLBACK_CLASSES = {"automatic", "manual_documented", "irreversible"}
OLD_ROLLBACK_NAMES = {
    "reversal_or_recovery_plan",
    "reversible_by_edr",
    "manual_recovery_required",
    "irreversible_requires_compensation",
}
HANDOFF_FIELDS = {
    "action_type",
    "approval_mode",
    "audit_ref",
    "authorization_record_ref",
    "blast_radius",
    "evidence_refs",
    "execution_result",
    "handoff_id",
    "idempotency_key",
    "policy_snapshot",
    "policy_snapshot_version",
    "replay_linkage",
    "rollback_plan",
    "tape_ref",
    "target",
    "tenant_id",
}


def _sample_tape_with_verdict() -> dict:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    tape = create_tape(raw, evidence)
    timeline = build_initial_timeline(tape)
    tape = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    return attach_verdict(tape, verdict)


def _demo_pipeline_tape() -> dict:
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))
    tape = create_tape(raw, evidence, tenant_id=committed_tape["tenant_id"])
    tape["tape_id"] = committed_tape["tape_id"]
    tape["audit_ref"] = committed_tape["audit_ref"]
    timeline = build_initial_timeline(tape)
    tape = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    return attach_verdict(tape, verdict)


def _evidence_entry(evidence_id: str, source_type: str = "edr_alert") -> dict:
    return {
        "evidence_id": evidence_id,
        "hash": "0" * 64,
        "ingested_at": "2026-05-01T10:00:00Z",
        "raw_content": {
            "alert_id": "alert-test",
            "host": "HOST-TEST",
            "timestamp": "2026-05-01T10:00:00Z",
        },
        "source_type": source_type,
    }


def _finding(severity: str, evidence_refs: list[str] | None = None) -> dict:
    return {
        "evidence_refs": evidence_refs if evidence_refs is not None else ["ev-1"],
        "model_contribution": False,
        "severity": severity,
        "title": f"{severity} test finding",
    }


def _tape_with_findings(findings: list[dict]) -> dict:
    tape = {
        "audit_ref": None,
        "created_at": "2026-05-01T10:00:00Z",
        "findings": findings,
        "raw_evidence": [_evidence_entry("ev-1")],
        "schema_version": "tape/1.0",
        "source_alert_ref": "alert-test",
        "state": "recording",
        "tape_id": "tape-test",
        "tenant_id": "tenant-001",
        "timeline": [],
        "verdict": None,
    }
    tape["verdict"] = derive_verdict(tape)
    return tape


def _with_forged_verdict(tape: dict, value: str) -> dict:
    forged = deepcopy(tape)
    forged["verdict"] = deepcopy(tape["verdict"])
    forged["verdict"]["value"] = value
    snapshot = {
        "findings": forged["findings"],
        "raw_evidence": forged["raw_evidence"],
        "schema_version": forged["schema_version"],
        "source_alert_ref": forged["source_alert_ref"],
        "tape_id": forged["tape_id"],
        "tenant_id": forged["tenant_id"],
        "verdict_value": value,
    }
    forged["verdict"]["signing_tag"] = "sig-" + sha256_of_obj(snapshot)
    return forged


def test_demo_pipeline_handoff_matches_committed_contract():
    committed_handoff = json.loads(DEMO_HANDOFF_PATH.read_text(encoding="utf-8"))

    handoff = derive_handoff(_demo_pipeline_tape())

    assert handoff == committed_handoff


def test_build_handoff_accepts_explicit_matching_verdict():
    tape = _sample_tape_with_verdict()

    assert build_handoff(tape, tape["verdict"]) == derive_handoff(tape)


def test_handoff_is_deterministic_across_repeated_runs():
    tape = _sample_tape_with_verdict()

    first = derive_handoff(tape)
    second = derive_handoff(tape)

    assert first == second


def test_approval_gate_invariants_prevent_execution():
    handoff = derive_handoff(_sample_tape_with_verdict())

    assert set(handoff) == HANDOFF_FIELDS
    assert handoff["approval_mode"] == APPROVAL_MODE
    assert handoff["authorization_record_ref"] == AUTHORIZATION_RECORD_REF
    assert handoff["execution_result"] == {
        "completed_at": None,
        "error": None,
        "reason": "recommendation_only_no_dispatcher_in_slice_001",
        "started_at": None,
        "status": "pending",
        "vendor_response_ref": None,
    }
    assert handoff["execution_result"]["status"] not in {"completed", "success"}


def test_rollback_plan_uses_openspec_field_and_enum():
    handoff = derive_handoff(_sample_tape_with_verdict())
    rollback_plan = handoff["rollback_plan"]

    assert "rollback_plan" in handoff
    assert "reversal_or_recovery_plan" not in handoff
    assert rollback_plan["reversibility_class"] in ALLOWED_ROLLBACK_CLASSES
    assert rollback_plan["reversibility_class"] not in OLD_ROLLBACK_NAMES


def test_isolate_host_handoff_values_are_deterministic():
    tape = _demo_pipeline_tape()

    handoff = derive_handoff(tape)

    assert handoff["action_type"] == "isolate_host"
    assert handoff["target"]["kind"] == "host"
    assert handoff["target"]["identifier"] == "HOST-12"
    assert handoff["rollback_plan"]["vendor_reversal_action"] == "release_isolation"
    assert handoff["rollback_plan"]["reversibility_class"] == "automatic"
    assert handoff["idempotency_key"] == sha256_of_string(
        "tape-001:isolate_host:HOST-12"
    )


def test_notify_only_handoff_for_medium_only_verdict():
    tape = _tape_with_findings([_finding("medium")])

    handoff = derive_handoff(tape)

    assert handoff["action_type"] == "notify_only"
    assert handoff["target"] == {
        "identifier": "slice-001-static-sample",
        "kind": "custom",
        "validated_at": "2026-05-01T10:00:00Z",
    }
    assert handoff["rollback_plan"]["vendor_reversal_action"] == "none"
    assert handoff["rollback_plan"]["reversibility_class"] == "automatic"
    assert handoff["evidence_refs"] == ["ev-1"]


@pytest.mark.parametrize("missing_key", ["raw_evidence", "findings", "verdict"])
def test_missing_required_tape_fields_are_rejected(missing_key):
    tape = _sample_tape_with_verdict()
    tape.pop(missing_key)

    with pytest.raises(ZovarkValidationError):
        derive_handoff(tape)


def test_finding_refs_not_present_in_raw_evidence_are_rejected():
    tape = _sample_tape_with_verdict()
    tape["findings"][0]["evidence_refs"] = ["missing-ev"]

    with pytest.raises(ZovarkValidationError):
        derive_handoff(tape)


def test_malformed_raw_evidence_entries_are_rejected():
    tape = _sample_tape_with_verdict()
    tape["raw_evidence"][0].pop("raw_content")

    with pytest.raises(ZovarkValidationError):
        derive_handoff(tape)


def test_unsupported_or_forged_verdict_values_are_rejected():
    tape = _sample_tape_with_verdict()
    forged = _with_forged_verdict(tape, "benign")

    with pytest.raises(ZovarkValidationError):
        derive_handoff(forged)


def test_forged_self_consistent_looking_verdict_is_rejected_before_handoff():
    tape = _tape_with_findings([_finding("high")])
    forged = _with_forged_verdict(tape, "benign")
    forged["verdict"]["derivation_rule"] = "All findings severity low or info \u2192 benign"

    with pytest.raises(ZovarkValidationError):
        derive_handoff(forged)


def test_attach_handoff_returns_copied_tape_and_preserves_existing_state():
    tape = _sample_tape_with_verdict()
    original = deepcopy(tape)
    handoff = derive_handoff(tape)

    updated = attach_handoff(tape, handoff)

    assert updated is not tape
    assert "handoff" not in tape
    assert tape == original
    assert updated["raw_evidence"] == tape["raw_evidence"]
    assert updated["timeline"] == tape["timeline"]
    assert updated["findings"] == tape["findings"]
    assert updated["verdict"] == tape["verdict"]
    assert updated["audit_ref"] == tape["audit_ref"]
    assert updated["handoff_ref"] == handoff["handoff_id"]
    assert updated["handoff_summary"] == {
        "action_type": handoff["action_type"],
        "approval_mode": "approval_required",
        "execution_status": "pending",
        "target": {
            "identifier": handoff["target"]["identifier"],
            "kind": handoff["target"]["kind"],
        },
    }


def test_set_handoff_alias_matches_attach_handoff():
    tape = _sample_tape_with_verdict()
    handoff = derive_handoff(tape)

    assert set_handoff(tape, handoff) == attach_handoff(tape, handoff)


def test_mutating_caller_handoff_after_attach_does_not_mutate_tape_handoff():
    tape = _sample_tape_with_verdict()
    handoff = derive_handoff(tape)

    updated = attach_handoff(tape, handoff)
    handoff["execution_result"]["status"] = "completed"
    handoff["target"]["identifier"] = "changed"

    assert updated["handoff"]["execution_result"]["status"] == "pending"
    assert updated["handoff"]["target"]["identifier"] != "changed"


def test_mutating_original_tape_after_derivation_does_not_change_handoff():
    tape = _sample_tape_with_verdict()

    handoff = derive_handoff(tape)
    tape["raw_evidence"][0]["raw_content"]["host"] = "CHANGED"
    tape["findings"][0]["title"] = "changed"
    tape["verdict"]["value"] = "benign"

    assert handoff == derive_handoff(_sample_tape_with_verdict())


def test_attach_rejects_handoff_that_does_not_match_current_tape():
    tape = _sample_tape_with_verdict()
    handoff = derive_handoff(tape)
    handoff["action_type"] = "notify_only"

    with pytest.raises(ZovarkValidationError):
        attach_handoff(tape, handoff)


def test_attach_rejects_old_rollback_field_name():
    tape = _sample_tape_with_verdict()
    handoff = derive_handoff(tape)
    handoff["reversal_or_recovery_plan"] = handoff.pop("rollback_plan")

    with pytest.raises(ZovarkValidationError):
        attach_handoff(tape, handoff)


def test_attach_rejects_old_rollback_enum_value():
    tape = _sample_tape_with_verdict()
    handoff = derive_handoff(tape)
    handoff["rollback_plan"]["reversibility_class"] = "reversible_by_edr"

    with pytest.raises(ZovarkValidationError):
        attach_handoff(tape, handoff)


def test_no_forbidden_imports_in_handoff_module():
    source = Path("zovark/slice001/handoff.py").read_text(encoding="utf-8")

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
    ]
    for token in forbidden:
        assert token not in source
