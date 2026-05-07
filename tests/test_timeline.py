"""Tests for Slice 001 timeline construction."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.timeline import attach_timeline, build_initial_timeline
from zovark.slice001.tape import create_tape


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_SAMPLE_PATH = Path("demo/zovark-proof-package/samples/edr/phishing-powershell.json")
DEMO_TIMELINE_PATH = Path("demo/zovark-proof-package/out/tape-001/timeline.json")
DEMO_TAPE_PATH = Path("demo/zovark-proof-package/out/tape-001/investigation-tape.json")
TIMELINE_EVENT_FIELDS = {
    "actor",
    "at",
    "decision_contribution",
    "event_type",
    "evidence_refs",
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


def test_build_initial_timeline_succeeds_for_sample_tape():
    tape = _sample_tape()

    timeline = build_initial_timeline(tape)

    assert len(timeline) == 1 + len(tape["raw_evidence"])
    assert all(set(event) == TIMELINE_EVENT_FIELDS for event in timeline)


def test_demo_initial_timeline_matches_committed_contract_prefix():
    timeline = build_initial_timeline(_demo_tape())
    committed_timeline = json.loads(DEMO_TIMELINE_PATH.read_text(encoding="utf-8"))

    assert timeline == committed_timeline[: len(timeline)]


def test_timeline_has_alert_received_first():
    timeline = build_initial_timeline(_sample_tape())

    assert timeline[0]["event_type"] == "alert_received"
    assert timeline[0]["actor"] == "system"
    assert timeline[0]["decision_contribution"] is False


def test_one_evidence_added_event_per_raw_evidence_entry():
    tape = _sample_tape()

    timeline = build_initial_timeline(tape)
    evidence_added = [
        event for event in timeline if event["event_type"] == "evidence_added"
    ]

    assert len(evidence_added) == len(tape["raw_evidence"])


def test_evidence_added_events_preserve_raw_evidence_order():
    tape = _sample_tape()

    timeline = build_initial_timeline(tape)
    evidence_added = timeline[1:]

    assert [event["evidence_refs"][0] for event in evidence_added] == [
        entry["evidence_id"] for entry in tape["raw_evidence"]
    ]


def test_timeline_is_deterministic_across_repeated_runs():
    tape = _sample_tape()

    first = build_initial_timeline(tape)
    second = build_initial_timeline(tape)

    assert first == second
    assert all("event_id" not in event for event in first)


def test_timestamps_are_deterministic_and_non_decreasing():
    tape = _sample_tape()

    timeline = build_initial_timeline(tape)
    timestamps = [event["at"] for event in timeline]

    assert timestamps[0] == tape["created_at"]
    assert timestamps[1:] == [
        entry["ingested_at"] for entry in tape["raw_evidence"]
    ]
    assert timestamps == sorted(timestamps)


def test_evidence_refs_match_corresponding_evidence_ids():
    tape = _sample_tape()

    timeline = build_initial_timeline(tape)

    assert timeline[0]["evidence_refs"] == [tape["raw_evidence"][0]["evidence_id"]]
    for event, entry in zip(timeline[1:], tape["raw_evidence"], strict=True):
        assert event["evidence_refs"] == [entry["evidence_id"]]


def test_initial_timeline_events_do_not_contribute_to_decision():
    timeline = build_initial_timeline(_sample_tape())

    assert all(event["decision_contribution"] is False for event in timeline)


def test_timeline_construction_does_not_mutate_raw_evidence():
    tape = _sample_tape()
    original_raw_evidence = deepcopy(tape["raw_evidence"])

    build_initial_timeline(tape)

    assert tape["raw_evidence"] == original_raw_evidence


def test_attach_timeline_returns_new_tape_without_mutating_raw_evidence():
    tape = _sample_tape()
    timeline = build_initial_timeline(tape)
    original_tape = deepcopy(tape)

    updated = attach_timeline(tape, timeline)

    assert tape == original_tape
    assert updated is not tape
    assert updated["timeline"] == timeline
    assert updated["raw_evidence"] == original_tape["raw_evidence"]
    assert updated["state"] == "recording"
    assert updated["findings"] == []
    assert updated["verdict"] is None
    assert updated["audit_ref"] is None


@pytest.mark.parametrize("value", [[], "not-object", 42, None])
def test_invalid_tape_shape_raises_validation_error(value):
    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(value)  # type: ignore[arg-type]


def test_missing_raw_evidence_raises_validation_error():
    tape = _sample_tape()
    tape.pop("raw_evidence")

    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(tape)


def test_raw_evidence_must_be_list():
    tape = _sample_tape()
    tape["raw_evidence"] = {"evidence_id": "ev-not-list"}

    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(tape)


def test_missing_evidence_id_raises_validation_error():
    tape = _sample_tape()
    tape["raw_evidence"][0].pop("evidence_id")

    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(tape)


def test_missing_ingested_at_raises_validation_error():
    tape = _sample_tape()
    tape["raw_evidence"][0].pop("ingested_at")

    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(tape)


def test_decreasing_timestamps_raise_validation_error():
    tape = _sample_tape()
    tape["raw_evidence"][1]["ingested_at"] = "1999-01-01T00:00:00Z"

    with pytest.raises(ZovarkValidationError):
        build_initial_timeline(tape)


def test_attach_timeline_rejects_invalid_timeline_shape():
    tape = _sample_tape()

    with pytest.raises(ZovarkValidationError):
        attach_timeline(tape, [{"event_type": "evidence_added"}])


def test_no_forbidden_imports_in_timeline_module():
    source = Path("zovark/slice001/timeline.py").read_text(encoding="utf-8")
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
