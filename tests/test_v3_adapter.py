"""Tests for the V3 fixture to Slice proof-package adapter."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.package_verifier import verify_proof_package
from zovark.slice001.v3_adapter import (
    adapt_v3_fixture_to_slice_input,
    build_proof_package_from_v3_fixture,
    build_tape_from_v3_fixture,
    write_proof_package_from_v3_fixture,
)
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


def _representative_v3_fixture() -> dict:
    return {
        "fixture_id": "v3-fixture-saved-plan-001",
        "tenant_id": "tenant-v3",
        "alert": {
            "alert_id": "v3-alert-001",
            "alert_type": "v3_tool_investigation",
            "child_process": "powershell.exe",
            "description": "V3 saved-plan phishing investigation",
            "host": "workstation-42.corp.example",
            "host_fqdn": "workstation-42.corp.example",
            "ingested_at": "2026-05-01T10:00:00Z",
            "severity": "high",
            "source_process": "winword.exe",
            "timestamp": "2026-05-01T10:00:00Z",
        },
        "execution": {
            "execution_mode": "tools",
            "path_taken": "A",
            "source": "saved_plan",
            "plan_executed": "phishing_investigation",
            "tool_names": [
                "extract_ipv4",
                "score_brute_force",
                "correlate_with_history",
            ],
            "tool_results": {
                "extract_ipv4": {
                    "iocs": ["203.0.113.50"],
                    "status": "succeeded",
                },
                "correlate_with_history": {
                    "correlation_count": 1,
                    "status": "succeeded",
                },
            },
            "governance_decision": {
                "autonomy_level": "assist",
                "needs_human_review": True,
                "review_reason": "confirmed malicious verdict",
            },
        },
        "findings": [
            {
                "severity": "critical",
                "title": "Credential access via LSASS memory read",
            }
        ],
        "verdict": {"value": "confirmed_malicious"},
        "process_events": [
            {
                "command_line": "powershell.exe -EncodedCommand <base64>",
                "event_id": "v3-pe-001",
                "event_type": "process_event",
                "parent_pid": 1024,
                "parent_process": "winword.exe",
                "pid": 4812,
                "process_name": "powershell.exe",
                "timestamp": "2026-05-01T10:00:01Z",
                "user": "CORP\\analyst",
            }
        ],
        "network_events": [
            {
                "bytes_received": 245760,
                "destination_ip": "203.0.113.50",
                "destination_port": 443,
                "event_id": "v3-ne-001",
                "event_type": "network_event",
                "pid": 4812,
                "process": "powershell.exe",
                "process_name": "powershell.exe",
                "protocol": "HTTPS",
                "source_host": "workstation-42",
                "timestamp": "2026-05-01T10:00:02Z",
            }
        ],
        "credential_access_events": [
            {
                "event_id": "v3-ca-001",
                "event_type": "credential_access",
                "host": "workstation-42",
                "pid": 4812,
                "process": "powershell.exe",
                "target_process": "lsass.exe",
                "technique": "T1003.001",
                "technique_name": "LSASS Memory",
                "timestamp": "2026-05-01T10:00:03Z",
            }
        ],
        "lateral_movement_events": [
            {
                "destination_host": "HOST-13",
                "destination_ip": "198.51.100.13",
                "event_id": "v3-lm-001",
                "event_type": "lateral_movement_attempt",
                "pid": 4812,
                "process": "powershell.exe",
                "source_host": "workstation-42",
                "status": "blocked_by_firewall",
                "technique": "T1021.002",
                "technique_name": "SMB/Windows Admin Shares",
                "timestamp": "2026-05-01T10:00:04Z",
            }
        ],
    }


def test_v3_fixture_maps_to_slice_input_and_preserves_trace_context():
    raw_input = adapt_v3_fixture_to_slice_input(_representative_v3_fixture())

    assert raw_input["tenant_id"] == "tenant-v3"
    assert raw_input["alert_id"] == "v3-alert-001"
    assert raw_input["v3_trace_context"] == {
        "execution_mode": "tools",
        "path_taken": "A",
        "source": "saved_plan",
        "plan_executed": "phishing_investigation",
        "tool_names": [
            "extract_ipv4",
            "score_brute_force",
            "correlate_with_history",
        ],
        "tool_results": {
            "extract_ipv4": {
                "iocs": ["203.0.113.50"],
                "status": "succeeded",
            },
            "correlate_with_history": {
                "correlation_count": 1,
                "status": "succeeded",
            },
        },
        "governance_decision": {
            "autonomy_level": "assist",
            "needs_human_review": True,
            "review_reason": "confirmed malicious verdict",
        },
        "findings": [
            {
                "severity": "critical",
                "title": "Credential access via LSASS memory read",
            }
        ],
        "verdict": {"value": "confirmed_malicious"},
        "execution_path": "deterministic_tools",
    }


def test_v3_fixture_builds_replay_sealed_tape_and_existing_package():
    tape = build_tape_from_v3_fixture(_representative_v3_fixture())
    package = build_proof_package_from_v3_fixture(_representative_v3_fixture())
    v3_context = tape["raw_evidence"][0]["raw_content"]["v3_trace_context"]

    assert tape["state"] == "closed"
    assert tape["verdict"]["value"] == "confirmed_malicious"
    assert tape["replay_report"]["replay_state"]["state"] == "succeeded"
    assert v3_context["execution_path"] == "deterministic_tools"
    assert set(package) == set(EXPECTED_OUTPUT_FILES)
    assert package["investigation-tape.json"]["raw_evidence"][0]["raw_content"][
        "v3_trace_context"
    ] == v3_context


def test_v3_fixture_written_package_verifies_with_replay_v2(tmp_path):
    output_dir = tmp_path / "v3-package"

    manifest = write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
    )
    summary = verify_proof_package(output_dir)

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert sorted(manifest) == sorted(EXPECTED_OUTPUT_FILES)
    assert summary["status"] == "verified"
    assert summary["replay_state"] == "succeeded"
    assert not (output_dir / "manifest.json").exists()
    assert not (output_dir / "provenance.json").exists()


def test_v3_fixture_adapter_is_deterministic(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    write_proof_package_from_v3_fixture(_representative_v3_fixture(), first_dir)
    write_proof_package_from_v3_fixture(_representative_v3_fixture(), second_dir)

    first_contents = {
        path.name: path.read_text(encoding="utf-8") for path in first_dir.iterdir()
    }
    second_contents = {
        path.name: path.read_text(encoding="utf-8") for path in second_dir.iterdir()
    }
    rendered = json.dumps(first_contents, sort_keys=True)

    assert first_contents == second_contents
    assert str(tmp_path) not in rendered
    assert "/home/" not in rendered


@pytest.mark.parametrize(
    ("execution_mode", "source", "expected_path"),
    [
        ("tools", "saved_plan", "deterministic_tools"),
        ("tools", "llm_tool_call", "llm_selected_tools"),
        ("sandbox_fallback", "fallback", "sandbox_fallback"),
        ("sandbox", "generated", "explicit_sandbox"),
    ],
)
def test_v3_execution_paths_are_distinguished(
    execution_mode,
    source,
    expected_path,
):
    fixture = _representative_v3_fixture()
    fixture["execution"]["execution_mode"] = execution_mode
    fixture["execution"]["source"] = source

    raw_input = adapt_v3_fixture_to_slice_input(fixture)

    assert raw_input["v3_trace_context"]["execution_path"] == expected_path


def test_v3_fixture_rejects_verdict_mismatch():
    fixture = _representative_v3_fixture()
    fixture["verdict"] = {"value": "benign"}

    with pytest.raises(ZovarkValidationError, match="verdict does not match"):
        build_tape_from_v3_fixture(fixture)


def test_v3_fixture_rejects_nested_execution_verdict_mismatch():
    fixture = _representative_v3_fixture()
    fixture.pop("verdict")
    fixture["execution"]["verdict"] = {"value": "benign"}

    with pytest.raises(ZovarkValidationError, match="verdict does not match"):
        build_tape_from_v3_fixture(fixture)


def test_v3_fixture_rejects_conflicting_declared_verdicts():
    fixture = _representative_v3_fixture()
    fixture["execution"]["verdict"] = {"value": "benign"}

    with pytest.raises(ZovarkValidationError, match="conflicting verdicts"):
        build_tape_from_v3_fixture(fixture)


def test_adapter_returns_copies_not_caller_owned_structures():
    fixture = _representative_v3_fixture()
    raw_input = adapt_v3_fixture_to_slice_input(fixture)

    fixture["execution"]["tool_results"]["extract_ipv4"]["status"] = "mutated"

    assert raw_input["v3_trace_context"]["tool_results"]["extract_ipv4"][
        "status"
    ] == "succeeded"


def test_no_forbidden_imports_or_scope_creep_in_v3_adapter():
    source = Path("zovark/slice001/v3_adapter.py").read_text(encoding="utf-8")
    forbidden = [
        "requests",
        "httpx",
        "aiohttp",
        "openai",
        "anthropic",
        "boto3",
        "urllib.request",
        "socket",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "uuid.uuid4",
        "random",
        "manifest.json",
        "provenance.json",
    ]

    for token in forbidden:
        assert token not in source
