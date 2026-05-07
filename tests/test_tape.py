"""Tests for Slice 001 investigation tape creation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.hashing import sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.tape import create_tape


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
REQUIRED_TAPE_FIELDS = {
    "tape_id",
    "tenant_id",
    "schema_version",
    "source_alert_ref",
    "state",
    "created_at",
    "raw_evidence",
    "timeline",
    "findings",
    "verdict",
    "audit_ref",
}


def _sample_tape() -> tuple[dict, list[dict], dict]:
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    tape = create_tape(raw, evidence)
    return raw, evidence, tape


def test_create_tape_succeeds_from_sample_and_ingest_output():
    raw, evidence, tape = _sample_tape()

    assert tape["source_alert_ref"] == raw["alert_id"]
    assert tape["raw_evidence"] == evidence
    assert tape["state"] == "recording"


def test_tape_contains_required_initial_fields():
    _raw, _evidence, tape = _sample_tape()

    assert set(tape) == REQUIRED_TAPE_FIELDS
    assert tape["tenant_id"] == "tenant-001"
    assert tape["schema_version"] == "tape/1.0"
    assert tape["timeline"] == []
    assert tape["findings"] == []
    assert tape["verdict"] is None
    assert tape["audit_ref"] is None
    assert "replay_state_ref" not in tape
    assert tape["state"] != "replaying"


def test_tape_id_is_deterministic_across_repeated_runs():
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)

    first = create_tape(raw, evidence)
    second = create_tape(raw, evidence)

    expected = "tape-" + sha256_of_string("tenant-001:alert-20260501-001")[:16]
    assert first["tape_id"] == second["tape_id"] == expected


def test_tape_id_uses_explicit_tenant_id_when_provided():
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)

    tape = create_tape(raw, evidence, tenant_id="tenant-custom")

    expected = "tape-" + sha256_of_string("tenant-custom:alert-20260501-001")[:16]
    assert tape["tenant_id"] == "tenant-custom"
    assert tape["tape_id"] == expected


def test_created_at_is_deterministic_and_derived_from_source_alert():
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)

    first = create_tape(raw, evidence)
    second = create_tape(raw, evidence)

    assert first["created_at"] == second["created_at"]
    assert first["created_at"] == raw["timestamp"]


def test_demo_sample_uses_explicit_ingested_at_for_created_at():
    raw = load_sample(DEMO_SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    committed_demo_tape = json.loads(DEMO_TAPE_PATH.read_text(encoding="utf-8"))

    tape = create_tape(raw, evidence, tenant_id=committed_demo_tape["tenant_id"])

    assert tape["created_at"] == committed_demo_tape["created_at"]


def test_raw_evidence_equals_ingest_output_exactly():
    _raw, evidence, tape = _sample_tape()

    assert tape["raw_evidence"] == evidence


def test_evidence_ordering_is_preserved():
    _raw, evidence, tape = _sample_tape()

    assert [entry["evidence_id"] for entry in tape["raw_evidence"]] == [
        entry["evidence_id"] for entry in evidence
    ]


def test_raw_content_and_ingested_at_survive_unchanged():
    _raw, evidence, tape = _sample_tape()

    for original, stored in zip(evidence, tape["raw_evidence"], strict=True):
        assert stored["raw_content"] == original["raw_content"]
        assert stored["ingested_at"] == original["ingested_at"]


def test_empty_evidence_list_raises_validation_error():
    raw = load_sample(SAMPLE_PATH)

    with pytest.raises(ZovarkValidationError):
        create_tape(raw, [])


def test_invalid_evidence_entry_missing_required_field_raises_validation_error():
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    invalid = [dict(evidence[0])]
    invalid[0].pop("ingested_at")

    with pytest.raises(ZovarkValidationError):
        create_tape(raw, invalid)


def test_invalid_extra_evidence_field_raises_validation_error():
    raw = load_sample(SAMPLE_PATH)
    evidence = normalize_evidence(raw)
    invalid = [dict(evidence[0], unexpected="out-of-contract")]

    with pytest.raises(ZovarkValidationError):
        create_tape(raw, invalid)


@pytest.mark.parametrize("value", [[], "not-object", 42, None])
def test_non_dict_raw_input_raises_validation_error(value):
    evidence = normalize_evidence(load_sample(SAMPLE_PATH))

    with pytest.raises(ZovarkValidationError):
        create_tape(value, evidence)  # type: ignore[arg-type]


def test_missing_deterministic_timestamp_raises_validation_error():
    raw = {"alert_id": "alert-no-time"}
    evidence = [
        {
            "evidence_id": "ev-test",
            "source_type": "edr_alert",
            "hash": "0" * 64,
            "raw_content": {"alert_id": "alert-no-time"},
            "ingested_at": "2026-05-01T10:00:00Z",
        }
    ]

    with pytest.raises(ZovarkValidationError):
        create_tape(raw, evidence)


def test_no_forbidden_imports_in_tape_module():
    source = Path("zovark/slice001/tape.py").read_text(encoding="utf-8")
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
