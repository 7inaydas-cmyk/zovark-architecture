"""Tests for Slice 001 rule-driven findings derivation."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.findings import (
    append_findings,
    attach_findings,
    derive_findings,
)
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.tape import create_tape
from zovark.slice001.timeline import attach_timeline, build_initial_timeline


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_FINDINGS_PATH = Path("demo/zovark-proof-package/out/tape-001/findings.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
DEMO_FINDING_FIELDS = {
    "evidence_refs",
    "mitre_technique",
    "model_contribution",
    "rule_id",
    "severity",
    "title",
}


def _sample_tape() -> dict:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    return create_tape(raw, evidence)


def _demo_tape() -> dict:
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_demo_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))
    return create_tape(raw, evidence, tenant_id=committed_demo_tape["tenant_id"])


def _evidence_ids(tape: dict) -> set[str]:
    return {entry["evidence_id"] for entry in tape["raw_evidence"]}


def test_derive_findings_succeeds_for_sample_tape():
    findings, no_findings_flag = derive_findings(_sample_tape())

    assert no_findings_flag is False
    assert [finding["rule_id"] for finding in findings] == [
        "RULE-OFFICE-SPAWN-ENCODED-PS",
        "RULE-PS-EXTERNAL-C2",
    ]


def test_derive_findings_succeeds_for_committed_demo_sample():
    findings, no_findings_flag = derive_findings(_demo_tape())

    assert no_findings_flag is False
    assert len(findings) == 4


def test_demo_findings_match_committed_contract():
    findings, no_findings_flag = derive_findings(_demo_tape())
    committed_findings = json.loads(DEMO_FINDINGS_PATH.read_text(encoding="utf-8"))

    assert no_findings_flag is False
    assert findings == committed_findings


def test_all_demo_findings_have_required_contract_fields():
    findings, _no_findings_flag = derive_findings(_demo_tape())

    for finding in findings:
        assert set(finding) == DEMO_FINDING_FIELDS
        assert "finding_id" not in finding


def test_all_evidence_refs_exist_in_tape_raw_evidence():
    tape = _demo_tape()
    findings, _no_findings_flag = derive_findings(tape)
    known_evidence_ids = _evidence_ids(tape)

    for finding in findings:
        assert finding["evidence_refs"]
        assert set(finding["evidence_refs"]).issubset(known_evidence_ids)


def test_model_contribution_is_false_for_every_finding():
    findings, _no_findings_flag = derive_findings(_demo_tape())

    assert all(finding["model_contribution"] is False for finding in findings)


def test_output_is_deterministic_across_repeated_runs():
    tape = _demo_tape()

    first = derive_findings(tape)
    second = derive_findings(tape)

    assert first == second


def test_rule_ids_are_deterministic_and_unique():
    findings, _no_findings_flag = derive_findings(_demo_tape())
    rule_ids = [finding["rule_id"] for finding in findings]

    assert rule_ids == [
        "RULE-OFFICE-SPAWN-ENCODED-PS",
        "RULE-PS-EXTERNAL-C2",
        "RULE-LSASS-DUMP",
        "RULE-SMB-LATERAL-MOVEMENT",
    ]
    assert len(rule_ids) == len(set(rule_ids))


def test_empty_evidence_produces_no_findings_flag():
    findings, no_findings_flag = derive_findings([])

    assert no_findings_flag is True
    assert findings == [
        {
            "evidence_refs": [],
            "model_contribution": False,
            "severity": "info",
            "title": "No evidence - inconclusive",
        }
    ]


def test_non_matching_non_empty_evidence_sets_no_findings_flag():
    evidence = [
        {
            "evidence_id": "ev-network-flow-only",
            "hash": "0" * 64,
            "ingested_at": "2026-05-01T10:00:00Z",
            "raw_content": {"flow_id": "nf-1"},
            "source_type": "network_flow",
        }
    ]

    findings, no_findings_flag = derive_findings(evidence)

    assert findings == []
    assert no_findings_flag is True


@pytest.mark.parametrize("value", ["not-object-or-list", 42, None])
def test_invalid_findings_source_raises_validation_error(value):
    with pytest.raises(ZovarkValidationError):
        derive_findings(value)  # type: ignore[arg-type]


def test_missing_raw_evidence_raises_validation_error():
    tape = _sample_tape()
    tape.pop("raw_evidence")

    with pytest.raises(ZovarkValidationError):
        derive_findings(tape)


def test_raw_evidence_must_be_list():
    tape = _sample_tape()
    tape["raw_evidence"] = {"evidence_id": "ev-not-list"}

    with pytest.raises(ZovarkValidationError):
        derive_findings(tape)


@pytest.mark.parametrize(
    "field",
    ["evidence_id", "source_type", "hash", "raw_content", "ingested_at"],
)
def test_malformed_evidence_shape_raises_validation_error(field):
    tape = _sample_tape()
    tape["raw_evidence"][0].pop(field)

    with pytest.raises(ZovarkValidationError):
        derive_findings(tape)


def test_extra_evidence_shape_field_raises_validation_error():
    tape = _sample_tape()
    tape["raw_evidence"][0]["unexpected"] = "out-of-contract"

    with pytest.raises(ZovarkValidationError):
        derive_findings(tape)


def test_non_object_raw_content_raises_validation_error():
    tape = _sample_tape()
    tape["raw_evidence"][0]["raw_content"] = "not-object"

    with pytest.raises(ZovarkValidationError):
        derive_findings(tape)


def test_attach_findings_returns_copied_tape_without_mutating_raw_evidence():
    tape = _sample_tape()
    findings, no_findings_flag = derive_findings(tape)
    original_tape = deepcopy(tape)

    updated = attach_findings(tape, findings, no_findings_flag)

    assert tape == original_tape
    assert updated is not tape
    assert updated["findings"] == findings
    assert updated["raw_evidence"] == original_tape["raw_evidence"]


def test_attach_findings_preserves_timeline_and_later_stage_fields():
    tape = _sample_tape()
    timeline = build_initial_timeline(tape)
    tape_with_timeline = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape_with_timeline)

    updated = attach_findings(tape_with_timeline, findings, no_findings_flag)

    assert updated["timeline"] == timeline
    assert updated["state"] == "recording"
    assert updated["verdict"] is None
    assert updated["audit_ref"] is None


def test_append_findings_appends_to_existing_findings_on_copied_tape():
    tape = _sample_tape()
    findings, no_findings_flag = derive_findings(tape)

    updated = append_findings(tape, findings, no_findings_flag)

    assert tape["findings"] == []
    assert updated["findings"] == findings
    assert updated["raw_evidence"] == tape["raw_evidence"]
    assert "no_findings_flag" not in updated


def test_append_findings_sets_no_findings_flag_when_true():
    tape = dict(_sample_tape())
    tape["raw_evidence"] = []
    findings, no_findings_flag = derive_findings([])

    updated = append_findings(tape, findings, no_findings_flag)

    assert updated["no_findings_flag"] is True
    assert updated["findings"] == findings
    assert updated["verdict"] is None
    assert updated["audit_ref"] is None


def test_attach_findings_rejects_unknown_evidence_ref():
    tape = _sample_tape()
    findings, no_findings_flag = derive_findings(tape)
    findings[0]["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        attach_findings(tape, findings, no_findings_flag)


def test_attach_findings_rejects_model_contribution_true():
    tape = _sample_tape()
    findings, no_findings_flag = derive_findings(tape)
    findings[0]["model_contribution"] = True

    with pytest.raises(ZovarkValidationError):
        attach_findings(tape, findings, no_findings_flag)


def test_attach_findings_rejects_invalid_severity():
    tape = _sample_tape()
    findings, no_findings_flag = derive_findings(tape)
    findings[0]["severity"] = "urgent"

    with pytest.raises(ZovarkValidationError):
        attach_findings(tape, findings, no_findings_flag)


def test_attach_findings_rejects_duplicate_rule_id():
    tape = _demo_tape()
    findings, no_findings_flag = derive_findings(tape)
    findings[1]["rule_id"] = findings[0]["rule_id"]

    with pytest.raises(ZovarkValidationError):
        attach_findings(tape, findings, no_findings_flag)


def test_no_forbidden_imports_in_findings_module():
    source = Path("zovark/slice001/findings.py").read_text(encoding="utf-8")
    forbidden = [
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "datetime",
        "time",
        "openai",
        "ramalama",
        "temporalio",
        "redis",
        "psycopg2",
        "sqlalchemy",
        "boto3",
    ]

    for name in forbidden:
        assert f"import {name}" not in source
        assert f"from {name}" not in source
    assert "datetime.utcnow" not in source
    assert "datetime.now" not in source
    assert "time.time" not in source
