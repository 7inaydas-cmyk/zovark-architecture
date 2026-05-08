"""Offline proof-package verifier for Slice 002 Replay V2."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, NoReturn

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.audit import GENESIS_HASH, derive_audit_entry
from zovark.slice001.handoff import derive_handoff
from zovark.slice001.replay import derive_replay_report
from zovark.slice001.writer import (
    EXPECTED_OUTPUT_FILES,
    JSON_OUTPUT_FILES,
    render_customer_report,
)


MARKDOWN_OUTPUT_FILES = ("customer-report.md",)
_EXPECTED_FILE_SET = set(EXPECTED_OUTPUT_FILES)
_VERIFIED_COMPONENTS = (
    "file_set",
    "json_parse",
    "extracted_views",
    "handoff",
    "audit_entry",
    "replay_report",
    "customer_report",
)


def load_proof_package(package_dir: str | Path) -> dict[str, Any]:
    """Load the Slice 001 proof-package artifacts from *package_dir*."""
    package_path = Path(package_dir)
    _validate_package_dir(package_path)
    _validate_file_set(package_path)

    package: dict[str, Any] = {}
    for filename in JSON_OUTPUT_FILES:
        package[filename] = _load_json_file(package_path / filename)

    report_text = (package_path / "customer-report.md").read_text(encoding="utf-8")
    if not report_text:
        _fail("empty_customer_report", "customer-report.md must not be empty")
    package["customer-report.md"] = report_text
    return package


def validate_loaded_proof_package(package: dict[str, Any]) -> dict[str, Any]:
    """Validate an already-loaded Slice 001 proof package."""
    if not isinstance(package, dict):
        _fail("package_shape_invalid", "proof package must be an object")
    if set(package) != _EXPECTED_FILE_SET:
        _fail("package_shape_invalid", "proof package file set is invalid")
    for filename in JSON_OUTPUT_FILES:
        if not isinstance(package[filename], (dict, list)):
            _fail("package_shape_invalid", f"{filename} must be a JSON artifact")
    if not isinstance(package["customer-report.md"], str) or not package[
        "customer-report.md"
    ]:
        _fail("empty_customer_report", "customer-report.md must be non-empty text")

    full_tape = _reconstruct_verified_tape(package)
    _validate_customer_report(package, full_tape)
    return _verification_summary(full_tape)


def verify_proof_package(package_dir: str | Path) -> dict[str, Any]:
    """Load and verify a Slice 001 proof-package directory offline."""
    package = load_proof_package(package_dir)
    return validate_loaded_proof_package(package)


def _validate_package_dir(package_dir: Path) -> None:
    if not package_dir.exists():
        _fail("package_not_found", "proof package directory does not exist")
    if not package_dir.is_dir():
        _fail("package_not_directory", "proof package path must be a directory")


def _validate_file_set(package_dir: Path) -> None:
    actual_entries = {entry.name for entry in package_dir.iterdir()}
    if actual_entries != _EXPECTED_FILE_SET:
        _fail(
            "package_file_set_mismatch",
            "proof package directory file set is invalid",
        )
    for filename in EXPECTED_OUTPUT_FILES:
        if not (package_dir / filename).is_file():
            _fail("artifact_not_file", f"{filename} must be a file")


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ZovarkValidationError(
            f"malformed_json: {path.name} is not valid JSON"
        ) from exc
    except OSError as exc:
        raise ZovarkValidationError(
            f"malformed_json: {path.name} could not be read"
        ) from exc


def _reconstruct_verified_tape(package: dict[str, Any]) -> dict[str, Any]:
    tape = deepcopy(package["investigation-tape.json"])
    if not isinstance(tape, dict):
        _fail("package_shape_invalid", "investigation-tape.json must be an object")
    if tape.get("state") != "closed":
        _fail("tape_state_invalid", "investigation-tape.json state must be closed")

    _validate_extracted_views(package, tape)

    handoff = deepcopy(package["edr-handoff.json"])
    try:
        expected_handoff = derive_handoff(tape)
    except ZovarkValidationError as exc:
        raise ZovarkValidationError(
            f"handoff_mismatch: could not derive handoff: {exc}"
        ) from exc
    if handoff != expected_handoff:
        _fail("handoff_mismatch", "edr-handoff.json does not match derived handoff")
    _validate_handoff_tape_links(tape, handoff)

    with_handoff = deepcopy(tape)
    with_handoff["handoff"] = handoff
    audit_entry = deepcopy(package["audit-chain-entry.json"])
    if not isinstance(audit_entry, dict):
        _fail("audit_chain_mismatch", "audit-chain-entry.json must be an object")
    if (
        audit_entry.get("sequence") != 1
        or audit_entry.get("prev_entry_hash") != GENESIS_HASH
    ):
        _fail("audit_genesis_mismatch", "first audit entry must anchor to genesis")
    try:
        expected_audit_entry = derive_audit_entry(with_handoff)
    except ZovarkValidationError as exc:
        raise ZovarkValidationError(
            f"audit_chain_mismatch: could not derive audit entry: {exc}"
        ) from exc
    if audit_entry != expected_audit_entry:
        _fail(
            "audit_chain_mismatch",
            "audit-chain-entry.json does not match derived audit entry",
        )

    sealed_tape = deepcopy(with_handoff)
    sealed_tape["audit_entry"] = audit_entry

    replay_report = deepcopy(package["replay-report.json"])
    try:
        expected_replay_report = derive_replay_report(sealed_tape)
    except ZovarkValidationError as exc:
        raise ZovarkValidationError(
            f"replay_report_mismatch: could not derive replay report: {exc}"
        ) from exc
    if replay_report != expected_replay_report:
        _fail(
            "replay_report_mismatch",
            "replay-report.json does not match derived replay report",
        )

    full_tape = deepcopy(sealed_tape)
    full_tape["replay_report"] = replay_report
    return full_tape


def _validate_extracted_views(
    package: dict[str, Any],
    tape: dict[str, Any],
) -> None:
    expected_views = {
        "evidence-ledger.json": "raw_evidence",
        "timeline.json": "timeline",
        "findings.json": "findings",
        "verdict.json": "verdict",
    }
    for filename, tape_field in expected_views.items():
        if tape_field not in tape:
            _fail(
                "extracted_view_mismatch",
                f"investigation-tape.json is missing {tape_field}",
            )
        if package[filename] != tape[tape_field]:
            _fail(
                "extracted_view_mismatch",
                f"{filename} does not match investigation tape",
            )


def _validate_handoff_tape_links(
    tape: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    try:
        handoff_id = handoff["handoff_id"]
        expected_summary = {
            "action_type": handoff["action_type"],
            "approval_mode": handoff["approval_mode"],
            "execution_status": handoff["execution_result"]["status"],
            "target": {
                "identifier": handoff["target"]["identifier"],
                "kind": handoff["target"]["kind"],
            },
        }
    except (KeyError, TypeError) as exc:
        raise ZovarkValidationError(
            "handoff_link_mismatch: edr-handoff.json link fields are invalid"
        ) from exc

    if tape.get("handoff_ref") != handoff_id:
        _fail("handoff_link_mismatch", "investigation-tape handoff_ref is invalid")
    if tape.get("handoff_summary") != expected_summary:
        _fail(
            "handoff_link_mismatch",
            "investigation-tape handoff_summary is invalid",
        )


def _validate_customer_report(
    package: dict[str, Any],
    full_tape: dict[str, Any],
) -> None:
    try:
        expected_report = render_customer_report(full_tape)
    except ZovarkValidationError as exc:
        raise ZovarkValidationError(
            f"customer_report_mismatch: could not render customer report: {exc}"
        ) from exc
    if package["customer-report.md"] != expected_report:
        _fail(
            "customer_report_mismatch",
            "customer-report.md does not match derived report",
        )


def _verification_summary(full_tape: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_count": len(EXPECTED_OUTPUT_FILES),
        "audit_entry_id": full_tape["audit_entry"]["entry_id"],
        "checks_passed": len(_VERIFIED_COMPONENTS),
        "customer_report_verified": True,
        "evidence_entries_checked": len(full_tape["raw_evidence"]),
        "failure_codes": [],
        "failure_count": 0,
        "handoff_id": full_tape["handoff"]["handoff_id"],
        "package_contract": "slice-001-proof-package/1.0",
        "replay_id": full_tape["replay_report"]["replay_state"]["replay_id"],
        "replay_state": full_tape["replay_report"]["replay_state"]["state"],
        "status": "verified",
        "tape_id": full_tape["tape_id"],
        "verdict": full_tape["verdict"]["value"],
        "verified_components": list(_VERIFIED_COMPONENTS),
    }


def _fail(code: str, message: str) -> NoReturn:
    raise ZovarkValidationError(f"{code}: {message}")
