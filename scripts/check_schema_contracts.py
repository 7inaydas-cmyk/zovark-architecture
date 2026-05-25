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


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "architecture" / "blueprint" / "schemas"

EXPECTED_SCHEMA_COUNT = 25

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


def valid_replay_record() -> dict[str, Any]:
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
        "structured_failure_codes": [
            "REPLAY_TOOL_RETIRED",
            "REPLAY_SCHEMA_INCOMPATIBLE",
        ],
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
        if path.name in {"verdict_input.schema.json", "replay_record.schema.json"}:
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
    replay_record = valid_replay_record()
    try:
        expect_valid(verdict_schema, schemas_by_id, verdict_input)
        expect_valid(replay_schema, schemas_by_id, replay_record)
    except Exception as exc:
        failures.append(f"valid example rejected: {exc}")

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

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print(f"METASCHEMA_OK authoritative schemas: {len(schemas_by_path)}")
    print("OBJECT_CLOSURE_OK authoritative schemas")
    print("LOCAL_REF_CLOSURE_OK authoritative schemas")
    print("ORDER_METADATA_OK verdict_input replay_record")
    print("CONTRACT_EXAMPLES_OK verdict_input replay_record")
    print("SCHEMA_CONTRACTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
