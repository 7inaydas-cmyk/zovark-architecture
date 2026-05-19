#!/usr/bin/env python3
"""
Minimal JSON Schema validator (Draft 2020-12 subset) — pure stdlib.

Why this exists: the v3.2.4.5 patch self-test must validate that every
schema example satisfies (or fails) its schema. We can't depend on the
'jsonschema' pip package being available in the customer's CI environment,
and silently skipping the test would make schema validation non-falsifiable.

Scope: handles the subset of JSON Schema actually used by Zovark's
schemas. Explicitly errors on unsupported constructs rather than silently
passing them. Constructs supported:

  type (string, integer, number, boolean, array, object, null)
  enum
  const
  required
  additionalProperties (true | false | schema)
  properties
  items (single schema)
  minItems, maxItems
  uniqueItems
  contains, minContains, maxContains
  pattern (Python re.search)
  minimum, maximum (inclusive)
  minLength, maxLength
  format: date-time, uri, uuid
  oneOf, anyOf, allOf
  if / then / else
  $defs and $ref (local only, e.g. "#/$defs/Name")

NEW IN v3.2.4.5:
  * `contains` / `minContains` / `maxContains` — required by the
    update_bundle_signed and update_promotion_decision schemas to enforce
    role composition (e.g., exactly one release-engineer + one security-
    officer signature, or Tier-3 promotion with >=2 maintainers and >=1
    security-officer reviewer).
"""
from __future__ import annotations

import json
import re
import sys
import uuid
import datetime
from pathlib import Path
from typing import Any


SUPPORTED_KEYWORDS = {
    "$schema", "$id", "$ref", "$defs",
    "title", "description", "type", "enum", "const",
    "required", "additionalProperties", "properties",
    "items", "minItems", "maxItems", "uniqueItems",
    "contains", "minContains", "maxContains",
    "pattern", "minimum", "maximum", "minLength", "maxLength",
    "format",
    "oneOf", "anyOf", "allOf",
    "if", "then", "else",
    "examples", "default",
    # x-zovark-* metadata, ignored for validation purposes
    "x-zovark-license", "x-zovark-open-source", "x-zovark-publication",
    "x-zovark-schema-version", "x-zovark-compatibility",
    "x-zovark-standards-attribution", "x-zovark-standard-attribution",
    "x-zovark-owner", "x-zovark-visibility",
    "x-zovark-breaking-change-requires-adr",
    # Schemas in this patch use this informational key as a list of fields
    # that must NEVER appear, captured via additionalProperties: false +
    # explicit properties enumeration. The key itself is documentation.
    "description-forbidden-fields",
}


class ValidationError(Exception):
    def __init__(self, path: str, msg: str):
        super().__init__(f"{path or '<root>'}: {msg}")
        self.path = path
        self.msg = msg


