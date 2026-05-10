"""Tests for the Slice 002 offline proof-package verifier."""

from __future__ import annotations

import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.cli import main
from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    load_proof_package,
    validate_loaded_proof_package,
    verify_proof_package,
)
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES, JSON_OUTPUT_FILES


DEMO_PACKAGE_DIR = Path("demo/zovark-proof-package/out/tape-001")
SAMPLE_PATH = Path("samples/edr-sample-001.json")
FORBIDDEN_IMPORTS = (
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
    "cli.py",
    "__main__",
    "manifest.json",
    "provenance.json",
)
EXPECTED_VERIFIED_COMPONENTS = [
    "file_set",
    "json_parse",
    "extracted_views",
    "handoff",
    "audit_entry",
    "replay_report",
    "customer_report",
]
EXPECTED_V2_VERIFIED_COMPONENTS = EXPECTED_VERIFIED_COMPONENTS + [
    "package_version",
    "v2_required_objects",
    "v2_object_shapes",
]


def _copy_demo_package(tmp_path: Path) -> Path:
    package_dir = tmp_path / "package"
    shutil.copytree(DEMO_PACKAGE_DIR, package_dir)
    return package_dir


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_json(package_dir: Path, filename: str):
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _store_json(package_dir: Path, filename: str, obj) -> None:
    _write_json(package_dir / filename, obj)


def _load_tape(package_dir: Path) -> dict:
    return _load_json(package_dir, "investigation-tape.json")


def _store_tape(package_dir: Path, tape: dict) -> None:
    _store_json(package_dir, "investigation-tape.json", tape)


def _v2_object(
    object_type: str,
    *,
    status: str = "populated",
    source_refs: list[str] | None = None,
    data_unavailable_reason: str | None = None,
) -> dict:
    obj = {
        "object_type": object_type,
        "object_version": "v2-skeleton/0.1",
        "source_refs": source_refs or ["evidence:ev-alert"],
        "status": status,
    }
    if data_unavailable_reason is not None:
        obj["data_unavailable_reason"] = data_unavailable_reason
    return obj


def _v2_marker() -> dict:
    return {
        "base_package_contract": "slice-001-proof-package/1.0",
        "conditions": {
            "analyst_override_present": False,
            "benign_verdict": False,
            "containment_recommended": False,
            "context_enrichment_used": False,
            "customer_impact_language_present": False,
            "rejected_findings_present": False,
            "response_action_present": False,
        },
        "objects": {
            "approval_record": _v2_object("approval_record"),
            "blast_radius": _v2_object("blast_radius", status="not_applicable", source_refs=[]),
            "compliance_mapping": _v2_object(
                "compliance_mapping",
                status="not_applicable",
                source_refs=[],
            ),
            "context_enrichment": _v2_object("context_enrichment"),
            "controls_in_place_at_incident": _v2_object(
                "controls_in_place_at_incident",
                status="unavailable",
                source_refs=[],
                data_unavailable_reason="customer_not_supplied",
            ),
            "customer_report_v2": _v2_object("customer_report_v2"),
            "decision_rationale": _v2_object("decision_rationale"),
            "false_positive_reasoning": _v2_object(
                "false_positive_reasoning",
                status="not_applicable",
                source_refs=[],
            ),
            "rollback_plan": _v2_object(
                "rollback_plan",
                status="not_applicable",
                source_refs=[],
            ),
            "visibility_gaps": _v2_object(
                "visibility_gaps",
                status="unavailable",
                source_refs=[],
                data_unavailable_reason="not_emitted_by_v3",
            ),
        },
        "package_version": V2_PACKAGE_CONTRACT,
    }


def _add_v2_marker(package_dir: Path, marker: dict | None = None) -> None:
    _store_json(package_dir, V2_MARKER_FILE, marker or _v2_marker())


def _sync_tape_view(package_dir: Path, field: str, filename: str, value) -> None:
    tape = _load_tape(package_dir)
    tape[field] = deepcopy(value)
    _store_tape(package_dir, tape)
    _store_json(package_dir, filename, value)


