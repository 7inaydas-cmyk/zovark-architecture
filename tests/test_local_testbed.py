"""Tests for the local static proof/Replay testbed runner."""

from __future__ import annotations

import json
from pathlib import Path

from zovark.slice001.local_testbed import main
from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    verify_proof_package,
)
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


SAMPLE_FIXTURE = Path("samples/v3-local-proof-fixture.json")
RAW_LEAK_SENTINELS = (
    "RAW_COUNTER_EVIDENCE_CONTENT_SENTINEL",
    "RAW_MESSAGE_SENTINEL",
    "RAW_ANALYST_NOTE_SENTINEL",
    "RAW_REASONING_SENTINEL",
    "RAW_USER_PROMPT_SENTINEL",
    "RAW_TOOL_OUTPUT_SENTINEL",
    "RAW_PAYLOAD_SENTINEL",
    "HIDDEN_REASONING_SENTINEL",
    "RAW_PROMPT_MESSAGE_SENTINEL",
    "RAW_SYSTEM_PROMPT_SENTINEL",
    "RAW_USER_PROMPT_TEXT_SENTINEL",
    "RAW_TOOL_ARGUMENT_SENTINEL",
    "RAW_TOOL_MESSAGE_SENTINEL",
    "RAW_TOOL_OUTPUT_BODY_SENTINEL",
    "RAW_TOOL_PAYLOAD_SENTINEL",
    "RAW_TOOL_REASONING_SENTINEL",
)
UNSAFE_SAMPLE_KEYS = {
    "args",
    "arguments",
    "chain_of_thought",
    "content",
    "hidden_reasoning",
    "messages",
    "notes",
    "output",
    "payload",
    "prompt",
    "raw_system_prompt",
    "raw_user_prompt",
    "reasoning",
    "tool_results",
}


def _run_local_testbed(
    output_dir: Path,
    *,
    package_version: str,
    input_path: Path = SAMPLE_FIXTURE,
) -> int:
    return main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--package-version",
            package_version,
        ]
    )


def _load_json(package_dir: Path, filename: str):
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _render_package(package_dir: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(package_dir.iterdir())
        if path.is_file()
    )


def _collect_keys(value) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for child in value.values():
            keys.update(_collect_keys(child))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_collect_keys(item))
        return keys
    return set()


def _v3_trace_context(package_dir: Path) -> dict:
    tape = _load_json(package_dir, "investigation-tape.json")
    return tape["raw_evidence"][0]["raw_content"]["v3_trace_context"]


def test_local_testbed_v1_generation_remains_v1_only(tmp_path, capsys):
    output_dir = tmp_path / "local-v1"

    exit_code = _run_local_testbed(output_dir, package_version="v1")
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert V2_MARKER_FILE not in {path.name for path in output_dir.iterdir()}
    assert "Package version: v1" in stdout
    assert "Offline Replay verification: succeeded" in stdout
    assert verify_proof_package(output_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )
    context = _v3_trace_context(output_dir)
    for key in (
        "context_enrichment",
        "visibility_gaps",
        "approval_record",
        "customer_report_v2",
        "prompt_transformation_log",
        "tool_call_chain_summary",
    ):
        assert key not in context


def test_local_testbed_v2_generation_verifies_with_offline_replay(tmp_path, capsys):
    output_dir = tmp_path / "local-v2"

    exit_code = _run_local_testbed(output_dir, package_version="v2")
    stdout = capsys.readouterr().out
    summary = verify_proof_package(output_dir)

    assert exit_code == 0
    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES + (V2_MARKER_FILE,)
    )
    assert "Package version: v2" in stdout
    assert "Offline Replay verification: succeeded" in stdout
    assert summary["status"] == "verified"
    assert summary["replay_state"] == "succeeded"
    assert summary["failure_count"] == 0
    assert summary["package_contract"] == V2_PACKAGE_CONTRACT
    assert summary["package_version"] == V2_PACKAGE_CONTRACT


def test_local_testbed_sample_fixture_and_output_have_no_raw_leakage(tmp_path):
    fixture = json.loads(SAMPLE_FIXTURE.read_text(encoding="utf-8"))
    output_dir = tmp_path / "local-v2"

    assert _run_local_testbed(output_dir, package_version="v2") == 0
    rendered = _render_package(output_dir)

    assert not (_collect_keys(fixture) & UNSAFE_SAMPLE_KEYS)
    for sentinel in RAW_LEAK_SENTINELS:
        assert sentinel not in rendered
        assert sentinel not in SAMPLE_FIXTURE.read_text(encoding="utf-8")


def test_local_testbed_v2_output_is_deterministic(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    assert _run_local_testbed(first_dir, package_version="v2") == 0
    assert _run_local_testbed(second_dir, package_version="v2") == 0

    first = {path.name: path.read_text(encoding="utf-8") for path in first_dir.iterdir()}
    second = {
        path.name: path.read_text(encoding="utf-8") for path in second_dir.iterdir()
    }
    assert first == second
    assert verify_proof_package(first_dir) == verify_proof_package(second_dir)


def test_local_testbed_bad_input_errors_are_bounded(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not-json", encoding="utf-8")

    assert _run_local_testbed(tmp_path / "missing-out", input_path=missing, package_version="v2") == 1
    assert "input not found" in capsys.readouterr().err
    assert _run_local_testbed(tmp_path / "bad-out", input_path=bad_json, package_version="v2") == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_local_testbed_module_does_not_add_out_of_scope_dependencies():
    source = Path("zovark/slice001/local_testbed.py").read_text(encoding="utf-8")
    forbidden = (
        "requests",
        "httpx",
        "openai",
        "anthropic",
        "boto3",
        "socket",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "uuid.uuid4",
        "slsa",
        "in_toto",
        "opentimestamps",
    )
    for token in forbidden:
        assert token not in source
