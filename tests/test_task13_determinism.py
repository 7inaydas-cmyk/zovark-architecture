"""Task 13 determinism and replay-integrity verification."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.replay import derive_replay_report
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES, JSON_OUTPUT_FILES


SAMPLE_PATH = Path("samples/edr-sample-001.json")
FORBIDDEN_SLICE_IMPORTS = {
    "aiohttp",
    "anthropic",
    "boto3",
    "httpx",
    "openai",
    "requests",
    "urllib.request",
}
TIMESTAMP_KEYS = {
    "completed_at",
    "created_at",
    "ingested_at",
    "set_at",
    "started_at",
    "timestamp",
    "validated_at",
}


def _run_module_cli(output_dir: Path, tenant_id: str = "tenant-task13") -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "zovark.slice001",
            "--input",
            str(SAMPLE_PATH),
            "--output",
            str(output_dir),
            "--tenant-id",
            tenant_id,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Slice 001 complete." in result.stdout
    assert "Replay: succeeded" in result.stdout


def _read_file_bytes(output_dir: Path) -> dict[str, bytes]:
    return {
        filename: (output_dir / filename).read_bytes()
        for filename in EXPECTED_OUTPUT_FILES
    }


def _load_json_outputs(output_dir: Path) -> dict[str, object]:
    return {
        filename: json.loads((output_dir / filename).read_text(encoding="utf-8"))
        for filename in JSON_OUTPUT_FILES
    }


def _strip_timestamp_fields(value):
    if isinstance(value, dict):
        return {
            key: _strip_timestamp_fields(item)
            for key, item in value.items()
            if key not in TIMESTAMP_KEYS
        }
    if isinstance(value, list):
        return [_strip_timestamp_fields(item) for item in value]
    return value


def _sealed_tape_from_output(output_dir: Path) -> dict:
    tape = json.loads((output_dir / "investigation-tape.json").read_text(encoding="utf-8"))
    tape["handoff"] = json.loads((output_dir / "edr-handoff.json").read_text(encoding="utf-8"))
    tape["audit_entry"] = json.loads(
        (output_dir / "audit-chain-entry.json").read_text(encoding="utf-8")
    )
    return tape


def test_task13_cli_double_run_outputs_are_deterministic(tmp_path):
    first_out = tmp_path / "first"
    second_out = tmp_path / "second"

    _run_module_cli(first_out)
    _run_module_cli(second_out)

    assert sorted(path.name for path in first_out.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert sorted(path.name for path in second_out.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert _read_file_bytes(first_out) == _read_file_bytes(second_out)


def test_task13_non_timestamp_fields_have_zero_diff_between_cli_runs(tmp_path):
    first_out = tmp_path / "first"
    second_out = tmp_path / "second"

    _run_module_cli(first_out)
    _run_module_cli(second_out)

    first_json = _load_json_outputs(first_out)
    second_json = _load_json_outputs(second_out)
    for filename in JSON_OUTPUT_FILES:
        assert _strip_timestamp_fields(first_json[filename]) == _strip_timestamp_fields(
            second_json[filename]
        )

    assert first_json["verdict.json"]["value"] == second_json["verdict.json"]["value"]
    assert (
        first_json["edr-handoff.json"]["idempotency_key"]
        == second_json["edr-handoff.json"]["idempotency_key"]
    )
    assert (
        first_json["verdict.json"]["signing_tag"]
        == second_json["verdict.json"]["signing_tag"]
    )
    assert (
        first_json["audit-chain-entry.json"]["this_entry_hash"]
        == second_json["audit-chain-entry.json"]["this_entry_hash"]
    )


def test_task13_replay_fails_closed_on_corrupted_evidence_hash(tmp_path):
    output_dir = tmp_path / "out"
    _run_module_cli(output_dir)
    tape = _sealed_tape_from_output(output_dir)

    tape["raw_evidence"][0]["hash"] = "0" * 64

    with pytest.raises(ZovarkValidationError):
        derive_replay_report(tape)


def test_task13_slice001_modules_do_not_import_forbidden_clients():
    for path in sorted(Path("zovark/slice001").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SLICE_IMPORTS:
            assert f"import {forbidden}" not in source, path
            assert f"from {forbidden}" not in source, path
