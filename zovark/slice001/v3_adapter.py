"""Adapter from representative V3 fixture shapes to Slice proof packages."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.cli import build_completed_tape
from zovark.slice001.writer import build_proof_package, write_proof_package


_EVENT_ARRAY_KEYS = (
    "process_events",
    "network_events",
    "credential_access_events",
    "lateral_movement_events",
)
_EXECUTION_MODES = {"tools", "sandbox", "sandbox_fallback"}
_LLM_SELECTED_SOURCES = {"llm_selected", "llm_tool_call"}
_DETERMINISTIC_SOURCES = {"builtin", "db_saved", "saved_plan", "template"}


def adapt_v3_fixture_to_slice_input(fixture: dict[str, Any]) -> dict[str, Any]:
    """Map a representative V3 fixture into the existing Slice input shape."""
    _validate_fixture(fixture)
    alert = _alert_from_fixture(fixture)
    execution = _execution_from_fixture(fixture)
    v3_context = _v3_context_from_fixture(fixture, execution=execution)

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
    raw_input = adapt_v3_fixture_to_slice_input(fixture)
    tape = build_completed_tape(raw_input, tenant_id=tenant_id)
    expected_verdict = fixture.get("verdict")
    if expected_verdict is not None:
        expected_value = _verdict_value(expected_verdict)
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
) -> dict[str, Any]:
    """Build the existing 9-file proof package in memory from a V3 fixture."""
    return build_proof_package(
        build_tape_from_v3_fixture(fixture, tenant_id=tenant_id)
    )


def write_proof_package_from_v3_fixture(
    fixture: dict[str, Any],
    output_dir: str | Path,
    *,
    tenant_id: str | None = None,
) -> dict[str, str]:
    """Write the existing 9-file proof package from a V3 fixture."""
    return write_proof_package(
        build_tape_from_v3_fixture(fixture, tenant_id=tenant_id),
        output_dir,
    )


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
