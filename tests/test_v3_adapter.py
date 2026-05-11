"""Tests for the V3 fixture to Slice proof-package adapter."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    verify_proof_package,
)
from zovark.slice001.v3_adapter import (
    adapt_v3_fixture_to_slice_input,
    build_proof_package_from_v3_fixture,
    build_tape_from_v3_fixture,
    build_v2_marker_from_tape,
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


def _false_positive_context_v3_fixture() -> dict:
    fixture = _representative_v3_fixture()
    fixture["execution"]["rejected_findings"] = ["candidate-benign-office-macro"]
    fixture["execution"]["benign_explanations_considered"] = [
        "expected document macro execution",
    ]
    fixture["execution"]["benign_indicators"] = [
        "known user opened business document",
    ]
    fixture["execution"]["contradicting_evidence_refs"] = []
    return fixture


def _false_positive_tuning_v3_fixture() -> dict:
    fixture = _false_positive_context_v3_fixture()
    fixture["execution"]["detection_tuning_recommendation"] = (
        "Require approved macro allowlist evidence before auto-closing similar alerts"
    )
    return fixture


def _context_visibility_v3_fixture() -> dict:
    fixture = _representative_v3_fixture()
    fixture["execution"].update(
        {
            "access_denied_paths": ["saas-admin-audit-log"],
            "asset_criticality": "high",
            "asset_owner": "finance-it",
            "context_enrichment": {
                "source": "recorded_fixture",
                "summary": "Finance workstation with prior phishing ticket history",
            },
            "correlation_history": [
                {
                    "correlation_count": 1,
                    "matched_indicator": "203.0.113.50",
                }
            ],
            "crown_jewel_status": True,
            "embedded_ai_in_saas_visibility_gap": (
                "No SaaS AI usage telemetry was present in the fixture"
            ),
            "geo_ip_data": {
                "country_code": "ZZ",
                "source": "static_fixture",
            },
            "institutional_knowledge": {
                "asset_tier": "tier-1",
                "business_unit": "finance",
            },
            "known_blind_spots": [
                {
                    "affected_question": "Were DNS resolver logs available?",
                    "gap_id": "vg-dns-logs",
                    "gap_type": "missing_dns_logs",
                    "impact_on_confidence": (
                        "Domain-level command-and-control evidence could not be "
                        "corroborated from this fixture."
                    ),
                    "data_unavailable_reason": "fixture_does_not_include_dns_logs",
                }
            ],
            "recent_ticket_history": [
                {
                    "ticket_id": "INC-1001",
                    "summary": "Prior phishing triage on same host",
                }
            ],
            "shadow_it_unknown": True,
            "telemetry_missing": ["dns_resolver_logs"],
            "threat_intel_ip_match": {
                "indicator": "203.0.113.50",
                "list": "static-fixture-ti",
            },
            "user_department": "finance",
            "user_job_title": "senior analyst",
            "user_role": "finance analyst",
            "user_typical_behavior": {
                "powershell_usage": "rare",
            },
        }
    )
    return fixture


def _context_values_without_existing_gate_fixture() -> dict:
    fixture = _representative_v3_fixture()
    fixture["execution"]["tool_names"] = ["extract_ipv4", "score_brute_force"]
    fixture["execution"]["tool_results"] = {
        "extract_ipv4": {
            "iocs": ["203.0.113.50"],
            "status": "succeeded",
        }
    }
    fixture["execution"].update(
        {
            "asset_criticality": "high",
            "geo_ip_data": {
                "country_code": "ZZ",
                "source": "static_fixture",
            },
            "threat_intel_ip_match": {
                "indicator": "203.0.113.50",
                "list": "static-fixture-ti",
            },
        }
    )
    return fixture


def _action_card_v3_fixture() -> dict:
    fixture = _context_visibility_v3_fixture()
    fixture["execution"].update(
        {
            "affected_user_count": 42,
            "approval_channel": "recorded_ticket",
            "approval_reason": "containment recommended for confirmed malicious host",
            "approval_status": "conditional",
            "approval_timestamp": "2026-05-01T10:05:00Z",
            "approver_identity": "soc-lead-001",
            "approver_role": "SOC lead",
            "backup_availability": "not_recorded",
            "backup_verification_status": "not_recorded",
            "business_processes_affected": ["finance reporting"],
            "conditional_approval_constraints": [
                "Validate business owner notification before isolation"
            ],
            "customer_defined_autonomy_boundary": "approval_required",
            "data_leak_assessment": "not_recorded_in_fixture",
            "direct_dependencies": ["finance-workstation-access"],
            "emergency_flag": False,
            "estimated_recovery_time": "PT2H",
            "escalation_if_rollback_fails": "escalate_to_soc_manager",
            "isolation_method": "edr_isolate_host",
            "post_action_validation_required": True,
            "restore_steps": ["release host isolation after human approval"],
            "rollback_owner": "soc-lead-001",
            "rollforward_steps": ["continue containment if C2 persists"],
            "rpo_target": "not_recorded",
            "rto_target": "PT4H",
            "single_points_of_failure": ["workstation-42 user access"],
            "third_party_dependencies": ["EDR containment control"],
            "validation_after_rollback": [
                "confirm endpoint network connectivity",
                "rerun malware triage checks",
            ],
        }
    )
    return fixture


def _action_card_missing_people_v3_fixture() -> dict:
    fixture = _action_card_v3_fixture()
    for key in (
        "approval_channel",
        "approval_status",
        "approval_timestamp",
        "approver_identity",
        "approver_role",
        "rollback_owner",
    ):
        fixture["execution"].pop(key, None)
    return fixture


def _compliance_controls_v3_fixture() -> dict:
    fixture = _action_card_v3_fixture()
    fixture["execution"].update(
        {
            "backup_immutability": "enabled",
            "backup_status": "available",
            "central_incident_log_status": "enabled",
            "control_owner": "customer-security",
            "control_refs": [
                "mfa_status",
                "backup_status",
                "edr_status",
                "central_incident_log_status",
            ],
            "control_snapshot_timestamp": "2026-05-01T09:55:00Z",
            "control_source": "customer_supplied_fixture",
            "control_time_scope": "incident_time",
            "customer_attestation_ref": "customer-attestation-001",
            "data_inventory_evidence": "not_supplied",
            "edr_status": "enabled",
            "irp_adherence_evidence": "incident_record_opened",
            "logging_status": "centralized",
            "mfa_status": "enabled",
        }
    )
    return fixture


def _compliance_controls_with_unrelated_evidence_fixture() -> dict:
    fixture = _compliance_controls_v3_fixture()
    fixture["process_events"].append(
        {
            "command_line": "notepad.exe",
            "event_id": "v3-pe-unrelated",
            "event_type": "process_event",
            "parent_pid": 100,
            "parent_process": "explorer.exe",
            "pid": 5000,
            "process_name": "notepad.exe",
            "timestamp": "2026-05-01T10:00:01Z",
            "user": "CORP\\analyst",
        }
    )
    return fixture


def _control_metadata_only_v3_fixture() -> dict:
    fixture = _action_card_v3_fixture()
    fixture["execution"].update(
        {
            "control_owner": "customer-security",
            "control_refs": ["metadata-only-control-ref"],
            "control_snapshot_timestamp": "2026-05-01T09:55:00Z",
            "control_source": "customer_supplied_fixture",
            "control_time_scope": "incident_time",
            "customer_attestation_ref": "customer-attestation-001",
        }
    )
    return fixture


def _control_evidence_without_metadata_v3_fixture() -> dict:
    fixture = _action_card_v3_fixture()
    fixture["execution"].update(
        {
            "backup_status": "available",
            "mfa_status": "enabled",
        }
    )
    return fixture


def _disabled_control_v3_fixture() -> dict:
    fixture = _action_card_v3_fixture()
    fixture["execution"].update(
        {
            "backup_status": "available",
            "mfa_status": "disabled",
        }
    )
    return fixture


def _load_json(package_dir: Path, filename: str):
    return json.loads((package_dir / filename).read_text(encoding="utf-8"))


V2_ONLY_CONTEXT_KEYS = {
    "analyst_override",
    "access_denied_paths",
    "affected_user_count",
    "approval_channel",
    "approval_reason",
    "approval_status",
    "approval_timestamp",
    "approver_identity",
    "approver_role",
    "asset_criticality",
    "asset_owner",
    "authentication_path",
    "backup_availability",
    "backup_verification_status",
    "baseline_match_evidence",
    "benign_explanation_chosen",
    "benign_explanations_considered",
    "benign_indicators",
    "business_processes_affected",
    "confirmation_records",
    "backup_immutability",
    "central_incident_log_status",
    "contacted_parties",
    "context_enrichment",
    "correlation_history",
    "contradicting_evidence_refs",
    "conditional_approval_constraints",
    "crown_jewel_status",
    "customer_defined_autonomy_boundary",
    "customer_attestation_ref",
    "data_leak_assessment",
    "data_inventory_evidence",
    "decision_rationale",
    "denial_reason",
    "detection_tuning_recommendation",
    "direct_dependencies",
    "embedded_ai_in_saas_visibility_gap",
    "emergency_flag",
    "enrichment_results",
    "edr_status",
    "escalation_if_rollback_fails",
    "estimated_recovery_time",
    "false_positive_reasoning",
    "geo_ip_data",
    "incomplete_telemetry",
    "institutional_knowledge",
    "isolation_method",
    "known_blind_spots",
    "logging_status",
    "match_telemetry",
    "mfa_status",
    "normal_schedule_match",
    "post_action_validation_required",
    "recent_ticket_history",
    "rejected_finding_refs",
    "rejected_findings",
    "restore_steps",
    "revenue_streams_affected",
    "rollback_owner",
    "rollforward_steps",
    "rpo_target",
    "rto_target",
    "control_owner",
    "control_refs",
    "control_snapshot_timestamp",
    "control_source",
    "control_time_scope",
    "source_refs",
    "single_points_of_failure",
    "suppression_rule_id",
    "telemetry_missing",
    "third_party_integration_gaps",
    "third_party_dependencies",
    "threat_intel_hash_match",
    "threat_intel_ip_match",
    "unavailable_logs",
    "unobserved_integrations",
    "unsupported_integrations",
    "user_department",
    "user_job_title",
    "user_role",
    "user_typical_behavior",
    "validation_after_rollback",
    "v2_conditions",
    "visibility_gaps",
    "whitelist_match_evidence",
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


def test_v3_fixture_default_package_remains_v1(tmp_path):
    output_dir = tmp_path / "v1-package"

    manifest = write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
    )

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert sorted(manifest) == sorted(EXPECTED_OUTPUT_FILES)
    assert V2_MARKER_FILE not in manifest
    summary = verify_proof_package(output_dir)
    assert summary["package_contract"] == "slice-001-proof-package/1.0"
    assert "package_version" not in summary


def test_v3_fixture_default_v1_context_excludes_v2_only_fields(tmp_path):
    output_dir = tmp_path / "v1-package"

    write_proof_package_from_v3_fixture(
        _false_positive_context_v3_fixture(),
        output_dir,
    )
    context = _load_json(output_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert not (set(context) & V2_ONLY_CONTEXT_KEYS)


def test_v3_fixture_can_write_v2_package_that_verifies(tmp_path):
    output_dir = tmp_path / "v2-package"

    manifest = write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES + (V2_MARKER_FILE,)
    )
    assert sorted(manifest) == sorted(EXPECTED_OUTPUT_FILES + (V2_MARKER_FILE,))
    assert summary["status"] == "verified"
    assert summary["package_contract"] == V2_PACKAGE_CONTRACT
    assert summary["package_version"] == V2_PACKAGE_CONTRACT
    assert summary["failure_count"] == 0


def test_v1_then_v2_generation_does_not_mutate_v1_projection(tmp_path):
    fixture = _false_positive_context_v3_fixture()
    v1_dir = tmp_path / "v1-first"
    v2_dir = tmp_path / "v2-second"

    write_proof_package_from_v3_fixture(fixture, v1_dir)
    v1_before = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    v1_after = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }

    assert v1_before == v1_after
    assert sorted(v1_after) == sorted(EXPECTED_OUTPUT_FILES)
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_v2_then_v1_generation_does_not_contaminate_v1_projection(tmp_path):
    fixture = _false_positive_context_v3_fixture()
    v2_dir = tmp_path / "v2-first"
    v1_dir = tmp_path / "v1-second"

    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    write_proof_package_from_v3_fixture(fixture, v1_dir)
    context = _load_json(v1_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert sorted(path.name for path in v1_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert not (set(context) & V2_ONLY_CONTEXT_KEYS)
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_generated_v2_decision_rationale_refs_resolve_to_evidence(tmp_path):
    output_dir = tmp_path / "v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    decision_rationale = marker["objects"]["decision_rationale"]

    assert decision_rationale["source_refs"]
    assert set(decision_rationale["source_refs"]) <= verified_refs
    assert decision_rationale["working_hypothesis"]
    assert decision_rationale["final_decision"] == "confirmed_malicious"
    assert decision_rationale["decision_rationale_summary"]


def test_generated_v2_rejected_finding_emits_false_positive_reasoning(tmp_path):
    output_dir = tmp_path / "false-positive-v2-package"

    write_proof_package_from_v3_fixture(
        _false_positive_context_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    false_positive = marker["objects"]["false_positive_reasoning"]

    assert summary["status"] == "verified"
    assert marker["conditions"]["rejected_findings_present"] is True
    assert false_positive["status"] == "partial"
    assert false_positive["source_refs"]
    assert false_positive["rejected_finding_refs"] == []
    assert false_positive["rejected_finding_summaries"] == [
        "candidate-benign-office-macro"
    ]
    assert false_positive["reasoning_summary"]


def test_generated_v2_populates_context_enrichment_from_fixture_evidence(tmp_path):
    output_dir = tmp_path / "context-v2-package"

    write_proof_package_from_v3_fixture(
        _context_visibility_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    context_enrichment = marker["objects"]["context_enrichment"]

    assert summary["status"] == "verified"
    assert marker["conditions"]["context_enrichment_used"] is True
    assert context_enrichment["status"] == "partial"
    assert context_enrichment["source_refs"]
    assert set(context_enrichment["source_refs"]) <= verified_refs
    assert context_enrichment["evidence_refs"] == context_enrichment["source_refs"]
    assert context_enrichment["context_type"] == "v3_context_enrichment"
    assert context_enrichment["context_hash"]
    assert context_enrichment["context_values"]["asset_criticality"] == "high"
    assert context_enrichment["context_values"]["asset_owner"] == "finance-it"
    assert context_enrichment["context_values"]["threat_intel_ip_match"] == {
        "indicator": "203.0.113.50",
        "list": "static-fixture-ti",
    }
    assert context_enrichment["data_unavailable_reason"] == (
        "some_context_fields_not_emitted_by_v3"
    )


def test_generated_v2_context_enrichment_gate_uses_recorded_context_values(tmp_path):
    output_dir = tmp_path / "context-values-v2-package"

    write_proof_package_from_v3_fixture(
        _context_values_without_existing_gate_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    context_enrichment = marker["objects"]["context_enrichment"]

    assert summary["status"] == "verified"
    assert marker["conditions"]["context_enrichment_used"] is True
    assert context_enrichment["source_refs"]
    assert set(context_enrichment["source_refs"]) <= verified_refs
    assert context_enrichment["context_values"]["asset_criticality"] == "high"
    assert context_enrichment["context_values"]["geo_ip_data"] == {
        "country_code": "ZZ",
        "source": "static_fixture",
    }
    assert context_enrichment["context_values"]["threat_intel_ip_match"] == {
        "indicator": "203.0.113.50",
        "list": "static-fixture-ti",
    }


def test_generated_v2_populates_visibility_gaps_from_fixture_evidence(tmp_path):
    output_dir = tmp_path / "visibility-v2-package"

    write_proof_package_from_v3_fixture(
        _context_visibility_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    visibility_gaps = marker["objects"]["visibility_gaps"]

    assert summary["status"] == "verified"
    assert visibility_gaps["status"] == "partial"
    assert visibility_gaps["source_refs"]
    assert set(visibility_gaps["source_refs"]) <= verified_refs
    assert visibility_gaps["data_unavailable_reason"] == (
        "some_visibility_fields_not_emitted_by_v3"
    )
    assert {
        "missing_dns_logs",
        "telemetry_missing",
        "access_denied_paths",
        "shadow_it_unknown",
        "embedded_ai_in_saas_visibility_gap",
    } <= {gap["gap_type"] for gap in visibility_gaps["gaps"]}
    assert any(gap.get("detail") == "dns_resolver_logs" for gap in visibility_gaps["gaps"])


def test_generated_v2_missing_context_and_gap_data_is_explicit(tmp_path):
    output_dir = tmp_path / "minimal-v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)

    assert summary["status"] == "verified"
    context_enrichment = marker["objects"]["context_enrichment"]
    visibility_gaps = marker["objects"]["visibility_gaps"]
    assert context_enrichment["status"] == "unavailable"
    assert context_enrichment["data_unavailable_reason"] == (
        "recorded_context_summary_not_emitted_by_v3"
    )
    assert context_enrichment["source_refs"]
    assert visibility_gaps["status"] == "unavailable"
    assert visibility_gaps["data_unavailable_reason"] == "not_emitted_by_v3"
    assert visibility_gaps["source_refs"]


def test_default_v1_generation_excludes_context_and_visibility_fields(tmp_path):
    output_dir = tmp_path / "v1-context-package"

    write_proof_package_from_v3_fixture(
        _context_visibility_v3_fixture(),
        output_dir,
    )
    context = _load_json(output_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert not (set(context) & V2_ONLY_CONTEXT_KEYS)
    assert verify_proof_package(output_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_context_visibility_v1_and_v2_generation_do_not_cross_contaminate(tmp_path):
    fixture = _context_visibility_v3_fixture()
    v2_dir = tmp_path / "v2-first"
    v1_dir = tmp_path / "v1-second"

    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    write_proof_package_from_v3_fixture(fixture, v1_dir)
    v2_marker = _load_json(v2_dir, V2_MARKER_FILE)
    v1_context = _load_json(v1_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert "context_enrichment" in v2_marker["objects"]
    assert "visibility_gaps" in v2_marker["objects"]
    assert sorted(path.name for path in v1_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert not (set(v1_context) & V2_ONLY_CONTEXT_KEYS)
    assert verify_proof_package(v2_dir)["package_contract"] == V2_PACKAGE_CONTRACT
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_generated_v2_populates_approval_record_from_fixture_evidence(tmp_path):
    output_dir = tmp_path / "action-card-v2-package"

    write_proof_package_from_v3_fixture(
        _action_card_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    approval_record = marker["objects"]["approval_record"]

    assert summary["status"] == "verified"
    assert approval_record["source_refs"]
    assert set(approval_record["source_refs"]) <= verified_refs
    assert approval_record["status"] == "partial"
    assert approval_record["approval_state"] == "approval_required"
    assert approval_record["approver_ref"] == "soc-lead-001"
    assert approval_record["recorded_approval"]["approval_status"] == "conditional"
    assert approval_record["recorded_approval"]["approver_identity"] == "soc-lead-001"
    assert approval_record["recorded_approval"]["approval_channel"] == "recorded_ticket"


def test_generated_v2_populates_blast_radius_from_fixture_evidence(tmp_path):
    output_dir = tmp_path / "blast-radius-v2-package"

    write_proof_package_from_v3_fixture(
        _action_card_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    blast_radius = marker["objects"]["blast_radius"]

    assert summary["status"] == "verified"
    assert marker["conditions"]["response_action_present"] is True
    assert blast_radius["source_refs"]
    assert set(blast_radius["source_refs"]) <= verified_refs
    assert blast_radius["status"] == "partial"
    assert blast_radius["recorded_blast_radius"]["direct_dependencies"] == [
        "finance-workstation-access"
    ]
    assert blast_radius["recorded_blast_radius"]["isolation_method"] == (
        "edr_isolate_host"
    )
    assert blast_radius["recorded_blast_radius"]["affected_user_count"] == 42


def test_generated_v2_populates_rollback_plan_from_fixture_evidence(tmp_path):
    output_dir = tmp_path / "rollback-v2-package"

    write_proof_package_from_v3_fixture(
        _action_card_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    rollback_plan = marker["objects"]["rollback_plan"]

    assert summary["status"] == "verified"
    assert rollback_plan["source_refs"]
    assert set(rollback_plan["source_refs"]) <= verified_refs
    assert rollback_plan["status"] == "partial"
    assert rollback_plan["rollback_owner_ref"] == "soc-lead-001"
    assert rollback_plan["rollback_steps"] == [
        "release host isolation after human approval"
    ]
    assert rollback_plan["verification_steps"] == [
        "confirm endpoint network connectivity",
        "rerun malware triage checks",
    ]
    assert rollback_plan["recorded_rollback"]["backup_availability"] == "not_recorded"


def test_generated_v2_missing_approver_does_not_emit_synthetic_ref(tmp_path):
    output_dir = tmp_path / "missing-approver-v2-package"

    write_proof_package_from_v3_fixture(
        _action_card_missing_people_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    approval_record = marker["objects"]["approval_record"]

    assert summary["status"] == "verified"
    assert "approver_ref" not in approval_record
    assert "approver_identity" not in approval_record
    assert "approval_channel" not in approval_record
    assert "approval_status" not in approval_record
    assert "approval_timestamp" not in approval_record
    assert "recorded_approval" in approval_record
    assert "approval_reason" in approval_record["recorded_approval"]
    assert approval_record["source_refs"]
    assert set(approval_record["source_refs"]) <= verified_refs


def test_generated_v2_missing_rollback_owner_does_not_emit_synthetic_ref(tmp_path):
    output_dir = tmp_path / "missing-rollback-owner-v2-package"

    write_proof_package_from_v3_fixture(
        _action_card_missing_people_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    rollback_plan = marker["objects"]["rollback_plan"]

    assert summary["status"] == "verified"
    assert "rollback_owner_ref" not in rollback_plan
    assert "rollback_owner" not in rollback_plan
    assert "recorded_rollback" in rollback_plan
    assert "restore_steps" in rollback_plan["recorded_rollback"]
    assert rollback_plan["source_refs"]
    assert set(rollback_plan["source_refs"]) <= verified_refs


def test_generated_v2_missing_action_card_details_are_explicit(tmp_path):
    output_dir = tmp_path / "minimal-action-v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)

    assert summary["status"] == "verified"
    approval_record = marker["objects"]["approval_record"]
    blast_radius = marker["objects"]["blast_radius"]
    rollback_plan = marker["objects"]["rollback_plan"]
    assert approval_record["data_unavailable_reason"] == (
        "approval_details_not_fully_emitted_by_v3"
    )
    assert "approver_ref" not in approval_record
    assert approval_record["approval_limitation"]
    assert blast_radius["data_unavailable_reason"] == "not_emitted_by_v3"
    assert blast_radius["blast_radius_limitation"]
    assert rollback_plan["data_unavailable_reason"] == "not_emitted_by_v3"
    assert "rollback_owner_ref" not in rollback_plan
    assert rollback_plan["rollback_limitation"]


def test_default_v1_generation_excludes_action_card_fields(tmp_path):
    output_dir = tmp_path / "v1-action-card-package"

    write_proof_package_from_v3_fixture(
        _action_card_v3_fixture(),
        output_dir,
    )
    context = _load_json(output_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert not (set(context) & V2_ONLY_CONTEXT_KEYS)
    assert verify_proof_package(output_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_action_card_v1_and_v2_generation_do_not_cross_contaminate(tmp_path):
    fixture = _action_card_v3_fixture()
    v1_dir = tmp_path / "v1-first"
    v2_dir = tmp_path / "v2-second"

    write_proof_package_from_v3_fixture(fixture, v1_dir)
    v1_before = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    v1_after = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    v2_marker = _load_json(v2_dir, V2_MARKER_FILE)

    assert v1_before == v1_after
    assert "approval_record" in v2_marker["objects"]
    assert "blast_radius" in v2_marker["objects"]
    assert "rollback_plan" in v2_marker["objects"]
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )
    assert verify_proof_package(v2_dir)["package_contract"] == V2_PACKAGE_CONTRACT


def test_generated_v2_populates_compliance_mapping_from_verified_action(tmp_path):
    output_dir = tmp_path / "compliance-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    handoff = _load_json(output_dir, "edr-handoff.json")
    handoff_refs = {f"evidence:{ref}" for ref in handoff["evidence_refs"]}
    compliance_mapping = marker["objects"]["compliance_mapping"]

    assert summary["status"] == "verified"
    assert compliance_mapping["status"] == "partial"
    assert compliance_mapping["source_refs"]
    assert set(compliance_mapping["source_refs"]) <= verified_refs
    assert set(compliance_mapping["source_refs"]) == handoff_refs
    assert compliance_mapping["mapped_evidence_refs"] == compliance_mapping["source_refs"]
    assert compliance_mapping["action_type"] == "isolate_host"
    assert compliance_mapping["framework_name"] == (
        "Proof Package V2 practitioner requirements"
    )
    assert compliance_mapping["control_refs"] == [
        "approval_record",
        "blast_radius",
        "rollback_plan",
    ]


def test_generated_v2_compliance_mapping_excludes_unrelated_raw_evidence(tmp_path):
    output_dir = tmp_path / "compliance-unrelated-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_with_unrelated_evidence_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    handoff = _load_json(output_dir, "edr-handoff.json")
    unrelated_refs = {
        f"evidence:{entry['evidence_id']}"
        for entry in evidence
        if entry["raw_content"].get("event_id") == "v3-pe-unrelated"
    }
    handoff_refs = {f"evidence:{ref}" for ref in handoff["evidence_refs"]}
    compliance_mapping = marker["objects"]["compliance_mapping"]

    assert summary["status"] == "verified"
    assert unrelated_refs
    assert set(compliance_mapping["source_refs"]) == handoff_refs
    assert not (set(compliance_mapping["source_refs"]) & unrelated_refs)
    assert not (set(compliance_mapping["mapped_evidence_refs"]) & unrelated_refs)


def test_v2_unsupported_action_gets_no_compliance_mapping():
    tape = deepcopy(build_tape_from_v3_fixture(_representative_v3_fixture()))
    tape["handoff"]["action_type"] = "notify_only"

    marker = build_v2_marker_from_tape(tape)
    compliance_mapping = marker["objects"]["compliance_mapping"]

    assert marker["conditions"]["response_action_present"] is False
    assert compliance_mapping["status"] == "not_applicable"
    assert compliance_mapping["source_refs"] == []
    assert "control_refs" not in compliance_mapping


def test_v2_supported_action_without_handoff_refs_gets_no_fabricated_mapping():
    tape = deepcopy(build_tape_from_v3_fixture(_compliance_controls_v3_fixture()))
    tape["handoff"]["evidence_refs"] = []

    marker = build_v2_marker_from_tape(tape)
    compliance_mapping = marker["objects"]["compliance_mapping"]

    assert compliance_mapping["status"] == "unavailable"
    assert compliance_mapping["data_unavailable_reason"] == (
        "action_evidence_not_available"
    )
    assert compliance_mapping["source_refs"] == []
    assert "mapped_evidence_refs" not in compliance_mapping


def test_generated_v2_populates_controls_from_customer_snapshot(tmp_path):
    output_dir = tmp_path / "controls-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    control_evidence_refs = {
        f"evidence:{entry['evidence_id']}"
        for entry in evidence
        if entry["raw_content"]
        .get("v3_trace_context", {})
        .get("mfa_status")
        == "enabled"
    }
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert summary["status"] == "verified"
    assert controls["status"] == "partial"
    assert controls["source_refs"]
    assert set(controls["source_refs"]) <= verified_refs
    assert set(controls["source_refs"]) == control_evidence_refs
    assert controls["control_source_ref"] in controls["source_refs"]
    assert controls["control_time_scope"] == "incident_time"
    assert controls["customer_attestation_ref"] == "customer-attestation-001"
    assert controls["control_values"]["mfa_status"] == "enabled"
    assert controls["control_values"]["backup_status"] == "available"
    assert controls["control_values"]["edr_status"] == "enabled"
    assert controls["control_snapshot_hash"]


def test_generated_v2_controls_refs_exclude_unrelated_telemetry(tmp_path):
    output_dir = tmp_path / "controls-unrelated-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_with_unrelated_evidence_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    unrelated_refs = {
        f"evidence:{entry['evidence_id']}"
        for entry in evidence
        if entry["raw_content"].get("event_id") == "v3-pe-unrelated"
    }
    control_evidence_refs = {
        f"evidence:{entry['evidence_id']}"
        for entry in evidence
        if entry["raw_content"]
        .get("v3_trace_context", {})
        .get("backup_status")
        == "available"
    }
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert summary["status"] == "verified"
    assert unrelated_refs
    assert controls["source_refs"]
    assert set(controls["source_refs"]) == control_evidence_refs
    assert not (set(controls["source_refs"]) & unrelated_refs)


def test_v2_controls_without_control_evidence_uses_no_fabricated_ref():
    tape = deepcopy(build_tape_from_v3_fixture(_compliance_controls_v3_fixture()))
    tape["raw_evidence"] = [
        entry
        for entry in tape["raw_evidence"]
        if "v3_trace_context" not in entry.get("raw_content", {})
    ]

    marker = build_v2_marker_from_tape(tape)
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert controls["status"] == "unavailable"
    assert controls["data_unavailable_reason"] == "customer_not_supplied"
    assert controls["source_refs"] == []
    assert "control_values" not in controls


def test_generated_v2_control_metadata_only_is_unavailable(tmp_path):
    output_dir = tmp_path / "metadata-only-controls-v2-package"

    write_proof_package_from_v3_fixture(
        _control_metadata_only_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert summary["status"] == "verified"
    assert controls["status"] == "unavailable"
    assert controls["data_unavailable_reason"] == "customer_not_supplied"
    assert controls["source_refs"] == []
    assert "control_values" not in controls
    rendered = json.dumps(controls, sort_keys=True)
    assert "mfa_status" not in rendered
    assert "backup_status" not in rendered
    assert "edr_status" not in rendered
    assert "logging_status" not in rendered


def test_generated_v2_control_evidence_without_metadata_is_preserved(tmp_path):
    output_dir = tmp_path / "controls-no-metadata-v2-package"

    write_proof_package_from_v3_fixture(
        _control_evidence_without_metadata_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert summary["status"] == "verified"
    assert controls["status"] == "partial"
    assert controls["control_values"] == {
        "backup_status": "available",
        "mfa_status": "enabled",
    }
    assert controls["control_refs"] == ["backup_status", "mfa_status"]
    assert controls["control_time_scope"] == "incident_time"
    assert "control_snapshot_timestamp" not in controls["control_values"]


def test_generated_v2_missing_control_snapshot_is_explicit(tmp_path):
    output_dir = tmp_path / "missing-controls-v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    controls = marker["objects"]["controls_in_place_at_incident"]

    assert summary["status"] == "verified"
    assert controls["status"] == "unavailable"
    assert controls["data_unavailable_reason"] == "customer_not_supplied"
    assert controls["source_refs"] == []
    assert "control_values" not in controls


def test_default_v1_generation_excludes_compliance_and_control_fields(tmp_path):
    output_dir = tmp_path / "v1-compliance-controls-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
    )
    context = _load_json(output_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert sorted(path.name for path in output_dir.iterdir()) == sorted(
        EXPECTED_OUTPUT_FILES
    )
    assert not (set(context) & V2_ONLY_CONTEXT_KEYS)
    assert verify_proof_package(output_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_compliance_controls_v1_and_v2_generation_do_not_cross_contaminate(tmp_path):
    fixture = _compliance_controls_v3_fixture()
    v1_dir = tmp_path / "v1-first"
    v2_dir = tmp_path / "v2-second"

    write_proof_package_from_v3_fixture(fixture, v1_dir)
    v1_before = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    v1_after = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    v2_marker = _load_json(v2_dir, V2_MARKER_FILE)

    assert v1_before == v1_after
    assert v2_marker["objects"]["compliance_mapping"]["status"] == "partial"
    assert v2_marker["objects"]["controls_in_place_at_incident"]["status"] == (
        "partial"
    )
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )
    assert verify_proof_package(v2_dir)["package_contract"] == V2_PACKAGE_CONTRACT


def test_generated_v2_populates_customer_report_v2(tmp_path):
    output_dir = tmp_path / "customer-report-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    customer_report = marker["objects"]["customer_report_v2"]

    assert summary["status"] == "verified"
    assert customer_report["status"] == "partial"
    assert customer_report["source_refs"]
    assert customer_report["executive_summary"]
    assert customer_report["verified_scope"] == "recorded package artifacts only"
    assert customer_report["decision_summary"]
    assert customer_report["evidence_summary"]
    assert customer_report["visibility_gaps"]
    assert customer_report["customer_responsibility_actions"]
    assert customer_report["prevention_recommendations"]
    assert customer_report["proof_verification_status"]


def test_generated_v2_customer_report_decision_summary_uses_v2_objects(tmp_path):
    output_dir = tmp_path / "customer-report-decision-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    customer_report = marker["objects"]["customer_report_v2"]
    decision_rationale = marker["objects"]["decision_rationale"]
    approval_record = marker["objects"]["approval_record"]
    decision_summary = customer_report["decision_summary"]

    assert decision_summary["final_decision"] == "confirmed_malicious"
    assert decision_summary["decision_rationale_summary"] == decision_rationale[
        "decision_rationale_summary"
    ]
    assert decision_summary["working_hypothesis"] == decision_rationale[
        "working_hypothesis"
    ]
    assert decision_summary["action_type"] == "isolate_host"
    assert decision_summary["approval_state"] == approval_record["approval_state"]
    assert decision_summary["approval_status"] == "conditional"


def test_generated_v2_customer_report_evidence_summary_refs_resolve(tmp_path):
    output_dir = tmp_path / "customer-report-evidence-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    evidence = _load_json(output_dir, "evidence-ledger.json")
    verified_refs = {f"evidence:{entry['evidence_id']}" for entry in evidence}
    customer_report = marker["objects"]["customer_report_v2"]
    evidence_summary = customer_report["evidence_summary"]

    assert set(customer_report["source_refs"]) <= verified_refs
    assert set(evidence_summary["verdict_evidence_refs"]) <= verified_refs
    assert set(evidence_summary["action_evidence_refs"]) <= verified_refs
    assert evidence_summary["finding_summaries"]
    assert evidence_summary["compliance_mapping_summary"]["source_refs"] == marker[
        "objects"
    ]["compliance_mapping"]["source_refs"]
    assert evidence_summary["controls_summary"]["source_refs"] == marker["objects"][
        "controls_in_place_at_incident"
    ]["source_refs"]


def test_generated_v2_customer_report_includes_visibility_gaps(tmp_path):
    output_dir = tmp_path / "customer-report-gaps-v2-package"

    write_proof_package_from_v3_fixture(
        _context_visibility_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    customer_gaps = marker["objects"]["customer_report_v2"]["visibility_gaps"]

    assert customer_gaps["status"] == "partial"
    assert customer_gaps["gaps"]
    assert {
        "missing_dns_logs",
        "telemetry_missing",
        "access_denied_paths",
    } <= {gap["gap_type"] for gap in customer_gaps["gaps"]}


def test_generated_v2_customer_report_actions_are_supported_by_v2_objects(tmp_path):
    output_dir = tmp_path / "customer-report-actions-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    actions = marker["objects"]["customer_report_v2"][
        "customer_responsibility_actions"
    ]
    action_names = {action["action"] for action in actions}

    assert action_names == {
        "human_review_required",
        "rollback_validation_needed",
        "visibility_gap_follow_up",
    }
    for action in actions:
        assert "source_refs" in action
        assert "reason" in action


def test_generated_v2_customer_report_does_not_invent_visibility_gap_action(
    tmp_path,
):
    output_dir = tmp_path / "customer-report-no-recorded-gaps-v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    report = marker["objects"]["customer_report_v2"]
    action_names = {
        action["action"] for action in report["customer_responsibility_actions"]
    }

    assert report["visibility_gaps"]["status"] == "unavailable"
    assert "visibility_gap_follow_up" not in action_names
    assert "controls_evidence_unavailable" not in action_names
    assert "controls_follow_up_required" not in action_names


def test_generated_v2_customer_report_does_not_invent_controls_action_for_metadata(
    tmp_path,
):
    output_dir = tmp_path / "customer-report-metadata-only-controls-v2-package"

    write_proof_package_from_v3_fixture(
        _control_metadata_only_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    report = marker["objects"]["customer_report_v2"]
    action_names = {
        action["action"] for action in report["customer_responsibility_actions"]
    }

    assert marker["objects"]["controls_in_place_at_incident"]["status"] == (
        "unavailable"
    )
    assert "controls_evidence_unavailable" not in action_names
    assert "controls_follow_up_required" not in action_names


def test_generated_v2_customer_report_flags_recorded_disabled_control(tmp_path):
    output_dir = tmp_path / "customer-report-disabled-control-v2-package"

    write_proof_package_from_v3_fixture(
        _disabled_control_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    controls = marker["objects"]["controls_in_place_at_incident"]
    actions = marker["objects"]["customer_report_v2"][
        "customer_responsibility_actions"
    ]
    controls_actions = [
        action for action in actions if action["action"] == "controls_follow_up_required"
    ]

    assert summary["status"] == "verified"
    assert controls["status"] == "partial"
    assert controls["control_values"]["mfa_status"] == "disabled"
    assert len(controls_actions) == 1
    assert controls_actions[0]["control_refs"] == ["mfa_status"]
    assert controls_actions[0]["source_refs"] == controls["source_refs"]


def test_generated_v2_customer_report_prevention_uses_recorded_recommendations(
    tmp_path,
):
    output_dir = tmp_path / "customer-report-prevention-v2-package"

    write_proof_package_from_v3_fixture(
        _false_positive_tuning_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    summary = verify_proof_package(output_dir)
    marker = _load_json(output_dir, V2_MARKER_FILE)
    prevention = marker["objects"]["customer_report_v2"][
        "prevention_recommendations"
    ]

    assert summary["status"] == "verified"
    assert prevention["status"] == "populated"
    assert prevention["recommendations"] == [
        "Require approved macro allowlist evidence before auto-closing similar alerts"
    ]
    assert prevention["source_refs"]


def test_generated_v2_customer_report_missing_prevention_is_explicit(tmp_path):
    output_dir = tmp_path / "customer-report-no-prevention-v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    prevention = marker["objects"]["customer_report_v2"][
        "prevention_recommendations"
    ]

    assert prevention == {
        "data_unavailable_reason": "not_emitted_by_v3",
        "recommendations": [],
        "source_refs": [],
        "status": "unavailable",
    }


def test_generated_v2_customer_report_does_not_self_attest_verification(tmp_path):
    output_dir = tmp_path / "customer-report-verification-status-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    proof_status = marker["objects"]["customer_report_v2"][
        "proof_verification_status"
    ]

    assert proof_status["status"] == "not_verified_at_generation"
    assert proof_status["replay_state"] == "succeeded"
    assert proof_status["data_unavailable_reason"] == (
        "verifier_result_not_recorded_at_generation"
    )
    assert proof_status["status"] != "verified"


def test_default_v1_generation_excludes_customer_report_v2(tmp_path):
    output_dir = tmp_path / "v1-customer-report-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
    )
    context = _load_json(output_dir, "investigation-tape.json")["raw_evidence"][0][
        "raw_content"
    ]["v3_trace_context"]

    assert V2_MARKER_FILE not in {path.name for path in output_dir.iterdir()}
    assert "customer_report_v2" not in context
    assert verify_proof_package(output_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )


def test_customer_report_v1_and_v2_generation_do_not_cross_contaminate(tmp_path):
    fixture = _compliance_controls_v3_fixture()
    v1_dir = tmp_path / "v1-first"
    v2_dir = tmp_path / "v2-second"

    write_proof_package_from_v3_fixture(fixture, v1_dir)
    v1_before = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    write_proof_package_from_v3_fixture(
        fixture,
        v2_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    v1_after = {
        path.name: path.read_text(encoding="utf-8") for path in v1_dir.iterdir()
    }
    v2_marker = _load_json(v2_dir, V2_MARKER_FILE)

    assert v1_before == v1_after
    assert "customer_report_v2" in v2_marker["objects"]
    assert verify_proof_package(v1_dir)["package_contract"] == (
        "slice-001-proof-package/1.0"
    )
    assert verify_proof_package(v2_dir)["package_contract"] == V2_PACKAGE_CONTRACT


def test_generated_v2_customer_report_does_not_claim_legal_or_certification(
    tmp_path,
):
    output_dir = tmp_path / "customer-report-bounded-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    rendered = json.dumps(
        marker["objects"]["customer_report_v2"],
        sort_keys=True,
    ).lower()

    forbidden_claims = [
        "compliance achieved",
        "certified",
        "certification",
        "legal admissibility",
        "soc 2 compliant",
        "sec ready",
    ]
    for claim in forbidden_claims:
        assert claim not in rendered


def test_generated_v2_compliance_mapping_does_not_claim_certification(tmp_path):
    output_dir = tmp_path / "bounded-compliance-v2-package"

    write_proof_package_from_v3_fixture(
        _compliance_controls_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    marker = _load_json(output_dir, V2_MARKER_FILE)
    rendered = json.dumps(
        marker["objects"]["compliance_mapping"],
        sort_keys=True,
    ).lower()

    forbidden_claims = [
        "compliance achieved",
        "certified",
        "legal admissible",
        "soc 2 compliant",
        "sec ready",
    ]
    for claim in forbidden_claims:
        assert claim not in rendered


def test_generated_v2_marker_does_not_export_hidden_reasoning_or_raw_prompts(tmp_path):
    output_dir = tmp_path / "v2-package"

    write_proof_package_from_v3_fixture(
        _representative_v3_fixture(),
        output_dir,
        proof_package_version=V2_PACKAGE_CONTRACT,
    )
    rendered = json.dumps(_load_json(output_dir, V2_MARKER_FILE), sort_keys=True).lower()

    forbidden = [
        "chain_of_thought",
        "hidden_reasoning",
        "raw_reasoning",
        "raw_system_prompt",
        "system_prompt",
        "raw_prompt",
    ]
    for token in forbidden:
        assert token not in rendered


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
