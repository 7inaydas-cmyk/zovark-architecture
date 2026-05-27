#!/usr/bin/env python3
"""Validate authoritative architecture JSON Schema contracts.

The architecture contract gate requires more than JSON parsing: schemas must
pass the Draft 2020-12 metaschema, close object channels, resolve local refs
without remote/network access, and exercise valid/invalid examples for new
contracts whose semantic constraints are only partly expressible in JSON
Schema.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
    from jsonschema.validators import RefResolver
except Exception as exc:  # pragma: no cover - explicit local environment gate
    print(f"JSONSCHEMA_NOT_AVAILABLE: {exc!r}")
    sys.exit(1)

try:
    import yaml
except Exception as exc:  # pragma: no cover - explicit local environment gate
    print(f"YAML_NOT_AVAILABLE: {exc!r}")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "architecture" / "blueprint" / "schemas"
REPLAY_COMPATIBILITY_CONTRACT = REPO_ROOT / "architecture" / "replay-compatibility.yaml"
REPLAY_TOOL_CATALOG_DIR = REPO_ROOT / "architecture" / "replay" / "catalogs"
RUNTIME_PROOF_LOOP_COMPLETION_CONTRACT = REPO_ROOT / "architecture" / "proof" / "runtime-proof-loop-completion.yaml"
REPLAY_FAILURE_CODE_REF = (
    "https://schemas.zovark.io/replay_failure_record/v1.0.0/schema.json#/$defs/ReplayFailureCode"
)
REPLAY_FAILURE_CATEGORY_REF = (
    "https://schemas.zovark.io/replay_failure_record/v1.0.0/schema.json#/$defs/ReplayFailureCategory"
)
REPLAY_FAILURE_COMPONENT_REF = (
    "https://schemas.zovark.io/replay_failure_record/v1.0.0/schema.json#/$defs/ReplayFailureComponent"
)
REPLAY_TOOL_RETIRED_CODE = "REPLAY_TOOL_RETIRED"
REPLAY_TOOL_RETIRED_ROW_ID = "tool_compatibility.tool_retired"

EXPECTED_SCHEMA_COUNT = 28

REQUIRED_RUNTIME_PROOF_LOOP_MARKERS = {
    "SCANNER_FIXTURE_SCHEMA_OK",
    "VERDICT_FIXTURE_SCHEMA_OK",
    "VERDICT_INPUT_FIXTURE_SCHEMA_OK",
    "REPLAY_RECORD_FIXTURE_SCHEMA_OK",
    "DETERMINISTIC_VERDICT_DERIVATION_OK",
    "REPLAY_VALIDATION_PROOF_OK",
    "REPLAY_VALIDATION_FAIL_CLOSED_CASES_OK",
    "REPLAY_COMPATIBILITY_MATRIX_SCHEMA_OK",
    "REPLAY_COMPATIBILITY_ROW_COVERAGE_SCHEMA_OK",
    "REPLAY_TOOL_CATALOG_AUTHORITY_IMPORT_OK",
    "REPLAY_FAILURE_RECORD_SCHEMA_OK",
    "REPLAY_FAILURE_RECORD_FIXTURE_SCHEMA_OK",
    "REPLAY_FAILURE_CANONICAL_CODE_MAPPING_OK",
    "REPLAY_FAILURE_RECORD_EMISSION_OK",
    "REPLAY_COMPATIBILITY_MATRIX_ROW_MAPPING_OK",
    "REPLAY_DECODING_PARAMS_FAIL_CLOSED_OK",
    "REPLAY_TOOL_RETIRED_FAIL_CLOSED_OK",
    "REPLAY_COMPATIBILITY_MATRIX_COVERAGE_OK",
    "CONTRACT_METASCHEMA_OK",
}

REQUIRED_RUNTIME_PROOF_DEFERRED_POLICY = {
    "audit_chain_output": "future_scoped",
    "runtime_investigation_execution": "future_scoped",
    "alertforge_scenario_validation": "non_goal",
    "benchmark_proof": "non_goal",
    "dashboard_and_external_claims": "non_goal",
    "production_sla_compliance_workflows": "non_goal",
}

REQUIRED_RUNTIME_PROOF_NON_GOALS = {
    "AlertForge validation",
    "benchmarks",
    "dashboard readiness",
    "customer outreach readiness",
    "customer readiness",
    "product readiness",
    "production readiness",
    "compliance readiness",
    "SLA readiness",
}

FORBIDDEN_FIELD_NAMES = {
    "captured_at",
    "ctime",
    "current_timestamp",
    "filesystem_metadata",
    "hidden_reasoning",
    "hostname",
    "inode",
    "mtime",
    "network_io",
    "pid",
    "process_state",
    "prompt_payload",
    "random_seed",
    "raw_llm_payload",
    "raw_prompt",
    "raw_rows",
    "raw_tool_output",
    "time_time",
    "wall_clock_ns",
}


def load_schemas() -> tuple[dict[Path, dict[str, Any]], dict[str, dict[str, Any]]]:
    schemas_by_path: dict[Path, dict[str, Any]] = {}
    schemas_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = json.loads(path.read_text())
        schemas_by_path[path] = schema
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            schemas_by_id[schema_id.split("#", 1)[0]] = schema
    return schemas_by_path, schemas_by_id


def collect_refs(node: Any, refs: list[str]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            refs.append(ref)
        for value in node.values():
            collect_refs(value, refs)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, refs)


def load_replay_compatibility_matrix() -> dict[str, Any]:
    matrix = yaml.safe_load(REPLAY_COMPATIBILITY_CONTRACT.read_text())
    if not isinstance(matrix, dict):
        raise TypeError("architecture/replay-compatibility.yaml must load as an object")
    return matrix


def load_replay_tool_catalogs() -> dict[str, dict[str, Any]]:
    catalogs: dict[str, dict[str, Any]] = {}
    for path in sorted(REPLAY_TOOL_CATALOG_DIR.glob("*.yaml")):
        catalog = yaml.safe_load(path.read_text())
        if not isinstance(catalog, dict):
            raise TypeError(f"{path.relative_to(REPO_ROOT)} must load as an object")
        catalog_version = catalog.get("catalog_version")
        if not isinstance(catalog_version, str):
            raise TypeError(f"{path.relative_to(REPO_ROOT)} missing catalog_version")
        catalogs[catalog_version] = catalog
    return catalogs


def load_runtime_proof_loop_completion_contract() -> dict[str, Any]:
    contract = yaml.safe_load(RUNTIME_PROOF_LOOP_COMPLETION_CONTRACT.read_text())
    if not isinstance(contract, dict):
        raise TypeError("architecture/proof/runtime-proof-loop-completion.yaml must load as an object")
    return contract


def replay_failure_codes(schema: dict[str, Any]) -> list[str]:
    codes = schema["$defs"]["ReplayFailureCode"]["enum"]
    if not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
        raise TypeError("ReplayFailureCode enum must be a list of strings")
    return codes


def replay_failure_outcome_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = matrix.get("failure_outcome_rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise TypeError("failure_outcome_rows must be a list of objects")
    return rows


def check_replay_compatibility_rows(
    matrix: dict[str, Any],
    failure_codes: list[str],
    failures: list[str],
) -> None:
    rows = replay_failure_outcome_rows(matrix)
    row_ids: set[str] = set()
    covered_codes: list[str] = []
    valid_codes = set(failure_codes)

    for row in rows:
        row_id = row.get("row_id")
        if not isinstance(row_id, str) or not row_id:
            failures.append("architecture/replay-compatibility.yaml: failure_outcome_rows row missing row_id")
            continue
        if row_id in row_ids:
            failures.append(f"architecture/replay-compatibility.yaml: duplicate failure_outcome_rows row_id {row_id}")
        row_ids.add(row_id)

        if row.get("outcome") != "fail_closed":
            failures.append(f"architecture/replay-compatibility.yaml: {row_id} outcome must be fail_closed")

        evidence = row.get("runtime_evidence_required")
        if not isinstance(evidence, list) or "canonical_replay_failure_record" not in evidence:
            failures.append(
                f"architecture/replay-compatibility.yaml: {row_id} must require canonical_replay_failure_record evidence"
            )

        row_codes = row.get("failure_codes")
        if not isinstance(row_codes, list) or not row_codes:
            failures.append(f"architecture/replay-compatibility.yaml: {row_id} must list failure_codes")
            continue
        for code in row_codes:
            if code not in valid_codes:
                failures.append(f"architecture/replay-compatibility.yaml: {row_id} references non-canonical {code}")
            covered_codes.append(code)

    if len(covered_codes) != len(set(covered_codes)):
        failures.append("architecture/replay-compatibility.yaml: failure_outcome_rows duplicate failure code coverage")
    if set(covered_codes) != valid_codes:
        missing = sorted(valid_codes - set(covered_codes))
        extra = sorted(set(covered_codes) - valid_codes)
        failures.append(
            "architecture/replay-compatibility.yaml: failure_outcome_rows must cover ReplayFailureCode enum exactly "
            f"missing={missing!r} extra={extra!r}"
        )


def tool_identity(entry: dict[str, Any]) -> tuple[str, str] | None:
    tool_name = entry.get("tool_name")
    tool_version = entry.get("tool_version")
    if isinstance(tool_name, str) and isinstance(tool_version, str):
        return (tool_name, tool_version)
    return None


def retired_tool_reference(entry: dict[str, Any]) -> tuple[str, str, str, str, str, str] | None:
    identity = tool_identity(entry)
    last_active = entry.get("last_active_catalog_version")
    retired_in = entry.get("retired_in_catalog_version")
    failure_code = entry.get("failure_code")
    row_id = entry.get("row_id")
    if (
        identity is not None
        and isinstance(last_active, str)
        and isinstance(retired_in, str)
        and isinstance(failure_code, str)
        and isinstance(row_id, str)
    ):
        return (*identity, last_active, retired_in, failure_code, row_id)
    return None


def check_unique_tool_identities(
    catalog: dict[str, Any],
    *,
    catalog_version: str,
    failures: list[str],
) -> None:
    for field_name in ("tools", "retired_tools"):
        entries = catalog.get(field_name)
        if not isinstance(entries, list):
            failures.append(f"replay tool catalog {catalog_version}: {field_name} must be a list")
            continue
        identities: list[tuple[str, str]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                failures.append(f"replay tool catalog {catalog_version}: {field_name} entries must be objects")
                continue
            identity = tool_identity(entry)
            if identity is None:
                failures.append(f"replay tool catalog {catalog_version}: {field_name} entry missing tool identity")
                continue
            identities.append(identity)
        if len(identities) != len(set(identities)):
            failures.append(f"replay tool catalog {catalog_version}: duplicate {field_name} tool identity")


def check_replay_tool_catalog_authority(
    matrix: dict[str, Any],
    catalogs: dict[str, dict[str, Any]],
    failures: list[str],
) -> None:
    tool_catalog = matrix.get("tool_catalog")
    if not isinstance(tool_catalog, dict):
        failures.append("architecture/replay-compatibility.yaml: tool_catalog must be an object")
        return

    current_version = matrix.get("current_tool_catalog_version")
    if not isinstance(current_version, str):
        failures.append("architecture/replay-compatibility.yaml: current_tool_catalog_version must be set")
        return
    if current_version not in tool_catalog:
        failures.append("architecture/replay-compatibility.yaml: current_tool_catalog_version must be a tool_catalog key")
        return
    if current_version not in catalogs:
        failures.append("architecture/replay-compatibility.yaml: current_tool_catalog_version catalog artifact is missing")
        return

    matrix_versions = set(tool_catalog)
    catalog_versions = set(catalogs)
    if matrix_versions != catalog_versions:
        failures.append(
            "architecture/replay-compatibility.yaml: tool_catalog versions must match replay catalog artifacts "
            f"matrix={sorted(matrix_versions)!r} catalogs={sorted(catalog_versions)!r}"
        )

    for version, entry in tool_catalog.items():
        if not isinstance(entry, dict):
            failures.append(f"architecture/replay-compatibility.yaml: tool_catalog {version} must be an object")
            continue
        artifact = entry.get("catalog_artifact")
        expected_artifact = f"architecture/replay/catalogs/{version}.yaml"
        if artifact != expected_artifact:
            failures.append(
                f"architecture/replay-compatibility.yaml: tool_catalog {version} catalog_artifact must be {expected_artifact}"
            )
        catalog = catalogs.get(version)
        if catalog is not None and catalog.get("catalog_version") != version:
            failures.append(f"architecture/replay/catalogs/{version}.yaml: catalog_version must match filename")

    tool_retired_rows = [
        row
        for row in replay_failure_outcome_rows(matrix)
        if REPLAY_TOOL_RETIRED_CODE in row.get("failure_codes", [])
    ]
    if len(tool_retired_rows) != 1:
        failures.append("architecture/replay-compatibility.yaml: REPLAY_TOOL_RETIRED must map to exactly one row")
        return
    if tool_retired_rows[0].get("row_id") != REPLAY_TOOL_RETIRED_ROW_ID:
        failures.append("architecture/replay-compatibility.yaml: REPLAY_TOOL_RETIRED row_id mismatch")

    for version, catalog in catalogs.items():
        check_unique_tool_identities(catalog, catalog_version=version, failures=failures)

    current_catalog = catalogs[current_version]
    current_active = {
        identity
        for entry in current_catalog.get("tools", [])
        if isinstance(entry, dict) and (identity := tool_identity(entry)) is not None
    }
    current_retired_entries = [
        entry
        for entry in current_catalog.get("retired_tools", [])
        if isinstance(entry, dict)
    ]
    if not current_retired_entries:
        failures.append("architecture/replay/catalogs current catalog must include at least one retired tool proof entry")

    matrix_removed_entries = tool_catalog[current_version].get("removed_tools", [])
    if not isinstance(matrix_removed_entries, list):
        failures.append("architecture/replay-compatibility.yaml: current removed_tools must be a list")
        matrix_removed_entries = []
    current_retired_refs = {
        ref
        for entry in current_retired_entries
        if (ref := retired_tool_reference(entry)) is not None
    }
    matrix_removed_refs = {
        ref
        for entry in matrix_removed_entries
        if isinstance(entry, dict) and (ref := retired_tool_reference(entry)) is not None
    }
    if current_retired_refs != matrix_removed_refs:
        failures.append("architecture/replay-compatibility.yaml: current removed_tools must match current catalog retired_tools")

    for entry in current_retired_entries:
        ref = retired_tool_reference(entry)
        if ref is None:
            failures.append("architecture/replay/catalogs current retired_tools entry is malformed")
            continue
        tool_name, tool_version, last_active, retired_in, failure_code, row_id = ref
        identity = (tool_name, tool_version)
        if failure_code != REPLAY_TOOL_RETIRED_CODE:
            failures.append("architecture/replay/catalogs current retired_tools entry must use REPLAY_TOOL_RETIRED")
        if row_id != REPLAY_TOOL_RETIRED_ROW_ID:
            failures.append("architecture/replay/catalogs current retired_tools entry must map to tool_retired row")
        if retired_in != current_version:
            failures.append("architecture/replay/catalogs current retired_tools retired_in_catalog_version mismatch")
        last_catalog = catalogs.get(last_active)
        if last_catalog is None:
            failures.append(f"architecture/replay/catalogs retired tool {tool_name}: missing last active catalog")
            continue
        last_active_tools = {
            active_identity
            for active_entry in last_catalog.get("tools", [])
            if isinstance(active_entry, dict) and (active_identity := tool_identity(active_entry)) is not None
        }
        if identity not in last_active_tools:
            failures.append(f"architecture/replay/catalogs retired tool {tool_name}: not present in last active catalog")
        if identity in current_active:
            failures.append(f"architecture/replay/catalogs retired tool {tool_name}: still active in current catalog")


def check_runtime_proof_loop_completion_authority(contract: dict[str, Any], failures: list[str]) -> None:
    if contract.get("proof_marker") != "ARCH_RUNTIME_PROOF_LOOP_COMPLETION_CRITERIA_OK":
        failures.append("runtime-proof-loop-completion.yaml: proof_marker mismatch")
    if contract.get("scope") != "deterministic_replay_proof_loop":
        failures.append("runtime-proof-loop-completion.yaml: scope must be deterministic_replay_proof_loop")

    transition = contract.get("status_transition")
    if not isinstance(transition, dict):
        failures.append("runtime-proof-loop-completion.yaml: status_transition must be an object")
        return
    if transition.get("runtime_proof_loop_complete_allowed") is not True:
        failures.append("runtime-proof-loop-completion.yaml: completion must be explicitly allowed")
    if transition.get("runtime_must_import_or_cite_authority") is not True:
        failures.append("runtime-proof-loop-completion.yaml: runtime must import or cite architecture authority")
    if transition.get("completion_claim") != "deterministic_replay_proof_loop_complete":
        failures.append("runtime-proof-loop-completion.yaml: completion claim must be scoped to deterministic replay")
    authority = transition.get("required_architecture_authority")
    if not isinstance(authority, list) or "ADR-0053" not in authority:
        failures.append("runtime-proof-loop-completion.yaml: required_architecture_authority must include ADR-0053")

    markers = contract.get("required_proof_markers")
    if not isinstance(markers, list) or set(markers) != REQUIRED_RUNTIME_PROOF_LOOP_MARKERS:
        failures.append(
            "runtime-proof-loop-completion.yaml: required_proof_markers must match scoped deterministic replay proof set "
            f"missing={sorted(REQUIRED_RUNTIME_PROOF_LOOP_MARKERS - set(markers or []))!r} "
            f"extra={sorted(set(markers or []) - REQUIRED_RUNTIME_PROOF_LOOP_MARKERS)!r}"
        )

    evidence_handles = set(contract.get("evidence_handle_requirements", []))
    for required_handle in ("test_file_path", "coverage_evidence_path", "expected_count"):
        if required_handle not in evidence_handles:
            failures.append(f"runtime-proof-loop-completion.yaml: missing evidence handle {required_handle}")

    policies = contract.get("deferred_entry_policy")
    if not isinstance(policies, list):
        failures.append("runtime-proof-loop-completion.yaml: deferred_entry_policy must be a list")
        return
    actual_policy: dict[str, str] = {}
    for policy in policies:
        if not isinstance(policy, dict):
            failures.append("runtime-proof-loop-completion.yaml: deferred_entry_policy entries must be objects")
            continue
        entry_id = policy.get("entry_id")
        classification = policy.get("classification")
        if isinstance(entry_id, str) and isinstance(classification, str):
            actual_policy[entry_id] = classification
        if entry_id in REQUIRED_RUNTIME_PROOF_DEFERRED_POLICY and policy.get("blocking_for_completion") is not False:
            failures.append(f"runtime-proof-loop-completion.yaml: {entry_id} must be non-blocking")
    if actual_policy != REQUIRED_RUNTIME_PROOF_DEFERRED_POLICY:
        failures.append(
            "runtime-proof-loop-completion.yaml: deferred policy must classify current runtime deferred entries exactly "
            f"expected={REQUIRED_RUNTIME_PROOF_DEFERRED_POLICY!r} actual={actual_policy!r}"
        )

    constraints = contract.get("proof_status_constraints")
    if not isinstance(constraints, dict):
        failures.append("runtime-proof-loop-completion.yaml: proof_status_constraints must be an object")
    else:
        for key in (
            "no_pytest_execution",
            "no_ci_log_parsing",
            "no_dynamic_completion_inference_from_local_state_alone",
            "requires_architecture_provenance",
        ):
            if constraints.get(key) is not True:
                failures.append(f"runtime-proof-loop-completion.yaml: proof_status_constraints.{key} must be true")

    non_goals = set(contract.get("non_goal_boundaries", []))
    missing_non_goals = REQUIRED_RUNTIME_PROOF_NON_GOALS - non_goals
    if missing_non_goals:
        failures.append(
            "runtime-proof-loop-completion.yaml: missing required non-goal boundaries "
            f"{sorted(missing_non_goals)!r}"
        )


def path_join(path: list[str]) -> str:
    return ".".join(path) if path else "$"


def check_object_closure(node: Any, path: list[str], failures: list[str]) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            if "additionalProperties" not in node and "unevaluatedProperties" not in node:
                failures.append(f"{path_join(path)}: object missing closure keyword")
            if node.get("additionalProperties") is True:
                failures.append(f"{path_join(path)}: additionalProperties true is not allowed")
            if "patternProperties" in node:
                has_bounds = (
                    "propertyNames" in node
                    or "maxProperties" in node
                    or node.get("additionalProperties") is False
                )
                if not has_bounds:
                    failures.append(f"{path_join(path)}: patternProperties map lacks bounds")
        for key, value in node.items():
            check_object_closure(value, path + [key], failures)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            check_object_closure(value, path + [str(idx)], failures)


def check_forbidden_field_names(node: Any, path: list[str], failures: list[str]) -> None:
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            for key in properties:
                if key in FORBIDDEN_FIELD_NAMES:
                    failures.append(f"{path_join(path + ['properties', key])}: forbidden field name")
        for key, value in node.items():
            check_forbidden_field_names(value, path + [key], failures)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            check_forbidden_field_names(value, path + [str(idx)], failures)


def sha(char: str) -> str:
    return char * 64


def decoding_params() -> dict[str, Any]:
    return {
        "temperature_basis_points": 0,
        "top_p_basis_points": 10000,
        "max_output_tokens": 512,
        "seed_policy": "no_seed",
    }


def valid_verdict_input() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "tenant_id": "22222222-2222-4222-8222-222222222222",
        "investigation_id": "33333333-3333-4333-8333-333333333333",
        "logical_clock": 42,
        "alert_envelope": {
            "envelope_id": "11111111-1111-4111-8111-111111111111",
            "tenant_id": "22222222-2222-4222-8222-222222222222",
            "received_at_ns": 1700000000000000000,
            "scanner_type": "edr",
            "scanner_version": "1.0.0",
            "ocsf_class": 4002,
            "raw_finding": {
                "source_finding_id": "synthetic-finding-001",
                "source_event_uid": "synthetic-event-001",
                "title": "Synthetic suspicious process observation",
                "description": "Synthetic bounded finding for schema contract validation.",
                "severity": "medium",
                "observed_at_ns": 1700000000000000000,
            },
            "ingest_provenance": {
                "adapter": "synthetic",
                "adapter_version": "1.0.0",
            },
        },
        "tenant_config": {
            "config_version": "1.0.0",
            "policy_snapshot_version": "1.0.0",
            "allowed_action_classes": ["no_op"],
            "blocked_action_classes": [],
            "policy_hash": sha("a"),
        },
        "tool_catalog_version": "1.0.0",
        "tool_results": [
            {
                "tool_call_id": "tool-call-001",
                "sequence_number": 1,
                "tool_name": "synthetic-tool",
                "tool_version": "1.0.0",
                "status": "success",
                "input_hash": sha("b"),
                "output_hash": sha("c"),
                "canonical_summary": "Synthetic bounded tool summary.",
            }
        ],
        "llm_records": [
            {
                "call_id": "llm-call-001",
                "sequence_number": 1,
                "model_id": "synthetic-model",
                "model_version": "1.0.0",
                "decoding_params": decoding_params(),
                "prompt_hash": sha("d"),
                "model_visible_input_hash": sha("e"),
                "model_visible_output": "Synthetic bounded model-visible output.",
                "model_visible_output_hash": sha("f"),
            }
        ],
        "db_results": [
            {
                "query_id": "db-query-001",
                "row_canonical_hash": sha("1"),
                "result_set_hash": sha("2"),
                "row_count": 1,
                "schema_version": "1.0.0",
            }
        ],
        "model_version": "1.0.0",
        "decoding_params": decoding_params(),
        "prompt_hash": sha("d"),
    }


def valid_replay_record(failure_codes: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "record_format_version": "1.0.0",
        "investigation_id": "33333333-3333-4333-8333-333333333333",
        "tenant_id": "22222222-2222-4222-8222-222222222222",
        "captured_logical_clock": 42,
        "replay_compatibility_contract": "architecture/replay-compatibility.yaml",
        "failure_policy": "fail_closed",
        "tool_catalog_version": "1.0.0",
        "model_id": "synthetic-model",
        "model_version": "1.0.0",
        "decoding_params": decoding_params(),
        "prompt_hashes": [sha("d")],
        "verdict_input": valid_verdict_input(),
        "verdict_input_hash": sha("3"),
        "llm_io": [
            {
                "call_id": "llm-call-001",
                "sequence_number": 1,
                "model_id": "synthetic-model",
                "model_version": "1.0.0",
                "prompt_hash": sha("d"),
                "model_visible_input_hash": sha("e"),
                "model_visible_output": "Synthetic bounded replay output.",
                "model_visible_output_hash": sha("f"),
            }
        ],
        "tool_io": [
            {
                "tool_call_id": "tool-call-001",
                "sequence_number": 1,
                "tool_name": "synthetic-tool",
                "tool_version": "1.0.0",
                "input_hash": sha("b"),
                "output_hash": sha("c"),
                "status": "success",
                "canonical_summary": "Synthetic bounded replay tool summary.",
            }
        ],
        "db_snapshots": [
            {
                "query_id": "db-query-001",
                "schema_version": "1.0.0",
                "row_count": 1,
                "result_set_hash": sha("2"),
                "snapshot_hash": sha("4"),
            }
        ],
        "verdict_envelope_hash": sha("5"),
        "structured_failure_codes": failure_codes,
    }


def valid_replay_failure_record() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "failure_code": "REPLAY_VERDICT_INPUT_HASH_MISMATCH",
        "failure_category": "hash_integrity",
        "tenant_id": "22222222-2222-4222-8222-222222222222",
        "investigation_id": "33333333-3333-4333-8333-333333333333",
        "replay_compatibility_contract": "architecture/replay-compatibility.yaml",
        "replay_record_hash": sha("6"),
        "component": "verdict_input",
        "field_path": "verdict_input_hash",
        "expected_hash": sha("7"),
        "observed_hash": sha("8"),
        "fail_closed_reason": "Synthetic bounded replay failure record for schema contract validation.",
    }


def expect_valid(schema: dict[str, Any], store: dict[str, dict[str, Any]], instance: dict[str, Any]) -> None:
    resolver = RefResolver.from_schema(schema, store=store)
    Draft202012Validator(schema, resolver=resolver).validate(instance)


def expect_invalid(
    schema: dict[str, Any],
    store: dict[str, dict[str, Any]],
    instance: dict[str, Any],
    label: str,
    failures: list[str],
) -> None:
    resolver = RefResolver.from_schema(schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver)
    errors = list(validator.iter_errors(instance))
    if not errors:
        failures.append(f"{label}: expected invalid example to be rejected")


def with_path_value(instance: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = copy.deepcopy(instance)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


def check_sort_metadata(schema: dict[str, Any], required: dict[str, list[str]], failures: list[str]) -> None:
    properties = schema.get("properties", {})
    for property_name, expected in required.items():
        actual = properties.get(property_name, {}).get("x-zovark-sort-key")
        if actual != expected:
            failures.append(
                f"{schema.get('title')}.{property_name}: expected x-zovark-sort-key {expected!r}, got {actual!r}"
            )


def main() -> int:
    schemas_by_path, schemas_by_id = load_schemas()
    failures: list[str] = []

    if len(schemas_by_path) != EXPECTED_SCHEMA_COUNT:
        failures.append(f"expected {EXPECTED_SCHEMA_COUNT} authoritative schemas, found {len(schemas_by_path)}")

    for path, schema in schemas_by_path.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)}: metaschema failure: {exc}")
        check_object_closure(schema, [path.name], failures)
        if path.name in {
            "verdict_input.schema.json",
            "replay_record.schema.json",
            "replay_failure_record.schema.json",
            "replay_tool_catalog.schema.json",
        }:
            check_forbidden_field_names(schema, [path.name], failures)

    for path, schema in schemas_by_path.items():
        refs: list[str] = []
        collect_refs(schema, refs)
        for ref in refs:
            if ref.startswith("#"):
                continue
            base = ref.split("#", 1)[0]
            if base not in schemas_by_id:
                failures.append(f"{path.relative_to(REPO_ROOT)}: missing local $ref target {ref}")

    verdict_schema = schemas_by_path[SCHEMA_DIR / "verdict_input.schema.json"]
    replay_schema = schemas_by_path[SCHEMA_DIR / "replay_record.schema.json"]
    replay_failure_schema = schemas_by_path[SCHEMA_DIR / "replay_failure_record.schema.json"]
    replay_compatibility_schema = schemas_by_path[SCHEMA_DIR / "replay-compatibility.schema.json"]
    replay_tool_catalog_schema = schemas_by_path[SCHEMA_DIR / "replay_tool_catalog.schema.json"]
    runtime_proof_loop_completion_schema = schemas_by_path[
        SCHEMA_DIR / "runtime_proof_loop_completion.schema.json"
    ]
    failure_codes = replay_failure_codes(replay_failure_schema)

    check_sort_metadata(
        verdict_schema,
        {
            "tool_results": ["tool_call_id", "sequence_number"],
            "llm_records": ["call_id", "sequence_number"],
            "db_results": ["query_id", "row_canonical_hash"],
        },
        failures,
    )
    check_sort_metadata(
        replay_schema,
        {
            "llm_io": ["call_id", "sequence_number"],
            "tool_io": ["tool_call_id", "sequence_number"],
            "db_snapshots": ["query_id", "snapshot_hash"],
        },
        failures,
    )

    verdict_input = valid_verdict_input()
    replay_record = valid_replay_record(failure_codes)
    replay_failure_record = valid_replay_failure_record()
    replay_compatibility_matrix = load_replay_compatibility_matrix()
    replay_tool_catalogs = load_replay_tool_catalogs()
    runtime_proof_loop_completion = load_runtime_proof_loop_completion_contract()
    try:
        expect_valid(verdict_schema, schemas_by_id, verdict_input)
        expect_valid(replay_schema, schemas_by_id, replay_record)
        expect_valid(replay_failure_schema, schemas_by_id, replay_failure_record)
        expect_valid(replay_compatibility_schema, schemas_by_id, replay_compatibility_matrix)
        expect_valid(runtime_proof_loop_completion_schema, schemas_by_id, runtime_proof_loop_completion)
        for replay_tool_catalog in replay_tool_catalogs.values():
            expect_valid(replay_tool_catalog_schema, schemas_by_id, replay_tool_catalog)
    except Exception as exc:
        failures.append(f"valid example rejected: {exc}")

    if replay_compatibility_matrix.get("structured_failure_codes") != failure_codes:
        failures.append(
            "architecture/replay-compatibility.yaml: structured_failure_codes must match "
            "replay_failure_record.schema.json ReplayFailureCode enum"
        )

    check_replay_compatibility_rows(replay_compatibility_matrix, failure_codes, failures)
    check_replay_tool_catalog_authority(replay_compatibility_matrix, replay_tool_catalogs, failures)
    check_runtime_proof_loop_completion_authority(runtime_proof_loop_completion, failures)

    compatibility_ref = (
        replay_compatibility_schema.get("properties", {})
        .get("structured_failure_codes", {})
        .get("items", {})
        .get("$ref")
    )
    if compatibility_ref != REPLAY_FAILURE_CODE_REF:
        failures.append("replay-compatibility.schema.json: structured_failure_codes must $ref ReplayFailureCode")

    outcome_row_schema = replay_compatibility_schema.get("$defs", {}).get("failure_outcome_row", {})
    outcome_row_properties = outcome_row_schema.get("properties", {})
    outcome_code_ref = (
        outcome_row_properties.get("failure_codes", {}).get("items", {}).get("$ref")
    )
    if outcome_code_ref != REPLAY_FAILURE_CODE_REF:
        failures.append("replay-compatibility.schema.json: failure_outcome_rows failure_codes must $ref ReplayFailureCode")
    outcome_category_ref = outcome_row_properties.get("compatibility_dimension", {}).get("$ref")
    if outcome_category_ref != REPLAY_FAILURE_CATEGORY_REF:
        failures.append("replay-compatibility.schema.json: failure_outcome_rows compatibility_dimension must $ref ReplayFailureCategory")
    outcome_component_ref = outcome_row_properties.get("component", {}).get("$ref")
    if outcome_component_ref != REPLAY_FAILURE_COMPONENT_REF:
        failures.append("replay-compatibility.schema.json: failure_outcome_rows component must $ref ReplayFailureComponent")

    replay_record_ref = (
        replay_schema.get("properties", {})
        .get("structured_failure_codes", {})
        .get("items", {})
        .get("$ref")
    )
    if replay_record_ref != REPLAY_FAILURE_CODE_REF:
        failures.append("replay_record.schema.json: structured_failure_codes must $ref ReplayFailureCode")

    current_catalog_version_schema = replay_compatibility_schema.get("properties", {}).get(
        "current_tool_catalog_version",
        {},
    )
    if current_catalog_version_schema.get("$ref") != "#/$defs/version_string":
        failures.append("replay-compatibility.schema.json: current_tool_catalog_version must use version_string")

    expect_invalid(
        verdict_schema,
        schemas_by_id,
        with_path_value(verdict_input, ["wall_clock_ns"], 1700000000000000000),
        "verdict_input top-level forbidden wall_clock_ns",
        failures,
    )
    expect_invalid(
        verdict_schema,
        schemas_by_id,
        with_path_value(verdict_input, ["tool_results", 0, "raw_tool_output"], "raw output"),
        "verdict_input raw_tool_output",
        failures,
    )
    expect_invalid(
        verdict_schema,
        schemas_by_id,
        with_path_value(verdict_input, ["llm_records", 0, "hidden_reasoning"], "hidden"),
        "verdict_input hidden_reasoning",
        failures,
    )
    expect_invalid(
        verdict_schema,
        schemas_by_id,
        with_path_value(verdict_input, ["llm_records", 0, "prompt_payload"], "raw prompt"),
        "verdict_input prompt_payload",
        failures,
    )
    expect_invalid(
        replay_schema,
        schemas_by_id,
        with_path_value(replay_record, ["captured_at"], "2026-05-25T00:00:00Z"),
        "replay_record wall-clock captured_at",
        failures,
    )
    expect_invalid(
        replay_schema,
        schemas_by_id,
        with_path_value(replay_record, ["llm_io", 0, "hidden_reasoning"], "hidden"),
        "replay_record hidden_reasoning",
        failures,
    )
    expect_invalid(
        replay_schema,
        schemas_by_id,
        with_path_value(replay_record, ["tool_io", 0, "raw_tool_output"], "raw"),
        "replay_record raw_tool_output",
        failures,
    )
    expect_invalid(
        replay_schema,
        schemas_by_id,
        with_path_value(replay_record, ["db_snapshots", 0, "raw_rows"], []),
        "replay_record raw_rows",
        failures,
    )
    expect_invalid(
        replay_failure_schema,
        schemas_by_id,
        with_path_value(replay_failure_record, ["unexpected_field"], "not allowed"),
        "replay_failure_record extra field",
        failures,
    )
    expect_invalid(
        replay_failure_schema,
        schemas_by_id,
        with_path_value(replay_failure_record, ["failure_code"], "REPLAY_RUNTIME_LOCAL_ONLY"),
        "replay_failure_record unknown failure code",
        failures,
    )
    expect_invalid(
        replay_compatibility_schema,
        schemas_by_id,
        with_path_value(replay_compatibility_matrix, ["failure_outcome_rows", 0, "runtime_coverage_claim"], True),
        "replay compatibility outcome row extra field",
        failures,
    )
    expect_invalid(
        replay_compatibility_schema,
        schemas_by_id,
        with_path_value(
            replay_compatibility_matrix,
            ["failure_outcome_rows", 0, "failure_codes"],
            ["REPLAY_RUNTIME_LOCAL_ONLY"],
        ),
        "replay compatibility outcome row unknown failure code",
        failures,
    )
    expect_invalid(
        replay_compatibility_schema,
        schemas_by_id,
        with_path_value(
            replay_compatibility_matrix,
            ["tool_catalog", "1.1.0", "removed_tools", 0, "raw_tool_output"],
            "raw",
        ),
        "replay compatibility removed tool extra field",
        failures,
    )
    current_catalog_version = replay_compatibility_matrix.get("current_tool_catalog_version")
    if isinstance(current_catalog_version, str) and current_catalog_version in replay_tool_catalogs:
        current_tool_catalog = replay_tool_catalogs[current_catalog_version]
        expect_invalid(
            replay_tool_catalog_schema,
            schemas_by_id,
            with_path_value(current_tool_catalog, ["unexpected_field"], "not allowed"),
            "replay tool catalog extra field",
            failures,
        )
        expect_invalid(
            replay_tool_catalog_schema,
            schemas_by_id,
            with_path_value(current_tool_catalog, ["retired_tools", 0, "failure_code"], "REPLAY_RUNTIME_LOCAL_ONLY"),
            "replay tool catalog retired tool unknown failure code",
            failures,
        )
        expect_invalid(
            replay_tool_catalog_schema,
            schemas_by_id,
            with_path_value(current_tool_catalog, ["tools", 0, "raw_tool_output"], "raw"),
            "replay tool catalog raw_tool_output",
            failures,
        )
    expect_invalid(
        runtime_proof_loop_completion_schema,
        schemas_by_id,
        with_path_value(runtime_proof_loop_completion, ["unexpected_field"], "not allowed"),
        "runtime proof-loop completion extra field",
        failures,
    )
    expect_invalid(
        runtime_proof_loop_completion_schema,
        schemas_by_id,
        with_path_value(runtime_proof_loop_completion, ["proof_status_constraints", "no_pytest_execution"], False),
        "runtime proof-loop completion pytest execution constraint",
        failures,
    )
    expect_invalid(
        runtime_proof_loop_completion_schema,
        schemas_by_id,
        with_path_value(runtime_proof_loop_completion, ["proof_marker"], "REPLAY_COMPATIBILITY_MATRIX_COVERAGE_OK"),
        "runtime proof-loop completion wrong proof marker",
        failures,
    )
    for forbidden_field in (
        "raw_prompt",
        "raw_llm_payload",
        "hidden_reasoning",
        "raw_tool_output",
        "filesystem_metadata",
        "process_state",
    ):
        expect_invalid(
            replay_failure_schema,
            schemas_by_id,
            with_path_value(replay_failure_record, [forbidden_field], "forbidden"),
            f"replay_failure_record forbidden {forbidden_field}",
            failures,
        )

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print(f"METASCHEMA_OK authoritative schemas: {len(schemas_by_path)}")
    print("OBJECT_CLOSURE_OK authoritative schemas")
    print("LOCAL_REF_CLOSURE_OK authoritative schemas")
    print("ORDER_METADATA_OK verdict_input replay_record")
    print("CONTRACT_EXAMPLES_OK verdict_input replay_record replay_failure_record replay_tool_catalog")
    print("REPLAY_COMPATIBILITY_CODES_OK")
    print("ARCH_REPLAY_COMPATIBILITY_ROW_COVERAGE_OK")
    print("ARCH_REPLAY_FAILURE_CONTRACT_OK")
    print("ARCH_REPLAY_TOOL_CATALOG_RETIREMENT_AUTHORITY_OK")
    print("ARCH_RUNTIME_PROOF_LOOP_COMPLETION_CRITERIA_OK")
    print("SCHEMA_CONTRACTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