def _resolve_ref(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValidationError("", f"only local $ref supported, got {ref!r}")
    parts = ref[2:].split("/")
    cur: Any = root
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            raise ValidationError("", f"unresolvable $ref {ref!r}")
        cur = cur[p]
    return cur


def _check_format(value: Any, fmt: str, path: str) -> None:
    if fmt == "date-time":
        if not isinstance(value, str):
            raise ValidationError(path, f"format date-time requires string, got {type(value).__name__}")
        s = value.replace("Z", "+00:00")
        try:
            datetime.datetime.fromisoformat(s)
        except ValueError:
            raise ValidationError(path, f"invalid date-time {value!r}")
    elif fmt == "uri":
        if not isinstance(value, str) or "://" not in value:
            raise ValidationError(path, f"invalid uri {value!r}")
    elif fmt == "uuid":
        if not isinstance(value, str):
            raise ValidationError(path, f"format uuid requires string")
        try:
            uuid.UUID(value)
        except (ValueError, AttributeError):
            raise ValidationError(path, f"invalid uuid {value!r}")


_PY_TYPE = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _check_type(value: Any, t: str, path: str) -> None:
    if t == "boolean":
        if not isinstance(value, bool):
            raise ValidationError(path, f"expected boolean, got {type(value).__name__}")
    elif t == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(path, f"expected integer, got {type(value).__name__}")
    elif t == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(path, f"expected number, got {type(value).__name__}")
    elif t in _PY_TYPE:
        if not isinstance(value, _PY_TYPE[t]):
            raise ValidationError(path, f"expected {t}, got {type(value).__name__}")
    else:
        raise ValidationError(path, f"unsupported type {t!r}")


def _validate(value: Any, schema: dict, root: dict, path: str = "") -> None:
    for k in schema.keys():
        if k not in SUPPORTED_KEYWORDS:
            raise ValidationError(path, f"unsupported schema keyword {k!r}")

    if "$ref" in schema:
        sub = _resolve_ref(root, schema["$ref"])
        _validate(value, sub, root, path)
        return

    if "type" in schema:
        t = schema["type"]
        if isinstance(t, list):
            errs = []
            for tt in t:
                try:
                    _check_type(value, tt, path)
                    break
                except ValidationError as e:
                    errs.append(e.msg)
            else:
                raise ValidationError(path, f"none of types {t} matched: {errs}")
        else:
            _check_type(value, t, path)

    if "const" in schema:
        if value != schema["const"]:
            raise ValidationError(path, f"expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema:
        if value not in schema["enum"]:
            raise ValidationError(path, f"value {value!r} not in enum {schema['enum']}")

    if isinstance(value, str):
        if "pattern" in schema:
            if not re.search(schema["pattern"], value):
                raise ValidationError(path, f"value {value!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ValidationError(path, f"length {len(value)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValidationError(path, f"length {len(value)} > maxLength {schema['maxLength']}")
        if "format" in schema:
            _check_format(value, schema["format"], path)

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValidationError(path, f"value {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValidationError(path, f"value {value} > maximum {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ValidationError(path, f"items {len(value)} < minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ValidationError(path, f"items {len(value)} > maxItems {schema['maxItems']}")
        if schema.get("uniqueItems") is True:
            seen = []
            for x in value:
                if x in seen:
                    raise ValidationError(path, "uniqueItems violation")
                seen.append(x)
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], root, f"{path}[{i}]")
        # contains / minContains / maxContains
        if "contains" in schema:
            min_c = schema.get("minContains", 1)
            max_c = schema.get("maxContains", None)
            count = 0
            for i, item in enumerate(value):
                try:
                    _validate(item, schema["contains"], root, f"{path}[{i}](contains-probe)")
                    count += 1
                except ValidationError:
                    pass
            if count < min_c:
                raise ValidationError(path,
                    f"contains: matched {count}, want >= {min_c}")
            if max_c is not None and count > max_c:
                raise ValidationError(path,
                    f"contains: matched {count}, want <= {max_c}")

    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                raise ValidationError(path, f"required property {req!r} missing")
        props = schema.get("properties", {})
        ap = schema.get("additionalProperties", True)
        for k, v in value.items():
            sub_path = f"{path}.{k}" if path else k
            if k in props:
                _validate(v, props[k], root, sub_path)
            else:
                if ap is False:
                    raise ValidationError(sub_path, "additionalProperties: false; property not allowed")
                elif isinstance(ap, dict):
                    _validate(v, ap, root, sub_path)

    for combinator in ("allOf", "anyOf", "oneOf"):
        if combinator in schema:
            schemas = schema[combinator]
            if combinator == "allOf":
                for s in schemas:
                    _validate(value, s, root, path)
            elif combinator == "anyOf":
                ok = False
                for s in schemas:
                    try:
                        _validate(value, s, root, path)
                        ok = True
                        break
                    except ValidationError:
                        pass
                if not ok:
                    raise ValidationError(path, f"value did not match any of {len(schemas)} schemas")
            elif combinator == "oneOf":
                matches = 0
                for s in schemas:
                    try:
                        _validate(value, s, root, path)
                        matches += 1
                    except ValidationError:
                        pass
                if matches != 1:
                    raise ValidationError(path, f"oneOf: matched {matches}, expected exactly 1")

    if "if" in schema:
        try:
            _validate(value, schema["if"], root, path)
            matched = True
        except ValidationError:
            matched = False
        if matched and "then" in schema:
            _validate(value, schema["then"], root, path)
        if (not matched) and "else" in schema:
            _validate(value, schema["else"], root, path)


def validate(value: Any, schema: dict) -> tuple[bool, str]:
    """Returns (ok, error_message). error_message is empty when ok=True."""
    try:
        _validate(value, schema, schema, "")
        return True, ""
    except ValidationError as e:
        return False, str(e)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: jsonschema_minimal.py <schema.json> <instance.json>", file=sys.stderr)
        return 2
    schema = json.loads(Path(sys.argv[1]).read_text())
    instance = json.loads(Path(sys.argv[2]).read_text())
    ok, err = validate(instance, schema)
    if ok:
        print("VALID")
        return 0
    print(f"INVALID: {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
