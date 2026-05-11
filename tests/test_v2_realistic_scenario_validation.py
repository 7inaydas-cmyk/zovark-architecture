"""Realistic static scenario validation for generated Proof Package V2 packages."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    verify_proof_package,
)
from zovark.slice001.v3_adapter import write_proof_package_from_v3_fixture
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


FIXTURE_DIR = Path("tests/fixtures/v3-realistic-scenarios")
REALISTIC_FIXTURE = FIXTURE_DIR / "alertforge-style-ransomware-containment.json"

RAW_LEAK_SENTINELS = [
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
]

UNSAFE_TRACE_KEYS = {
    "args",
    "arguments",
    "body",
    "chain_of_thought",
    "content",
    "hidden_reasoning",
    "input",
    "message",
    "messages",
    "notes",
    "output",
    "params",
    "payload",
    "prompt",
    "query",
    "rationale",
    "reasoning",
    "response",
    "result",
}


def _load_fixture() -> dict[str, Any]:
    return json.loads(REALISTIC_FIXTURE.read_text(encoding="utf-8"))


def _load_json(package_dir: Path, filename: str) -> Any:
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


def _write_v2_package(tmp_path: Path, fixture: dict[str, Any] | None = None) -> Path:
    package_dir = tmp_path / "alertforge-style-v2-package"
    write_proof_package_from_v3_fixture(
        fixture or _load_fixture(),
        package_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    return package_dir


def _write_v1_package(tmp_path: Path, fixture: dict[str, Any] | None = None) -> Path:
    package_dir = tmp_path / "alertforge-style-v1-package"
    write_proof_package_from_v3_fixture(fixture or _load_fixture(), package_dir)
    return package_dir


def _render_package_dir(package_dir: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(package_dir.iterdir())
        if path.is_file()
    )


def _trace_context(package_dir: Path) -> dict[str, Any]:
    tape = _load_json(package_dir, "investigation-tape.json")
    return tape["raw_evidence"][0]["raw_content"]["v3_trace_context"]


def _verified_evidence_refs(package_dir: Path) -> set[str]:
    ledger = _load_json(package_dir, "evidence-ledger.json")
    return {
        f"evidence:{entry['evidence_id']}"
        for entry in ledger
        if isinstance(entry, dict) and entry.get("evidence_id")
    }


def _collect_source_refs(value: Any) -> set[str]:
    if isinstance(value, dict):
        refs = value.get("source_refs", [])
        collected = {ref for ref in refs if isinstance(ref, str)}
        for child in value.values():
            collected.update(_collect_source_refs(child))
        return collected
    if isinstance(value, list):
        collected: set[str] = set()
        for item in value:
            collected.update(_collect_source_refs(item))
        return collected
    return set()


def _assert_no_raw_leaks(package_dir: Path) -> None:
    rendered = _render_package_dir(package_dir)
    for sentinel in RAW_LEAK_SENTINELS:
        assert sentinel not in rendered


def _assert_trace_fields_are_sanitized(context: dict[str, Any]) -> None:
    trace_values = [
        context.get("prompt_transformation_log"),
        context.get("tool_call_chain_summary"),
        context.get("counter_evidence_considered"),
        context.get("exploitability_validation"),
    ]
    for value in trace_values:
        rendered = json.dumps(value, sort_keys=True)
        for key in UNSAFE_TRACE_KEYS:
            assert f'"{key}"' not in rendered


def test_alertforge_style_generated_v2_package_verifies(tmp_path):
    package_dir = _write_v2_package(tmp_path)

    summary = verify_proof_package(package_dir)

    assert sorted(path.name for path in package_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES + (V2_MARKER_FILE,)
    )
    assert summary["status"] == "verified"
    assert summary["replay_state"] == "succeeded"
    assert summary["failure_count"] == 0
    assert summary["failure_codes"] == []
    assert summary["package_contract"] == V2_PACKAGE_CONTRACT
    assert summary["package_version"] == V2_PACKAGE_CONTRACT
    assert summary == verify_proof_package(package_dir)


def test_alertforge_style_v2_populates_practitioner_objects_from_recorded_evidence(
    tmp_path,
):
    package_dir = _write_v2_package(tmp_path)
    marker = _load_json(package_dir, V2_MARKER_FILE)
    objects = marker["objects"]

    assert marker["conditions"] == {
        "analyst_override_present": False,
        "benign_verdict": False,
        "containment_recommended": True,
        "context_enrichment_used": True,
        "customer_impact_language_present": True,
        "rejected_findings_present": False,
        "response_action_present": True,
    }
    assert objects["decision_rationale"]["status"] == "partial"
    assert objects["context_enrichment"]["status"] == "partial"
    assert objects["visibility_gaps"]["status"] == "partial"
    assert objects["approval_record"]["status"] == "partial"
    assert objects["blast_radius"]["status"] == "partial"
    assert objects["rollback_plan"]["status"] == "partial"
    assert objects["compliance_mapping"]["status"] == "partial"
    assert objects["controls_in_place_at_incident"]["status"] == "partial"
    assert objects["customer_report_v2"]["status"] == "partial"
    assert objects["context_enrichment"]["context_values"]["asset_criticality"] == (
        "high"
    )
    assert objects["visibility_gaps"]["gaps"]
    assert objects["controls_in_place_at_incident"]["control_values"][
        "mfa_status"
    ] == "enabled"
    assert objects["customer_report_v2"]["proof_verification_status"]["status"] == (
        "not_verified_at_generation"
    )


def test_alertforge_style_v2_source_refs_resolve_to_verified_evidence(tmp_path):
    package_dir = _write_v2_package(tmp_path)
    marker = _load_json(package_dir, V2_MARKER_FILE)
    verified_refs = _verified_evidence_refs(package_dir)
    source_refs = _collect_source_refs(marker["objects"])

    assert source_refs
    assert source_refs <= verified_refs
    objects_with_refs = [
        name
        for name, obj in marker["objects"].items()
        if isinstance(obj.get("source_refs"), list) and obj["source_refs"]
    ]
    assert objects_with_refs
    assert "decision_rationale" in objects_with_refs
    assert "customer_report_v2" in objects_with_refs


def test_alertforge_style_v2_leak_checks_cover_prompts_tools_payloads_and_reasoning(
    tmp_path,
):
    package_dir = _write_v2_package(tmp_path)
    context = _trace_context(package_dir)

    assert verify_proof_package(package_dir)["status"] == "verified"
    _assert_no_raw_leaks(package_dir)
    _assert_trace_fields_are_sanitized(context)
    assert context["prompt_transformation_log"] == [
        {
            "operation": "redact_prompt_body",
            "output_prompt_hash": "sha256:af-prompt-hash-static",
            "redaction_applied": True,
            "redaction_policy_ref": "prompt-redaction-policy-v1",
            "transformation_id": "af-prompt-transform-001",
        }
    ]
    assert context["tool_call_chain_summary"] == [
        {
            "call_id": "af-tool-call-001",
            "input_hash": "sha256:af-tool-input",
            "output_hash": "sha256:af-tool-output",
            "status": "succeeded",
            "tool_name": "extract_ipv4",
        }
    ]
    assert context["exploitability_validation"] == {
        "input_hash": "sha256:af-exploitability-input",
        "output_hash": "sha256:af-exploitability-output",
        "status": "attempted",
        "tool_name": "score_brute_force",
        "validation_status": "attempted",
    }
    assert context["counter_evidence_considered"] == [
        {
            "confidence": "low",
            "evidence_ref": "af-lm-001",
            "finding_id": "counter-evidence-lateral-movement",
            "reason_code": "blocked_not_successful",
            "status": "considered",
        }
    ]


def test_alertforge_style_generated_v2_package_is_deterministic(tmp_path):
    first_dir = tmp_path / "first-v2"
    second_dir = tmp_path / "second-v2"
    fixture = _load_fixture()

    write_proof_package_from_v3_fixture(
        fixture,
        first_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    write_proof_package_from_v3_fixture(
        deepcopy(fixture),
        second_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )

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
    assert verify_proof_package(first_dir) == verify_proof_package(second_dir)
    assert str(tmp_path) not in rendered
    assert "/home/" not in rendered
    assert "Codex-zov" not in rendered
    assert "Zovark-Kiro" not in rendered


def test_alertforge_style_default_v1_generation_remains_v1_only(tmp_path):
    fixture = _load_fixture()
    package_dir = _write_v1_package(tmp_path, fixture)
    context = _trace_context(package_dir)
    rendered = _render_package_dir(package_dir)

    assert sorted(path.name for path in package_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert verify_proof_package(package_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )
    assert V2_MARKER_FILE not in {path.name for path in package_dir.iterdir()}
    for key in (
        "prompt_transformation_log",
        "tool_call_chain_summary",
        "counter_evidence_considered",
        "exploitability_validation",
        "customer_report_v2",
        "compliance_mapping",
        "controls_in_place_at_incident",
    ):
        assert key not in context
    for sentinel in RAW_LEAK_SENTINELS:
        assert sentinel not in rendered


def test_alertforge_style_v2_has_no_customer_readiness_or_legal_claims(tmp_path):
    package_dir = _write_v2_package(tmp_path)
    rendered = _render_package_dir(package_dir).lower()
    filenames = {path.name for path in package_dir.iterdir()}

    assert "manifest.json" not in filenames
    assert "provenance.json" not in filenames
    assert "slsa" not in rendered
    assert "in-toto" not in rendered
    assert "opentimestamps" not in rendered
    assert "legal admissibility" not in rendered
    assert "compliance achieved" not in rendered
    assert "certification achieved" not in rendered
    assert "customer readiness" not in rendered
    assert "demo package" not in rendered
