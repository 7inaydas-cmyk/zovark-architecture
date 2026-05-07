"""Tests for Slice 001 sample ingestion and evidence normalization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string
from zovark.slice001.ingest import load_sample, normalize_evidence


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_LEDGER_PATH = Path("demo/zovark-proof-package/out/tape-001/evidence-ledger.json")


def test_sample_file_loads_successfully_with_path_and_str():
    loaded_from_path = load_sample(SAMPLE_PATH)
    loaded_from_str = load_sample(str(SAMPLE_PATH))

    assert loaded_from_path == loaded_from_str
    assert loaded_from_path["alert_id"] == "alert-20260501-001"


def test_sample_produces_deterministic_evidence_entries():
    raw = load_sample(SAMPLE_PATH)

    first = normalize_evidence(raw)
    second = normalize_evidence(raw)

    assert first == second
    assert [entry["source_type"] for entry in first] == [
        "edr_alert",
        "process_event",
        "network_event",
    ]


def test_first_entry_is_edr_alert():
    entries = normalize_evidence(load_sample(SAMPLE_PATH))

    assert entries[0]["source_type"] == "edr_alert"


def test_evidence_entries_have_exact_required_fields():
    entries = normalize_evidence(load_sample(SAMPLE_PATH))

    for entry in entries:
        assert set(entry) == {"evidence_id", "source_type", "hash", "raw_content"}


def test_hash_recomputes_from_raw_content():
    entries = normalize_evidence(load_sample(SAMPLE_PATH))

    for entry in entries:
        assert entry["hash"] == sha256_of_obj(entry["raw_content"])


def test_evidence_id_is_derived_from_source_type_and_hash():
    entries = normalize_evidence(load_sample(SAMPLE_PATH))

    for entry in entries:
        expected = "ev-" + sha256_of_string(
            f"{entry['source_type']}:{entry['hash']}"
        )
        assert entry["evidence_id"] == expected


def test_demo_sample_evidence_shape_matches_committed_contract():
    raw = load_sample(DEMO_SAMPLE_PATH)
    committed_ledger = json.loads(DEMO_LEDGER_PATH.read_text(encoding="utf-8"))

    evidence = normalize_evidence(raw)
    committed_without_ingest_time = [
        {key: value for key, value in entry.items() if key != "ingested_at"}
        for entry in committed_ledger
    ]

    assert [entry["source_type"] for entry in evidence] == [
        "edr_alert",
        "process_event",
        "network_event",
        "credential_access",
        "lateral_movement_attempt",
    ]
    assert len(evidence) == 5
    assert evidence == committed_without_ingest_time


def test_changing_raw_content_changes_hash_and_evidence_id():
    raw = load_sample(SAMPLE_PATH)
    changed = json.loads(json.dumps(raw))
    changed["process_events"][0]["command_line"] = "powershell.exe -NoProfile"

    original_process = normalize_evidence(raw)[1]
    changed_process = normalize_evidence(changed)[1]

    assert original_process["hash"] != changed_process["hash"]
    assert original_process["evidence_id"] != changed_process["evidence_id"]


def test_json_object_key_order_does_not_change_hash():
    raw_a = {
        "alert_id": "a-1",
        "alert_type": "edr_alert",
        "host": "workstation-42.corp.example",
    }
    raw_b = {
        "host": "workstation-42.corp.example",
        "alert_type": "edr_alert",
        "alert_id": "a-1",
    }

    entry_a = normalize_evidence(raw_a)[0]
    entry_b = normalize_evidence(raw_b)[0]

    assert entry_a["hash"] == entry_b["hash"]
    assert entry_a["evidence_id"] == entry_b["evidence_id"]


def test_array_order_is_preserved():
    raw = {
        "alert_id": "alert-order",
        "process_events": [
            {"event_id": "pe-2", "event_type": "process_event"},
            {"event_id": "pe-1", "event_type": "process_event"},
        ],
        "network_events": [
            {"event_id": "ne-2", "event_type": "network_event"},
            {"event_id": "ne-1", "event_type": "network_event"},
        ],
    }

    entries = normalize_evidence(raw)

    assert [entry["raw_content"].get("event_id") for entry in entries] == [
        None,
        "pe-2",
        "pe-1",
        "ne-2",
        "ne-1",
    ]


def test_network_flows_key_is_supported():
    raw = {
        "alert_id": "alert-flow",
        "network_flows": [
            {"flow_id": "nf-1", "destination_ip": "203.0.113.50"},
        ],
    }

    entries = normalize_evidence(raw)

    assert entries[1]["source_type"] == "network_flow"
    assert entries[1]["raw_content"]["flow_id"] == "nf-1"


def test_missing_process_and_network_arrays_do_not_fail_when_alert_exists():
    entries = normalize_evidence({"alert_id": "alert-only"})

    assert len(entries) == 1
    assert entries[0]["source_type"] == "edr_alert"


def test_empty_object_raises_validation_error():
    with pytest.raises(ZovarkValidationError):
        normalize_evidence({})


@pytest.mark.parametrize("value", [[], "not-object", 42, None])
def test_non_object_top_level_json_raises_validation_error(value):
    with pytest.raises(ZovarkValidationError):
        normalize_evidence(value)  # type: ignore[arg-type]


def test_load_sample_rejects_non_object_top_level_json(tmp_path):
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ZovarkValidationError):
        load_sample(path)


def test_load_sample_rejects_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ZovarkValidationError):
        load_sample(path)


def test_source_objects_must_be_json_objects():
    raw = {
        "alert_id": "alert-bad-event",
        "process_events": ["not-object"],
    }

    with pytest.raises(ZovarkValidationError):
        normalize_evidence(raw)


def test_event_collections_must_be_arrays():
    raw = {
        "alert_id": "alert-bad-array",
        "network_events": {"event_id": "ne-1"},
    }

    with pytest.raises(ZovarkValidationError):
        normalize_evidence(raw)


def test_no_forbidden_imports_in_ingest_module():
    source = Path("zovark/slice001/ingest.py").read_text(encoding="utf-8")
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
    ]

    for name in forbidden:
        assert f"import {name}" not in source
        assert f"from {name}" not in source
