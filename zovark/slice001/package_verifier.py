"""Offline proof-package verifier for Slice 002 Replay V2."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

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
        raise ZovarkValidationError("customer-report.md must not be empty")
    package["customer-report.md"] = report_text
    return package


def validate_loaded_proof_package(package: dict[str, Any]) -> dict[str, Any]:
    """Validate an already-loaded Slice 001 proof package."""
    if not isinstance(package, dict):
        raise ZovarkValidationError("proof package must be an object")
    if set(package) != _EXPECTED_FILE_SET:
        raise ZovarkValidationError("proof package file set is invalid")
    for filename in JSON_OUTPUT_FILES:
        if not isinstance(package[filename], (dict, list)):
            raise ZovarkValidationError(f"{filename} must be a JSON artifact")
    if not isinstance(package["customer-report.md"], str) or not package[
        "customer-report.md"
    ]:
        raise ZovarkValidationError("customer-report.md must be non-empty text")

    full_tape = _reconstruct_verified_tape(package)
    _validate_customer_report(package, full_tape)
    return _verification_summary(full_tape)


def verify_proof_package(package_dir: str | Path) -> dict[str, Any]:
    """Load and verify a Slice 001 proof-package directory offline."""
    package = load_proof_package(package_dir)
    return validate_loaded_proof_package(package)


def _validate_package_dir(package_dir: Path) -> None:
    if not package_dir.exists():
        raise ZovarkValidationError("proof package directory does not exist")
    if not package_dir.is_dir():
        raise ZovarkValidationError("proof package path must be a directory")


def _validate_file_set(package_dir: Path) -> None:
    actual_entries = {entry.name for entry in package_dir.iterdir()}
    if actual_entries != _EXPECTED_FILE_SET:
        raise ZovarkValidationError("proof package directory file set is invalid")
    for filename in EXPECTED_OUTPUT_FILES:
        if not (package_dir / filename).is_file():
            raise ZovarkValidationError(f"{filename} must be a file")


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ZovarkValidationError(f"{path.name} is not valid JSON") from exc
    except OSError as exc:
        raise ZovarkValidationError(f"{path.name} could not be read") from exc


def _reconstruct_verified_tape(package: dict[str, Any]) -> dict[str, Any]:
    tape = deepcopy(package["investigation-tape.json"])
    if not isinstance(tape, dict):
        raise ZovarkValidationError("investigation-tape.json must be an object")
    if tape.get("state") != "closed":
        raise ZovarkValidationError("investigation-tape.json state must be closed")

    _validate_extracted_views(package, tape)

    handoff = deepcopy(package["edr-handoff.json"])
    expected_handoff = derive_handoff(tape)
    if handoff != expected_handoff:
        raise ZovarkValidationError("edr-handoff.json does not match derived handoff")
    _validate_handoff_tape_links(tape, handoff)

    with_handoff = deepcopy(tape)
    with_handoff["handoff"] = handoff
    audit_entry = deepcopy(package["audit-chain-entry.json"])
    expected_audit_entry = derive_audit_entry(with_handoff)
    if audit_entry != expected_audit_entry:
        raise ZovarkValidationError(
            "audit-chain-entry.json does not match derived audit entry"
        )
    if audit_entry["sequence"] != 1 or audit_entry["prev_entry_hash"] != GENESIS_HASH:
        raise ZovarkValidationError("first audit entry must anchor to genesis")

    sealed_tape = deepcopy(with_handoff)
    sealed_tape["audit_entry"] = audit_entry

    replay_report = deepcopy(package["replay-report.json"])
    expected_replay_report = derive_replay_report(sealed_tape)
    if replay_report != expected_replay_report:
        raise ZovarkValidationError(
            "replay-report.json does not match derived replay report"
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
            raise ZovarkValidationError(f"investigation-tape.json is missing {tape_field}")
        if package[filename] != tape[tape_field]:
            raise ZovarkValidationError(f"{filename} does not match investigation tape")


def _validate_handoff_tape_links(
    tape: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    if tape.get("handoff_ref") != handoff["handoff_id"]:
        raise ZovarkValidationError("investigation-tape handoff_ref is invalid")
    expected_summary = {
        "action_type": handoff["action_type"],
        "approval_mode": handoff["approval_mode"],
        "execution_status": handoff["execution_result"]["status"],
        "target": {
            "identifier": handoff["target"]["identifier"],
            "kind": handoff["target"]["kind"],
        },
    }
    if tape.get("handoff_summary") != expected_summary:
        raise ZovarkValidationError("investigation-tape handoff_summary is invalid")


def _validate_customer_report(
    package: dict[str, Any],
    full_tape: dict[str, Any],
) -> None:
    expected_report = render_customer_report(full_tape)
    if package["customer-report.md"] != expected_report:
        raise ZovarkValidationError("customer-report.md does not match derived report")


def _verification_summary(full_tape: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_count": len(EXPECTED_OUTPUT_FILES),
        "audit_entry_id": full_tape["audit_entry"]["entry_id"],
        "customer_report_verified": True,
        "evidence_entries_checked": len(full_tape["raw_evidence"]),
        "handoff_id": full_tape["handoff"]["handoff_id"],
        "package_contract": "slice-001-proof-package/1.0",
        "replay_id": full_tape["replay_report"]["replay_state"]["replay_id"],
        "replay_state": full_tape["replay_report"]["replay_state"]["state"],
        "status": "verified",
        "tape_id": full_tape["tape_id"],
        "verdict": full_tape["verdict"]["value"],
    }