def _assert_failure_code(callback, expected_code: str) -> None:
    with pytest.raises(ZovarkValidationError) as exc:
        callback()
    assert str(exc.value).startswith(f"{expected_code}:")


def test_committed_demo_package_verifies_successfully():
    summary = verify_proof_package(DEMO_PACKAGE_DIR)

    assert summary == {
        "artifact_count": 9,
        "audit_entry_id": "audit-entry-1",
        "checks_passed": len(EXPECTED_VERIFIED_COMPONENTS),
        "customer_report_verified": True,
        "evidence_entries_checked": 5,
        "failure_codes": [],
        "failure_count": 0,
        "handoff_id": summary["handoff_id"],
        "package_contract": "slice-001-proof-package/1.0",
        "replay_id": "replay-001",
        "replay_state": "succeeded",
        "status": "verified",
        "tape_id": "tape-001",
        "verdict": "confirmed_malicious",
        "verified_components": EXPECTED_VERIFIED_COMPONENTS,
    }
    assert summary["handoff_id"].startswith("handoff-")


def test_cli_generated_temporary_package_verifies_successfully(tmp_path):
    package_dir = tmp_path / "out"

    assert main(
        [
            "--input",
            str(SAMPLE_PATH),
            "--output",
            str(package_dir),
            "--tenant-id",
            "tenant-verify",
        ]
    ) == 0

    summary = verify_proof_package(package_dir)
    assert summary["status"] == "verified"
    assert summary["artifact_count"] == len(EXPECTED_OUTPUT_FILES)
    assert summary["checks_passed"] == len(EXPECTED_VERIFIED_COMPONENTS)
    assert summary["failure_count"] == 0
    assert summary["failure_codes"] == []
    assert summary["replay_state"] == "succeeded"
    assert summary["verified_components"] == EXPECTED_VERIFIED_COMPONENTS


def test_v1_package_remains_backward_compatible_without_v2_marker(tmp_path):
    package_dir = _copy_demo_package(tmp_path)

    summary = verify_proof_package(package_dir)

    assert summary["package_contract"] == "slice-001-proof-package/1.0"
    assert "package_version" not in summary
    assert V2_MARKER_FILE not in {path.name for path in package_dir.iterdir()}


def test_minimal_static_v2_package_verifies_successfully(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    _add_v2_marker(package_dir)

    summary = verify_proof_package(package_dir)

    assert summary["status"] == "verified"
    assert summary["base_package_contract"] == "slice-001-proof-package/1.0"
    assert summary["package_contract"] == V2_PACKAGE_CONTRACT
    assert summary["package_version"] == V2_PACKAGE_CONTRACT
    assert summary["artifact_count"] == len(EXPECTED_OUTPUT_FILES)
    assert summary["checks_passed"] == len(EXPECTED_V2_VERIFIED_COMPONENTS)
    assert summary["failure_count"] == 0
    assert summary["failure_codes"] == []
    assert summary["v2_object_count"] == len(_v2_marker()["objects"])
    assert summary["v2_objects_checked"] == sorted(_v2_marker()["objects"])
    assert summary["verified_components"] == EXPECTED_V2_VERIFIED_COMPONENTS
    assert summary == verify_proof_package(package_dir)


def test_v2_package_missing_required_object_fails_with_stable_code(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    marker = _v2_marker()
    del marker["objects"]["decision_rationale"]
    _add_v2_marker(package_dir, marker)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "v2_required_object_missing",
    )


def test_v2_package_missing_conditions_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    marker = _v2_marker()
    del marker["conditions"]
    _add_v2_marker(package_dir, marker)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "v2_package_shape_invalid",
    )


def test_v2_package_missing_conditional_object_fails_with_stable_code(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    marker = _v2_marker()
    marker["conditions"]["rejected_findings_present"] = True
    del marker["objects"]["false_positive_reasoning"]
    _add_v2_marker(package_dir, marker)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "v2_conditional_object_missing",
    )


