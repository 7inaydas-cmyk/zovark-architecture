"""Rule-driven findings derivation for Slice 001."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from zovark.slice001 import ZovarkValidationError


_REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "source_type",
    "hash",
    "raw_content",
    "ingested_at",
}
_REQUIRED_FINDING_FIELDS = {
    "evidence_refs",
    "model_contribution",
    "severity",
    "title",
}
_ALLOWED_SEVERITIES = {"info", "low", "medium", "high", "critical"}

RULES: tuple[dict[str, Any], ...] = (
    {
        "evidence_source_types": ("edr_alert", "process_event"),
        "mitre_technique": "T1059.001",
        "rule_id": "RULE-OFFICE-SPAWN-ENCODED-PS",
        "severity": "high",
        "title": "Office application spawned encoded PowerShell",
    },
    {
        "evidence_source_types": ("process_event", "network_event"),
        "mitre_technique": "T1071.001",
        "rule_id": "RULE-PS-EXTERNAL-C2",
        "severity": "high",
        "title": "PowerShell contacted external IP over HTTPS",
    },
    {
        "evidence_source_types": ("credential_access",),
        "mitre_technique": "T1003.001",
        "rule_id": "RULE-LSASS-DUMP",
        "severity": "critical",
        "title": "Credential access via LSASS memory read",
    },
    {
        "evidence_source_types": ("lateral_movement_attempt",),
        "mitre_technique": "T1021.002",
        "rule_id": "RULE-SMB-LATERAL-MOVEMENT",
        "severity": "high",
        "title": "Lateral movement attempt to HOST-13 (blocked by firewall)",
    },
)


def derive_findings(
    evidence_source: dict[str, Any] | list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    """Derive deterministic findings from evidence entries or a tape."""
    evidence_entries = _evidence_entries_from(evidence_source)

    if not evidence_entries:
        return [
            {
                "evidence_refs": [],
                "model_contribution": False,
                "severity": "info",
                "title": "No evidence - inconclusive",
            }
        ], True

    evidence_by_type = _evidence_by_source_type(evidence_entries)
    findings: list[dict[str, Any]] = []

    for rule in RULES:
        source_types = rule["evidence_source_types"]
        if not all(source_type in evidence_by_type for source_type in source_types):
            continue
        evidence_refs = [
            evidence_by_type[source_type][0]["evidence_id"]
            for source_type in source_types
        ]
        findings.append(_finding_from_rule(rule, evidence_refs))

    no_findings_flag = not findings
    _validate_findings(
        findings,
        evidence_ids={entry["evidence_id"] for entry in evidence_entries},
        no_findings_flag=no_findings_flag,
    )
    return findings, no_findings_flag


def append_findings(
    tape: dict[str, Any],
    findings: list[dict[str, Any]],
    no_findings_flag: bool,
) -> dict[str, Any]:
    """Return a copy of *tape* with derived findings appended."""
    evidence_entries = _evidence_entries_from(tape)
    _validate_findings(
        findings,
        evidence_ids={entry["evidence_id"] for entry in evidence_entries},
        no_findings_flag=no_findings_flag,
    )
    if "findings" in tape and not isinstance(tape["findings"], list):
        raise ZovarkValidationError("tape.findings must be a list")
    if not isinstance(no_findings_flag, bool):
        raise ZovarkValidationError("no_findings_flag must be boolean")

    updated = deepcopy(tape)
    updated["findings"] = deepcopy(updated.get("findings", [])) + deepcopy(findings)
    if no_findings_flag:
        updated["no_findings_flag"] = True
    else:
        updated.pop("no_findings_flag", None)
    return updated


def attach_findings(
    tape: dict[str, Any],
    findings: list[dict[str, Any]],
    no_findings_flag: bool = False,
) -> dict[str, Any]:
    """Return a copy of *tape* with *findings* attached."""
    evidence_entries = _evidence_entries_from(tape)
    _validate_findings(
        findings,
        evidence_ids={entry["evidence_id"] for entry in evidence_entries},
        no_findings_flag=no_findings_flag,
    )
    if "findings" in tape and not isinstance(tape["findings"], list):
        raise ZovarkValidationError("tape.findings must be a list")
    if not isinstance(no_findings_flag, bool):
        raise ZovarkValidationError("no_findings_flag must be boolean")

    updated = deepcopy(tape)
    updated["findings"] = deepcopy(findings)
    if no_findings_flag:
        updated["no_findings_flag"] = True
    else:
        updated.pop("no_findings_flag", None)
    return updated


def _evidence_entries_from(
    evidence_source: dict[str, Any] | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(evidence_source, dict):
        if "raw_evidence" not in evidence_source:
            raise ZovarkValidationError("tape is missing raw_evidence")
        evidence_entries = evidence_source["raw_evidence"]
    else:
        evidence_entries = evidence_source

    if not isinstance(evidence_entries, list):
        raise ZovarkValidationError("evidence_entries must be a list")

    _validate_evidence_entries(evidence_entries)
    return evidence_entries


def _validate_evidence_entries(evidence_entries: list[dict[str, Any]]) -> None:
    seen_ids: set[str] = set()
    for index, entry in enumerate(evidence_entries):
        if not isinstance(entry, dict):
            raise ZovarkValidationError(f"evidence_entries[{index}] must be an object")
        if set(entry) != _REQUIRED_EVIDENCE_FIELDS:
            raise ZovarkValidationError(
                f"evidence_entries[{index}] does not match the Slice 001 evidence shape"
            )
        for key in ("evidence_id", "source_type", "hash", "ingested_at"):
            if not isinstance(entry[key], str) or not entry[key]:
                raise ZovarkValidationError(
                    f"evidence_entries[{index}].{key} must be a non-empty string"
                )
        if entry["evidence_id"] in seen_ids:
            raise ZovarkValidationError(
                f"evidence_entries[{index}].evidence_id must be unique"
            )
        seen_ids.add(entry["evidence_id"])
        if not isinstance(entry["raw_content"], dict):
            raise ZovarkValidationError(
                f"evidence_entries[{index}].raw_content must be an object"
            )


def _evidence_by_source_type(
    evidence_entries: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for entry in evidence_entries:
        by_type.setdefault(entry["source_type"], []).append(entry)
    return by_type


def _finding_from_rule(
    rule: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "evidence_refs": evidence_refs,
        "mitre_technique": rule["mitre_technique"],
        "model_contribution": False,
        "rule_id": rule["rule_id"],
        "severity": rule["severity"],
        "title": rule["title"],
    }


def _validate_findings(
    findings: list[dict[str, Any]],
    *,
    evidence_ids: set[str],
    no_findings_flag: bool,
) -> None:
    if not isinstance(findings, list):
        raise ZovarkValidationError("findings must be a list")
    if not isinstance(no_findings_flag, bool):
        raise ZovarkValidationError("no_findings_flag must be boolean")
    if not findings and not no_findings_flag:
        raise ZovarkValidationError("empty findings require no_findings_flag")

    seen_rule_ids: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ZovarkValidationError(f"findings[{index}] must be an object")
        if not _REQUIRED_FINDING_FIELDS.issubset(finding):
            raise ZovarkValidationError(
                f"findings[{index}] does not match the Slice 001 finding shape"
            )
        if finding["model_contribution"] is not False:
            raise ZovarkValidationError(
                f"findings[{index}].model_contribution must be false"
            )
        _non_empty_string(finding, "title")
        severity = _non_empty_string(finding, "severity")
        if severity not in _ALLOWED_SEVERITIES:
            raise ZovarkValidationError(f"findings[{index}].severity is invalid")

        if "rule_id" in finding:
            rule_id = _non_empty_string(finding, "rule_id")
            if rule_id in seen_rule_ids:
                raise ZovarkValidationError(
                    f"findings[{index}].rule_id must be unique"
                )
            seen_rule_ids.add(rule_id)
        if "mitre_technique" in finding:
            _non_empty_string(finding, "mitre_technique")

        refs = finding["evidence_refs"]
        if not isinstance(refs, list):
            raise ZovarkValidationError(
                f"findings[{index}].evidence_refs must be a list"
            )
        if not refs and not no_findings_flag:
            raise ZovarkValidationError(
                f"findings[{index}].evidence_refs must not be empty"
            )
        for ref_index, evidence_ref in enumerate(refs):
            if not isinstance(evidence_ref, str) or not evidence_ref:
                raise ZovarkValidationError(
                    f"findings[{index}].evidence_refs[{ref_index}] must be a non-empty string"
                )
            if evidence_ref not in evidence_ids:
                raise ZovarkValidationError(
                    f"findings[{index}].evidence_refs[{ref_index}] is not present in raw_evidence"
                )


def _non_empty_string(source: dict[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise ZovarkValidationError(f"{key} must be a non-empty string")
    return value
