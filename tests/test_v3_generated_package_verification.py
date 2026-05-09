"""End-to-end gate for V3-generated proof packages and Replay V2 verification."""

from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path

from zovark.slice001.cli import main
from zovark.slice001.package_verifier import verify_proof_package
from zovark.slice001.v3_adapter import write_proof_package_from_v3_fixture
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


def _v3_fixture() -> dict:
    return {
        "fixture_id": "v3-e2e-fixture-001",
        "tenant_id": "tenant-v3-e2e",
        "alert": {
            "alert_id": "v3-e2e-alert-001",
            "alert_type": "v3_tool_investigation",
            "child_process": "powershell.exe",
            "description": "V3 generated package verification fixture",
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
                "event_id": "v3-e2e-pe-001",
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
                "event_id": "v3-e2e-ne-001",
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
                "event_id": "v3-e2e-ca-001",
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
                "event_id": "v3-e2e-lm-001",
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


def _write_package(tmp_path: Path, fixture: dict | None = None) -> Path:
    package_dir = tmp_path / "v3-package"
    write_proof_package_from_v3_fixture(fixture or _v3_fixture(), package_dir)
    return package_dir


def _load_json(package_dir: Path, filename: str):
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _trace_context(package_dir: Path) -> dict:
    tape = _load_json(package_dir, "investigation-tape.json")
    return tape["raw_evidence"][0]["raw_content"]["v3_trace_context"]


def test_v3_generated_package_verifies_with_replay_v2(tmp_path):
    package_dir = _write_package(tmp_path)
    summary = verify_proof_package(package_dir)

    assert sorted(path.name for path in package_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert summary["status"] == "verified"
    assert summary["replay_state"] == "succeeded"
    assert summary["failure_count"] == 0
    assert summary["failure_codes"] == []
    assert summary == verify_proof_package(package_dir)


def test_v3_generated_package_cli_verify_succeeds(tmp_path, capsys):
    package_dir = _write_package(tmp_path)

    exit_code = main(["verify", "--package", str(package_dir)])

    assert exit_code == 0
    stdout = capsys.readouterr().out
    assert "Zovark package verification: succeeded" in stdout
    assert "Result: verified" in stdout
    assert str(package_dir) not in stdout


def test_v3_generated_package_preserves_non_conflicting_context(tmp_path):
    package_dir = _write_package(tmp_path)
    context = _trace_context(package_dir)
    verdict = _load_json(package_dir, "verdict.json")

    assert context["execution_mode"] == "tools"
    assert context["path_taken"] == "A"
    assert context["source"] == "saved_plan"
    assert context["plan_executed"] == "phishing_investigation"
    assert context["execution_path"] == "deterministic_tools"
    assert context["verdict"]["value"] == verdict["value"]
    assert context["verdict"]["value"] == "confirmed_malicious"


def test_v3_generated_package_path_distinctions_are_visible(tmp_path):
    cases = [
        ("tools", "saved_plan", "deterministic_tools"),
        ("tools", "llm_tool_call", "llm_selected_tools"),
        ("sandbox_fallback", "fallback", "sandbox_fallback"),
    ]

    for execution_mode, source, expected_path in cases:
        fixture = deepcopy(_v3_fixture())
        fixture["execution"]["execution_mode"] = execution_mode
        fixture["execution"]["source"] = source
        if expected_path == "llm_selected_tools":
            fixture["execution"]["prompt_hash"] = "sha256:prompt-hash"
            fixture["execution"]["prompt_version"] = "prompt/v1"
        if expected_path == "sandbox_fallback":
            fixture["execution"]["generated_code_hash"] = "sha256:generated-code"
            fixture["execution"]["scrubbed_code_hash"] = "sha256:scrubbed-code"
            fixture["execution"]["ast_validation_result"] = "passed"
            fixture["execution"]["sandbox_policy_id"] = "sandbox-policy-v1"
            fixture["execution"]["sandbox_execution_result"] = {
                "exit_code": 0,
                "stdout_hash": "sha256:stdout",
                "stderr_hash": "sha256:stderr",
            }
        package_dir = tmp_path / expected_path

        write_proof_package_from_v3_fixture(fixture, package_dir)

        assert verify_proof_package(package_dir)["status"] == "verified"
        context = _trace_context(package_dir)
        assert context["execution_path"] == expected_path
        assert context["execution_mode"] == execution_mode
        assert context["source"] == source


def test_v3_generated_package_determinism_and_no_environment_metadata(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    write_proof_package_from_v3_fixture(_v3_fixture(), first_dir)
    write_proof_package_from_v3_fixture(_v3_fixture(), second_dir)

    first = {path.name: path.read_text(encoding="utf-8") for path in first_dir.iterdir()}
    second = {
        path.name: path.read_text(encoding="utf-8") for path in second_dir.iterdir()
    }
    rendered = json.dumps(
        {
            "package": first,
            "verification": verify_proof_package(first_dir),
        },
        sort_keys=True,
    )

    assert first == second
    assert str(tmp_path) not in rendered
    assert "/home/" not in rendered
    assert "Codex-zov" not in rendered
    assert "Zovark-Kiro" not in rendered
    assert "manifest.json" not in first
    assert "provenance.json" not in first


def test_no_forbidden_imports_or_scope_creep_in_v3_verification_gate():
    imported_modules = _imported_modules(
        Path("tests/test_v3_generated_package_verification.py")
    ) | _imported_modules(Path("zovark/slice001/v3_adapter.py"))
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
    ]

    for token in forbidden:
        assert token not in imported_modules


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return imports
