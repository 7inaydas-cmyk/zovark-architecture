"""Local proof/Replay testbed runner for static V3-like fixtures.

Feature lifecycle: this runner is local workflow plumbing for F-002, the Replay
engine and tape recorder feature recorded in the archived ownership metadata.
It does not introduce AlertForge ingest, live integrations, benchmarks, or a
customer-ready product surface.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from zovark.slice001 import ZovarkValidationError
from zovark.slice001.cli import render_verification_failure
from zovark.slice001.package_verifier import (
    V2_MARKER_FILE,
    V2_PACKAGE_CONTRACT,
    verify_proof_package,
)
from zovark.slice001.v3_adapter import (
    V1_PACKAGE_CONTRACT,
    write_proof_package_from_v3_fixture,
)
from zovark.slice001.writer import EXPECTED_OUTPUT_FILES


PACKAGE_VERSION_CONTRACTS = {
    "v1": V1_PACKAGE_CONTRACT,
    "v2": V2_PACKAGE_CONTRACT,
}


def main(argv: Sequence[str] | None = None) -> int:
    """Generate a local V1 or explicit V2 proof package and verify it offline."""
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else sys.argv[1:])
    input_path = Path(args.input)
    output_dir = Path(args.output)
    package_version = args.package_version
    package_contract = PACKAGE_VERSION_CONTRACTS[package_version]

    try:
        fixture = _load_fixture(input_path)
        manifest = write_proof_package_from_v3_fixture(
            fixture,
            output_dir,
            tenant_id=args.tenant_id,
            proof_package_version=package_contract,
        )
        verification = None if args.no_verify else verify_proof_package(output_dir)
    except _TestbedError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except ZovarkValidationError as exc:
        if not args.no_verify and _looks_like_verifier_failure(exc):
            print(render_verification_failure(exc), file=sys.stderr)
        else:
            print(f"Local testbed validation failed: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"Local testbed I/O error: {exc}", file=sys.stderr)
        return 4

    print(
        render_success(
            manifest,
            output_dir=output_dir,
            package_version=package_version,
            verification=verification,
        )
    )
    return 0


def render_success(
    manifest: dict[str, str],
    *,
    output_dir: Path,
    package_version: str,
    verification: dict | None,
) -> str:
    """Render a deterministic local-run summary."""
    expected_files = list(EXPECTED_OUTPUT_FILES)
    if package_version == "v2":
        expected_files.append(V2_MARKER_FILE)
    lines = [
        "Zovark local proof/Replay testbed complete.",
        f"Package version: {package_version}",
        f"Output directory: {output_dir}",
        "",
        "Generated artifacts:",
    ]
    lines.extend(f"- {filename}: {manifest[filename]}" for filename in expected_files)
    lines.append("")
    if verification is None:
        lines.append("Offline Replay verification: skipped")
    else:
        lines.extend(
            [
                "Offline Replay verification: succeeded",
                f"Verification status: {verification['status']}",
                f"Replay state: {verification['replay_state']}",
                f"Failure count: {verification['failure_count']}",
                f"Package contract: {verification['package_contract']}",
            ]
        )
        package_version_contract = verification.get("package_version")
        if package_version_contract is not None:
            lines.append(f"Package version contract: {package_version_contract}")
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zovark.slice001.local_testbed",
        description=(
            "Run the local static V3-like fixture -> proof package -> offline "
            "Replay verification workflow."
        ),
    )
    parser.add_argument("--input", required=True, help="Sanitized V3-like JSON fixture")
    parser.add_argument("--output", required=True, help="Local output directory")
    parser.add_argument(
        "--package-version",
        choices=sorted(PACKAGE_VERSION_CONTRACTS),
        default="v2",
        help="Proof package version to generate",
    )
    parser.add_argument("--tenant-id", default=None, help="Optional tenant identifier")
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Generate only; skip offline Replay verification",
    )
    return parser


def _load_fixture(input_path: Path) -> dict:
    if not input_path.exists() or not input_path.is_file():
        raise _TestbedError(1, f"Local testbed input not found: {input_path}")
    try:
        fixture = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _TestbedError(
            2,
            f"Local testbed input is not valid JSON: {input_path}",
        ) from exc
    if not isinstance(fixture, dict):
        raise ZovarkValidationError("local testbed fixture must be a JSON object")
    return fixture


def _looks_like_verifier_failure(exc: ZovarkValidationError) -> bool:
    message = str(exc)
    return ":" in message and message.partition(":")[0].replace("_", "").isalnum()


class _TestbedError(Exception):
    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


if __name__ == "__main__":
    raise SystemExit(main())
