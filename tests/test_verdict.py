"""Tests for Slice 001 deterministic verdict derivation."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.hashing import sha256_of_obj
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.tape import create_tape
from zovark.slice001.verdict import (
    APPROVED_VERDICTS,
    attach_verdict,
    compute_verdict,
    derive_verdict,
    set_verdict,
)


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
DEMO_VERDICT_PATH = Path("demo/zovark-proof-package/out/tape-001/verdict.json")
VERDICT_FIELDS = {
    "derivation_rule",
    "evidence_refs",
    "highest_severity_finding",
    "model_contribution",
    "set_at",
    "signing_tag",
    "value",
}


def _sample_tape_with_findings() -> dict:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    tape = create_tape(raw, evidence)
    findings, no_findings_flag = derive_findings(tape)
    return attach_findings(tape, findings, no_findings_flag)


def _demo_committed_tape() -> dict:
    return json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))


def _evidence_entry(evidence_id: str, source_type: str = "edr_alert") -> dict:
    return {
        "evidence_id": evidence_id,
        "hash": "0" * 64,
        "ingested_at": "2026-05-01T10:00:00Z",
        "raw_content": {"event_id": evidence_id},
        "source_type": source_type,
    }


def _finding(
    severity: str,
    evidence_refs: list[str] | None = None,
    *,
    rule_id: str | None = None,
) -> dict:
    finding = {
        "evidence_refs": evidence_refs if evidence_refs is not None else ["ev-1"],
        "model_contribution": False,
        "severity": severity,
        "title": f"{severity} test finding",
    }
    if rule_id is not None:
        finding["rule_id"] = rule_id
    return finding


def _tape_with_findings(
    findings: list[dict],
    *,
    evidence_entries: list[dict] | None = None,
    no_findings_flag: bool = False,
) -> dict:
    entries = evidence_entries if evidence_entries is not None else [_evidence_entry("ev-1")]
    tape = {
        "audit_ref": None,
        "created_at": "2026-05-01T10:00:00Z",
        "findings": findings,
        "raw_evidence": entries,
        "schema_version": "tape/1.0",
        "source_alert_ref": "alert-test",
        "state": "recording",
        "tape_id": "tape-test",
        "tenant_id": "tenant-001",
        "timeline": [],
        "verdict": None,
    }
    if no_findings_flag:
        tape["no_findings_flag"] = True
    return tape


def test_derive_verdict_succeeds_for_committed_demo_sample_pipeline():
    tape = _demo_committed_tape()

    verdict = derive_verdict(tape)

    assert verdict["value"] == "confirmed_malicious"
    assert set(verdict) == VERDICT_FIELDS


def test_derived_demo_verdict_matches_committed_contract():
    tape = _demo_committed_tape()
    committed_verdict = json.loads(DEMO_VERDICT_PATH.read_text(encoding="utf-8"))

    verdict = derive_verdict(tape)

    assert verdict == committed_verdict


def test_sample_pipeline_derives_confirmed_malicious_verdict():
    verdict = derive_verdict(_sample_tape_with_findings())

    assert verdict["value"] == "confirmed_malicious"
    assert verdict["model_contribution"] is False


def test_approved_verdict_enum_only():
    assert APPROVED_VERDICTS == {
        "benign",
        "confirmed_malicious",
        "inconclusive_insufficient_evidence",
        "suspicious_unconfirmed",
    }


def test_high_finding_derives_confirmed_malicious():
    tape = _tape_with_findings([_finding("high")])

    verdict = derive_verdict(tape)

    assert verdict["value"] == "confirmed_malicious"


def test_critical_finding_derives_confirmed_malicious():
    tape = _tape_with_findings([_finding("critical")])

    verdict = derive_verdict(tape)

    assert verdict["value"] == "confirmed_malicious"


def test_medium_only_finding_derives_suspicious_unconfirmed():
    tape = _tape_with_findings([_finding("medium")])

    verdict = derive_verdict(tape)

    assert verdict["value"] == "suspicious_unconfirmed"


@pytest.mark.parametrize("severity", ["low", "info"])
def test_low_or_info_only_finding_derives_benign(severity):
    tape = _tape_with_findings([_finding(severity)])

    verdict = derive_verdict(tape)

    assert verdict["value"] == "benign"


def test_no_findings_flag_derives_inconclusive_insufficient_evidence():
    tape = _tape_with_findings(
        [
            {
                "evidence_refs": [],
                "model_contribution": False,
                "severity": "info",
                "title": "No evidence - inconclusive",
            }
        ],
        evidence_entries=[],
        no_findings_flag=True,
    )

    verdict = derive_verdict(tape)

    assert verdict["value"] == "inconclusive_insufficient_evidence"
    assert verdict["evidence_refs"] == []


def test_empty_findings_without_no_findings_flag_raises_validation_error():
    tape = _tape_with_findings([])

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_verdict_is_deterministic_across_repeated_runs():
    tape = _sample_tape_with_findings()

    first = derive_verdict(tape)
    second = derive_verdict(tape)

    assert first == second


def test_verdict_evidence_refs_are_valid_and_preserve_evidence_order():
    evidence_entries = [
        _evidence_entry("ev-1"),
        _evidence_entry("ev-2", source_type="process_event"),
        _evidence_entry("ev-3", source_type="network_event"),
    ]
    tape = _tape_with_findings(
        [
            _finding("high", ["ev-3", "ev-1"]),
            _finding("medium", ["ev-2"], rule_id="RULE-MEDIUM"),
        ],
        evidence_entries=evidence_entries,
    )

    verdict = derive_verdict(tape)

    assert verdict["evidence_refs"] == ["ev-1", "ev-2", "ev-3"]


def test_signing_tag_is_deterministic_and_recomputable():
    tape = _sample_tape_with_findings()

    verdict = derive_verdict(tape)
    snapshot = {
        "findings": tape["findings"],
        "raw_evidence": tape["raw_evidence"],
        "schema_version": tape["schema_version"],
        "source_alert_ref": tape["source_alert_ref"],
        "tape_id": tape["tape_id"],
        "tenant_id": tape["tenant_id"],
        "verdict_value": verdict["value"],
    }

    assert verdict["signing_tag"] == "sig-" + sha256_of_obj(snapshot)


def test_signing_tag_excludes_timeline_state_audit_and_set_at():
    tape = _sample_tape_with_findings()

    first = derive_verdict(tape)
    changed = deepcopy(tape)
    changed["timeline"] = [{"event_type": "ignored", "at": "2099-01-01T00:00:00Z"}]
    changed["state"] = "closed"
    changed["audit_ref"] = "audit-entry-1"

    second = derive_verdict(changed)

    assert first["signing_tag"] == second["signing_tag"]
    assert first["value"] == second["value"]


def test_set_at_is_deterministic_from_verdict_timeline_event_when_present():
    verdict = derive_verdict(_demo_committed_tape())

    assert verdict["set_at"] == "2026-05-02T09:14:23Z"


def test_set_at_is_deterministic_without_wall_clock():
    tape = _sample_tape_with_findings()

    verdict = derive_verdict(tape)

    assert verdict["set_at"] == "2026-05-01T10:00:01Z"


def test_unknown_finding_evidence_ref_raises_validation_error():
    tape = _tape_with_findings([_finding("high", ["ev-not-present"])])

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_invalid_finding_severity_raises_validation_error():
    tape = _tape_with_findings([_finding("urgent")])

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_finding_model_contribution_true_raises_validation_error():
    finding = _finding("high")
    finding["model_contribution"] = True
    tape = _tape_with_findings([finding])

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_duplicate_rule_ids_raise_validation_error():
    tape = _tape_with_findings(
        [
            _finding("high", ["ev-1"], rule_id="RULE-DUP"),
            _finding("medium", ["ev-1"], rule_id="RULE-DUP"),
        ]
    )

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_finding_id_presence_raises_validation_error():
    finding = _finding("high")
    finding["finding_id"] = "finding-1"
    tape = _tape_with_findings([finding])

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_invalid_verdict_value_raises_validation_error():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    verdict["value"] = "malicious"

    with pytest.raises(ZovarkValidationError):
        attach_verdict(tape, verdict)


@pytest.mark.parametrize("value", [[], "not-object", 42, None])
def test_non_object_tape_raises_validation_error(value):
    with pytest.raises(ZovarkValidationError):
        derive_verdict(value)  # type: ignore[arg-type]


def test_missing_findings_raises_validation_error():
    tape = _sample_tape_with_findings()
    tape.pop("findings")

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_missing_raw_evidence_raises_validation_error():
    tape = _sample_tape_with_findings()
    tape.pop("raw_evidence")

    with pytest.raises(ZovarkValidationError):
        derive_verdict(tape)


def test_compute_verdict_accepts_explicit_findings_evidence_and_tape():
    tape = _sample_tape_with_findings()

    verdict = compute_verdict(tape["findings"], tape["raw_evidence"], tape)

    assert verdict == derive_verdict(tape)


def test_attach_verdict_returns_copy_and_preserves_existing_fields():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    original_tape = deepcopy(tape)

    updated = attach_verdict(tape, verdict)

    assert tape == original_tape
    assert updated is not tape
    assert updated["verdict"] == verdict
    assert updated["raw_evidence"] == original_tape["raw_evidence"]
    assert updated["timeline"] == original_tape["timeline"]
    assert updated["findings"] == original_tape["findings"]
    assert updated["audit_ref"] is None
    assert updated["state"] == "recording"


def test_set_verdict_matches_attach_verdict_behavior():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)

    assert set_verdict(tape, verdict) == attach_verdict(tape, verdict)


def test_attach_verdict_rejects_unknown_evidence_ref():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    verdict["evidence_refs"] = ["ev-not-present"]

    with pytest.raises(ZovarkValidationError):
        attach_verdict(tape, verdict)


def test_attach_verdict_rejects_wrong_signing_tag():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    verdict["signing_tag"] = "sig-" + ("0" * 64)

    with pytest.raises(ZovarkValidationError):
        attach_verdict(tape, verdict)


def test_attach_verdict_rejects_signed_but_non_derived_value():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    verdict["value"] = "benign"
    snapshot = {
        "findings": tape["findings"],
        "raw_evidence": tape["raw_evidence"],
        "schema_version": tape["schema_version"],
        "source_alert_ref": tape["source_alert_ref"],
        "tape_id": tape["tape_id"],
        "tenant_id": tape["tenant_id"],
        "verdict_value": "benign",
    }
    verdict["signing_tag"] = "sig-" + sha256_of_obj(snapshot)

    with pytest.raises(ZovarkValidationError):
        attach_verdict(tape, verdict)


def test_attach_verdict_rejects_model_contribution_true():
    tape = _sample_tape_with_findings()
    verdict = derive_verdict(tape)
    verdict["model_contribution"] = True

    with pytest.raises(ZovarkValidationError):
        attach_verdict(tape, verdict)


def test_no_forbidden_imports_in_verdict_module():
    source = Path("zovark/slice001/verdict.py").read_text(encoding="utf-8")
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
