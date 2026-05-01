#!/usr/bin/env python3
"""
check_telemetry_boundary_schema_present.py

Verifies that telemetry_envelope.schema.json:

  1. Exists at architecture/blueprint/schemas/.
  2. Has additionalProperties: false at the root.
  3. Has additionalProperties: false on every nested **data-shape** object
     schema in $defs (StatusPayload, HealthPayload, etc.) and inside
     `properties:` chains.
  4. Defines exactly the four payload_kind enum values: status, health,
     failure_signature, none.
  5. Top-level required includes: envelope_version, instance_pseudonym,
     sent_at, payload_kind, payload, customer_audit_id.
  6. payload_kind is BOUND to payload shape via allOf+if/then with a
     branch for each of the four kinds (added in v3.2.4.5).

DATA-SHAPE vs CONSTRAINT-MATCHER distinction (added in v3.2.4.5):

  Object schemas that appear inside `if`, `then`, `else`, `not`,
  `oneOf`, `anyOf`, `allOf` branches are CONSTRAINT MATCHERS — they
  describe conditional shape, not data shape. The
  additionalProperties:false requirement does NOT apply to them. The
  requirement DOES apply to:

    * the root schema
    * every entry in $defs
    * every object schema reached through `properties`

NO marker-based fixture handling. Inspects actual file contents.

Exit codes:
  0  schema satisfies all rules
  1  any rule fails
  2  invocation error
"""
from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

REQUIRED_TOP = {
    "envelope_version", "instance_pseudonym", "sent_at",
    "payload_kind", "payload", "customer_audit_id",
}
EXPECTED_PAYLOAD_KINDS = {"status", "health", "failure_signature", "none"}


def _walk_data_shape_schemas(node, path="$", inside_constraint=False):
    """Yield (path, node) for object schemas that describe data shape.

    Object schemas inside if/then/else/not/oneOf/anyOf/allOf branches are
    constraint matchers and are NOT yielded — *unless* you reach them by
    descending through a `properties:` or `$defs:` member, which always
    yields a real data-shape.
    """
    if isinstance(node, dict):
        is_object_schema = node.get("type") == "object" or "properties" in node
        if is_object_schema and not inside_constraint:
            yield path, node

        for k, v in node.items():
            if k in ("if", "then", "else", "not"):
                yield from _walk_data_shape_schemas(v, f"{path}.{k}", inside_constraint=True)
            elif k in ("oneOf", "anyOf", "allOf") and isinstance(v, list):
                for i, item in enumerate(v):
                    yield from _walk_data_shape_schemas(
                        item, f"{path}.{k}[{i}]", inside_constraint=True)
            elif k in ("properties", "$defs") and isinstance(v, dict):
                # Always real data shapes, regardless of where we are.
                for sub_k, sub_v in v.items():
                    yield from _walk_data_shape_schemas(
                        sub_v, f"{path}.{k}.{sub_k}", inside_constraint=False)
            elif isinstance(v, (dict, list)):
                yield from _walk_data_shape_schemas(
                    v, f"{path}.{k}", inside_constraint=inside_constraint)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_data_shape_schemas(
                v, f"{path}[{i}]", inside_constraint=inside_constraint)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture-root", type=Path, default=None)
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    root = args.fixture_root if args.fixture_root else args.repo_root
    schema_path = root / "architecture" / "blueprint" / "schemas" / "telemetry_envelope.schema.json"

    if not schema_path.exists():
        print(f"FAIL: telemetry_envelope.schema.json missing at {schema_path}", file=sys.stderr)
        return 1
    try:
        doc = json.loads(schema_path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: invalid JSON: {e}", file=sys.stderr)
        return 1

    failures = []

    if doc.get("additionalProperties") is not False:
        failures.append("root additionalProperties is not false")

    for path, sub in _walk_data_shape_schemas(doc):
        if "properties" in sub and sub.get("additionalProperties") is not False:
            failures.append(f"data-shape object schema at {path} does not set additionalProperties: false")

    required = set(doc.get("required", []))
    missing = REQUIRED_TOP - required
    if missing:
        failures.append(f"missing required top-level fields: {sorted(missing)}")

    pk = doc.get("properties", {}).get("payload_kind", {})
    enum = set(pk.get("enum", []))
    if enum != EXPECTED_PAYLOAD_KINDS:
        failures.append(f"payload_kind enum mismatch: got {sorted(enum)}, want {sorted(EXPECTED_PAYLOAD_KINDS)}")

    # v3.2.4.5: payload_kind must be bound to payload via allOf+if/then
    allof = doc.get("allOf", [])
    if not isinstance(allof, list) or len(allof) < 4:
        failures.append("missing allOf with payload_kind→payload binding (need ≥4 if/then entries)")
    else:
        bound_kinds = set()
        for entry in allof:
            if isinstance(entry, dict) and "if" in entry and "then" in entry:
                if_props = entry["if"].get("properties", {})
                if "payload_kind" in if_props and "const" in if_props["payload_kind"]:
                    bound_kinds.add(if_props["payload_kind"]["const"])
        if bound_kinds != EXPECTED_PAYLOAD_KINDS:
            failures.append(f"payload_kind bindings: bound={sorted(bound_kinds)}, want {sorted(EXPECTED_PAYLOAD_KINDS)}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    if not args.quiet:
        print("PASS: telemetry boundary schema is allowlist-shaped, additionalProperties:false at every data-shape level, four payload_kinds bound to payload shape")
    return 0


if __name__ == "__main__":
    sys.exit(main())