def test_v2_package_malformed_object_fails_with_stable_code(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    marker = _v2_marker()
    marker["objects"]["decision_rationale"]["status"] = "not-a-status"
    _add_v2_marker(package_dir, marker)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "v2_object_shape_invalid",
    )


def test_v2_unavailable_object_requires_reason(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    marker = _v2_marker()
    marker["objects"]["visibility_gaps"].pop("data_unavailable_reason")
    _add_v2_marker(package_dir, marker)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "v2_unavailable_reason_missing",
    )


def test_repeated_verification_is_deterministic_and_path_free(tmp_path):
    package_dir = _copy_demo_package(tmp_path)

    first = verify_proof_package(package_dir)
    second = verify_proof_package(package_dir)
    rendered = json.dumps(first, sort_keys=True)

    assert first == second
    assert str(tmp_path) not in rendered
    assert "/home/" not in rendered
    assert "Zovark-Kiro" not in rendered
    assert "Codex-zov" not in rendered


@pytest.mark.parametrize("filename", EXPECTED_OUTPUT_FILES)
def test_missing_required_file_fails_closed(tmp_path, filename):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / filename).unlink()

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "package_file_set_mismatch",
    )


def test_extra_file_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "extra.json").write_text("{}", encoding="utf-8")

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "package_file_set_mismatch",
    )


def test_extra_directory_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "extra-dir").mkdir()

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "package_file_set_mismatch",
    )


def test_missing_package_maps_to_stable_failure_code(tmp_path):
    _assert_failure_code(
        lambda: verify_proof_package(tmp_path / "missing-package"),
        "package_not_found",
    )


def test_non_directory_package_maps_to_stable_failure_code(tmp_path):
    package_path = tmp_path / "not-a-directory"
    package_path.write_text("not a package", encoding="utf-8")

    _assert_failure_code(
        lambda: verify_proof_package(package_path),
        "package_not_directory",
    )


def test_artifact_path_that_is_not_file_maps_to_stable_failure_code(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "verdict.json").unlink()
    (package_dir / "verdict.json").mkdir()

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "artifact_not_file",
    )


def test_malformed_json_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "verdict.json").write_text("{not-json", encoding="utf-8")

    _assert_failure_code(lambda: verify_proof_package(package_dir), "malformed_json")


def test_empty_customer_report_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "customer-report.md").write_text("", encoding="utf-8")

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "empty_customer_report",
    )


def test_customer_report_mismatch_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    (package_dir / "customer-report.md").write_text("tampered\n", encoding="utf-8")

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "customer_report_mismatch",
    )


@pytest.mark.parametrize(
    ("filename", "field"),
    [
        ("evidence-ledger.json", "raw_evidence"),
        ("timeline.json", "timeline"),
        ("findings.json", "findings"),
        ("verdict.json", "verdict"),
    ],
)
def test_extracted_views_must_match_tape_fields(tmp_path, filename, field):
    package_dir = _copy_demo_package(tmp_path)
    artifact = _load_json(package_dir, filename)
    if isinstance(artifact, list):
        artifact = deepcopy(artifact)
        artifact.append({"tampered": True})
    else:
        artifact = deepcopy(artifact)
        artifact["tampered"] = True
    _store_json(package_dir, filename, artifact)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "extracted_view_mismatch",
    )

    tape = _load_tape(package_dir)
    assert tape[field] != artifact


def test_tampered_verdict_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    verdict = _load_json(package_dir, "verdict.json")
    verdict["value"] = "benign"
    _sync_tape_view(package_dir, "verdict", "verdict.json", verdict)

    with pytest.raises(ZovarkValidationError):
        verify_proof_package(package_dir)


def test_tampered_handoff_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    handoff = _load_json(package_dir, "edr-handoff.json")
    handoff["execution_result"]["status"] = "succeeded"
    _store_json(package_dir, "edr-handoff.json", handoff)

    _assert_failure_code(lambda: verify_proof_package(package_dir), "handoff_mismatch")


