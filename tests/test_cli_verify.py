"""Tests for the Slice 002 package verification CLI wrapper."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from zovark.slice001.cli import main
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


SAMPLE_PATH = Path("samples/edr-sample-001.json")
DEMO_PACKAGE_DIR = Path("demo/zovark-proof-package/out/tape-001")
FORBIDDEN_IMPORTS = (
    "requests",
    "httpx",
    "aiohttp",
    "openai",
    "anthropic",
    "boto3",
    "urllib.request",
    "socket",
    "manifest.json",
    "provenance.json",
)


def _run_generate(output_dir: Path) -> int:
    return main(
        [
            "--input",
            str(SAMPLE_PATH),
            "--output",
            str(output_dir),
            "--tenant-id",
            "tenant-001",
        ]
    )


def _run_verify(package_dir: Path) -> int:
    return main(["verify", "--package", str(package_dir)])


def _load_json(package_dir: Path, filename: str):
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _store_json(package_dir: Path, filename: str, obj) -> None:
    (package_dir / filename).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def test_existing_generation_cli_still_writes_expected_artifacts(tmp_path):
    output_dir = tmp_path / "out"

    assert _run_generate(output_dir) == 0

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )


def test_verify_generated_package_succeeds(tmp_path, capsys):
    output_dir = tmp_path / "out"
    assert _run_generate(output_dir) == 0

    exit_code = _run_verify(output_dir)
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert "Slice 001 package verification succeeded." in stdout
    assert "status: verified" in stdout
    assert "package_contract: slice-001-proof-package/1.0" in stdout
    assert "artifact_count: 9" in stdout
    assert "replay_state: succeeded" in stdout


def test_verify_committed_demo_package_succeeds(capsys):
    exit_code = _run_verify(DEMO_PACKAGE_DIR)
    stdout = capsys.readouterr().out

    assert exit_code == 0
    assert "Slice 001 package verification succeeded." in stdout
    assert "verdict: confirmed_malicious" in stdout
    assert "tape_id: tape-001" in stdout


def test_verify_tampered_package_fails(tmp_path, capsys):
    output_dir = tmp_path / "out"
    assert _run_generate(output_dir) == 0
    tape = _load_json(output_dir, "investigation-tape.json")
    tape["state"] = "recording"
    _store_json(output_dir, "investigation-tape.json", tape)

    exit_code = _run_verify(output_dir)
    stderr = capsys.readouterr().err

    assert exit_code == 3
    assert "package verification failed" in stderr
    assert "state must be closed" in stderr


def test_verify_missing_package_fails(tmp_path, capsys):
    exit_code = _run_verify(tmp_path / "missing-package")
    stderr = capsys.readouterr().err

    assert exit_code == 3
    assert "package verification failed" in stderr
    assert "directory does not exist" in stderr


def test_verify_extra_file_fails(tmp_path, capsys):
    output_dir = tmp_path / "out"
    assert _run_generate(output_dir) == 0
    (output_dir / "extra.txt").write_text("unexpected", encoding="utf-8")

    exit_code = _run_verify(output_dir)
    stderr = capsys.readouterr().err

    assert exit_code == 3
    assert "file set is invalid" in stderr


def test_verify_does_not_mutate_output_files(tmp_path):
    output_dir = tmp_path / "out"
    assert _run_generate(output_dir) == 0
    before = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(output_dir.iterdir())
    }

    assert _run_verify(output_dir) == 0

    after = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(output_dir.iterdir())
    }
    assert after == before


def test_verify_malformed_package_fails(tmp_path, capsys):
    package_dir = tmp_path / "package"
    shutil.copytree(DEMO_PACKAGE_DIR, package_dir)
    (package_dir / "verdict.json").write_text("{not-json", encoding="utf-8")

    exit_code = _run_verify(package_dir)
    stderr = capsys.readouterr().err

    assert exit_code == 3
    assert "not valid JSON" in stderr


def test_verify_cli_requires_package_flag():
    try:
        main(["verify"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("verify without --package should exit through argparse")


def test_no_forbidden_imports_or_scope_creep_in_cli_verify_path():
    sources = [
        Path("zovark/slice001/cli.py").read_text(encoding="utf-8"),
        Path("zovark/slice001/__main__.py").read_text(encoding="utf-8"),
    ]

    for source in sources:
        for token in FORBIDDEN_IMPORTS:
            assert token not in source
    assert set(EXPECTED_OUTPUT_FILES) == {
        "audit-chain-entry.json",
        "customer-report.md",
        "edr-handoff.json",
        "evidence-ledger.json",
        "findings.json",
        "investigation-tape.json",
        "replay-report.json",
        "timeline.json",
        "verdict.json",
    }
