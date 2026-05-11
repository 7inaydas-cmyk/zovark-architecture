"""Adapter from representative V3 fixture shapes to Slice proof packages."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.cli import build_completed_tape
from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    _derive_v2_conditions,
)
from zovark.slice001.hashing import sha256_of_obj
from zovark.slice001.writer import build_proof_package, write_proof_package


V1_PACKAGE_CONTRACT = "slice-001-proof-package/1.0"
_EVENT_ARRAY_KEYS = (
    "process_events",
    "network_events",
    "credential_access_events",
    "lateral_movement_events",
)
_EXECUTION_MODES = {"tools", "sandbox", "sandbox_fallback"}
_LLM_SELECTED_SOURCES = {"llm_selected", "llm_tool_call"}
_DETERMINISTIC_SOURCES = {"builtin", "db_saved", "saved_plan", "template"}
_CONTEXT_ENRICHMENT_KEYS = (
    "asset_criticality",
    "asset_owner",
    "crown_jewel_status",
    "threat_intel_hash_match",
    "threat_intel_ip_match",
    "geo_ip_data",
    "recent_ticket_history",
    "user_role",
    "user_job_title",
    "user_department",
    "user_typical_behavior",
    "baseline_match_evidence",
    "context_enrichment",
    "institutional_knowledge",
    "correlation_history",
)
_VISIBILITY_GAP_KEYS = (
    "known_blind_spots",
    "telemetry_missing",
    "access_denied_paths",
    "shadow_it_unknown",
    "third_party_integration_gaps",
    "embedded_ai_in_saas_visibility_gap",
    "unavailable_logs",
    "incomplete_telemetry",
    "unsupported_integrations",
    "unobserved_integrations",
)
_APPROVAL_RECORD_KEYS = (
    "approver_identity",
    "approver_role",
    "approval_channel",
    "approval_status",
    "approval_timestamp",
    "approval_reason",
    "denial_reason",
    "emergency_flag",
    "post_action_validation_required",
    "conditional_approval_constraints",
    "customer_defined_autonomy_boundary",
)
_BLAST_RADIUS_KEYS = (
    "direct_dependencies",
    "third_party_dependencies",
    "single_points_of_failure",
    "business_processes_affected",
    "revenue_streams_affected",
    "rto_target",
    "rpo_target",
    "compliance_obligations",
    "data_leak_assessment",
    "isolation_method",
    "affected_user_count",
)
_ROLLBACK_PLAN_KEYS = (
    "restore_steps",
    "backup_availability",
    "backup_verification_status",
    "authentication_path",
    "rollback_owner",
    "rollforward_steps",
    "validation_after_rollback",
    "estimated_recovery_time",
    "escalation_if_rollback_fails",
)
_CONTROL_EVIDENCE_KEYS = (
    "mfa_status",
    "backup_status",
    "backup_immutability",
    "backup_verification_status",
    "edr_status",
    "logging_status",
    "central_incident_log_status",
    "irp_adherence_evidence",
    "data_inventory_evidence",
    "control_enabled",
    "control_disabled",
)
_CONTROL_METADATA_KEYS = (
    "control_snapshot_timestamp",
    "control_time_scope",
    "control_source",
    "control_owner",
    "control_refs",
    "customer_attestation_ref",
)
_CONTROL_SNAPSHOT_KEYS = _CONTROL_EVIDENCE_KEYS + _CONTROL_METADATA_KEYS
_COMPLIANCE_ACTION_MAPPINGS = {
    "isolate_host": {
        "control_refs": [
            "approval_record",
            "blast_radius",
            "rollback_plan",
        ],
        "framework_name": "Proof Package V2 practitioner requirements",
        "framework_version": V2_PACKAGE_CONTRACT,
        "mapping_limitations": [
            "Mapping connects verified action evidence to V2 practitioner objects only.",
            "Mapping is not a compliance certification or legal conclusion.",
        ],
        "mapping_version": "v2-adapter/0.1",
    }
}


def adapt_v3_fixture_to_slice_input(fixture: dict[str, Any]) -> dict[str, Any]:
    """Map a representative V3 fixture into the existing Slice input shape."""
    return _adapt_v3_fixture_to_slice_input(fixture, include_v2_context=False)


def _adapt_v3_fixture_to_slice_input(
    fixture: dict[str, Any],
    *,
    include_v2_context: bool,
) -> dict[str, Any]:
    _validate_fixture(fixture)
    alert = _alert_from_fixture(fixture)
    execution = _execution_from_fixture(fixture)
    v3_context = _v3_context_from_fixture(
        fixture,
        execution=execution,
        include_v2_context=include_v2_context,
    )

    raw_input: dict[str, Any] = {
        "alert_id": _non_empty_string(alert, "alert_id"),
        "alert_type": _string_value(alert, "alert_type", default="v3_runtime_alert"),
        "description": _string_value(
            alert,
            "description",
            default="Representative V3 investigation fixture",
        ),
        "host": _string_value(alert, "host", default="unknown-host"),
        "ingested_at": _timestamp_from(alert),
        "severity": _string_value(alert, "severity", default="high"),
        "source_alert_ref": _string_value(
            alert,
            "source_alert_ref",
            default=_non_empty_string(alert, "alert_id"),
        ),
        "timestamp": _timestamp_from(alert),
        "v3_trace_context": v3_context,
    }

    for optional_key in ("host_fqdn", "source_process", "child_process"):
        if optional_key in alert:
            raw_input[optional_key] = _non_empty_string(alert, optional_key)

    tenant_id = fixture.get("tenant_id")
    if tenant_id is not None:
        if not isinstance(tenant_id, str) or not tenant_id:
            raise ZovarkValidationError("tenant_id must be a non-empty string")
        raw_input["tenant_id"] = tenant_id

    for key in _EVENT_ARRAY_KEYS:
        raw_input[key] = _event_array(fixture, key)

    return raw_input


def build_tape_from_v3_fixture(
    fixture: dict[str, Any],
    *,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """Build a complete replay-sealed Slice tape from a V3 fixture."""
    return _build_tape_from_v3_fixture(
        fixture,
        tenant_id=tenant_id,
        include_v2_context=False,
    )


def _build_tape_from_v3_fixture(
    fixture: dict[str, Any],
    *,
    tenant_id: str | None,
    include_v2_context: bool,
) -> dict[str, Any]:
    raw_input = _adapt_v3_fixture_to_slice_input(
        fixture,
        include_v2_context=include_v2_context,
    )
    tape = build_completed_tape(raw_input, tenant_id=tenant_id)
    expected_value = _declared_verdict_value(fixture)
    if expected_value is not None:
        actual_value = tape["verdict"]["value"]
        if expected_value != actual_value:
            raise ZovarkValidationError(
                "V3 fixture verdict does not match derived Slice proof verdict"
            )
    return tape


def build_proof_package_from_v3_fixture(
    fixture: dict[str, Any],
    *,
    tenant_id: str | None = None,
    proof_package_version: str = V1_PACKAGE_CONTRACT,
) -> dict[str, Any]:
    """Build a proof package in memory from a V3 fixture."""
    if proof_package_version == V1_PACKAGE_CONTRACT:
        tape = build_tape_from_v3_fixture(fixture, tenant_id=tenant_id)
        return build_proof_package(tape)
    if proof_package_version == V2_PACKAGE_CONTRACT:
        v2_tape = _build_tape_from_v3_fixture(
            fixture,
            tenant_id=tenant_id,
            include_v2_context=True,
        )
        package = build_proof_package(v2_tape)
        package[V2_MARKER_FILE] = build_v2_marker_from_tape(v2_tape)
        return package
    raise ZovarkValidationError("proof_package_version is unsupported")


def write_proof_package_from_v3_fixture(
    fixture: dict[str, Any],
    output_dir: str | Path,
    *,
    tenant_id: str | None = None,
    proof_package_version: str = V1_PACKAGE_CONTRACT,
) -> dict[str, str]:
    """Write a proof package from a V3 fixture."""
    if proof_package_version not in (V1_PACKAGE_CONTRACT, V2_PACKAGE_CONTRACT):
        raise ZovarkValidationError("proof_package_version is unsupported")
    if proof_package_version == V1_PACKAGE_CONTRACT:
        tape = build_tape_from_v3_fixture(fixture, tenant_id=tenant_id)
        return write_proof_package(tape, output_dir)

    v2_tape = _build_tape_from_v3_fixture(
        fixture,
        tenant_id=tenant_id,
        include_v2_context=True,
    )
    written = write_proof_package(v2_tape, output_dir)
    destination = Path(output_dir) / V2_MARKER_FILE
    destination.write_text(
        json.dumps(
            build_v2_marker_from_tape(v2_tape),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    written[V2_MARKER_FILE] = str(destination)
    return written


def build_v2_marker_from_tape(tape: dict[str, Any]) -> dict[str, Any]:
    """Build the minimal V2 marker from an already sealed V1 tape."""
    source_refs = _v2_source_refs(tape)
    conditions = _derive_v2_conditions(tape)
    objects = {
        "approval_record": _approval_record(tape, source_refs),
        "compliance_mapping": _compliance_mapping(tape),
        "controls_in_place_at_incident": _controls_in_place_at_incident(tape),
        "decision_rationale": _decision_rationale(tape, source_refs),
        "visibility_gaps": _visibility_gaps(tape, source_refs),
    }
    if conditions["benign_verdict"] or conditions["rejected_findings_present"] or conditions[
        "analyst_override_present"
    ]:
        objects["false_positive_reasoning"] = _false_positive_reasoning(
            tape,
            source_refs,
        )
    else:
        objects["false_positive_reasoning"] = _not_applicable_object(
            "false_positive_reasoning"
        )
    if conditions["context_enrichment_used"]:
        objects["context_enrichment"] = _context_enrichment(tape, source_refs)
    if (
        conditions["response_action_present"]
        or conditions["containment_recommended"]
        or conditions["customer_impact_language_present"]
    ):
        objects["blast_radius"] = _blast_radius(tape, source_refs)
    if conditions["response_action_present"] or conditions["containment_recommended"]:
        objects["rollback_plan"] = _rollback_plan(tape, source_refs)
    objects["customer_report_v2"] = _customer_report_v2(tape, objects)
    return {
        "base_package_contract": V1_PACKAGE_CONTRACT,
        "conditions": conditions,
        "objects": objects,
        "package_version": V2_PACKAGE_CONTRACT,
    }


def _v2_source_refs(tape: dict[str, Any]) -> list[str]:
    evidence = tape.get("raw_evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ZovarkValidationError("V2 package population requires evidence")
    refs: list[str] = []
    for entry in evidence:
        evidence_id = _non_empty_string(entry, "evidence_id")
        refs.append(f"evidence:{evidence_id}")
    return refs


def _base_v2_object(
    object_type: str,
    *,
    source_refs: list[str],
    status: str = "partial",
    data_unavailable_reason: str | None = None,
    content: dict[str, Any] | None = None,
) -> dict[str, Any]:
    obj = {
        "object_type": object_type,
        "object_version": "v2-adapter/0.1",
        "source_refs": deepcopy(source_refs),
        "status": status,
    }
    if data_unavailable_reason is not None:
        obj["data_unavailable_reason"] = data_unavailable_reason
    if content:
        obj.update(deepcopy(content))
    return obj


def _not_applicable_object(object_type: str) -> dict[str, Any]:
    return _base_v2_object(
        object_type,
        source_refs=[],
        status="not_applicable",
    )


def _unavailable_optional_object(
    object_type: str,
    data_unavailable_reason: str,
) -> dict[str, Any]:
    return _base_v2_object(
        object_type,
        source_refs=[],
        status="unavailable",
        data_unavailable_reason=data_unavailable_reason,
    )


def _minimal_required_placeholder(
    object_type: str,
    source_refs: list[str],
    data_unavailable_reason: str,
) -> dict[str, Any]:
    return _base_v2_object(
        object_type,
        source_refs=source_refs,
        status="unavailable",
        data_unavailable_reason=data_unavailable_reason,
    )


def _decision_rationale(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    context = _primary_v3_context(tape)
    verdict = tape["verdict"]
    handoff = tape["handoff"]
    content = {
        "business_impact_assessment": handoff["blast_radius"].get(
            "estimated_business_impact"
        ),
        "counter_evidence_considered": context.get("counter_evidence_considered"),
        "decision_boundary": (
            "This rationale summarizes recorded package evidence only; replay does "
            "not prove upstream evidence completeness."
        ),
        "decision_rationale_summary": (
            f"Deterministic Slice verdict {verdict['value']} was derived from "
            f"{len(tape['findings'])} finding(s) and mapped to "
            f"{handoff['action_type']} with human approval required."
        ),
        "escalation_justification": _escalation_justification(context, handoff),
        "escalation_path": "human_review",
        "evidence_considered": _evidence_considered(tape),
        "final_decision": verdict["value"],
        "lessons_learned": context.get("lessons_learned"),
        "preventive_recommendations": context.get("preventive_recommendations"),
        "rationale_items": _rationale_items(tape),
        "working_hypothesis": _working_hypothesis(tape),
    }
    return _base_v2_object(
        "decision_rationale",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="not_emitted_by_v3",
        content=content,
    )


def _false_positive_reasoning(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    context = _primary_v3_context(tape)
    content = {
        "auto_close_eligibility": None,
        "baseline_match_evidence": context.get("baseline_match_evidence"),
        "benign_explanation_chosen": context.get("benign_explanation_chosen"),
        "benign_explanations_considered": context.get(
            "benign_explanations_considered",
            [],
        ),
        "benign_indicators": context.get("benign_indicators", []),
        "confirmation_records": context.get("confirmation_records"),
        "contacted_parties": context.get("contacted_parties"),
        "contradicting_evidence_refs": context.get("contradicting_evidence_refs", []),
        "detection_tuning_recommendation": context.get(
            "detection_tuning_recommendation"
        ),
        "enrichment_results": context.get("enrichment_results"),
        "match_telemetry": context.get("match_telemetry"),
        "normal_schedule_match": context.get("normal_schedule_match"),
        "reasoning_summary": (
            f"False-positive reasoning is required because the verified verdict is "
            f"{tape['verdict']['value']}. Current V3 fixture data does not emit "
            "all practitioner false-positive fields."
        ),
        "rejected_finding_refs": context.get("rejected_finding_refs", []),
        "rejected_finding_summaries": context.get("rejected_findings", []),
        "suppression_rule_id": context.get("suppression_rule_id"),
        "whitelist_match_evidence": context.get("whitelist_match_evidence"),
    }
    return _base_v2_object(
        "false_positive_reasoning",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="not_emitted_by_v3",
        content=content,
    )


def _context_enrichment(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    context = _primary_v3_context(tape)
    context_values = _recorded_context_values(context)
    if not context_values:
        return _minimal_required_placeholder(
            "context_enrichment",
            source_refs,
            "recorded_context_summary_not_emitted_by_v3",
        )
    content = {
        "context_hash": sha256_of_obj(context_values),
        "context_source": "recorded_v3_fixture_context",
        "context_type": "v3_context_enrichment",
        "context_values": context_values,
        "evidence_refs": deepcopy(source_refs),
        "trace_record_refs": [],
    }
    return _base_v2_object(
        "context_enrichment",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="some_context_fields_not_emitted_by_v3",
        content=content,
    )


def _visibility_gaps(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    gap_records = _visibility_gap_records(_primary_v3_context(tape))
    if gap_records:
        return _base_v2_object(
            "visibility_gaps",
            source_refs=source_refs,
            status="partial",
            data_unavailable_reason="some_visibility_fields_not_emitted_by_v3",
            content={"gaps": gap_records},
        )
    return _base_v2_object(
        "visibility_gaps",
        source_refs=source_refs,
        status="unavailable",
        data_unavailable_reason="not_emitted_by_v3",
        content={
            "gaps": [
                {
                    "affected_question": "Which upstream V3 trace fields were not emitted?",
                    "gap_id": "vg-v3-trace-fields",
                    "gap_type": "not_emitted_by_v3",
                    "impact_on_confidence": (
                        "Package verification remains deterministic, but V2 "
                        "practitioner context is incomplete."
                    ),
                }
            ]
        },
    )


def _recorded_context_values(context: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(context[key])
        for key in _CONTEXT_ENRICHMENT_KEYS
        if key in context and _has_enrichment_value(context[key])
    }


def _visibility_gap_records(context: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in _VISIBILITY_GAP_KEYS:
        if key not in context or not _has_gap_value(context[key]):
            continue
        value = context[key]
        items = value if isinstance(value, list) else [value]
        for index, item in enumerate(items, start=1):
            records.append(_visibility_gap_record(key, item, index))
    return records


def _visibility_gap_record(key: str, item: Any, index: int) -> dict[str, Any]:
    if isinstance(item, dict):
        record = deepcopy(item)
        record.setdefault("gap_id", f"vg-{key.replace('_', '-')}-{index}")
        record.setdefault("gap_type", key)
        record.setdefault("affected_question", f"Recorded V3 visibility gap: {key}")
        record.setdefault(
            "impact_on_confidence",
            "Recorded V3 fixture identified this visibility limitation.",
        )
        record.setdefault("data_unavailable_reason", "recorded_visibility_gap")
        return record
    return {
        "affected_question": f"Recorded V3 visibility gap: {key}",
        "data_unavailable_reason": "recorded_visibility_gap",
        "detail": deepcopy(item),
        "gap_id": f"vg-{key.replace('_', '-')}-{index}",
        "gap_type": key,
        "impact_on_confidence": (
            "Recorded V3 fixture identified this visibility limitation."
        ),
    }


def _has_enrichment_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value)
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _has_gap_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _has_enrichment_value(value)


def _approval_record(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    handoff = tape["handoff"]
    context = _primary_v3_context(tape)
    governance_decision = context.get("governance_decision", {})
    review_required = governance_decision.get("needs_human_review", True)
    review_reason = governance_decision.get(
        "review_reason",
        "approval_required handoff generated by Slice proof package",
    )
    approval_values = _recorded_values(context, _APPROVAL_RECORD_KEYS)
    content = {
        "approval_state": handoff["approval_mode"],
        "governance_decision": deepcopy(governance_decision),
        "governance_decision_ref": f"handoff:{handoff['handoff_id']}",
        "handoff_ref": handoff["handoff_id"],
        "review_reason": review_reason,
        "review_required": review_required,
    }
    if approval_values:
        content["recorded_approval"] = approval_values
        approver_identity = approval_values.get("approver_identity")
        if isinstance(approver_identity, str) and approver_identity:
            content["approver_ref"] = approver_identity
    else:
        content["approval_limitation"] = (
            "V3 fixture did not emit approver identity, channel, status, or "
            "timestamp evidence."
        )
    return _base_v2_object(
        "approval_record",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="approval_details_not_fully_emitted_by_v3",
        content=content,
    )


def _compliance_mapping(
    tape: dict[str, Any],
) -> dict[str, Any]:
    action_type = tape["handoff"]["action_type"]
    mapping = _COMPLIANCE_ACTION_MAPPINGS.get(action_type)
    if mapping is None:
        return _not_applicable_object("compliance_mapping")
    source_refs = _action_handoff_source_refs(tape)
    if not source_refs:
        return _unavailable_optional_object(
            "compliance_mapping",
            "action_evidence_not_available",
        )
    content = deepcopy(mapping)
    content["action_type"] = action_type
    content["mapped_evidence_refs"] = deepcopy(source_refs)
    return _base_v2_object(
        "compliance_mapping",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="external_framework_mapping_not_supplied",
        content=content,
    )


def _controls_in_place_at_incident(
    tape: dict[str, Any],
) -> dict[str, Any]:
    context = _primary_v3_context(tape)
    actual_control_values = _recorded_control_evidence_values(context)
    if not actual_control_values:
        return _unavailable_optional_object(
            "controls_in_place_at_incident",
            "customer_not_supplied",
        )
    source_refs = _control_evidence_source_refs(tape)
    if not source_refs:
        return _unavailable_optional_object(
            "controls_in_place_at_incident",
            "control_evidence_source_ref_unavailable",
        )
    control_values = {
        **actual_control_values,
        **_recorded_values(context, _CONTROL_METADATA_KEYS),
    }
    content = {
        "control_refs": _control_refs(control_values),
        "control_snapshot_hash": sha256_of_obj(control_values),
        "control_source_ref": source_refs[0],
        "control_time_scope": control_values.get("control_time_scope", "incident_time"),
        "control_values": control_values,
    }
    customer_attestation_ref = control_values.get("customer_attestation_ref")
    if isinstance(customer_attestation_ref, str) and customer_attestation_ref:
        content["customer_attestation_ref"] = customer_attestation_ref
    return _base_v2_object(
        "controls_in_place_at_incident",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="customer_control_snapshot_partially_supplied",
        content=content,
    )


def _control_refs(control_values: dict[str, Any]) -> list[str]:
    refs = control_values.get("control_refs")
    if isinstance(refs, list) and refs:
        return deepcopy(refs)
    return sorted(
        key
        for key in control_values
        if key
        not in {
            "control_refs",
            "control_snapshot_timestamp",
            "control_time_scope",
            "control_source",
            "control_owner",
            "customer_attestation_ref",
        }
    )


def _recorded_control_evidence_values(context: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(context[key])
        for key in _CONTROL_EVIDENCE_KEYS
        if key in context and _has_control_evidence_value(context[key])
    }


def _has_control_evidence_value(value: Any) -> bool:
    if isinstance(value, str) and value in {
        "not_recorded",
        "not_supplied",
        "unknown",
    }:
        return False
    return _has_enrichment_value(value)


def _action_handoff_source_refs(tape: dict[str, Any]) -> list[str]:
    evidence_refs = tape["handoff"].get("evidence_refs", [])
    if not isinstance(evidence_refs, list):
        return []
    return [
        f"evidence:{evidence_ref}"
        for evidence_ref in evidence_refs
        if isinstance(evidence_ref, str) and evidence_ref
    ]


def _control_evidence_source_refs(tape: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    evidence_entries = tape.get("raw_evidence", [])
    if not isinstance(evidence_entries, list):
        return refs
    for entry in evidence_entries:
        if not isinstance(entry, dict):
            continue
        raw_content = entry.get("raw_content", {})
        if not isinstance(raw_content, dict):
            continue
        contexts = [raw_content]
        v3_context = raw_content.get("v3_trace_context")
        if isinstance(v3_context, dict):
            contexts.append(v3_context)
        if any(_recorded_control_evidence_values(context) for context in contexts):
            refs.append(f"evidence:{_non_empty_string(entry, 'evidence_id')}")
    return refs


def _customer_report_v2(
    tape: dict[str, Any],
    objects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_refs = _customer_report_source_refs(tape, objects)
    return _base_v2_object(
        "customer_report_v2",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="verification_not_written_at_generation",
        content={
            "customer_responsibility_actions": _customer_responsibility_actions(
                objects
            ),
            "decision_summary": _customer_decision_summary(tape, objects),
            "evidence_summary": _customer_evidence_summary(tape, objects),
            "executive_summary": (
                "Proof Package V2 customer report generated from recorded V3 "
                "fixture data and deterministic Slice package evidence."
            ),
            "limitations": [
                "V2 reports exported package consistency only.",
                "No signing, external anchoring, compliance status, legal conclusion, or upstream evidence completeness claim is made.",
            ],
            "prevention_recommendations": _customer_prevention_recommendations(
                objects
            ),
            "proof_verification_status": {
                "data_unavailable_reason": "verifier_result_not_recorded_at_generation",
                "replay_state": tape["replay_report"]["replay_state"]["state"],
                "status": "not_verified_at_generation",
                "verification_scope": "run the verifier against the exported package",
            },
            "visibility_gaps": _customer_visibility_gaps(objects),
            "verified_scope": "recorded package artifacts only",
        },
    )


def _customer_report_source_refs(
    tape: dict[str, Any],
    objects: dict[str, dict[str, Any]],
) -> list[str]:
    refs: list[str] = []
    for evidence_ref in tape["verdict"].get("evidence_refs", []):
        if isinstance(evidence_ref, str) and evidence_ref:
            refs.append(f"evidence:{evidence_ref}")
    refs.extend(_action_handoff_source_refs(tape))
    for object_name in (
        "context_enrichment",
        "visibility_gaps",
        "compliance_mapping",
        "controls_in_place_at_incident",
    ):
        obj = objects.get(object_name, {})
        obj_refs = obj.get("source_refs", [])
        if isinstance(obj_refs, list):
            refs.extend(ref for ref in obj_refs if isinstance(ref, str) and ref)
    if not refs:
        refs = _v2_source_refs(tape)
    return sorted(set(refs))


def _customer_decision_summary(
    tape: dict[str, Any],
    objects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    decision_rationale = objects["decision_rationale"]
    approval_record = objects["approval_record"]
    summary = {
        "action_type": tape["handoff"]["action_type"],
        "approval_state": approval_record.get("approval_state"),
        "decision_rationale_summary": decision_rationale.get(
            "decision_rationale_summary"
        ),
        "final_decision": tape["verdict"]["value"],
        "working_hypothesis": decision_rationale.get("working_hypothesis"),
    }
    recorded_approval = approval_record.get("recorded_approval")
    if isinstance(recorded_approval, dict):
        approval_status = recorded_approval.get("approval_status")
        if isinstance(approval_status, str) and approval_status:
            summary["approval_status"] = approval_status
    return summary


def _customer_evidence_summary(
    tape: dict[str, Any],
    objects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    summary = {
        "action_evidence_refs": _action_handoff_source_refs(tape),
        "finding_summaries": [
            {
                "evidence_refs": [
                    f"evidence:{ref}" for ref in finding["evidence_refs"]
                ],
                "severity": finding["severity"],
                "title": finding["title"],
            }
            for finding in tape["findings"]
        ],
        "verdict_evidence_refs": [
            f"evidence:{ref}" for ref in tape["verdict"]["evidence_refs"]
        ],
    }
    context_enrichment = objects.get("context_enrichment")
    if isinstance(context_enrichment, dict) and context_enrichment.get(
        "status"
    ) != "not_applicable":
        summary["context_summary"] = {
            "context_type": context_enrichment.get("context_type"),
            "source_refs": context_enrichment.get("source_refs", []),
            "status": context_enrichment.get("status"),
        }
    compliance_mapping = objects.get("compliance_mapping")
    if isinstance(compliance_mapping, dict) and compliance_mapping.get(
        "status"
    ) == "partial":
        summary["compliance_mapping_summary"] = {
            "action_type": compliance_mapping.get("action_type"),
            "control_refs": compliance_mapping.get("control_refs", []),
            "mapping_only": True,
            "source_refs": compliance_mapping.get("source_refs", []),
            "status": compliance_mapping.get("status"),
        }
    controls = objects.get("controls_in_place_at_incident")
    if isinstance(controls, dict):
        summary["controls_summary"] = {
            "control_refs": controls.get("control_refs", []),
            "data_unavailable_reason": controls.get("data_unavailable_reason"),
            "source_refs": controls.get("source_refs", []),
            "status": controls.get("status"),
        }
    return summary


def _customer_visibility_gaps(
    objects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    visibility_gaps = objects["visibility_gaps"]
    return {
        "data_unavailable_reason": visibility_gaps.get("data_unavailable_reason"),
        "gaps": deepcopy(visibility_gaps.get("gaps", [])),
        "source_refs": deepcopy(visibility_gaps.get("source_refs", [])),
        "status": visibility_gaps.get("status"),
    }


def _customer_responsibility_actions(
    objects: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    approval_record = objects["approval_record"]
    if approval_record.get("review_required") is True:
        actions.append(
            {
                "action": "human_review_required",
                "reason": approval_record.get("review_reason"),
                "source_refs": deepcopy(approval_record.get("source_refs", [])),
            }
        )
    rollback_plan = objects.get("rollback_plan")
    if isinstance(rollback_plan, dict) and rollback_plan.get("verification_steps"):
        actions.append(
            {
                "action": "rollback_validation_needed",
                "reason": "recorded rollback verification steps are present",
                "source_refs": deepcopy(rollback_plan.get("source_refs", [])),
            }
        )
    controls = objects.get("controls_in_place_at_incident")
    control_action = _customer_control_follow_up_action(controls)
    if control_action is not None:
        actions.append(control_action)
    visibility_gaps = objects["visibility_gaps"]
    if visibility_gaps.get("status") != "unavailable" and visibility_gaps.get("gaps"):
        actions.append(
            {
                "action": "visibility_gap_follow_up",
                "reason": "recorded visibility gaps affect investigation confidence",
                "source_refs": deepcopy(visibility_gaps.get("source_refs", [])),
            }
        )
    return actions


def _customer_control_follow_up_action(
    controls: Any,
) -> dict[str, Any] | None:
    if not isinstance(controls, dict):
        return None
    source_refs = controls.get("source_refs", [])
    if not source_refs:
        return None
    control_values = controls.get("control_values")
    if not isinstance(control_values, dict):
        return None
    control_refs = sorted(
        key
        for key, value in control_values.items()
        if key not in _CONTROL_METADATA_KEYS and _control_value_needs_follow_up(value)
    )
    if not control_refs:
        return None
    return {
        "action": "controls_follow_up_required",
        "control_refs": control_refs,
        "reason": "recorded control evidence indicates customer follow-up is needed",
        "source_refs": deepcopy(source_refs),
    }


def _control_value_needs_follow_up(value: Any) -> bool:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        return normalized in {
            "disabled",
            "failed",
            "incomplete",
            "missing",
            "not_available",
            "not_configured",
            "not_enabled",
            "unavailable",
        }
    if isinstance(value, dict):
        return any(_control_value_needs_follow_up(child) for child in value.values())
    if isinstance(value, list):
        return any(_control_value_needs_follow_up(child) for child in value)
    return False


def _customer_prevention_recommendations(
    objects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    recommendations: list[Any] = []
    decision_recommendations = objects["decision_rationale"].get(
        "preventive_recommendations"
    )
    if decision_recommendations:
        recommendations.extend(
            decision_recommendations
            if isinstance(decision_recommendations, list)
            else [decision_recommendations]
        )
    false_positive = objects.get("false_positive_reasoning", {})
    tuning = false_positive.get("detection_tuning_recommendation")
    if tuning:
        recommendations.append(tuning)
    if recommendations:
        return {
            "recommendations": deepcopy(recommendations),
            "source_refs": sorted(
                set(
                    objects["decision_rationale"].get("source_refs", [])
                    + false_positive.get("source_refs", [])
                )
            ),
            "status": "populated",
        }
    return {
        "data_unavailable_reason": "not_emitted_by_v3",
        "recommendations": [],
        "source_refs": [],
        "status": "unavailable",
    }


def _blast_radius(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    handoff_blast_radius = tape["handoff"]["blast_radius"]
    context = _primary_v3_context(tape)
    recorded_blast_radius = _recorded_values(context, _BLAST_RADIUS_KEYS)
    content = {
        "asset_refs": handoff_blast_radius.get("directly_affected", []),
        "confidence": "derived_from_slice_handoff",
        "identity_refs": [],
        "network_refs": handoff_blast_radius.get("lateral_movement_blocked", []),
        "process_refs": [],
        "scope_summary": handoff_blast_radius.get("estimated_business_impact"),
    }
    if recorded_blast_radius:
        content["recorded_blast_radius"] = recorded_blast_radius
    else:
        content["blast_radius_limitation"] = (
            "V3 fixture did not emit dependency, business-process, RTO/RPO, or "
            "data-leak assessment evidence."
        )
    return _base_v2_object(
        "blast_radius",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="not_emitted_by_v3",
        content=content,
    )


def _rollback_plan(
    tape: dict[str, Any],
    source_refs: list[str],
) -> dict[str, Any]:
    rollback = tape["handoff"]["rollback_plan"]
    context = _primary_v3_context(tape)
    recorded_rollback = _recorded_values(context, _ROLLBACK_PLAN_KEYS)
    rollback_steps = recorded_rollback.get("restore_steps", rollback.get("manual_steps", []))
    verification_steps = recorded_rollback.get("validation_after_rollback", [])
    if isinstance(verification_steps, str):
        verification_steps = [verification_steps]
    content = {
        "action_ref": tape["handoff"]["handoff_id"],
        "preconditions": recorded_rollback.get("preconditions", []),
        "risks": [rollback["recovery_notes"]],
        "rollback_steps": rollback_steps,
        "verification_steps": verification_steps,
    }
    if recorded_rollback:
        content["recorded_rollback"] = recorded_rollback
        rollback_owner = recorded_rollback.get("rollback_owner")
        if isinstance(rollback_owner, str) and rollback_owner:
            content["rollback_owner_ref"] = rollback_owner
    else:
        content["rollback_limitation"] = (
            "V3 fixture did not emit backup, restore, owner, or validation evidence."
        )
    return _base_v2_object(
        "rollback_plan",
        source_refs=source_refs,
        status="partial",
        data_unavailable_reason="not_emitted_by_v3",
        content=content,
    )


def _primary_v3_context(tape: dict[str, Any]) -> dict[str, Any]:
    for entry in tape["raw_evidence"]:
        raw_content = entry.get("raw_content", {})
        if not isinstance(raw_content, dict):
            continue
        context = raw_content.get("v3_trace_context")
        if isinstance(context, dict):
            return context
    return {}


def _evidence_considered(tape: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "evidence_id": entry["evidence_id"],
            "evidence_ref": f"evidence:{entry['evidence_id']}",
            "source_type": entry["source_type"],
        }
        for entry in tape["raw_evidence"]
    ]


def _rationale_items(tape: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "evidence_refs": deepcopy(finding["evidence_refs"]),
            "severity": finding["severity"],
            "summary": finding["title"],
        }
        for finding in tape["findings"]
    ]


def _working_hypothesis(tape: dict[str, Any]) -> str:
    raw_content = tape["raw_evidence"][0]["raw_content"]
    description = raw_content.get("description")
    if isinstance(description, str) and description:
        return description
    return "Evaluate the recorded V3 fixture evidence with deterministic Slice rules."


def _escalation_justification(
    context: dict[str, Any],
    handoff: dict[str, Any],
) -> str:
    governance_decision = context.get("governance_decision", {})
    if isinstance(governance_decision, dict):
        review_reason = governance_decision.get("review_reason")
        if isinstance(review_reason, str) and review_reason:
            return review_reason
    return f"{handoff['approval_mode']} required for {handoff['action_type']}"


def _recorded_values(context: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {
        key: deepcopy(context[key])
        for key in keys
        if key in context and _has_enrichment_value(context[key])
    }


def _validate_fixture(fixture: dict[str, Any]) -> None:
    if not isinstance(fixture, dict):
        raise ZovarkValidationError("V3 fixture must be an object")
    _alert_from_fixture(fixture)
    _execution_from_fixture(fixture)


def _alert_from_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    alert = fixture.get("alert", fixture)
    if not isinstance(alert, dict):
        raise ZovarkValidationError("V3 fixture alert must be an object")
    _non_empty_string(alert, "alert_id")
    _timestamp_from(alert)
    return alert


def _execution_from_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    execution = fixture.get("execution", fixture.get("v3_execution", {}))
    if not isinstance(execution, dict):
        raise ZovarkValidationError("V3 fixture execution must be an object")
    execution_mode = _non_empty_string(execution, "execution_mode")
    if execution_mode not in _EXECUTION_MODES:
        raise ZovarkValidationError("V3 fixture execution_mode is unsupported")
    return execution


def _v3_context_from_fixture(
    fixture: dict[str, Any],
    *,
    execution: dict[str, Any],
    include_v2_context: bool = False,
) -> dict[str, Any]:
    preserved = {
        "execution_mode": execution.get("execution_mode"),
        "path_taken": execution.get("path_taken"),
        "source": execution.get("source"),
        "plan_executed": execution.get("plan_executed"),
        "tool_names": execution.get("tool_names"),
        "tool_results": execution.get("tool_results"),
        "prompt_hash": execution.get("prompt_hash"),
        "prompt_version": execution.get("prompt_version"),
        "generated_code_hash": execution.get("generated_code_hash"),
        "scrubbed_code_hash": execution.get("scrubbed_code_hash"),
        "ast_validation_result": execution.get("ast_validation_result"),
        "sandbox_policy_id": execution.get("sandbox_policy_id"),
        "sandbox_execution_result": execution.get("sandbox_execution_result"),
        "governance_decision": execution.get("governance_decision"),
        "findings": fixture.get("findings", execution.get("findings")),
        "verdict": fixture.get("verdict", execution.get("verdict")),
    }
    if include_v2_context:
        preserved.update(
            {
                "analyst_override": execution.get("analyst_override"),
                "rejected_findings": execution.get("rejected_findings"),
                "rejected_finding_refs": execution.get("rejected_finding_refs"),
                "benign_indicators": execution.get("benign_indicators"),
                "contradicting_evidence_refs": execution.get(
                    "contradicting_evidence_refs"
                ),
                "benign_explanations_considered": execution.get(
                    "benign_explanations_considered"
                ),
                "benign_explanation_chosen": execution.get(
                    "benign_explanation_chosen"
                ),
                "contacted_parties": execution.get("contacted_parties"),
                "confirmation_records": execution.get("confirmation_records"),
                "match_telemetry": execution.get("match_telemetry"),
                "enrichment_results": execution.get("enrichment_results"),
                "baseline_match_evidence": execution.get("baseline_match_evidence"),
                "whitelist_match_evidence": execution.get("whitelist_match_evidence"),
                "normal_schedule_match": execution.get("normal_schedule_match"),
                "suppression_rule_id": execution.get("suppression_rule_id"),
                "detection_tuning_recommendation": execution.get(
                    "detection_tuning_recommendation"
                ),
                "asset_criticality": execution.get("asset_criticality"),
                "asset_owner": execution.get("asset_owner"),
                "crown_jewel_status": execution.get("crown_jewel_status"),
                "threat_intel_hash_match": execution.get("threat_intel_hash_match"),
                "threat_intel_ip_match": execution.get("threat_intel_ip_match"),
                "geo_ip_data": execution.get("geo_ip_data"),
                "recent_ticket_history": execution.get("recent_ticket_history"),
                "user_role": execution.get("user_role"),
                "user_job_title": execution.get("user_job_title"),
                "user_department": execution.get("user_department"),
                "user_typical_behavior": execution.get("user_typical_behavior"),
                "context_enrichment": execution.get("context_enrichment"),
                "institutional_knowledge": execution.get("institutional_knowledge"),
                "correlation_history": execution.get("correlation_history"),
                "known_blind_spots": execution.get("known_blind_spots"),
                "telemetry_missing": execution.get("telemetry_missing"),
                "access_denied_paths": execution.get("access_denied_paths"),
                "shadow_it_unknown": execution.get("shadow_it_unknown"),
                "third_party_integration_gaps": execution.get(
                    "third_party_integration_gaps"
                ),
                "embedded_ai_in_saas_visibility_gap": execution.get(
                    "embedded_ai_in_saas_visibility_gap"
                ),
                "unavailable_logs": execution.get("unavailable_logs"),
                "incomplete_telemetry": execution.get("incomplete_telemetry"),
                "unsupported_integrations": execution.get("unsupported_integrations"),
                "unobserved_integrations": execution.get("unobserved_integrations"),
                "approver_identity": execution.get("approver_identity"),
                "approver_role": execution.get("approver_role"),
                "approval_channel": execution.get("approval_channel"),
                "approval_status": execution.get("approval_status"),
                "approval_timestamp": execution.get("approval_timestamp"),
                "approval_reason": execution.get("approval_reason"),
                "denial_reason": execution.get("denial_reason"),
                "emergency_flag": execution.get("emergency_flag"),
                "post_action_validation_required": execution.get(
                    "post_action_validation_required"
                ),
                "conditional_approval_constraints": execution.get(
                    "conditional_approval_constraints"
                ),
                "customer_defined_autonomy_boundary": execution.get(
                    "customer_defined_autonomy_boundary"
                ),
                "direct_dependencies": execution.get("direct_dependencies"),
                "third_party_dependencies": execution.get("third_party_dependencies"),
                "single_points_of_failure": execution.get("single_points_of_failure"),
                "business_processes_affected": execution.get(
                    "business_processes_affected"
                ),
                "revenue_streams_affected": execution.get("revenue_streams_affected"),
                "rto_target": execution.get("rto_target"),
                "rpo_target": execution.get("rpo_target"),
                "compliance_obligations": execution.get("compliance_obligations"),
                "data_leak_assessment": execution.get("data_leak_assessment"),
                "isolation_method": execution.get("isolation_method"),
                "affected_user_count": execution.get("affected_user_count"),
                "restore_steps": execution.get("restore_steps"),
                "backup_availability": execution.get("backup_availability"),
                "backup_verification_status": execution.get(
                    "backup_verification_status"
                ),
                "authentication_path": execution.get("authentication_path"),
                "rollback_owner": execution.get("rollback_owner"),
                "rollforward_steps": execution.get("rollforward_steps"),
                "validation_after_rollback": execution.get(
                    "validation_after_rollback"
                ),
                "estimated_recovery_time": execution.get("estimated_recovery_time"),
                "escalation_if_rollback_fails": execution.get(
                    "escalation_if_rollback_fails"
                ),
                "mfa_status": execution.get("mfa_status"),
                "backup_status": execution.get("backup_status"),
                "backup_immutability": execution.get("backup_immutability"),
                "edr_status": execution.get("edr_status"),
                "logging_status": execution.get("logging_status"),
                "central_incident_log_status": execution.get(
                    "central_incident_log_status"
                ),
                "irp_adherence_evidence": execution.get("irp_adherence_evidence"),
                "data_inventory_evidence": execution.get("data_inventory_evidence"),
                "control_snapshot_timestamp": execution.get(
                    "control_snapshot_timestamp"
                ),
                "control_time_scope": execution.get("control_time_scope"),
                "control_source": execution.get("control_source"),
                "control_owner": execution.get("control_owner"),
                "control_refs": execution.get("control_refs"),
                "customer_attestation_ref": execution.get("customer_attestation_ref"),
            }
        )
        context_values = _recorded_context_values(
            {key: value for key, value in preserved.items() if value is not None}
        )
        if context_values and not _has_enrichment_value(
            preserved.get("context_enrichment")
        ):
            preserved["context_enrichment"] = {
                "recorded_fields": sorted(context_values),
                "source": "recorded_v3_fixture_context",
            }
    context = {
        key: deepcopy(value)
        for key, value in preserved.items()
        if value is not None
    }
    context["execution_path"] = _execution_path(execution)
    return context


def _execution_path(execution: dict[str, Any]) -> str:
    execution_mode = _non_empty_string(execution, "execution_mode")
    source = execution.get("source")
    if source is not None and (not isinstance(source, str) or not source):
        raise ZovarkValidationError("V3 fixture source must be a non-empty string")

    if execution_mode == "sandbox_fallback":
        return "sandbox_fallback"
    if execution_mode == "sandbox":
        return "explicit_sandbox"
    if source in _LLM_SELECTED_SOURCES:
        return "llm_selected_tools"
    if source in _DETERMINISTIC_SOURCES or source is None:
        return "deterministic_tools"
    raise ZovarkValidationError("V3 fixture source is unsupported")


def _event_array(fixture: dict[str, Any], key: str) -> list[dict[str, Any]]:
    if key in fixture:
        events = fixture[key]
    else:
        events = fixture.get("alert", {}).get(key, [])
    if not isinstance(events, list):
        raise ZovarkValidationError(f"{key} must be a list")
    copied = deepcopy(events)
    for index, event in enumerate(copied):
        if not isinstance(event, dict):
            raise ZovarkValidationError(f"{key}[{index}] must be an object")
    return copied


def _verdict_value(verdict: Any) -> str:
    if isinstance(verdict, str) and verdict:
        return verdict
    if isinstance(verdict, dict):
        return _non_empty_string(verdict, "value")
    raise ZovarkValidationError("V3 fixture verdict is invalid")


def _declared_verdict_value(fixture: dict[str, Any]) -> str | None:
    declared_values = []
    if "verdict" in fixture:
        declared_values.append(_verdict_value(fixture["verdict"]))

    execution = _execution_from_fixture(fixture)
    if "verdict" in execution:
        declared_values.append(_verdict_value(execution["verdict"]))

    if not declared_values:
        return None
    if len(set(declared_values)) != 1:
        raise ZovarkValidationError("V3 fixture declares conflicting verdicts")
    return declared_values[0]


def _timestamp_from(alert: dict[str, Any]) -> str:
    for key in ("ingested_at", "observed_at", "event_time", "timestamp", "created_at"):
        value = alert.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            raise ZovarkValidationError(f"{key} must be a non-empty string")
        return value
    raise ZovarkValidationError("V3 fixture alert is missing a deterministic timestamp")


def _string_value(source: dict[str, Any], key: str, *, default: str) -> str:
    if key not in source:
        return default
    return _non_empty_string(source, key)


def _non_empty_string(source: dict[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise ZovarkValidationError(f"{key} must be a non-empty string")
    return value
