"""End-to-end tests for the Slice 001 CLI."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from zovark.slice001.cli import build_completed_tape, main
from zovark.slice001.ingest import load_sample
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES, JSON_OUTPUT_FILES


SAMPLE_PATH = Path("samples/edr-sample-001.json")


def _run_cli(input_path: Path, output_dir: Path, tenant_id: str = "tenant-001") -> int:
    return main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_dir),
            "--tenant-id",
            tenant_id,
        ]
    )


def _load_output(output_dir: Path, filename: str):
    return json.loads((output_dir / filename).read_text(encoding="utf-8"))


def test_cli_end_to_end_writes_all_expected_artifacts(tmp_path, capsys):
    output_dir = tmp_path / "out"

    exit_code = _run_cli(SAMPLE_PATH, output_dir)

    assert exit_code == 0
    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert "phishing-powershell.json" not in {
        path.name for path in output_dir.iterdir()
    }
    stdout = capsys.readouterr().out
    assert "Slice 001 complete." in stdout
    assert "Replay: succeeded" in stdout
    for filename in EXPECTED_OUTPUT_FILES:
        assert filename in stdout
        assert str(output_dir / filename) in stdout


def test_cli_json_outputs_parse_and_customer_report_is_non_empty(tmp_path):
    output_dir = tmp_path / "out"

    assert _run_cli(SAMPLE_PATH, output_dir) == 0

    for filename in JSON_OUTPUT_FILES:
        assert _load_output(output_dir, filename)
    assert (output_dir / "customer-report.md").read_text(encoding="utf-8")


def test_cli_replay_report_succeeds(tmp_path):
    output_dir = tmp_path / "out"

    assert _run_cli(SAMPLE_PATH, output_dir) == 0

    replay_report = _load_output(output_dir, "replay-report.json")
    assert replay_report["replay_state"]["state"] == "succeeded"
    assert replay_report["replay_state"]["no_live_llm_call"] is True
    assert replay_report["replay_state"]["no_live_edr_call"] is True


def test_cli_output_artifacts_match_investigation_tape_fields(tmp_path):
    output_dir = tmp_path / "out"

    assert _run_cli(SAMPLE_PATH, output_dir) == 0

    investigation_tape = _load_output(output_dir, "investigation-tape.json")
    assert _load_output(output_dir, "evidence-ledger.json") == investigation_tape[
        "raw_evidence"
    ]
    assert _load_output(output_dir, "timeline.json") == investigation_tape["timeline"]
    assert _load_output(output_dir, "findings.json") == investigation_tape["findings"]
    assert _load_output(output_dir, "verdict.json") == investigation_tape["verdict"]


def test_cli_missing_input_file_exits_1(tmp_path, capsys):
    exit_code = _run_cli(tmp_path / "missing.json", tmp_path / "out")

    assert exit_code == 1
    assert "input not found" in capsys.readouterr().err


def test_cli_invalid_json_exits_2(tmp_path, capsys):
    bad_input = tmp_path / "bad.json"
    bad_input.write_text("{not-json", encoding="utf-8")

    exit_code = _run_cli(bad_input, tmp_path / "out")

    assert exit_code == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_cli_validation_error_exits_3(tmp_path, capsys):
    invalid_input = tmp_path / "invalid.json"
    invalid_input.write_text(
        json.dumps({"alert_id": "alert-missing-time"}),
        encoding="utf-8",
    )

    exit_code = _run_cli(invalid_input, tmp_path / "out")

    assert exit_code == 3
    assert "validation failed" in capsys.readouterr().err


def test_cli_output_directory_error_exits_4(tmp_path, capsys):
    output_path = tmp_path / "not-a-directory"
    output_path.write_text("file", encoding="utf-8")

    exit_code = _run_cli(SAMPLE_PATH, output_path)

    assert exit_code == 4
    assert "validation failed" in capsys.readouterr().err


def test_cli_twice_same_input_has_identical_deterministic_fields(tmp_path):
    first_out = tmp_path / "out-1"
    second_out = tmp_path / "out-2"

    assert _run_cli(SAMPLE_PATH, first_out, tenant_id="tenant-repeat") == 0
    assert _run_cli(SAMPLE_PATH, second_out, tenant_id="tenant-repeat") == 0

    first_verdict = _load_output(first_out, "verdict.json")
    second_verdict = _load_output(second_out, "verdict.json")
    first_handoff = _load_output(first_out, "edr-handoff.json")
    second_handoff = _load_output(second_out, "edr-handoff.json")
    first_audit = _load_output(first_out, "audit-chain-entry.json")
    second_audit = _load_output(second_out, "audit-chain-entry.json")

    assert first_verdict["value"] == second_verdict["value"]
    assert first_verdict["signing_tag"] == second_verdict["signing_tag"]
    assert first_handoff["idempotency_key"] == second_handoff["idempotency_key"]
    assert first_audit["this_entry_hash"] == second_audit["this_entry_hash"]


def test_cli_runs_with_socket_blocked(tmp_path):
    output_dir = tmp_path / "out"

    with patch.object(socket, "socket", side_effect=OSError("network blocked")):
        exit_code = _run_cli(SAMPLE_PATH, output_dir)

    assert exit_code == 0
    assert (output_dir / "replay-report.json").exists()


def test_python_module_entrypoint_imports_cli_main():
    import zovark.slice001.__main__ as module_main
    import zovark.slice001.cli as cli

    assert module_main.main is cli.main


def test_build_completed_tape_is_deterministic():
    raw_input = load_sample(SAMPLE_PATH)

    first = build_completed_tape(raw_input, tenant_id="tenant-repeat")
    second = build_completed_tape(raw_input, tenant_id="tenant-repeat")

    assert first == second
    assert first["state"] == "closed"
    assert first["replay_report"]["replay_state"]["state"] == "succeeded"


def test_no_forbidden_imports_or_scope_creep_in_cli_modules():
    sources = [
        Path("zovark/slice001/cli.py").read_text(encoding="utf-8"),
        Path("zovark/slice001/__main__.py").read_text(encoding="utf-8"),
    ]
    forbidden = [
        "requests",
        "httpx",
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
        "Sentry",
        "sentry",
    ]
    for source in sources:
        for token in forbidden:
            assert token not in source


@pytest.mark.parametrize("flag", ["--input", "--output"])
def test_cli_requires_input_and_output_flags(flag):
    args = ["--input", "samples/edr-sample-001.json", "--output", "out"]
    index = args.index(flag)
    del args[index : index + 2]

    with pytest.raises(SystemExit):
        main(args)
