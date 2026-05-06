"""Static sample loading and evidence normalization for Slice 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.hashing import sha256_of_obj, sha256_of_string


_PROCESS_EVENT_KEYS = ("process_events",)
_NETWORK_FLOW_KEYS = ("network_events", "network_flows")
_EVENT_ARRAY_KEYS = set(_PROCESS_EVENT_KEYS + _NETWORK_FLOW_KEYS)


def load_sample(path: str | Path) -> dict[str, Any]:
    """Load a static EDR-style JSON sample from disk."""
    sample_path = Path(path)
    try:
        raw = sample_path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ZovarkValidationError(f"invalid Slice 001 sample: {sample_path}") from exc

    if not isinstance(parsed, dict):
        raise ZovarkValidationError("Slice 001 sample must be a JSON object")
    return parsed


def normalize_evidence(raw_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize a raw EDR-style object into deterministic evidence entries."""
    if not isinstance(raw_input, dict):
        raise ZovarkValidationError("raw input must be a JSON object")

    entries: list[dict[str, Any]] = []

    alert_object = {
        key: value for key, value in raw_input.items() if key not in _EVENT_ARRAY_KEYS
    }
    if alert_object:
        entries.append(_evidence_entry("edr_alert", alert_object))

    for key in _PROCESS_EVENT_KEYS:
        entries.extend(
            _entries_from_array(raw_input, key, source_type="process_event")
        )

    for key in _NETWORK_FLOW_KEYS:
        entries.extend(
            _entries_from_array(raw_input, key, source_type="network_flow")
        )

    if not entries:
        raise ZovarkValidationError("raw input did not produce any evidence")
    return entries


def _entries_from_array(
    raw_input: dict[str, Any], key: str, *, source_type: str
) -> list[dict[str, Any]]:
    if key not in raw_input:
        return []

    raw_events = raw_input[key]
    if not isinstance(raw_events, list):
        raise ZovarkValidationError(f"{key} must be a JSON array")

    entries = []
    for index, event in enumerate(raw_events):
        if not isinstance(event, dict):
            raise ZovarkValidationError(f"{key}[{index}] must be a JSON object")
        entries.append(_evidence_entry(source_type, event))
    return entries


def _evidence_entry(source_type: str, raw_content: dict[str, Any]) -> dict[str, Any]:
    content_hash = sha256_of_obj(raw_content)
    evidence_id = "ev-" + sha256_of_string(f"{source_type}:{content_hash}")
    return {
        "evidence_id": evidence_id,
        "source_type": source_type,
        "hash": content_hash,
        "raw_content": raw_content,
    }
