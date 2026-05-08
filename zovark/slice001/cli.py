"""Command-line entry point for the deterministic Slice 001 pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.audit import attach_audit_entry, derive_audit_entry
from zovark.slice001.findings import attach_findings, derive_findings
from zovark.slice001.handoff import attach_handoff, derive_handoff
from zovark.slice001.ingest import load_sample, normalize_evidence
from zovark.slice001.package_verifier import verify_proof_package
from zovark.slice001.replay import attach_replay_report, derive_replay_report
from zovark.slice001.tape import create_tape
from zovark.slice001.timeline import attach_timeline, build_initial_timeline
from zovark.slice001.verdict import attach_verdict, derive_verdict
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES, write_proof_package


def main(argv: Sequence[str] | None = None) -> int:
    """Run Slice 001 from static input to deterministic proof-package output."""
    args_list = list(argv) if argv is not None else sys.argv[1:]
    if args_list and args_list[0] == "verify":
        return _verify_main(args_list[1:])

    parser = _parser()
    args = parser.parse_args(args_list)
    input_path = Path(args.input)
    output_dir = Path(args.output)

    try:
        raw_input = _load_input(input_path)
        tape = build_completed_tape(raw_input, tenant_id=args.tenant_id)
        manifest = write_proof_package(tape, output_dir)
    except _CliError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except ZovarkValidationError as exc:
        exit_code = 4 if str(exc).startswith("output_dir ") else 3
        print(f"Slice 001 validation failed: {exc}", file=sys.stderr)
        return exit_code
    except OSError as exc:
        print(f"Slice 001 output error: {exc}", file=sys.stderr)
        return 4

    _print_success(manifest, replay_state=tape["replay_report"]["replay_state"]["state"])
    return 0


def _verify_main(argv: Sequence[str]) -> int:
    parser = _verify_parser()
    args = parser.parse_args(argv)

    try:
        summary = verify_proof_package(Path(args.package))
    except ZovarkValidationError as exc:
        print(f"Slice 001 package verification failed: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"Slice 001 package verification error: {exc}", file=sys.stderr)
        return 4

    _print_verify_success(summary)
    return 0


def build_completed_tape(raw_input: dict, *, tenant_id: str | None = None) -> dict:
    """Build the complete replay-sealed Slice 001 tape from static input."""
    evidence_entries = normalize_evidence(raw_input)
    tape = create_tape(raw_input, evidence_entries, tenant_id=tenant_id)
    timeline = build_initial_timeline(tape)
    tape = attach_timeline(tape, timeline)
    findings, no_findings_flag = derive_findings(tape)
    tape = attach_findings(tape, findings, no_findings_flag)
    verdict = derive_verdict(tape)
    tape = attach_verdict(tape, verdict)
    tape["audit_ref"] = "audit-entry-1"
    handoff = derive_handoff(tape)
    tape = attach_handoff(tape, handoff)
    audit_entry = derive_audit_entry(tape)
    tape = attach_audit_entry(tape, audit_entry)
    replay_report = derive_replay_report(tape)
    return attach_replay_report(tape, replay_report)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zovark.slice001",
        description="Run the deterministic Slice 001 proof-package pipeline.",
    )
    parser.add_argument("--input", required=True, help="Static EDR-style JSON sample")
    parser.add_argument("--output", required=True, help="Output artifact directory")
    parser.add_argument("--tenant-id", default="tenant-001", help="Tenant identifier")
    return parser


def _verify_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zovark.slice001 verify",
        description="Verify an exported Slice 001 proof package offline.",
    )
    parser.add_argument("--package", required=True, help="Proof-package directory")
    return parser


def _load_input(input_path: Path) -> dict:
    if not input_path.exists() or not input_path.is_file():
        raise _CliError(1, f"Slice 001 input not found: {input_path}")
    try:
        return load_sample(input_path)
    except ZovarkValidationError as exc:
        if str(exc).startswith("invalid Slice 001 sample"):
            raise _CliError(2, f"Slice 001 input is not valid JSON: {input_path}") from exc
        raise


def _print_success(manifest: dict[str, str], *, replay_state: str) -> None:
    print("Slice 001 complete.")
    for filename in EXPECTED_OUTPUT_FILES:
        print(f"  {filename:<24} \u2192 {manifest[filename]}")
    print(f"Replay: {replay_state}")


def _print_verify_success(summary: dict) -> None:
    print("Slice 001 package verification succeeded.")
    print(f"  status: {summary['status']}")
    print(f"  package_contract: {summary['package_contract']}")
    print(f"  artifact_count: {summary['artifact_count']}")
    print(f"  evidence_entries_checked: {summary['evidence_entries_checked']}")
    print(f"  verdict: {summary['verdict']}")
    print(f"  replay_state: {summary['replay_state']}")
    print(f"  tape_id: {summary['tape_id']}")


class _CliError(Exception):
    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