def test_tampered_handoff_link_fails_with_stable_code(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    tape = _load_tape(package_dir)
    tape["handoff_ref"] = "handoff-not-present"
    _store_tape(package_dir, tape)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "handoff_link_mismatch",
    )


def test_tampered_audit_entry_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    audit_entry = _load_json(package_dir, "audit-chain-entry.json")
    audit_entry["payload"]["verdict_value"] = "benign"
    _store_json(package_dir, "audit-chain-entry.json", audit_entry)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "audit_chain_mismatch",
    )


def test_tampered_replay_report_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    replay_report = _load_json(package_dir, "replay-report.json")
    replay_report["replay_state"]["state"] = "failed"
    _store_json(package_dir, "replay-report.json", replay_report)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "replay_report_mismatch",
    )


def test_tampered_investigation_tape_state_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    tape = _load_tape(package_dir)
    tape["state"] = "recording"
    _store_tape(package_dir, tape)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "tape_state_invalid",
    )


def test_evidence_raw_content_change_without_hash_update_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    evidence = _load_json(package_dir, "evidence-ledger.json")
    evidence[0]["raw_content"]["host"] = "tampered-host"
    _sync_tape_view(package_dir, "raw_evidence", "evidence-ledger.json", evidence)

    with pytest.raises(ZovarkValidationError):
        verify_proof_package(package_dir)


def test_unknown_timeline_evidence_ref_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    timeline = _load_json(package_dir, "timeline.json")
    timeline[0]["evidence_refs"] = ["ev-not-present"]
    _sync_tape_view(package_dir, "timeline", "timeline.json", timeline)

    with pytest.raises(ZovarkValidationError):
        verify_proof_package(package_dir)


def test_unknown_finding_evidence_ref_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    findings = _load_json(package_dir, "findings.json")
    findings[0]["evidence_refs"] = ["ev-not-present"]
    _sync_tape_view(package_dir, "findings", "findings.json", findings)

    with pytest.raises(ZovarkValidationError):
        verify_proof_package(package_dir)


def test_non_genesis_first_audit_entry_fails_closed(tmp_path):
    package_dir = _copy_demo_package(tmp_path)
    audit_entry = _load_json(package_dir, "audit-chain-entry.json")
    audit_entry["prev_entry_hash"] = "not-genesis"
    _store_json(package_dir, "audit-chain-entry.json", audit_entry)

    _assert_failure_code(
        lambda: verify_proof_package(package_dir),
        "audit_genesis_mismatch",
    )


def test_load_and_validate_loaded_package_match_verify(tmp_path):
    package_dir = _copy_demo_package(tmp_path)

    loaded = load_proof_package(package_dir)

    assert validate_loaded_proof_package(loaded) == verify_proof_package(package_dir)
    assert set(loaded) == set(EXPECTED_OUTPUT_FILES)
    for filename in JSON_OUTPUT_FILES:
        assert loaded[filename]


def test_loaded_package_with_extra_key_is_rejected(tmp_path):
    package = load_proof_package(_copy_demo_package(tmp_path))
    package["manifest.json"] = {}

    _assert_failure_code(
        lambda: validate_loaded_proof_package(package),
        "package_shape_invalid",
    )


def test_loaded_package_with_malformed_artifact_shape_is_rejected(tmp_path):
    package = load_proof_package(_copy_demo_package(tmp_path))
    package["verdict.json"] = "not a JSON artifact"

    _assert_failure_code(
        lambda: validate_loaded_proof_package(package),
        "package_shape_invalid",
    )


def test_no_forbidden_imports_or_scope_creep_in_package_verifier():
    source = Path("zovark/slice001/package_verifier.py").read_text(encoding="utf-8")

    for token in FORBIDDEN_IMPORTS:
        assert token not in source
    assert len(EXPECTED_OUTPUT_FILES) == 9
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
